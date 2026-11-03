from __future__ import annotations

from datetime import date, datetime
from enum import IntEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class Severity(IntEnum):
    LOW = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4

    @property
    def label(self) -> str:
        return self.name.lower()


class ObservationQuality(BaseModel):
    valid_pixel_fraction: float = Field(ge=0, le=1)
    optical_image_count: int = Field(ge=0)
    sar_image_count: int = Field(ge=0)
    co_image_count: int = Field(ge=0)
    status: Literal["valid", "low_coverage", "missing"]
    reasons: list[str] = Field(default_factory=list)


class MonthlyObservation(BaseModel):
    region_id: str
    period_start: date
    period_end: date
    provider: str
    source_collections: list[str]
    ndvi_mean: float | None = Field(default=None, ge=-1, le=1)
    ndvi_p10: float | None = Field(default=None, ge=-1, le=1)
    ndvi_p90: float | None = Field(default=None, ge=-1, le=1)
    ndmi_mean: float | None = Field(default=None, ge=-1, le=1)
    vv_mean: float | None = None
    vh_mean: float | None = None
    co_mean: float | None = Field(default=None, ge=0)
    quality: ObservationQuality
    provenance: dict[str, Any] = Field(default_factory=dict)
    acquired_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.period_end <= self.period_start:
            raise ValueError("period_end must be after period_start")
        return self


class ModelPrediction(BaseModel):
    model_version: str
    expected_ndvi: float = Field(ge=-1, le=1)
    residual: float
    anomaly_score: float = Field(ge=0)
    uncertainty: float = Field(ge=0)
    feature_values: dict[str, float]


class RiskDecision(BaseModel):
    severity: Severity
    score: float = Field(ge=0, le=100)
    evidence: list[str]
    recommendations: list[str]
    rule_version: str = "risk-rules-v1"
    requires_human_review: bool = False
