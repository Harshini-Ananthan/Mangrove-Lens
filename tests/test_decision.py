from datetime import date

from src.domain.contracts import ModelPrediction, MonthlyObservation, ObservationQuality, Severity
from src.services.decision import assess_risk


def observation(**overrides):
    values = dict(
        region_id="cell-a", period_start=date(2025, 1, 1), period_end=date(2025, 2, 1),
        provider="demo", source_collections=["demo"], ndvi_mean=0.4, ndmi_mean=0.3,
        vv_mean=-12, vh_mean=-20, co_mean=0.045,
        quality=ObservationQuality(valid_pixel_fraction=0.8, optical_image_count=4, sar_image_count=4, co_image_count=10, status="valid"),
    )
    values.update(overrides)
    return MonthlyObservation(**values)


def test_multiple_independent_signals_raise_critical_risk():
    prediction = ModelPrediction(
        model_version="test", expected_ndvi=0.55, residual=-0.15, anomaly_score=3,
        uncertainty=0.04, feature_values={},
    )
    decision = assess_risk(observation(), prediction)
    assert decision.severity == Severity.CRITICAL
    assert decision.requires_human_review is True
    assert any("non-causal" in item for item in decision.evidence)


def test_low_coverage_never_claims_high_risk():
    poor = observation(quality=ObservationQuality(
        valid_pixel_fraction=0.1, optical_image_count=1, sar_image_count=0, co_image_count=2,
        status="low_coverage", reasons=["clouds"],
    ))
    prediction = ModelPrediction(
        model_version="test", expected_ndvi=0.8, residual=-0.5, anomaly_score=8,
        uncertainty=0.03, feature_values={},
    )
    assert assess_risk(poor, prediction).severity == Severity.LOW
