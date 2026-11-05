"""Run the autonomous monthly monitoring scheduler."""
from datetime import date, datetime, timedelta, timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from dateutil.relativedelta import relativedelta

from src.agents.orchestrator import MangroveGuardianAgent
from src.database.db import Base, SessionLocal, engine
from src.database.models import MonitoringJobRecord
from src.providers import get_satellite_provider
from src.services.operations import emit_operation_event
from src.utils.config import settings
from scripts.backfill_earth_engine import backfill
from scripts.train_model import main as train_model


def monitor_latest_complete_month():
    period = date.today().replace(day=1) - relativedelta(months=1)
    db = SessionLocal()
    try:
        provider = get_satellite_provider()
        existing = db.query(MonitoringJobRecord).filter_by(
            region_id="sundarbans-transboundary-v1",
            period_start=period,
            provider=provider.name,
            status="completed",
        ).first()
        if existing:
            print(f"Monitoring already completed as job {existing.id} for {period}; skipping")
            emit_operation_event(
                "scheduler", "monitoring_current", "Latest completed month is already monitored",
                job_id=existing.id, period_start=period,
                details={"provider": provider.name}, db=db,
            )
            return
        emit_operation_event(
            "scheduler", "monitoring_started", "Scheduled monitoring cycle started",
            period_start=period, details={"provider": provider.name}, db=db,
        )
        result = MangroveGuardianAgent(db).monitor(period)
        print(f"Monitoring job {result['job_id']} completed for {period}")
    finally:
        db.close()


def autonomous_monthly_cycle():
    """Acquire, infer/report/alert, then retrain for the following month."""
    latest = date.today().replace(day=1) - relativedelta(months=1)
    end_exclusive = latest + relativedelta(months=1)
    emit_operation_event(
        "scheduler", "cycle_started", "Autonomous monthly reconciliation started",
        period_start=latest,
        details={"backfill_start": settings.ANALYSIS_START_DATE, "end_exclusive": end_exclusive.isoformat()},
    )
    backfill(settings.ANALYSIS_START_DATE, end_exclusive.isoformat(), workers=4)
    monitor_latest_complete_month()
    if settings.ENABLE_AUTOMATED_RETRAINING:
        emit_operation_event(
            "retraining_agent", "training_started", "Post-acquisition model retraining started",
            period_start=latest,
        )
        train_model()
        emit_operation_event(
            "retraining_agent", "training_completed", "Model retraining and validation completed",
            period_start=latest,
        )
    emit_operation_event(
        "scheduler", "cycle_completed", "Autonomous monthly reconciliation completed",
        period_start=latest,
    )


def main():
    Base.metadata.create_all(bind=engine)
    emit_operation_event(
        "scheduler", "service_started", "Autonomous scheduler service started",
        details={"timezone": "UTC", "monthly_schedule": "day 5 at 03:00 UTC"},
    )
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        autonomous_monthly_cycle,
        trigger="cron",
        day=5,
        hour=3,
        id="monthly-sundarbans-monitoring",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=86400,
    )
    scheduler.add_job(
        autonomous_monthly_cycle,
        trigger="date",
        run_date=datetime.now(timezone.utc) + timedelta(seconds=10),
        id="startup-reconciliation",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()


if __name__ == "__main__":
    main()
