from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App Config
    APP_NAME: str = "Mangrove Health API"
    ENVIRONMENT: Literal["development", "test", "production"] = "development"
    SATELLITE_PROVIDER: Literal["demo", "earth_engine"] = "demo"
    
    # Database
    DATABASE_URL: str = "sqlite:///data/mangrove_guardian.db"
    
    # Thresholds (Configurable)
    NDVI_CRITICAL_THRESHOLD: float = 0.2
    NDVI_WARNING_THRESHOLD: float = 0.4
    CO_CRITICAL_THRESHOLD: float = 0.05
    CO_WARNING_THRESHOLD: float = 0.03
    HEALTH_CRITICAL_THRESHOLD: float = 30.0
    HEALTH_WARNING_THRESHOLD: float = 60.0
    
    # Satellite Integration (Earth Engine)
    # E.g., paths to service account keys if needed
    EE_PROJECT_ID: str = "nex-sync"
    AOI_PATH: str = "data/aoi/sundarbans_transboundary_envelope.geojson"
    ANALYSIS_START_DATE: str = "2019-01-01"
    MIN_VALID_PIXEL_FRACTION: float = 0.30
    
    # Notifications
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    NOTIFICATION_EMAIL: str = ""

    CORS_ORIGINS: str = "http://localhost:5173"
    ENABLE_SCHEDULER: bool = False

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
