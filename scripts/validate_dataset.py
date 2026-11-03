"""Validate temporal completeness and quality of the observational feature store."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.database.db import SessionLocal
from src.database.models import MonthlyFeatureRecord


def main():
    db = SessionLocal()
    try:
        query = db.query(MonthlyFeatureRecord).filter_by(provider="earth_engine").order_by(
            MonthlyFeatureRecord.region_id, MonthlyFeatureRecord.period_start
        )
        frame = pd.read_sql(query.statement, db.bind)
    finally:
        db.close()
    if frame.empty:
        raise SystemExit("No Earth Engine observations found")
    duplicate_count = int(frame.duplicated(["region_id", "period_start", "provider"]).sum())
    missing_periods = []
    for region_id, group in frame.groupby("region_id"):
        expected = pd.date_range(group["period_start"].min(), group["period_start"].max(), freq="MS")
        actual = set(pd.to_datetime(group["period_start"]))
        missing_periods.extend(f"{region_id}:{period.date()}" for period in expected if period not in actual)
    report = {
        "status": "passed" if not missing_periods and duplicate_count == 0 else "failed",
        "rows": len(frame),
        "regions": int(frame["region_id"].nunique()),
        "period_start": str(pd.to_datetime(frame["period_start"]).min().date()),
        "period_end": str(pd.to_datetime(frame["period_start"]).max().date()),
        "duplicate_count": duplicate_count,
        "missing_periods": missing_periods,
        "quality_status_counts": frame["quality_status"].value_counts().to_dict(),
        "mean_valid_pixel_fraction": float(frame["valid_pixel_fraction"].mean()),
        "null_counts": {
            column: int(frame[column].isna().sum())
            for column in ["ndvi_mean", "ndmi_mean", "vv_mean", "vh_mean", "co_mean"]
        },
    }
    Path("reports").mkdir(exist_ok=True)
    Path("reports/dataset_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "passed":
        raise SystemExit("Dataset validation failed")


if __name__ == "__main__":
    main()
