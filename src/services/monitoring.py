from __future__ import annotations

import json
import uuid
from datetime import date, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from src.database.models import AlertOutboxRecord, MonitoringJobRecord, MonthlyFeatureRecord, RiskDecisionRecord
from src.models.forecast import ForecastModel
from src.providers.base import SatelliteProvider
from src.services.decision import assess_risk
from src.services.grid import resolve_region_geometry
from src.services.notifications import configured_channels, send_channel
from src.services.reporting import generate_monitoring_report
from src.utils.config import settings


def load_operational_geometry(path: str) -> dict:
    collection = json.loads(Path(path).read_text(encoding="utf-8"))
    return collection["features"][0]["geometry"]


class MonitoringWorkflow:
    def __init__(self, provider: SatelliteProvider, model: ForecastModel, db: Session, aoi_path: str):
        self.provider, self.model, self.db, self.aoi_path = provider, model, db, aoi_path

    def run(self, region_id: str, period_start: date, job_id: str | None = None) -> dict:
        period_start = period_start.replace(day=1)
        job = self.db.get(MonitoringJobRecord, job_id) if job_id else None
        if job is None:
            job = MonitoringJobRecord(
                id=job_id or str(uuid.uuid4()), region_id=region_id, period_start=period_start,
                status="running", provider=self.provider.name, checkpoint="acquisition",
            )
            self.db.add(job)
        else:
            job.status, job.checkpoint, job.started_at, job.error = "running", "acquisition", datetime.utcnow(), None
        self.db.commit()
        try:
            observation = self.provider.monthly_observation(
                region_id,
                resolve_region_geometry(region_id, load_operational_geometry(self.aoi_path)),
                period_start,
            )
            feature = self.store_observation(observation)
            job.checkpoint = "prediction"
            self.db.commit()
            prediction = self.model.predict(self._prediction_features(region_id, feature))
            decision = assess_risk(observation, prediction)
            record = self._upsert_decision(region_id, period_start, prediction, decision)
            generated_report, report_error = None, None
            try:
                images = (
                    self.provider.report_images(
                        resolve_region_geometry(region_id, load_operational_geometry(self.aoi_path)),
                        period_start,
                        settings.REPORT_IMAGE_DIMENSIONS,
                    )
                    if hasattr(self.provider, "report_images")
                    else {}
                )
                generated_report = generate_monitoring_report(
                    record.id, observation, prediction, decision, images, self._system_audit()
                )
            except Exception as exc:
                report_error = str(exc)
            self._queue_alerts(record, decision, generated_report)
            job.status, job.checkpoint, job.finished_at = "completed", "reported", datetime.utcnow()
            self.db.commit()
            return {
                "job_id": job.id,
                "observation": observation.model_dump(mode="json"),
                "prediction": prediction.model_dump(mode="json"),
                "decision": {**decision.model_dump(mode="json"), "severity": decision.severity.label},
                "decision_id": record.id,
                "report_path": str(generated_report) if generated_report else None,
                "report_error": report_error,
            }
        except Exception as exc:
            job.status, job.error, job.finished_at = "failed", str(exc), datetime.utcnow()
            self.db.commit()
            raise

    def store_observation(self, observation):
        record = self.db.query(MonthlyFeatureRecord).filter_by(
            region_id=observation.region_id,
            period_start=observation.period_start,
            provider=observation.provider,
        ).one_or_none() or MonthlyFeatureRecord(
            region_id=observation.region_id,
            period_start=observation.period_start,
            provider=observation.provider,
        )
        record.period_end = observation.period_end
        for name in ("ndvi_mean", "ndvi_p10", "ndvi_p90", "ndmi_mean", "vv_mean", "vh_mean", "co_mean"):
            setattr(record, name, getattr(observation, name))
        record.valid_pixel_fraction = observation.quality.valid_pixel_fraction
        record.quality_status = observation.quality.status
        record.quality = observation.quality.model_dump(mode="json")
        record.provenance = {**observation.provenance, "sources": observation.source_collections}
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def _queue_alerts(self, decision_record, decision, generated_report=None):
        payload = {
            "decision_id": decision_record.id,
            "region_id": decision_record.region_id,
            "period_start": decision_record.period_start.isoformat(),
            "severity": decision.severity.label,
            "risk_score": decision.score,
            "evidence": decision.evidence,
            "recommendations": decision.recommendations,
            "notification_type": "risk_alert" if decision.severity.value >= 2 else "monthly_report",
            "report_path": str(generated_report) if generated_report else None,
        }
        channels = configured_channels()
        if decision.severity.value < 2:
            channels = [channel for channel in channels if channel == "email" and settings.AUTO_EMAIL_REPORTS]
        dispatchable = []
        for channel in channels:
            existing = self.db.query(AlertOutboxRecord).filter_by(
                decision_id=decision_record.id, channel=channel
            ).one_or_none()
            if existing is None:
                if channel == "dashboard":
                    status = "sent"
                elif self.model.manifest.get("production_approved"):
                    status = "pending_review" if settings.REQUIRE_ALERT_APPROVAL else "approved"
                else:
                    status = "pending_validation"
                alert = AlertOutboxRecord(
                    decision_id=decision_record.id,
                    channel=channel,
                    status=status,
                    payload=payload,
                    sent_at=datetime.utcnow() if channel == "dashboard" else None,
                )
                self.db.add(alert)
                dispatchable.append(alert)
        self.db.commit()
        if not settings.ENABLE_EXTERNAL_NOTIFICATIONS:
            return
        for alert in dispatchable:
            if alert.channel == "dashboard" or alert.status != "approved":
                continue
            try:
                alert.attempts += 1
                send_channel(alert.channel, alert.payload)
                alert.status, alert.sent_at, alert.last_error = "sent", datetime.utcnow(), None
            except Exception as exc:
                alert.status, alert.last_error = "failed", str(exc)
        self.db.commit()

    def _prediction_features(self, region_id: str, current: MonthlyFeatureRecord) -> dict[str, float]:
        history = self.db.query(MonthlyFeatureRecord).filter(
            MonthlyFeatureRecord.region_id == region_id,
            MonthlyFeatureRecord.period_start < current.period_start,
            MonthlyFeatureRecord.quality_status == "valid",
        ).order_by(MonthlyFeatureRecord.period_start.desc()).limit(12).all()
        if len(history) < 12:
            raise ValueError("At least 12 prior valid monthly observations are required for prediction")
        return {
            "actual_ndvi": current.ndvi_mean,
            "ndvi_lag_1": history[0].ndvi_mean,
            "ndvi_lag_12": history[11].ndvi_mean,
            "ndvi_roll_3": sorted([row.ndvi_mean for row in history[:3]])[1],
            "co_lag_1": history[0].co_mean,
            "ndmi_lag_1": history[0].ndmi_mean,
            "vv_lag_1": history[0].vv_mean,
            "vh_lag_1": history[0].vh_mean,
            "month": current.period_start.month,
        }

    def _upsert_decision(self, region_id, period_start, prediction, decision):
        record = self.db.query(RiskDecisionRecord).filter_by(
            region_id=region_id, period_start=period_start, rule_version=decision.rule_version
        ).one_or_none() or RiskDecisionRecord(
            region_id=region_id, period_start=period_start, rule_version=decision.rule_version
        )
        record.severity = decision.severity.label
        record.risk_score = decision.score
        record.model_version = prediction.model_version
        record.expected_ndvi = prediction.expected_ndvi
        record.anomaly_score = prediction.anomaly_score
        record.evidence = decision.evidence
        record.recommendations = decision.recommendations
        record.requires_human_review = decision.requires_human_review
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def _system_audit(self) -> dict:
        manifest = self.model.manifest
        return {
            "observation_count": self.db.query(MonthlyFeatureRecord).count(),
            "valid_count": self.db.query(MonthlyFeatureRecord).filter_by(quality_status="valid").count(),
            "low_coverage_count": self.db.query(MonthlyFeatureRecord).filter_by(quality_status="low_coverage").count(),
            "completed_job_count": self.db.query(MonitoringJobRecord).filter_by(status="completed").count(),
            "decision_count": self.db.query(RiskDecisionRecord).count(),
            "alert_count": self.db.query(AlertOutboxRecord).count(),
            "dataset_kind": manifest.get("dataset_kind"),
            "data_start": manifest.get("data_period", {}).get("start"),
            "data_end": manifest.get("data_period", {}).get("end"),
            "model_metrics": manifest.get("metrics", {}),
            "observational_gate_passed": manifest.get("observational_gate_passed", False),
            "production_approved": manifest.get("production_approved", False),
            "scheduler_enabled": settings.ENABLE_SCHEDULER,
            "automatic_email_enabled": bool(
                settings.ENABLE_EXTERNAL_NOTIFICATIONS
                and settings.AUTO_EMAIL_REPORTS
                and settings.SMTP_HOST
                and settings.ALERT_EMAIL_TO
            ),
        }
