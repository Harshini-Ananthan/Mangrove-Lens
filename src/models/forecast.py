from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.domain.contracts import ModelPrediction


FEATURES = ["ndvi_lag_1", "ndvi_lag_12", "ndvi_roll_3", "co_mean", "ndmi_mean", "vv_mean", "vh_mean", "month"]


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.sort_values(["region_id", "period_start"]).copy()
    grouped = data.groupby("region_id", sort=False)
    data["ndvi_lag_1"] = grouped["ndvi_mean"].shift(1)
    data["ndvi_lag_12"] = grouped["ndvi_mean"].shift(12)
    data["ndvi_roll_3"] = grouped["ndvi_mean"].transform(lambda values: values.shift(1).rolling(3).median())
    data["month"] = pd.to_datetime(data["period_start"]).dt.month
    data["target_ndvi"] = grouped["ndvi_mean"].shift(-1)
    return data


@dataclass
class ForecastModel:
    artifact_path: Path = Path("models/ndvi_forecast_rf.joblib")
    manifest_path: Path = Path("models/ndvi_forecast_rf.manifest.json")

    def __post_init__(self):
        self.model = joblib.load(self.artifact_path) if self.artifact_path.exists() else None
        self.manifest = json.loads(self.manifest_path.read_text()) if self.manifest_path.exists() else {}

    @property
    def ready(self) -> bool:
        return self.model is not None

    @property
    def version(self) -> str:
        return self.manifest.get("model_version", "seasonal-persistence-baseline-v1")

    def predict(self, feature_values: dict[str, float]) -> ModelPrediction:
        missing = [name for name in FEATURES if feature_values.get(name) is None]
        if missing:
            raise ValueError(f"Cannot predict; missing features: {missing}")
        row = pd.DataFrame([{name: feature_values[name] for name in FEATURES}])
        if self.model is None:
            expected = float(0.7 * row.iloc[0]["ndvi_lag_1"] + 0.3 * row.iloc[0]["ndvi_lag_12"])
            uncertainty = 0.08
        else:
            expected = float(self.model.predict(row)[0])
            tree_predictions = np.array([tree.predict(row.to_numpy())[0] for tree in self.model.estimators_])
            uncertainty = float(tree_predictions.std())
        actual = float(feature_values["actual_ndvi"])
        residual = actual - expected
        anomaly_score = abs(residual) / max(uncertainty, 0.03)
        return ModelPrediction(
            model_version=self.version,
            expected_ndvi=expected,
            residual=residual,
            anomaly_score=anomaly_score,
            uncertainty=uncertainty,
            feature_values={key: float(value) for key, value in feature_values.items() if value is not None},
        )
