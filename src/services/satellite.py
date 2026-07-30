import ee
import random
import logging
import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Try to initialize Earth Engine. If no credentials exist, we will use mock logic for demo purposes.
EE_INITIALIZED = False
try:
    # ee.Authenticate() # Usually required first time
    ee.Initialize()
    EE_INITIALIZED = True
    logger.info("Google Earth Engine initialized successfully.")
except Exception as e:
    logger.warning(f"Failed to initialize Earth Engine. Falling back to mock data generator. Error: {e}")

def get_satellite_data(polygon: dict, target_date: datetime.datetime):
    """
    Fetches Sentinel-2 (NDVI) and Sentinel-5P (CO) data for the given polygon and date.
    Returns calculated statistics.
    """
    if EE_INITIALIZED:
        try:
            return _fetch_gee_data(polygon, target_date)
        except Exception as e:
            logger.error(f"GEE Fetch failed: {e}. Falling back to mock.")
            return _generate_mock_data(polygon, target_date)
    else:
        return _generate_mock_data(polygon, target_date)

def _fetch_gee_data(polygon, target_date):
    # Construct EE geometry
    # Assumes polygon is a GeoJSON dict like {"type": "Polygon", "coordinates": [[[...]]]}
    coords = polygon.get('coordinates', [])
    if not coords:
        raise ValueError("Invalid polygon coordinates")
        
    roi = ee.Geometry.Polygon(coords)
    
    # Date range (30 days around target)
    start_date = (target_date - datetime.timedelta(days=15)).strftime('%Y-%m-%d')
    end_date = (target_date + datetime.timedelta(days=15)).strftime('%Y-%m-%d')
    
    # --- Sentinel-2 NDVI ---
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(roi) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
        .median()
        
    # NDVI = (B8 - B4) / (B8 + B4)
    ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')
    
    ndvi_stats = ndvi.reduceRegion(
        reducer=ee.Reducer.mean().combine(ee.Reducer.minMax(), sharedInputs=True),
        geometry=roi,
        scale=10,
        maxPixels=1e9
    ).getInfo()
    
    # --- Sentinel-5P CO ---
    s5p = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_CO') \
        .select('CO_column_number_density') \
        .filterBounds(roi) \
        .filterDate(start_date, end_date) \
        .median()
        
    co_stats = s5p.reduceRegion(
        reducer=ee.Reducer.mean().combine(ee.Reducer.minMax(), sharedInputs=True),
        geometry=roi,
        scale=1113.2,
        maxPixels=1e9
    ).getInfo()
    
    return {
        "ndvi_mean": ndvi_stats.get('NDVI_mean', 0.0),
        "ndvi_min": ndvi_stats.get('NDVI_min', 0.0),
        "ndvi_max": ndvi_stats.get('NDVI_max', 0.0),
        "co_mean": co_stats.get('CO_column_number_density_mean', 0.0),
        "co_min": co_stats.get('CO_column_number_density_min', 0.0),
        "co_max": co_stats.get('CO_column_number_density_max', 0.0),
        "acquisition_date": target_date.isoformat()
    }

import hashlib

def _generate_mock_data(polygon, target_date):
    """
    Generates realistic mock data for Sentinel-2 and Sentinel-5P with spatial variance.
    """
    logger.info("Generating mock satellite data...")
    
    # Create a spatial hash from the polygon coordinates to ensure different areas have different base stats
    coords_str = str(polygon.get('coordinates', []))
    spatial_hash = int(hashlib.md5(coords_str.encode()).hexdigest()[:8], 16)
    
    # Base seasonal effect
    month = target_date.month
    season_factor = (month - 6) ** 2 / 36.0 # Lower in summer
    
    # Map hash to a variance scale (-0.4 to 0.2 for NDVI, -0.02 to 0.04 for CO)
    # This allows some areas to be highly degraded and others pristine!
    ndvi_spatial_variance = ((spatial_hash % 1000) / 1000.0) * 0.6 - 0.4
    co_spatial_variance = ((spatial_hash % 1000) / 1000.0) * 0.06 - 0.02
    
    base_ndvi = 0.70 - (season_factor * 0.1) + ndvi_spatial_variance + random.uniform(-0.02, 0.02)
    base_co = 0.030 + (season_factor * 0.01) + co_spatial_variance + random.uniform(-0.002, 0.002)
    
    # Clamp values
    base_ndvi = max(0.1, min(0.95, base_ndvi))
    base_co = max(0.01, min(0.1, base_co))
    
    return {
        "ndvi_mean": round(base_ndvi, 4),
        "ndvi_min": round(max(0.05, base_ndvi - 0.15), 4),
        "ndvi_max": round(min(0.99, base_ndvi + 0.1), 4),
        "co_mean": round(base_co, 4),
        "co_min": round(max(0.01, base_co - 0.01), 4),
        "co_max": round(base_co + 0.02, 4),
        "acquisition_date": target_date.isoformat()
    }
