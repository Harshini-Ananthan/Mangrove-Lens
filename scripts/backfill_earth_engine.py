"""Backfill live monthly Earth Engine observations for model training."""
from __future__ import annotations

import argparse
from datetime import date

from dateutil.relativedelta import relativedelta

from src.database.db import Base, SessionLocal, engine
from src.database.models import MonthlyFeatureRecord
from src.providers.earth_engine import EarthEngineProvider
from src.services.monitoring import MonitoringWorkflow, load_operational_geometry
from src.models.forecast import ForecastModel
from src.utils.config import settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default=settings.ANALYSIS_START_DATE)
    parser.add_argument("--end", default=date.today().replace(day=1).isoformat())
    parser.add_argument("--region-id", default="sundarbans-transboundary-v1")
    args = parser.parse_args()
    provider = EarthEngineProvider()
    ready, detail = provider.readiness()
    if not ready:
        raise SystemExit(detail)
    Base.metadata.create_all(engine)
    db, geometry = SessionLocal(), load_operational_geometry(settings.AOI_PATH)
    try:
        cursor, end = date.fromisoformat(args.start).replace(day=1), date.fromisoformat(args.end).replace(day=1)
        workflow = MonitoringWorkflow(provider, ForecastModel(), db, settings.AOI_PATH)
        while cursor < end:
            exists = db.query(MonthlyFeatureRecord).filter_by(
                region_id=args.region_id, period_start=cursor, provider=provider.name
            ).one_or_none()
            if exists is None:
                observation = provider.monthly_observation(args.region_id, geometry, cursor)
                workflow.store_observation(observation)
                print(f"Stored {cursor}: {observation.quality.status}")
            else:
                print(f"Skipped existing {cursor}")
            cursor += relativedelta(months=1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
