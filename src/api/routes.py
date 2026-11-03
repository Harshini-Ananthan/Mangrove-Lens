from __future__ import annotations

import datetime
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import MonthlyFeatureRecord, MonitoringJobRecord, RiskDecisionRecord
from src.models.forecast import ForecastModel
from src.providers import get_satellite_provider
from src.services.monitoring import MonitoringWorkflow
from src.utils.config import settings

router = APIRouter()


class MonitoringRunRequest(BaseModel):
    region_id: str = "sundarbans-transboundary-v1"
    period_start: datetime.date


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


@router.post("/monitoring/run")
def run_monitoring(request: MonitoringRunRequest, db: Session = Depends(get_db)):
    workflow = MonitoringWorkflow(
        provider=get_satellite_provider(), model=ForecastModel(), db=db, aoi_path=settings.AOI_PATH
    )
    try:
        return workflow.run(request.region_id, request.period_start)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


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


@router.get("/aoi")
def get_aoi():
    return json.loads(Path(settings.AOI_PATH).read_text(encoding="utf-8"))
