"""Run the autonomous monthly monitoring scheduler."""
from datetime import date

from apscheduler.schedulers.blocking import BlockingScheduler
from dateutil.relativedelta import relativedelta

from src.agents.orchestrator import MangroveGuardianAgent
from src.database.db import SessionLocal
from src.database.models import MonitoringJobRecord
from src.providers import get_satellite_provider


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
            return
        result = MangroveGuardianAgent(db).monitor(period)
        print(f"Monitoring job {result['job_id']} completed for {period}")
    finally:
        db.close()


def main():
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        monitor_latest_complete_month,
        trigger="cron",
        day=5,
        hour=3,
        id="monthly-sundarbans-monitoring",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=86400,
    )
    scheduler.start()


if __name__ == "__main__":
    main()
