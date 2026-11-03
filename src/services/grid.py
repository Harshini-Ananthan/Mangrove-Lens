from __future__ import annotations

import math


def build_grid(envelope: dict, cell_size_km: float = 5.0) -> dict:
    """Create stable WGS84 analysis cells over an envelope.

    Earth Engine performs the final mangrove-extent mask, so empty coastal/water
    cells can be retained here without making scientific claims about them.
    """
    ring = envelope["coordinates"][0]
    min_lon, max_lon = min(p[0] for p in ring), max(p[0] for p in ring)
    min_lat, max_lat = min(p[1] for p in ring), max(p[1] for p in ring)
    mid_lat = (min_lat + max_lat) / 2
    lat_step = cell_size_km / 111.32
    lon_step = cell_size_km / (111.32 * math.cos(math.radians(mid_lat)))
    features = []
    row, south = 0, min_lat
    while south < max_lat:
        north = min(south + lat_step, max_lat)
        col, west = 0, min_lon
        while west < max_lon:
            east = min(west + lon_step, max_lon)
            cell_id = f"sundarbans-r{row:03d}-c{col:03d}"
            features.append({
                "type": "Feature",
                "properties": {"id": cell_id, "row": row, "column": col, "cell_size_km": cell_size_km},
                "geometry": {"type": "Polygon", "coordinates": [[
                    [west, south], [east, south], [east, north], [west, north], [west, south]
                ]]},
            })
            col, west = col + 1, east
        row, south = row + 1, north
    return {"type": "FeatureCollection", "name": f"sundarbans_grid_{cell_size_km:g}km", "features": features}


def resolve_region_geometry(region_id: str, envelope: dict, cell_size_km: float = 5.0) -> dict:
    if region_id == "sundarbans-transboundary-v1":
        return envelope
    for feature in build_grid(envelope, cell_size_km)["features"]:
        if feature["properties"]["id"] == region_id:
            return feature["geometry"]
    raise ValueError(f"Unknown region_id: {region_id}")
