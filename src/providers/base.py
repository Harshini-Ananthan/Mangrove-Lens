from abc import ABC, abstractmethod
from datetime import date
from typing import Any

from src.domain.contracts import MonthlyObservation


class SatelliteProvider(ABC):
    name: str

    @abstractmethod
    def monthly_observation(
        self, region_id: str, geometry: dict[str, Any], period_start: date
    ) -> MonthlyObservation:
        raise NotImplementedError

    @abstractmethod
    def readiness(self) -> tuple[bool, str]:
        raise NotImplementedError
