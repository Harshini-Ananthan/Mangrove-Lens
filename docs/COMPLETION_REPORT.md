# Mangrove Lens completion report

Date: 2026-11-03
Software status: end-to-end implementation complete; external conservation validation gates remain deliberately locked.

## Verified live outcome

- Google Earth Engine project: `nex-sync`
- Observational period: January 2019 through October 2026
- Monthly observations: 94
- Temporal gaps/duplicates: 0/0
- Quality: 90 valid, 4 low-coverage periods
- Mean valid-pixel fraction: 0.8622
- Missing NDVI/NDMI/SAR/CO model fields: 0
- Model: Random Forest current-month expected NDVI from prior observations
- Held-out MAE: 0.03055
- Persistence MAE: 0.04841
- Held-out R2: 0.4888
- End-to-end October 2026 decision: low risk, anomaly score 0.1295

Evidence is versioned in `reports/dataset_validation.json`, `reports/model_evaluation.json`, and `reports/end_to_end_validation_2026-10.json`.

## Implemented system

- full transboundary operational AOI and stable 5 km analysis grid;
- CGMD 2023 independent mangrove extent mask;
- Sentinel-2 cloud/shadow masking and NDVI/NDMI;
- Sentinel-1 VV/VH evidence and Sentinel-5P OFFL CO context;
- idempotent historical acquisition and provenance/quality storage;
- leakage-safe temporal model training and held-out baseline comparison;
- versioned model artifact and manifest;
- asynchronous API monitoring jobs with checkpoints and failure state;
- deterministic risk engine with non-causal CO wording;
- alert review/outbox lifecycle with API-key protection;
- dashboard status, trends, AOI, job execution, and alert review;
- monthly scheduler, PostgreSQL/SQLite support, Docker Compose, CI, and runbook;
- 13 backend tests at 73% source coverage plus frontend lint/build verification.

## Deliberately locked external gates

These are not software defects and cannot be truthfully self-certified by the development agent:

1. A named mangrove/conservation expert must review risk thresholds and recommended actions.
2. Independent field/reference samples must be used for local accuracy and alert validation.
3. Shadow alerts must run before operational notification recipients are enabled.
4. A deployment operator must configure secrets, backup policy, recipients, and the production service account.

Until those gates are documented, `production_approved` remains false and email/Telegram alerts remain `pending_validation`. Dashboard monitoring and research analysis are operational.
