from __future__ import annotations

import asyncio
import datetime
import json
import uuid
import hmac
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.db import SessionLocal, get_db
from src.database.models import (
    AlertOutboxRecord, MonthlyFeatureRecord, MonitoringJobRecord, OperationEventRecord,
    RiskDecisionRecord,
)
from src.models.forecast import ForecastModel
from src.providers import get_satellite_provider
from src.services.monitoring import MonitoringWorkflow
from src.services.notifications import send_channel
from src.services.operations import emit_operation_event
from src.services.grid import build_grid
from src.services.grid import resolve_region_geometry
from src.providers.earth_engine import EarthEngineProvider
from src.services.reporting import report_path
from src.utils.config import settings

router = APIRouter()


class MonitoringRunRequest(BaseModel):
    region_id: str = "sundarbans-transboundary-v1"
    period_start: datetime.date
    refresh: bool = False


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
    ready = satellite_ready and database["ready"] and model.ready
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
    earliest = datetime.date.fromisoformat(settings.ANALYSIS_START_DATE).replace(day=1)
    latest_complete = datetime.date.today().replace(day=1) - relativedelta(months=1)
    if period < earliest or period > latest_complete:
        raise HTTPException(
            status_code=422,
            detail=f"period_start must be between {earliest} and {latest_complete}",
        )
    provider = get_satellite_provider()
    provider_ready, provider_detail = provider.readiness()
    if not provider_ready:
        raise HTTPException(status_code=503, detail=provider_detail)
    try:
        resolve_region_geometry(request.region_id, get_aoi()["features"][0]["geometry"])
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    prior_valid = db.query(MonthlyFeatureRecord).filter(
        MonthlyFeatureRecord.region_id == request.region_id,
        MonthlyFeatureRecord.period_start < period,
        MonthlyFeatureRecord.quality_status == "valid",
    ).count()
    if prior_valid < 12:
        raise HTTPException(
            status_code=422,
            detail=f"At least 12 prior valid monthly observations are required; found {prior_valid}",
        )
    existing = db.query(MonitoringJobRecord).filter_by(
        region_id=request.region_id, period_start=period, provider=provider.name
    ).filter(MonitoringJobRecord.status.in_(["queued", "running", "completed"])).order_by(
        MonitoringJobRecord.requested_at.desc()
    ).first()
    if existing and not request.refresh:
        feature = db.query(MonthlyFeatureRecord).filter_by(
            region_id=request.region_id, period_start=period, provider=provider.name
        ).one_or_none()
        emit_operation_event(
            "api", "verified_data_reused",
            "Using persisted results from a completed live satellite analysis",
            job_id=existing.id, region_id=request.region_id, period_start=period,
            details={
                "provider": provider.name,
                "quality_status": feature.quality_status if feature else None,
                "query_executed_at": (feature.provenance or {}).get("query_executed_at") if feature else None,
                "reason": "interactive speed optimization; no mock or synthetic substitution",
            },
            db=db,
        )
        return {
            "job_id": existing.id, "status": existing.status, "deduplicated": True,
            "data_source": "persisted_live_satellite_observation",
        }
    job = MonitoringJobRecord(
        id=str(uuid.uuid4()), region_id=request.region_id, period_start=period,
        status="queued", provider=provider.name, checkpoint="created",
    )
    db.add(job)
    db.commit()
    emit_operation_event(
        "api", "job_queued", "New live monitoring job queued",
        job_id=job.id, region_id=request.region_id, period_start=period,
        details={"provider": provider.name, "refresh_requested": request.refresh}, db=db,
    )
    background_tasks.add_task(_run_monitoring_job, job.id, request.region_id, period)
    return {
        "job_id": job.id, "status": "queued", "deduplicated": False,
        "data_source": "live_satellite_query",
    }


@router.get("/monitoring/features")
def get_features(
    region_id: str = "sundarbans-transboundary-v1", limit: int = Query(120, ge=1, le=500), db: Session = Depends(get_db)
):
    return db.query(MonthlyFeatureRecord).filter_by(region_id=region_id).order_by(
        MonthlyFeatureRecord.period_start.desc()
    ).limit(min(limit, 500)).all()


