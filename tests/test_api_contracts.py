from datetime import date

import pytest
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes import MonitoringRunRequest, get_aoi, get_grid, health_check, run_monitoring
from src.database.db import Base
from src.providers.demo import DemoSatelliteProvider
from src.utils.config import settings


def test_health_contract_exposes_provider_and_model():
    payload = health_check()
    assert payload["status"] == "ok"
    assert payload["satellite"]["provider"] == settings.SATELLITE_PROVIDER
    assert isinstance(payload["satellite"]["ready"], bool)
    assert "version" in payload["model"]


def test_aoi_is_transboundary_operational_envelope():
    payload = get_aoi()
    assert payload["type"] == "FeatureCollection"
    assert payload["features"][0]["properties"]["id"] == "sundarbans-transboundary-v1"


def test_monitoring_rejects_incomplete_future_period_before_acquisition():
    request = MonitoringRunRequest(period_start=date(2099, 1, 1))
    with pytest.raises(HTTPException) as exc:
        run_monitoring(request, BackgroundTasks(), None, None)
    assert exc.value.status_code == 422


def test_grid_rejects_unsupported_cell_size():
    with pytest.raises(HTTPException) as exc:
        get_grid(0.5)
    assert exc.value.status_code == 422


def test_monitoring_rejects_region_without_twelve_prior_months(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    monkeypatch.setattr("src.api.routes.get_satellite_provider", lambda: DemoSatelliteProvider())
    request = MonitoringRunRequest(period_start=date(2020, 1, 1))
    with pytest.raises(HTTPException) as exc:
        run_monitoring(request, BackgroundTasks(), db, None)
    assert exc.value.status_code == 422
    assert "12 prior valid" in exc.value.detail
    db.close()
