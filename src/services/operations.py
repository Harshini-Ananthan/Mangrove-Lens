from __future__ import annotations

import json
from datetime import date

from sqlalchemy.orm import Session

from src.database.db import SessionLocal
from src.database.models import OperationEventRecord
from src.utils.logger import get_logger


logger = get_logger("mangrove_lens.operations")


def emit_operation_event(
    source: str,
    stage: str,
    message: str,
    *,
    level: str = "info",
    job_id: str | None = None,
    region_id: str | None = None,
    period_start: date | None = None,
    details: dict | None = None,
    db: Session | None = None,
) -> OperationEventRecord | None:
    """Persist and log an operational event without making observation optional.

    The monitoring pipeline works normally when no observer is connected. Events
    are append-only evidence that a CLI or other read-only client may stream.
    """
    payload = details or {}
    log = getattr(logger, level if level in {"debug", "info", "warning", "error"} else "info")
    log(
        "%s.%s | %s | %s",
        source,
        stage,
        message,
        json.dumps(payload, sort_keys=True, default=str),
    )
    session = db or SessionLocal()
    owns_session = db is None
    try:
        event = OperationEventRecord(
            source=source,
            stage=stage,
            level=level,
            message=message,
            job_id=job_id,
            region_id=region_id,
            period_start=period_start,
            details=payload,
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        return event
    except Exception:
        session.rollback()
        logger.exception("Unable to persist operational event %s.%s", source, stage)
        return None
    finally:
        if owns_session:
            session.close()
