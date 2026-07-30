from src.utils.logger import get_logger
from src.utils.config import settings

logger = get_logger(__name__)

def send_notification(alert_data: dict, region_id: str):
    """
    Sends notifications based on alert data.
    Supports dashboard logging and simulated email.
    """
    logger.warning(f"🚨 ALERT GENERATED for {region_id}: {alert_data['severity']} - {alert_data['message']}")
    
    if settings.ENABLE_EMAIL_NOTIFICATIONS:
        _send_email(alert_data, region_id)

def _send_email(alert_data: dict, region_id: str):
    """
    Simulated email sending. In a real scenario, use smtplib or an API like SendGrid.
    """
    logger.info(f"📧 Sending Email Notification to {settings.NOTIFICATION_EMAIL}")
    logger.info(f"Subject: {alert_data['severity']} Alert for Mangrove Region: {region_id}")
    logger.info(f"Body: {alert_data['message']}\nAction: {alert_data['recommended_action']}")
