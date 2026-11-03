# Mangrove Lens - Verified Implementation Plan

Status: implementation baseline, 2026-11-03
Scope: transboundary Sundarbans (India and Bangladesh), research/noncommercial deployment

## 1. Product outcome

Mangrove Lens will be an auditable, autonomous monitoring system that:

1. acquires satellite and environmental observations for a versioned Sundarbans area of interest (AOI);
2. creates quality-controlled monthly spatial cells and time-series features;
3. forecasts expected vegetation condition and detects statistically unusual change;
4. evaluates mangrove loss evidence against independent reference data;
5. produces explainable risk assessments, recommended actions, alerts, and reports;
6. exposes the results through an API and the existing React map dashboard; and
7. runs on a schedule with idempotency, retries, provenance, and human review for high-impact alerts.

The system is decision support, not proof that CO caused vegetation loss. Every alert must show observation date, source coverage, model version, confidence/evidence, and the rule that fired.

## 2. Scientific decisions

### 2.1 Primary task

The first defensible model is a Random Forest regression model that forecasts monthly NDVI anomaly (or next-month NDVI) per spatial cell. Residuals and sustained trend changes feed anomaly detection. This avoids circular evaluation.

A supervised healthy/moderate/degraded classifier is a secondary model only after labels are created from independent mangrove-extent/change products and/or reviewed field observations. NDVI-derived classes must not be used as both target and evidence of independent predictive skill.

### 2.2 Spatial and temporal unit

- AOI: versioned GeoJSON covering the transboundary Sundarbans; start from authoritative protected-area boundaries, then intersect/expand with a Global Mangrove Watch (GMW) mangrove mask and document the chosen operational boundary.
- Analysis grid: equal-area cells, initially 1 km, with stable cell IDs. Ten-metre products remain available for map tiles and targeted inspection.
- Cadence: monthly composites for modeling; new source observations checked weekly.
- Initial history: January 2019 through the latest complete month. Older Landsat/GMW data can support historical validation.
- Split: expanding-window temporal cross-validation; the final 12 complete months are held out. Nearby pixels from the same month must not leak across train/test folds.

### 2.3 Evidence hierarchy

1. Independent extent/change or reviewed field evidence.
2. Persistent optical and SAR change agreeing across multiple periods.
3. Optical-only vegetation anomaly with adequate clear-pixel coverage.
4. Context variables such as CO, rainfall, cyclone exposure, and water occurrence.

CO is contextual evidence at its native/coarse support and is never treated as a pixel-scale causal label.

## 3. Dataset suitability

| Source | Role | Resolution/cadence | Suitability and controls |
|---|---|---|---|
| `COPERNICUS/S2_SR_HARMONIZED` | NDVI, EVI, NDMI, NDWI, NBR; map imagery | 10-20 m, about 5 days | Primary optical source. Mask clouds/shadows with SCL plus Cloud Score+/cloud probability; store valid-pixel fraction and observation count. Harmonized collection prevents the 2022 processing-baseline shift from becoming a false change. |
| `COPERNICUS/S1_GRD` | VV/VH backscatter and change evidence | 10 m, all-weather | Essential in the persistently cloudy delta. Filter to a homogeneous orbit, mode, resolution, and polarization; compare like-for-like monthly composites. |
| `COPERNICUS/S5P/OFFL/L3_CO` | atmospheric context | about 1.1 km grid, frequent orbits | Suitable only after quality filtering and monthly aggregation. Do not resample it as if it were 10 m evidence. Use OFFL, not NRTI, for reproducible history. |
| Global Mangrove Watch v4.1 | mangrove mask and independent annual extent/change reference | 30 m, annual 1985-2025 | Best current open baseline. Use for AOI refinement and weak/independent labels, while reporting global-product uncertainty and local validation limits. Pin the exact release and checksum. |
| CHIRPS daily/monthly | rainfall anomaly | about 5 km | Useful environmental driver; aggregate to cells/months and track missing coverage. |
| ERA5-Land monthly | temperature, soil moisture, wind/context | about 9 km | Optional coarse covariates; no fine-scale claims. |
| IBTrACS | cyclone proximity/intensity | storm tracks | Event context and validation windows for known disturbances. |
| JRC Global Surface Water | persistent/seasonal water mask | 30 m | Prevent water/tidal transitions from being mislabeled as vegetation loss. |
| Field observations | validation and alert closure | point/polygon, irregular | Required for local accuracy claims. Store reviewer, timestamp, geometry, photo/reference, and label provenance. |

