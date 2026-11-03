import pandas as pd

from src.models.forecast import build_features


def test_feature_builder_uses_only_prior_ndvi_values():
    frame = pd.DataFrame({
        "region_id": ["a"] * 14,
        "period_start": pd.date_range("2024-01-01", periods=14, freq="MS"),
        "ndvi_mean": list(range(14)),
    })
    result = build_features(frame)
    row = result.iloc[12]
    assert row["ndvi_lag_1"] == 11
    assert row["ndvi_lag_12"] == 0
    assert row["ndvi_roll_3"] == 10
    assert row["target_ndvi"] == 13
