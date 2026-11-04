from __future__ import annotations

import json
import smtplib
import urllib.parse
import urllib.request
from pathlib import Path
from email.message import EmailMessage

from src.utils.config import settings


def configured_channels() -> list[str]:
    channels = ["dashboard"]
    if settings.ALERT_EMAIL_TO and settings.SMTP_HOST:
        channels.append("email")
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        channels.append("telegram")
    return channels


def send_channel(channel: str, payload: dict) -> None:
    if channel == "dashboard":
        return
    if not settings.ENABLE_EXTERNAL_NOTIFICATIONS:
        raise RuntimeError("External notifications are disabled")
    if channel == "email":
        message = EmailMessage()
        kind = payload.get("notification_type", "risk_alert")
        message["Subject"] = (
            f"Mangrove Lens monthly monitoring report — {payload['period_start']}"
            if kind == "monthly_report"
            else f"Mangrove Lens {payload['severity'].upper()} alert — {payload['period_start']}"
        )
        message["From"] = settings.SMTP_USERNAME
        message["To"] = settings.ALERT_EMAIL_TO
        message.set_content(json.dumps(payload, indent=2))
        report = payload.get("report_path")
        if report and Path(report).is_file():
            message.add_attachment(
                Path(report).read_bytes(), maintype="application", subtype="pdf",
                filename=Path(report).name,
            )
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
            server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
        return
    if channel == "telegram":
        text = f"Mangrove Lens {payload['severity'].upper()}\n" + "\n".join(payload["evidence"])
        data = urllib.parse.urlencode({"chat_id": settings.TELEGRAM_CHAT_ID, "text": text}).encode()
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        with urllib.request.urlopen(url, data=data, timeout=20) as response:
            if response.status >= 300:
                raise RuntimeError(f"Telegram returned HTTP {response.status}")
        return
    raise ValueError(f"Unknown notification channel: {channel}")
