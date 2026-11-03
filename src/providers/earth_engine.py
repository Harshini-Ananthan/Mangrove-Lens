from __future__ import annotations

from datetime import date
from typing import Any

from dateutil.relativedelta import relativedelta

from src.domain.contracts import MonthlyObservation, ObservationQuality
from src.providers.base import SatelliteProvider
from src.utils.config import settings


class EarthEngineProvider(SatelliteProvider):
    name = "earth_engine"
    S2 = "COPERNICUS/S2_SR_HARMONIZED"
    S1 = "COPERNICUS/S1_GRD"
    CO = "COPERNICUS/S5P/OFFL/L3_CO"
    MANGROVE_EXTENT = "projects/mangrovedatahub2/assets/CGMD-Extent30"
    MANGROVE_REFERENCE_YEAR = 2023

    def __init__(self):
        self._ee = None
        self._error: str | None = None
        try:
            import ee

            ee.Initialize(project=settings.EE_PROJECT_ID)
            self._ee = ee
        except Exception as exc:  # readiness reports actionable detail
            self._error = str(exc)

    def readiness(self) -> tuple[bool, str]:
        if self._ee is None:
            return False, f"Earth Engine unavailable: {self._error}"
        return True, f"Earth Engine ready via project {settings.EE_PROJECT_ID}"

    @staticmethod
    def _mask_s2(image):
        scl = image.select("SCL")
        valid = (
            scl.neq(1)
            .And(scl.neq(3))
            .And(scl.neq(7))
            .And(scl.neq(8))
            .And(scl.neq(9))
            .And(scl.neq(10))
            .And(scl.neq(11))
        )
        return image.updateMask(valid).divide(10000).copyProperties(image, ["system:time_start"])

    @staticmethod
    def _add_indices(image):
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
        ndmi = image.normalizedDifference(["B8", "B11"]).rename("NDMI")
        return image.addBands([ndvi, ndmi])

    def monthly_observation(
        self, region_id: str, geometry: dict[str, Any], period_start: date
    ) -> MonthlyObservation:
        ready, message = self.readiness()
        if not ready:
            raise RuntimeError(message)
        ee = self._ee
        period_start = period_start.replace(day=1)
        period_end = period_start + relativedelta(months=1)
        start, end = period_start.isoformat(), period_end.isoformat()
        roi = ee.Geometry(geometry)
        extent = (
            ee.FeatureCollection(self.MANGROVE_EXTENT)
            .filter(ee.Filter.eq("year", self.MANGROVE_REFERENCE_YEAR))
            .filterBounds(roi)
        )
        if int(extent.size().getInfo()) == 0:
            raise RuntimeError("The operational AOI does not intersect the configured mangrove reference extent")
        # Rasterize the independent extent instead of reducing over its highly
        # complex multipart geometry. This keeps whole-delta reductions bounded.
        mangrove_mask = extent.reduceToImage(["gridcode"], ee.Reducer.first()).gt(0)

        s2 = (
            ee.ImageCollection(self.S2)
            .filterBounds(roi)
            .filterDate(start, end)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 80))
            .map(self._mask_s2)
            .map(self._add_indices)
        )
        s2_count = int(s2.size().getInfo())
        s1 = (
            ee.ImageCollection(self.S1)
            .filterBounds(roi)
            .filterDate(start, end)
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
            .select(["VV", "VH"])
        )
        co = (
            ee.ImageCollection(self.CO)
            .filterBounds(roi)
            .filterDate(start, end)
            .select("CO_column_number_density")
        )
        s1_count, co_count = int(s1.size().getInfo()), int(co.size().getInfo())
        if s2_count == 0:
            quality = ObservationQuality(
                valid_pixel_fraction=0,
                optical_image_count=0,
                sar_image_count=s1_count,
                co_image_count=co_count,
                status="missing",
                reasons=["no Sentinel-2 images for period"],
            )
            return MonthlyObservation(
                region_id=region_id,
                period_start=period_start,
                period_end=period_end,
                provider=self.name,
                source_collections=[self.S2, self.S1, self.CO, self.MANGROVE_EXTENT],
                quality=quality,
                provenance={"ee_project": settings.EE_PROJECT_ID},
            )

        optical = s2.median().select(["NDVI", "NDMI"]).updateMask(mangrove_mask)
        optical_stats = optical.reduceRegion(
            reducer=ee.Reducer.mean().combine(ee.Reducer.percentile([10, 90]), sharedInputs=True),
            geometry=roi,
            scale=100,
            maxPixels=1e9,
            bestEffort=True,
        ).getInfo()
        pixel_area = ee.Image.pixelArea()
        valid_area = pixel_area.updateMask(optical.select("NDVI").mask()).reduceRegion(
            reducer=ee.Reducer.sum(), geometry=roi, scale=100, maxPixels=1e8, bestEffort=True
        ).get("area", 0)
        mangrove_area = pixel_area.updateMask(mangrove_mask).reduceRegion(
            reducer=ee.Reducer.sum(), geometry=roi, scale=100, maxPixels=1e8, bestEffort=True
        ).get("area", 0)
        valid_fraction = float(ee.Number(valid_area).divide(ee.Number(mangrove_area).max(1)).getInfo())
        sar_stats = (
            s1.median().updateMask(mangrove_mask).reduceRegion(
                ee.Reducer.mean(), roi, 100, maxPixels=1e8, bestEffort=True
            ).getInfo()
            if s1_count
            else {}
        )
        co_stats = (
            co.mean().reduceRegion(ee.Reducer.mean(), roi, 1113.2, maxPixels=1e8, bestEffort=True).getInfo()
            if co_count
            else {}
        )
        reasons = [] if valid_fraction >= settings.MIN_VALID_PIXEL_FRACTION else ["optical valid-pixel coverage below threshold"]
        return MonthlyObservation(
            region_id=region_id,
            period_start=period_start,
            period_end=period_end,
            provider=self.name,
            source_collections=[self.S2, self.S1, self.CO, self.MANGROVE_EXTENT],
            ndvi_mean=optical_stats.get("NDVI_mean"),
            ndvi_p10=optical_stats.get("NDVI_p10"),
            ndvi_p90=optical_stats.get("NDVI_p90"),
            ndmi_mean=optical_stats.get("NDMI_mean"),
            vv_mean=sar_stats.get("VV"),
            vh_mean=sar_stats.get("VH"),
            co_mean=co_stats.get("CO_column_number_density"),
            quality=ObservationQuality(
                valid_pixel_fraction=valid_fraction,
                optical_image_count=s2_count,
                sar_image_count=s1_count,
                co_image_count=co_count,
                status="valid" if not reasons else "low_coverage",
                reasons=reasons,
            ),
            provenance={
                "ee_project": settings.EE_PROJECT_ID,
                "aggregation_scale_m": 100,
                "native_optical_resolution_m": 10,
                "mangrove_reference_year": self.MANGROVE_REFERENCE_YEAR,
                "mangrove_reference_role": "independent extent mask",
            },
        )