@router.get("/monitoring/decisions")
def get_decisions(
    region_id: str = "sundarbans-transboundary-v1", limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)
):
    return db.query(RiskDecisionRecord).filter_by(region_id=region_id).order_by(
        RiskDecisionRecord.period_start.desc()
    ).limit(min(limit, 500)).all()


@router.get("/monitoring/jobs")
def get_jobs(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return db.query(MonitoringJobRecord).order_by(MonitoringJobRecord.started_at.desc()).limit(
        min(limit, 200)
    ).all()


def _operation_event_payload(event: OperationEventRecord) -> dict:
    return {
        "id": event.id,
        "timestamp": event.created_at.isoformat(timespec="milliseconds") + "Z",
        "source": event.source,
        "stage": event.stage,
        "level": event.level,
        "message": event.message,
        "job_id": event.job_id,
        "region_id": event.region_id,
        "period_start": event.period_start.isoformat() if event.period_start else None,
        "details": event.details or {},
    }


@router.get("/operations/events")
def get_operation_events(
    after_id: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
    latest: bool = False,
    db: Session = Depends(get_db),
    _: None = Depends(require_operator),
):
    query = db.query(OperationEventRecord).filter(OperationEventRecord.id > after_id)
    if latest:
        rows = list(reversed(query.order_by(OperationEventRecord.id.desc()).limit(limit).all()))
    else:
        rows = query.order_by(OperationEventRecord.id.asc()).limit(limit).all()
    return [_operation_event_payload(row) for row in rows]


@router.get("/operations/events/stream")
def stream_operation_events(
    after_id: int = Query(0, ge=0), _: None = Depends(require_operator),
):
    """Stream persisted operational evidence without controlling the pipeline."""

    async def event_stream():
        cursor = after_id
        while True:
            session = SessionLocal()
            try:
                rows = session.query(OperationEventRecord).filter(
                    OperationEventRecord.id > cursor
                ).order_by(OperationEventRecord.id.asc()).limit(100).all()
                payloads = [_operation_event_payload(row) for row in rows]
            finally:
                session.close()
            if payloads:
                for payload in payloads:
                    cursor = payload["id"]
                    yield (
                        f"id: {cursor}\n"
                        "event: operation\n"
                        f"data: {json.dumps(payload, separators=(',', ':'), default=str)}\n\n"
                    )
            else:
                yield f": heartbeat {datetime.datetime.utcnow().isoformat()}Z\n\n"
            await asyncio.sleep(0.75)

    return StreamingResponse(
        event_stream(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/alerts/outbox")
def get_alert_outbox(status_filter: str | None = None, limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
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
    if alert.status == "pending_validation":
        raise HTTPException(status_code=409, detail="Alert is blocked until the model is production-approved")
    if alert.status != "pending_review":
        raise HTTPException(status_code=409, detail=f"Alert status {alert.status} cannot be approved")
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
    if alert.channel == "dashboard":
        raise HTTPException(status_code=409, detail="Dashboard alerts are delivered through the outbox feed")
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


@router.get("/map/tiles")
def get_live_map_tiles(period_start: datetime.date, layer: str = "ndvi"):
    period = period_start.replace(day=1)
    latest_complete = datetime.date.today().replace(day=1) - relativedelta(months=1)
    if period > latest_complete:
        raise HTTPException(status_code=422, detail=f"period_start must not exceed {latest_complete}")
    provider = get_satellite_provider()
    if not isinstance(provider, EarthEngineProvider):
        raise HTTPException(status_code=409, detail="Live map tiles require SATELLITE_PROVIDER=earth_engine")
    try:
        return provider.visualization_tile(get_aoi()["features"][0]["geometry"], period, layer)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/reports/{decision_id}")
def download_report(decision_id: int, db: Session = Depends(get_db)):
    if db.get(RiskDecisionRecord, decision_id) is None:
        raise HTTPException(status_code=404, detail="Decision not found")
    path = report_path(decision_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Report has not been generated for this decision")
    return FileResponse(
        path, media_type="application/pdf", filename=path.name,
        headers={"Cache-Control": "no-store"},
    )
