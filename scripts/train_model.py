"""Train and evaluate the Random Forest NDVI forecasting baseline."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.database.db import SessionLocal
from src.database.models import MonthlyFeatureRecord
from src.models.forecast import FEATURES, build_features


def main():
    db = SessionLocal()
    try:
        query = db.query(MonthlyFeatureRecord).filter_by(quality_status="valid").order_by(
            MonthlyFeatureRecord.region_id, MonthlyFeatureRecord.period_start
        )
        frame = pd.read_sql(query.statement, db.bind)
    finally:
        db.close()
    prepared = build_features(frame).dropna(subset=FEATURES + ["target_ndvi"])
    if len(prepared) < 36:
        raise SystemExit("Need at least 36 leakage-safe training rows. Run scripts/bootstrap_demo.py first.")
    cutoff = pd.to_datetime(prepared["period_start"]).max() - pd.DateOffset(months=12)
    train = prepared[pd.to_datetime(prepared["period_start"]) < cutoff]
    test = prepared[pd.to_datetime(prepared["period_start"]) >= cutoff]
    if train.empty or test.empty:
        raise SystemExit("Temporal split produced an empty train or test set")
    model = RandomForestRegressor(
        n_estimators=400, max_depth=10, min_samples_leaf=2, random_state=42, n_jobs=-1
    )
    model.fit(train[FEATURES], train["target_ndvi"])
    predictions = model.predict(test[FEATURES])
    persistence = test["ndvi_lag_1"]
    evaluation = test[["period_start", "target_ndvi"]].copy()
    evaluation["prediction"] = predictions
    evaluation["absolute_error"] = (evaluation["target_ndvi"] - evaluation["prediction"]).abs()
    evaluation["month"] = pd.to_datetime(evaluation["period_start"]).dt.month
    evaluation["season"] = evaluation["month"].map(
        lambda month: "monsoon" if month in {6, 7, 8, 9} else "post_monsoon" if month in {10, 11} else "dry_pre_monsoon"
    )
    seasonal_mae = evaluation.groupby("season")["absolute_error"].mean().to_dict()
    metrics = {
        "mae": mean_absolute_error(test["target_ndvi"], predictions),
        "rmse": mean_squared_error(test["target_ndvi"], predictions) ** 0.5,
        "r2": r2_score(test["target_ndvi"], predictions),
        "persistence_mae": mean_absolute_error(test["target_ndvi"], persistence),
        "train_rows": len(train), "test_rows": len(test), "cutoff": cutoff.date().isoformat(),
        "seasonal_mae": seasonal_mae,
        "mean_bias": float((predictions - test["target_ndvi"]).mean()),
    }
    if metrics["mae"] >= metrics["persistence_mae"]:
        raise SystemExit(f"Model rejected: MAE {metrics['mae']:.4f} does not beat persistence {metrics['persistence_mae']:.4f}")
    models, reports = Path("models"), Path("reports")
    models.mkdir(exist_ok=True)
    reports.mkdir(exist_ok=True)
    artifact = models / "ndvi_forecast_rf.joblib"
    joblib.dump(model, artifact)
    version = f"rf-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{hashlib.sha256(artifact.read_bytes()).hexdigest()[:8]}"
    manifest = {
        "model_version": version, "features": FEATURES, "metrics": metrics,
        "trained_at": datetime.now(timezone.utc).isoformat(), "target": "current_month_ndvi_from_prior_observations",
        "validation": "last 12 complete observations held out", "random_seed": 42,
        "dataset_kind": "synthetic_demo" if set(frame["provider"]) == {"demo"} else "observational",
        "production_approved": False,
        "observational_gate_passed": set(frame["provider"]) == {"earth_engine"},
        "data_period": {
            "start": str(pd.to_datetime(frame["period_start"]).min().date()),
            "end": str(pd.to_datetime(frame["period_start"]).max().date()),
        },
        "feature_importance": dict(sorted(
            zip(FEATURES, [float(value) for value in model.feature_importances_]),
            key=lambda item: item[1], reverse=True,
        )),
    }
    (models / "ndvi_forecast_rf.manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (reports / "model_evaluation.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
