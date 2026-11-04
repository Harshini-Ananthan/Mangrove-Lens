# Mangrove Lens live-system evidence — 2026-11-04

## Verification scope

The Docker Compose deployment was run with `SATELLITE_PROVIDER=earth_engine`, Google Earth Engine project `nex-sync`, PostgreSQL, and model `rf-20261103124059-3ebfaf48`. Existing host credentials were mounted read-only; no authentication was repeated and no credentials or map tokens are recorded here.

## Live dataset

`python -m scripts.backfill_earth_engine --start 2019-01-01 --workers 4` was executed inside the deployed API container, followed by `python -m scripts.validate_dataset`.

| Check | Result |
|---|---:|
| Period | 2019-01-01 through 2026-10-01 |
| Monthly observations | 94 |
| Valid | 90 |
| Low coverage | 4 |
| Missing months | 0 |
| Duplicate months | 0 |
| Mean valid-pixel fraction | 0.8622307431 |
| Null NDVI/NDMI/VV/VH/CO values | 0 |

The low-coverage periods were retained as quality evidence rather than replaced or imputed.

## Forced fresh Earth Engine REST run

`POST /api/v1/monitoring/run` was called for October 2026 with `refresh=true`.

- Job: `9defa8cc-8efe-4a1e-88ac-25c1bc9f7644`
- Provider: `earth_engine`
- Deduplicated: `false`
- Final checkpoint: `reported`
- Source window: `[2026-10-01, 2026-11-01)`
- Valid-pixel fraction: `0.9994215616`
- Sentinel-2 images: `121`
- Sentinel-1 images: `22`
- Sentinel-5P CO images: `439`
- Actual NDVI: `0.6934509982`
- NDMI: `0.4149540291`
- VV: `-8.5881232454`
- VH: `-14.5614040903`
- CO: `0.0443894327`

Stored source provenance:

- `COPERNICUS/S2_SR_HARMONIZED`
- `COPERNICUS/S1_GRD`
- `COPERNICUS/S5P/OFFL/L3_CO`
- `projects/mangrovedatahub2/assets/CGMD-Extent30`

The acquisition stored a new `query_executed_at` timestamp, proving that the forced run queried the provider rather than returning the earlier completed job.

## Model inference

For the refreshed October observation:

- Model version: `rf-20261103124059-3ebfaf48`
- Expected NDVI: `0.6895662664`
- Actual minus expected: `+0.0038847319`
- Anomaly score: `0.1294910620`
- Risk: `low`, `10/100`

The model used the previous 12 valid live monthly observations. Current NDVI is compared with the prediction after inference and is not included among the predictor inputs.

## Real critical alert case

A forced live run for March 2026 completed as job `59f6fa37-c9bb-4eec-91c6-b263f4504c39` and produced:

- Severity: `critical`
- Risk score: `80/100`
- Expected NDVI: `0.6687790715`
- NDVI residual: `-0.102527`
- Anomaly score: `3.4175823243`
- Human review required: `true`
- Evidence: NDVI below expectation, anomaly above three standard units, low moisture, and elevated CO treated as non-causal context
- Recommendation: urgent expert review and field verification before external action

The alert agent created dashboard outbox record `1` with status `sent`. Attempts to approve or externally dispatch this dashboard record both returned HTTP 409, demonstrating that dashboard delivery cannot bypass the external-notification review policy.

## Live map evidence

`GET /api/v1/map/tiles?period_start=2026-10-01&layer=ndvi` dynamically created a masked Sentinel-2 Earth Engine tile layer:

- Source: `COPERNICUS/S2_SR_HARMONIZED`
- Mask: `projects/mangrovedatahub2/assets/CGMD-Extent30`
- Images in composite: `121`
- Sample tile response: HTTP 200, `image/png`, 44,191 bytes

The signed tile URL/token is deliberately omitted.

## Agent and endpoint verification

The scheduler entry point was invoked once and completed the latest complete month as job `b8d8abdd-3a74-4cf3-aeda-e36a48a269a5`.

| Endpoint | Verified result |
|---|---|
| `GET /health` | 200; provider `earth_engine`, model ready |
| `GET /readiness` | 200; database, Earth Engine and model ready |
| `POST /monitoring/run` | 202; fresh live jobs completed |
| `GET /monitoring/features` | 200; live observations and provenance returned |
| `GET /monitoring/decisions` | 200; model/rule decisions returned |
| `GET /monitoring/jobs` | 200; acquisition-to-report checkpoints returned |
| `GET /alerts/outbox` | 200; real critical dashboard alert returned |
| `POST /alerts/outbox/{id}/approve` | Expected 409 guard for dashboard channel |
| `POST /alerts/outbox/{id}/dispatch` | Expected 409 guard for dashboard channel |
| `GET /aoi` | 200; transboundary operational AOI |
| `GET /grid` | 200; 1,276 5-km cells |
| `GET /map/tiles` | 200; generated live Earth Engine tiles |

Validation guards also returned HTTP 422 for a future monitoring month, a sub-1-km grid, and a zero result limit. Browser CORS preflight from `http://localhost:5173` returned HTTP 200 with the correct allow-origin header.

## Safety boundary

Dashboard monitoring is fully operational. Email and Telegram are implemented but were not invoked because no recipients are configured, external notifications are disabled, and the observational model is not marked production-approved. Those controls are intentional; they prevent an unreviewed scientific model from sending external conservation alerts.
