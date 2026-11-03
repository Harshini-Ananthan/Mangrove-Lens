"""Deterministic observe-analyze-decide-report orchestration.

The workflow deliberately keeps scientific calculations out of an LLM. A future
language model may summarize stored evidence, but it may not alter measurements,
risk scores, or approval policy.
"""
from datetime import date

from sqlalchemy.orm import Session

from src.models.forecast import ForecastModel
from src.providers import get_satellite_provider
from src.services.monitoring import MonitoringWorkflow
from src.utils.config import settings


class MangroveGuardianAgent:
    def __init__(self, db: Session):
        self.workflow = MonitoringWorkflow(
            get_satellite_provider(), ForecastModel(), db, settings.AOI_PATH
        )

    def monitor(self, period_start: date, region_id: str = "sundarbans-transboundary-v1") -> dict:
        """Run the auditable agent graph for a single monthly monitoring period."""
        return self.workflow.run(region_id, period_start)
