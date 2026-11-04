"""Backfill live monthly Earth Engine observations for model training."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

from dateutil.relativedelta import relativedelta

from src.database.db import Base, SessionLocal, engine
from src.database.models import MonthlyFeatureRecord
from src.providers.earth_engine import EarthEngineProvider
from src.services.monitoring import MonitoringWorkflow, load_operational_geometry
from src.models.forecast import ForecastModel
from src.utils.config import settings


def backfill(start, end, region_id="sundarbans-transboundary-v1", workers=4):
    provider = EarthEngineProvider()
    ready, detail = provider.readiness()
    if not ready:
        raise SystemExit(detail)
    Base.metadata.create_all(engine)
    db, geometry = SessionLocal(), load_operational_geometry(settings.AOI_PATH)
    try:
        cursor = date.fromisoformat(str(start)).replace(day=1)
        end = date.fromisoformat(str(end)).replace(day=1)
        workflow = MonitoringWorkflow(provider, ForecastModel(), db, settings.AOI_PATH)
        periods = []
        while cursor < end:
            exists = db.query(MonthlyFeatureRecord).filter_by(
                region_id=region_id, period_start=cursor, provider=provider.name
            ).one_or_none()
            if exists is None:
                periods.append(cursor)
            else:
                print(f"Skipped existing {cursor}")
            cursor += relativedelta(months=1)
        failures = []
        with ThreadPoolExecutor(max_workers=max(1, min(workers, 6))) as executor:
            futures = {
                executor.submit(provider.monthly_observation, region_id, geometry, period): period
                for period in periods
            }
            for future in as_completed(futures):
                period = futures[future]
                try:
                    observation = future.result()
                    workflow.store_observation(observation)
                    print(f"Stored {period}: {observation.quality.status}")
                except Exception as exc:
                    print(f"Failed {period}: {exc}")
                    failures.append((period, str(exc)))
        if failures:
            raise RuntimeError(f"Earth Engine backfill failed for {len(failures)} period(s): {failures}")
        return {"requested": len(periods), "failed": 0}
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default=settings.ANALYSIS_START_DATE)
    parser.add_argument("--end", default=date.today().replace(day=1).isoformat())
    parser.add_argument("--region-id", default="sundarbans-transboundary-v1")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    backfill(args.start, args.end, args.region_id, args.workers)


if __name__ == "__main__":
    main()
