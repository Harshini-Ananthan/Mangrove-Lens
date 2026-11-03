from src.api.routes import get_aoi, health_check


def test_health_contract_exposes_provider_and_model():
    payload = health_check()
    assert payload["status"] == "ok"
    assert payload["satellite"]["provider"] == "demo"
    assert isinstance(payload["satellite"]["ready"], bool)
    assert "version" in payload["model"]


def test_aoi_is_transboundary_operational_envelope():
    payload = get_aoi()
    assert payload["type"] == "FeatureCollection"
    assert payload["features"][0]["properties"]["id"] == "sundarbans-transboundary-v1"
