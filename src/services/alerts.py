from src.utils.logger import get_logger
from src.utils.config import settings

logger = get_logger(__name__)

def check_alerts(ndvi: float, co_level: float, health_score: float):
    """
    Evaluates thresholds and returns an alert object if necessary.
    Returns None if no alerts are triggered.
    """
    alerts = []
    severity = "Low"
    
    if ndvi < settings.NDVI_CRITICAL_THRESHOLD:
        alerts.append(f"NDVI is critically low ({ndvi}).")
        severity = "Critical"
    elif ndvi < settings.NDVI_WARNING_THRESHOLD:
        alerts.append(f"NDVI is below warning threshold ({ndvi}).")
        severity = max(severity, "High")
        
    if co_level > settings.CO_CRITICAL_THRESHOLD:
        alerts.append(f"CO level is critically high ({co_level}).")
        severity = "Critical"
    elif co_level > settings.CO_WARNING_THRESHOLD:
        alerts.append(f"CO level is above warning threshold ({co_level}).")
        severity = max(severity, "Medium")
        
    if health_score < settings.HEALTH_CRITICAL_THRESHOLD:
        alerts.append(f"Overall health score is critical ({health_score}).")
        severity = "Critical"
    elif health_score < settings.HEALTH_WARNING_THRESHOLD:
        alerts.append(f"Overall health score is poor ({health_score}).")
        severity = max(severity, "High")
        
    if not alerts:
        return None
        
    message = " | ".join(alerts)
    
    if severity == "Critical":
        recommended_action = "Immediate physical inspection required. Notify local authorities."
    elif severity == "High":
        recommended_action = "Schedule field visit within 7 days. Investigate potential localized damage."
    elif severity == "Medium":
        recommended_action = "Monitor closely in the next satellite pass."
    else:
        recommended_action = "Routine monitoring."
        
    return {
        "severity": severity,
        "message": message,
        "recommended_action": recommended_action
    }
