import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.database.db import Base

class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(String, index=True, nullable=True)
    polygon = Column(JSON, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Sentinel-2
    ndvi_actual = Column(Float, nullable=True)
    
    # ML Model
    ndvi_predicted = Column(Float, nullable=True)
    
    # Sentinel-5P
    co_level = Column(Float, nullable=True)
    
    # Evaluation
    health_score = Column(Float, nullable=True)
    health_status = Column(String, nullable=True) # Excellent, Healthy, Moderate, Poor, Critical
    
    alert_status = Column(String, default="OK") # OK, ALERT
    alert_level = Column(String, nullable=True) # Low, Medium, High, Critical
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    alerts = relationship("AlertRecord", back_populates="analysis")


class AlertRecord(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    severity = Column(String) # Low, Medium, High, Critical
    message = Column(String)
    recommended_action = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    analysis = relationship("AnalysisRecord", back_populates="alerts")
