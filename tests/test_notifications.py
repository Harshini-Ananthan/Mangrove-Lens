import pytest
from fastapi import HTTPException
from email.message import EmailMessage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes import AlertApprovalRequest, approve_alert, dispatch_alert, require_operator
from src.database.db import Base
from src.database.models import AlertOutboxRecord
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


def _alert_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_pending_validation_alert_cannot_bypass_model_approval():
    db = _alert_db()
    alert = AlertOutboxRecord(
        decision_id=1, channel="email", status="pending_validation", payload={"severity": "high"}
    )
    db.add(alert)
    db.commit()
    with pytest.raises(HTTPException) as exc:
        approve_alert(alert.id, AlertApprovalRequest(approved_by="operator"), db, None)
    assert exc.value.status_code == 409
    db.close()


def test_dashboard_alert_cannot_be_dispatched_as_external_notification():
    db = _alert_db()
    alert = AlertOutboxRecord(
        decision_id=1, channel="dashboard", status="sent", payload={"severity": "moderate"}
    )
    db.add(alert)
    db.commit()
    with pytest.raises(HTTPException) as exc:
        dispatch_alert(alert.id, db, None)
    assert exc.value.status_code == 409
    db.close()


def test_configured_email_sends_pdf_report_attachment(monkeypatch, tmp_path):
    report = tmp_path / "monitoring-report.pdf"
    report.write_bytes(b"%PDF-1.4 verified report")
    sent = []

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            assert host == "smtp.example.test"

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def starttls(self):
            pass

        def login(self, username, password):
            assert (username, password) == ("sender@example.test", "secret")

        def send_message(self, message: EmailMessage):
            sent.append(message)

    monkeypatch.setattr(settings, "ENABLE_EXTERNAL_NOTIFICATIONS", True)
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.example.test")
    monkeypatch.setattr(settings, "SMTP_PORT", 587)
    monkeypatch.setattr(settings, "SMTP_USERNAME", "sender@example.test")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "secret")
    monkeypatch.setattr(settings, "ALERT_EMAIL_TO", "official@example.test")
    monkeypatch.setattr("src.services.notifications.smtplib.SMTP", FakeSMTP)

    send_channel("email", {
        "severity": "critical", "period_start": "2026-03-01", "evidence": ["verified"],
        "notification_type": "risk_alert", "report_path": str(report),
    })

    assert len(sent) == 1
    assert sent[0]["To"] == "official@example.test"
    attachments = list(sent[0].iter_attachments())
    assert len(attachments) == 1
    assert attachments[0].get_filename() == "monitoring-report.pdf"
