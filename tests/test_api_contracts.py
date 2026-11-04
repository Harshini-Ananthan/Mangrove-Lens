from datetime import date

import pytest
from fastapi import BackgroundTasks, HTTPException

from src.api.routes import MonitoringRunRequest, get_aoi, get_grid, health_check, run_monitoring
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
