from src.services.grid import build_grid, resolve_region_geometry


ENVELOPE = {"type": "Polygon", "coordinates": [[[88, 21.5], [90, 21.5], [90, 22.7], [88, 22.7], [88, 21.5]]]}


def test_grid_has_stable_unique_cells_and_resolves_geometry():
    grid = build_grid(ENVELOPE, 5)
    ids = [feature["properties"]["id"] for feature in grid["features"]]
    assert len(ids) > 500
    assert len(ids) == len(set(ids))
    geometry = resolve_region_geometry(ids[0], ENVELOPE, 5)
    assert geometry["type"] == "Polygon"


def test_full_region_returns_original_envelope():
    assert resolve_region_geometry("sundarbans-transboundary-v1", ENVELOPE) == ENVELOPE
