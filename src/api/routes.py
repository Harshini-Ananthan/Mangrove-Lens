from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import datetime

from src.database.db import get_db
from src.database.models import AnalysisRecord, AlertRecord
from src.services.satellite import get_satellite_data
from src.services.health import evaluate_health
from src.services.alerts import check_alerts
from src.services.notifications import send_notification
from src.models.predict_model import predict_ndvi

router = APIRouter()

class RegionRequest(BaseModel):
    region_id: str = "custom_region"
    polygon: Dict[str, Any]
    target_date: Optional[str] = None # ISO format date string

class PredictRequest(BaseModel):
    data: List[Dict[str, float]] # e.g., [{"CO": 0.03, "month": 6, "year": 2025, "dayofyear": 160}]

@router.get("/health")
def health_check():
    return {"status": "ok", "message": "Mangrove Health API is running."}

@router.post("/satellite/fetch")
def fetch_satellite_data(request: RegionRequest):
    target_date = datetime.datetime.fromisoformat(request.target_date) if request.target_date else datetime.datetime.utcnow()
    try:
        data = get_satellite_data(request.polygon, target_date)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate")
def calculate_metrics(request: RegionRequest):
    # For now, calculation is bundled into the fetch process since EE/mock does it directly
    target_date = datetime.datetime.fromisoformat(request.target_date) if request.target_date else datetime.datetime.utcnow()
    data = get_satellite_data(request.polygon, target_date)
    return {
        "ndvi": data["ndvi_mean"],
        "co": data["co_mean"]
    }

@router.post("/predict")
def run_prediction(request: PredictRequest):
    result = predict_ndvi(request.data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/analyze")
def analyze_region(request: RegionRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Full pipeline: Satellite -> Calculate -> ML Predict -> Health Assess -> DB Store -> Alert
    """
    target_date = datetime.datetime.fromisoformat(request.target_date) if request.target_date else datetime.datetime.utcnow()
    
    # 1 & 2. Satellite & CO
    sat_data = get_satellite_data(request.polygon, target_date)
    actual_ndvi = sat_data["ndvi_mean"]
    actual_co = sat_data["co_mean"]
    
    # 3. Feature Generation for ML
    features = {
        "CO": actual_co,
        "month": target_date.month,
        "year": target_date.year,
        "dayofyear": target_date.timetuple().tm_yday
    }
    
    # 4. ML Prediction
    pred_result = predict_ndvi(features)
    if "error" in pred_result:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {pred_result['error']}")
    
    predicted_ndvi = pred_result["predictions"][0]
    
    # 5. Health Assessment
    health_score, health_status = evaluate_health(actual_ndvi, predicted_ndvi, actual_co)
    
    # 6. Check Alerts
    alert_data = check_alerts(actual_ndvi, actual_co, health_score)
    
    # 7. Store in Database
    analysis = AnalysisRecord(
        region_id=request.region_id,
        polygon=request.polygon,
        date=target_date,
        ndvi_actual=actual_ndvi,
        ndvi_predicted=predicted_ndvi,
        co_level=actual_co,
        health_score=health_score,
        health_status=health_status,
        alert_status="ALERT" if alert_data else "OK",
        alert_level=alert_data["severity"] if alert_data else None
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    # 8. Store Alert & Notify
    if alert_data:
        alert_record = AlertRecord(
            analysis_id=analysis.id,
            severity=alert_data["severity"],
            message=alert_data["message"],
            recommended_action=alert_data["recommended_action"]
        )
        db.add(alert_record)
        db.commit()
        
        # Fire notification in background
        background_tasks.add_task(send_notification, alert_data, request.region_id)
        
    return {
        "status": "success",
        "analysis_id": analysis.id,
        "results": {
            "ndvi_actual": actual_ndvi,
            "ndvi_predicted": predicted_ndvi,
            "co_level": actual_co,
            "health_score": health_score,
            "health_status": health_status,
            "alert_triggered": bool(alert_data)
        }
    }

@router.get("/alerts")
def get_alerts(limit: int = 50, db: Session = Depends(get_db)):
    alerts = db.query(AlertRecord).order_by(AlertRecord.timestamp.desc()).limit(limit).all()
    return alerts

@router.get("/history")
def get_history(limit: int = 100, db: Session = Depends(get_db)):
    history = db.query(AnalysisRecord).order_by(AnalysisRecord.date.desc()).limit(limit).all()
    return history
