from src.providers.base import SatelliteProvider
from src.providers.demo import DemoSatelliteProvider
from src.providers.earth_engine import EarthEngineProvider
from src.utils.config import settings


def get_satellite_provider() -> SatelliteProvider:
    if settings.SATELLITE_PROVIDER == "earth_engine":
        return EarthEngineProvider()
    return DemoSatelliteProvider()
