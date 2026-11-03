"""Populate deterministic demo history and run the latest monitoring decision."""
from __future__ import annotations

import argparse
from datetime import date

from dateutil.relativedelta import relativedelta

from src.database.db import Base, SessionLocal, engine
from src.database.models import MonthlyFeatureRecord
from src.models.forecast import ForecastModel
from src.providers.demo import DemoSatelliteProvider
from src.services.monitoring import MonitoringWorkflow, load_operational_geometry
from src.utils.config import settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2019-01-01")
    parser.add_argument("--end", default=date.today().replace(day=1).isoformat())
    parser.add_argument("--region-id", default="sundarbans-transboundary-v1")
    args = parser.parse_args()
    Base.metadata.create_all(engine)
    provider = DemoSatelliteProvider()
    geometry = load_operational_geometry(settings.AOI_PATH)
    db = SessionLocal()
    try:
        cursor, end = date.fromisoformat(args.start).replace(day=1), date.fromisoformat(args.end).replace(day=1)
        while cursor < end:
            observation = provider.monthly_observation(args.region_id, geometry, cursor)
            existing = db.query(MonthlyFeatureRecord).filter_by(
                region_id=args.region_id, period_start=cursor, provider=provider.name
            ).one_or_none()
            if existing is None:
                existing = MonthlyFeatureRecord(
                    region_id=args.region_id, period_start=cursor, provider=provider.name,
                    period_end=observation.period_end,
                )
            for name in ("ndvi_mean", "ndvi_p10", "ndvi_p90", "ndmi_mean", "vv_mean", "vh_mean", "co_mean"):
                setattr(existing, name, getattr(observation, name))
            existing.valid_pixel_fraction = observation.quality.valid_pixel_fraction
            existing.quality_status = observation.quality.status
            existing.quality = observation.quality.model_dump(mode="json")
            existing.provenance = {**observation.provenance, "sources": observation.source_collections}
            db.add(existing)
            cursor += relativedelta(months=1)
        db.commit()
        result = MonitoringWorkflow(provider, ForecastModel(), db, settings.AOI_PATH).run(args.region_id, end)
        print(f"Demo history ready; monitoring job {result['job_id']} completed with {result['decision']['severity']} severity")
    finally:
        db.close()


if __name__ == "__main__":
    main()