Raw imagery should remain in Earth Engine/object storage. The application stores compact features, provenance, thumbnails/tile references, and derived products rather than duplicating the full archive.

## 4. Target architecture

```text
Scheduler/API
    -> acquisition workflow (GEE adapters + source registry)
    -> quality checks and monthly composites
    -> spatial-cell feature store
    -> model registry and inference
    -> deterministic risk/decision engine
    -> recommendation and alert policy
    -> database/outbox
    -> dashboard, email/Telegram adapters, periodic reports
```

Agent orchestration will use a durable state graph, but scientific calculations and risk rules remain deterministic Python services. An LLM is optional for natural-language summaries only; it cannot invent observations, change risk scores, or send high-severity external notifications without policy approval.

### Agent responsibilities

- Collector: plans periods/cells, queries sources, records lineage, and retries transient failures.
- Quality agent: rejects low-coverage or inconsistent observations and records reasons.
- Prediction agent: loads an approved model/version and writes predictions plus uncertainty.
- Decision agent: combines residuals, trends, persistence, cross-sensor evidence, and data quality.
- Recommendation agent: selects actions from a version-controlled rule catalogue.
- Alert agent: deduplicates alerts, applies cooldown/escalation, and writes to an outbox.
- Reporting agent: creates source-linked summaries from stored results.

## 5. Repository implementation

### Phase 0 - engineering baseline

- Pin Python and Node dependencies; add reproducible setup commands and CI.
- Add typed settings, structured logging, migrations, error contracts, and separate development/test databases.
- Remove silent production fallback to random data. A clearly labeled deterministic demo provider is allowed only in demo/test mode.
- Add health/readiness endpoints that report database, model, and Earth Engine readiness independently.

Acceptance: clean install, backend and frontend builds, migration succeeds, and smoke tests run without network credentials.

### Phase 1 - geospatial data foundation

- Add a versioned Sundarbans AOI and grid-generation script.
- Implement source/provider interfaces and an Earth Engine provider initialized with `EE_PROJECT_ID`.
- Implement optical cloud/shadow masking, indices, SAR composites, OFFL CO aggregation, coverage metrics, and provenance.
- Add idempotent ingestion jobs and feature-store tables.
- Add a small deterministic fixture dataset for offline integration tests.

Acceptance: one command creates monthly features for a requested period; rerunning creates no duplicates; invalid/empty imagery produces an explicit data-quality state.

### Phase 2 - model and validation

- Build feature generation with lags, rolling medians, seasonal baselines, deltas, observation coverage, rainfall/SAR/CO context, and strict cutoff dates.
- Add naive seasonal and persistence baselines.
- Train/tune Random Forest with temporal cross-validation; record parameters, features, metrics, data manifest, code revision, and artifact hash.
- Generate residual/anomaly thresholds from validation data and spatial block diagnostics.
- Add optional classification only when independent labels meet a documented label-quality gate.

Acceptance: reproducible training command; no temporal leakage tests; model beats the declared baseline on held-out MAE/RMSE (or is rejected); evaluation includes per-season/per-region errors and uncertainty limitations.

### Phase 3 - autonomous decision workflow

- Implement state graph, job state/checkpoints, retry policy, and audit events.
- Implement explicit severity enum and calibrated evidence rules.
- Add alert deduplication, cooldown, acknowledgement, resolution, and notification outbox.
- Add dry-run mode and human approval for external high/critical notifications.

Acceptance: replaying a job is safe; each decision is reproducible from stored inputs/rules/model; failure resumes from the last safe checkpoint; alert tests cover escalation and suppression.

### Phase 4 - API and dashboard

