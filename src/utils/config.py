import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Mangrove Health API"
    ENVIRONMENT: str = "development"
    
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
    EE_PROJECT_ID: str = ""
    
    # Notifications
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    NOTIFICATION_EMAIL: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
