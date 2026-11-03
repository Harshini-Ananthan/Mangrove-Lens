import datetime
from sqlalchemy import Boolean, Column, Date, Integer, String, Float, DateTime, ForeignKey, JSON, UniqueConstraint
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


class MonthlyFeatureRecord(Base):
    __tablename__ = "monthly_features"
    __table_args__ = (UniqueConstraint("region_id", "period_start", "provider", name="uq_feature_period_provider"),)

    id = Column(Integer, primary_key=True)
    region_id = Column(String, nullable=False, index=True)
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False)
    provider = Column(String, nullable=False)
    ndvi_mean = Column(Float)
    ndvi_p10 = Column(Float)
    ndvi_p90 = Column(Float)
    ndmi_mean = Column(Float)
    vv_mean = Column(Float)
    vh_mean = Column(Float)
    co_mean = Column(Float)
    valid_pixel_fraction = Column(Float, nullable=False)
    quality_status = Column(String, nullable=False)
    quality = Column(JSON, nullable=False)
    provenance = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)


class MonitoringJobRecord(Base):
    __tablename__ = "monitoring_jobs"

    id = Column(String, primary_key=True)
    region_id = Column(String, nullable=False, index=True)
    period_start = Column(Date, nullable=False)
    status = Column(String, nullable=False, index=True)
    provider = Column(String, nullable=False)
    checkpoint = Column(String, nullable=False, default="created")
    error = Column(String)
    started_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    finished_at = Column(DateTime)
    requested_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class RiskDecisionRecord(Base):
    __tablename__ = "risk_decisions"
    __table_args__ = (UniqueConstraint("region_id", "period_start", "rule_version", name="uq_decision_period_rule"),)

    id = Column(Integer, primary_key=True)
    region_id = Column(String, nullable=False, index=True)
    period_start = Column(Date, nullable=False, index=True)
    severity = Column(String, nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    model_version = Column(String, nullable=False)
    expected_ndvi = Column(Float)
    anomaly_score = Column(Float)
    rule_version = Column(String, nullable=False)
    evidence = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    requires_human_review = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class AlertOutboxRecord(Base):
    __tablename__ = "alert_outbox"
    __table_args__ = (UniqueConstraint("decision_id", "channel", name="uq_alert_decision_channel"),)

    id = Column(Integer, primary_key=True)
    decision_id = Column(Integer, ForeignKey("risk_decisions.id"), nullable=False, index=True)
    channel = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending_review", index=True)
    payload = Column(JSON, nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    approved_by = Column(String)
    approved_at = Column(DateTime)
    sent_at = Column(DateTime)
    last_error = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