- Replace mock frontend data with API queries and environment-based base URL.
- Add map layers for AOI/grid, latest indices, risk, data quality, and time comparison.
- Add cell detail with trends, evidence, model/version, confidence, recommendations, and alert lifecycle.
- Add run status, source freshness, degraded-mode banners, exports, and accessible loading/error/empty states.

Acceptance: end-to-end Playwright tests cover map selection, history, evidence inspection, job execution in demo mode, alert acknowledgement, and failure states.

### Phase 5 - operations and research validation

- Containerize API, worker, scheduler, frontend, and database; provide local Compose deployment.
- Add scheduled weekly acquisition and monthly scoring with locks, metrics, backups, retention, and runbooks.
- Conduct local validation using stratified samples and expert/field review; calculate confusion/forecast metrics with confidence intervals.
- Run shadow alerts before enabling external delivery.

Acceptance: 30-day staging soak; no duplicate jobs/alerts; recovery drill passes; documented scientific sign-off and go/no-go checklist.

## 6. Test strategy

- Unit: masks, index formulas, aggregation, feature cutoffs, severity ordering, rule explanations, deduplication.
- Property/contract: geometry validation, provider schemas, bounded indices, timezone/date behavior.
- ML: schema checks, leakage guards, deterministic seeds, baseline comparison, artifact compatibility, drift calculations.
- Integration: fixture provider -> features -> prediction -> decision -> database -> API.
- Earth Engine smoke: small AOI/short period, marked and skipped without credentials.
- API: validation, pagination, idempotency, authorization-ready boundaries, failure contracts.
- Frontend: component tests, API mocking, accessibility, production build, end-to-end critical paths.
- Operations: migration forward/backward, scheduler locks, retry/replay, outbox delivery, backup restore.

## 7. Verification and review gates

The plan is considered verified only when the following reviewers/gates agree:

1. Scientific validity: independent labels, temporal/spatial leakage controls, baselines, uncertainty, and non-causal wording.
2. Geospatial validity: AOI provenance, sensor QA, scale/projection, tidal/water masking, and resolution alignment.
3. ML validity: reproducibility, held-out metrics, error slices, artifact lineage, and drift thresholds.
4. Software validity: tests, migrations, security/configuration, observability, and failure recovery.
5. Conservation workflow validity: recommendations reviewed by a domain expert; high-impact alerts require human confirmation until field performance is established.

## 8. Known gaps in the initial repository

- No training pipeline, trained model, model manifest, evaluation, or tests.
- Earth Engine initialization ignores configured project ID and silently falls back to random values.
- Sentinel-2 has scene-level cloud filtering but no pixel cloud/shadow mask or coverage score.
- Sentinel-5P uses NRTI rather than the paper's reproducible OFFL collection.
- Synchronous `getInfo()` calls block API requests and cannot support reliable bulk processing.
- Static universal thresholds are uncalibrated for seasonality, tides, or spatial variation.
- Severity uses string comparison, which does not implement the intended risk order.
- Database schema lacks source lineage, job state, model version, quality, evidence, acknowledgement, and deduplication fields.
- Notification is simulated; frontend API URL/CORS are hard-coded; mock UI data are not connected end to end.

## 9. Credentials and decisions needed from the project owner

Implementation can proceed in deterministic demo mode, but live validation/deployment needs:

- a registered noncommercial Google Cloud project with Earth Engine enabled (`EE_PROJECT_ID`), plus a decision between local user authentication and a deployment service account;
- confirmation that the operational AOI is the full transboundary ecosystem rather than only the Indian Sundarbans or UNESCO protected properties;
- preferred notification channels and test recipients (dashboard only, email, Telegram);
- access to any field observations/expert labels and the conservation expert who can review action recommendations;
- intended deployment target and whether PostgreSQL/PostGIS is acceptable for production.

## 10. Delivery and Git workflow

Work is performed on `codex/autonomous-mangrove-lens`. Each phase ends with passing checks and a reviewable commit. The pull request will include the data manifest, evaluation report, deployment/runbook documentation, and evidence of test results. Merge occurs only after CI and the scientific/software review gates pass; production notifications remain disabled until the shadow-alert gate is approved.
