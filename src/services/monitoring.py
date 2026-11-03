from __future__ import annotations

import json
import uuid
from datetime import date, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from src.database.models import MonitoringJobRecord, MonthlyFeatureRecord, RiskDecisionRecord
from src.models.forecast import ForecastModel
from src.providers.base import SatelliteProvider
from src.services.decision import assess_risk


def load_operational_geometry(path: str) -> dict:
    collection = json.loads(Path(path).read_text(encoding="utf-8"))
    return collection["features"][0]["geometry"]


class MonitoringWorkflow:
    def __init__(self, provider: SatelliteProvider, model: ForecastModel, db: Session, aoi_path: str):
        self.provider, self.model, self.db, self.aoi_path = provider, model, db, aoi_path

    def run(self, region_id: str, period_start: date) -> dict:
        period_start = period_start.replace(day=1)
        job = MonitoringJobRecord(
            id=str(uuid.uuid4()), region_id=region_id, period_start=period_start,
            status="running", provider=self.provider.name, checkpoint="acquisition",
        )
        self.db.add(job)
        self.db.commit()
        try:
            observation = self.provider.monthly_observation(
                region_id, load_operational_geometry(self.aoi_path), period_start
            )
            feature = self.store_observation(observation)
            job.checkpoint = "prediction"
            self.db.commit()
            prediction = self.model.predict(self._prediction_features(region_id, feature))
            decision = assess_risk(observation, prediction)
            record = self._upsert_decision(region_id, period_start, prediction, decision)
            job.status, job.checkpoint, job.finished_at = "completed", "reported", datetime.utcnow()
            self.db.commit()
            return {
                "job_id": job.id,
                "observation": observation.model_dump(mode="json"),
                "prediction": prediction.model_dump(mode="json"),
                "decision": {**decision.model_dump(mode="json"), "severity": decision.severity.label},
                "decision_id": record.id,
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
            "co_mean": current.co_mean,
            "ndmi_mean": current.ndmi_mean,
            "vv_mean": current.vv_mean,
            "vh_mean": current.vh_mean,
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
