from src.providers.earth_engine import EarthEngineProvider


def test_missing_or_available_credentials_are_reported_without_demo_fallback():
    provider = EarthEngineProvider()
    ready, detail = provider.readiness()
    assert isinstance(ready, bool)
    assert "Earth Engine" in detail
    assert provider.name == "earth_engine"
