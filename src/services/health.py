from src.utils.config import settings

def evaluate_health(actual_ndvi: float, predicted_ndvi: float, co_level: float):
    """
    Evaluates mangrove health based on actual NDVI, predicted NDVI (from RF model), and CO levels.
    Returns a health score (0-100) and classification string.
    """
    score = 100.0
    
    # Penalty for low actual NDVI
    if actual_ndvi < 0.3:
        score -= 40
    elif actual_ndvi < 0.5:
        score -= 20
        
    # Penalty if actual NDVI is significantly worse than predicted (anomaly)
    ndvi_diff = predicted_ndvi - actual_ndvi
    if ndvi_diff > 0.15:
        score -= 15
    elif ndvi_diff > 0.05:
        score -= 5
        
    # Penalty for high CO
    if co_level > settings.CO_CRITICAL_THRESHOLD:
        score -= 30
    elif co_level > settings.CO_WARNING_THRESHOLD:
        score -= 10
        
    score = max(0.0, min(100.0, score))
    
    # Classify
    if score >= 85:
        status = "Excellent"
    elif score >= 70:
        status = "Healthy"
    elif score >= 50:
        status = "Moderate"
    elif score >= 30:
        status = "Poor"
    else:
        status = "Critical"
        
    return score, status
