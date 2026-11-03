import pytest
from fastapi import HTTPException

from src.api.routes import require_operator
from src.services.notifications import configured_channels, send_channel
from src.utils.config import settings


def test_dashboard_channel_is_always_available_and_noop():
    assert "dashboard" in configured_channels()
    assert send_channel("dashboard", {"severity": "moderate", "evidence": []}) is None


def test_external_channel_is_blocked_by_default():
    with pytest.raises(RuntimeError, match="disabled"):
        send_channel("email", {"severity": "high", "evidence": []})


def test_operator_key_is_enforced_when_configured(monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "secret")
    with pytest.raises(HTTPException) as exc:
        require_operator("wrong")
    assert exc.value.status_code == 401
    assert require_operator("secret") is None
