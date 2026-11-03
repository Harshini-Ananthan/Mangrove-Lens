from __future__ import annotations

import hashlib
import math
from datetime import date
from typing import Any

from dateutil.relativedelta import relativedelta

from src.domain.contracts import MonthlyObservation, ObservationQuality
from src.providers.base import SatelliteProvider


class DemoSatelliteProvider(SatelliteProvider):
    """Deterministic provider for tests and UI demos. Never masquerades as live data."""

    name = "demo"

    def monthly_observation(
        self, region_id: str, geometry: dict[str, Any], period_start: date
    ) -> MonthlyObservation:
        period_start = period_start.replace(day=1)
        period_end = period_start + relativedelta(months=1)
        digest = hashlib.sha256(f"{region_id}:{period_start.isoformat()}".encode()).digest()
        spatial = (int.from_bytes(digest[:2], "big") / 65535 - 0.5) * 0.08
        seasonal = 0.08 * math.sin((period_start.month - 1) / 12 * 2 * math.pi)
        trend = -0.0015 * max(0, (period_start.year - 2019) * 12 + period_start.month - 1)
        ndvi = max(0.15, min(0.85, 0.62 + seasonal + spatial + trend))
        co = max(0.01, 0.028 - seasonal * 0.025 + spatial * 0.02)
        return MonthlyObservation(
            region_id=region_id,
            period_start=period_start,
            period_end=period_end,
            provider=self.name,
            source_collections=["DEMO/DETERMINISTIC/V1"],
            ndvi_mean=round(ndvi, 5),
            ndvi_p10=round(ndvi - 0.12, 5),
            ndvi_p90=round(ndvi + 0.10, 5),
            ndmi_mean=round(ndvi - 0.08, 5),
            vv_mean=round(-11.0 + spatial * 8, 4),
            vh_mean=round(-18.0 + spatial * 7, 4),
            co_mean=round(co, 7),
            quality=ObservationQuality(
                valid_pixel_fraction=0.82,
                optical_image_count=6,
                sar_image_count=4,
                co_image_count=20,
                status="valid",
            ),
            provenance={"synthetic": True, "geometry_type": geometry.get("type")},
        )

    def readiness(self) -> tuple[bool, str]:
        return True, "deterministic demo provider ready"
