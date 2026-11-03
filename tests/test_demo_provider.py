from datetime import date

from src.providers.demo import DemoSatelliteProvider


GEOMETRY = {"type": "Polygon", "coordinates": [[[88, 21], [90, 21], [90, 23], [88, 23], [88, 21]]]}


def test_demo_provider_is_deterministic_and_labeled():
    provider = DemoSatelliteProvider()
    first = provider.monthly_observation("cell-a", GEOMETRY, date(2025, 6, 1))
    second = provider.monthly_observation("cell-a", GEOMETRY, date(2025, 6, 20))
    assert first.ndvi_mean == second.ndvi_mean
    assert first.provenance["synthetic"] is True
    assert first.source_collections == ["DEMO/DETERMINISTIC/V1"]
    assert first.quality.status == "valid"
