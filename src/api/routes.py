from __future__ import annotations

import datetime
import json
import uuid
import hmac
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.db import SessionLocal, get_db
from src.database.models import AlertOutboxRecord, MonthlyFeatureRecord, MonitoringJobRecord, RiskDecisionRecord
from src.models.forecast import ForecastModel
from src.providers import get_satellite_provider
from src.services.monitoring import MonitoringWorkflow
from src.services.notifications import send_channel
from src.services.grid import build_grid
from src.utils.config import settings

router = APIRouter()


class MonitoringRunRequest(BaseModel):
    region_id: str = "sundarbans-transboundary-v1"
    period_start: datetime.date


class AlertApprovalRequest(BaseModel):
    approved_by: str


def require_operator(x_api_key: str | None = Header(default=None)):
    if settings.API_KEY and (x_api_key is None or not hmac.compare_digest(x_api_key, settings.API_KEY)):
        raise HTTPException(status_code=401, detail="Invalid or missing operator API key")


def _run_monitoring_job(job_id: str, region_id: str, period_start: datetime.date):
    db = SessionLocal()
    try:
        MonitoringWorkflow(
            provider=get_satellite_provider(), model=ForecastModel(), db=db, aoi_path=settings.AOI_PATH
        ).run(region_id, period_start, job_id=job_id)
    finally:
        db.close()


@router.get("/health")
def health_check():
    provider = get_satellite_provider()
    ready, detail = provider.readiness()
    model = ForecastModel()
    return {
        "status": "ok",
        "service": "Mangrove Lens API",
        "environment": settings.ENVIRONMENT,
        "satellite": {"provider": provider.name, "ready": ready, "detail": detail},
        "model": {"ready": model.ready, "version": model.version},
    }


@router.get("/readiness")
def readiness_check(db: Session = Depends(get_db)):
    provider = get_satellite_provider()
    satellite_ready, satellite_detail = provider.readiness()
    try:
        db.execute(text("SELECT 1"))
        database = {"ready": True, "detail": "database query succeeded"}
    except Exception as exc:
        database = {"ready": False, "detail": str(exc)}
    model = ForecastModel()
    ready = satellite_ready and database["ready"]
    return {
        "ready": ready,
        "database": database,
        "satellite": {"ready": satellite_ready, "detail": satellite_detail},
        "model": {"ready": model.ready, "version": model.version},
    }


@router.post("/monitoring/run", status_code=status.HTTP_202_ACCEPTED)
def run_monitoring(
    request: MonitoringRunRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db),
    _: None = Depends(require_operator),
):
    period = request.period_start.replace(day=1)
    provider = get_satellite_provider()
    existing = db.query(MonitoringJobRecord).filter_by(
        region_id=request.region_id, period_start=period, provider=provider.name
    ).filter(MonitoringJobRecord.status.in_(["queued", "running", "completed"])).order_by(
        MonitoringJobRecord.requested_at.desc()
    ).first()
    if existing:
        return {"job_id": existing.id, "status": existing.status, "deduplicated": True}
    job = MonitoringJobRecord(
        id=str(uuid.uuid4()), region_id=request.region_id, period_start=period,
        status="queued", provider=provider.name, checkpoint="created",
    )
    db.add(job)
    db.commit()
    background_tasks.add_task(_run_monitoring_job, job.id, request.region_id, period)
    return {"job_id": job.id, "status": "queued", "deduplicated": False}


@router.get("/monitoring/features")
def get_features(
    region_id: str = "sundarbans-transboundary-v1", limit: int = 120, db: Session = Depends(get_db)
):
    return db.query(MonthlyFeatureRecord).filter_by(region_id=region_id).order_by(
        MonthlyFeatureRecord.period_start.desc()
    ).limit(min(limit, 500)).all()


@router.get("/monitoring/decisions")
def get_decisions(
    region_id: str = "sundarbans-transboundary-v1", limit: int = 100, db: Session = Depends(get_db)
):
    return db.query(RiskDecisionRecord).filter_by(region_id=region_id).order_by(
        RiskDecisionRecord.period_start.desc()
    ).limit(min(limit, 500)).all()


@router.get("/monitoring/jobs")
def get_jobs(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(MonitoringJobRecord).order_by(MonitoringJobRecord.started_at.desc()).limit(
        min(limit, 200)
    ).all()


@router.get("/alerts/outbox")
def get_alert_outbox(status_filter: str | None = None, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(AlertOutboxRecord)
    if status_filter:
        query = query.filter_by(status=status_filter)
    return query.order_by(AlertOutboxRecord.created_at.desc()).limit(min(limit, 500)).all()


@router.post("/alerts/outbox/{alert_id}/approve")
def approve_alert(
    alert_id: int, request: AlertApprovalRequest, db: Session = Depends(get_db),
    _: None = Depends(require_operator),
):
    alert = db.get(AlertOutboxRecord, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.channel == "dashboard":
        raise HTTPException(status_code=409, detail="Dashboard alerts do not require approval")
    alert.status = "approved"
    alert.approved_by = request.approved_by
    alert.approved_at = datetime.datetime.utcnow()
    db.commit()
    return {"id": alert.id, "status": alert.status}


@router.post("/alerts/outbox/{alert_id}/dispatch")
def dispatch_alert(
    alert_id: int, db: Session = Depends(get_db), _: None = Depends(require_operator)
):
    alert = db.get(AlertOutboxRecord, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.status not in {"approved", "failed"}:
        raise HTTPException(status_code=409, detail=f"Alert status {alert.status} cannot be dispatched")
    try:
        alert.attempts += 1
        send_channel(alert.channel, alert.payload)
        alert.status, alert.sent_at, alert.last_error = "sent", datetime.datetime.utcnow(), None
        db.commit()
        return {"id": alert.id, "status": "sent"}
    except Exception as exc:
        alert.status, alert.last_error = "failed", str(exc)
        db.commit()
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/aoi")
def get_aoi():
    return json.loads(Path(settings.AOI_PATH).read_text(encoding="utf-8"))


@router.get("/grid")
def get_grid(cell_size_km: float = 5.0):
    if cell_size_km < 1 or cell_size_km > 25:
        raise HTTPException(status_code=422, detail="cell_size_km must be between 1 and 25")
    return build_grid(get_aoi()["features"][0]["geometry"], cell_size_km)
