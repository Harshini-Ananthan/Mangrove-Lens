from datetime import date
from pathlib import Path

from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.db import Base
from src.database.models import MonitoringJobRecord, OperationEventRecord, RiskDecisionRecord
from src.models.forecast import ForecastModel
from src.providers.demo import DemoSatelliteProvider
from src.services.monitoring import MonitoringWorkflow, load_operational_geometry


def test_workflow_persists_observation_prediction_decision_and_job():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    provider = DemoSatelliteProvider()
    aoi_path = "data/aoi/sundarbans_transboundary_envelope.geojson"
    geometry = load_operational_geometry(aoi_path)
    model = ForecastModel(Path("missing.joblib"), Path("missing.json"))
    workflow = MonitoringWorkflow(provider, model, db, aoi_path)
    start = date(2024, 1, 1)
    for offset in range(12):
        workflow.store_observation(provider.monthly_observation(
            "sundarbans-transboundary-v1", geometry, start + relativedelta(months=offset)
        ))
    result = workflow.run("sundarbans-transboundary-v1", start + relativedelta(months=12))
    assert result["decision"]["severity"] in {"low", "moderate", "high", "critical"}
    assert result["prediction"]["model_version"] == "seasonal-persistence-baseline-v1"
    assert db.query(MonitoringJobRecord).filter_by(status="completed").count() == 1
    assert db.query(RiskDecisionRecord).count() == 1
    stages = {event.stage for event in db.query(OperationEventRecord).all()}
    assert {"started", "query_completed", "inference_completed", "decision_persisted", "completed"} <= stages
    db.close()
