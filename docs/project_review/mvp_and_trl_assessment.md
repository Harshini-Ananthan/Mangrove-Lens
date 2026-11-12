# MVP status and technology readiness

Assessment date: **12 November 2026**. Source of implementation claims: inspected repository files and recorded runs; runtime availability today is not implied by a prior run. NASA defines TRL 4 as component validation in a laboratory and TRL 5 as validation in a relevant environment (NASA Earth Science and Technology Office, *Technology Readiness Levels*, date not stated, [definitions](https://esto.nasa.gov/trl/)).

| Capability | Status | Evidence / boundary |
|---|---|---|
| Earth Engine acquisition of S2/S1/S5P and mask | **Implemented** | [provider](../../src/providers/earth_engine.py); authenticated 2026-11-04 [run](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md). |
| Monthly AOI feature store and quality checks | **Implemented** | [dataset validation](../../reports/dataset_validation.json): 94 months, 90 valid, four low coverage. |
| Random Forest AOI NDVI expectation | **Implemented; partially validated** | [training code](../../scripts/train_model.py), [evaluation](../../reports/model_evaluation.json): 12-month temporal holdout only. |
| Deterministic agent stages, audit log and scheduler | **Implemented** | [orchestrator](../../src/agents/orchestrator.py), [scheduler](../../scripts/run_scheduler.py), [live run](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md). Long-term uptime unmeasured. |
| Dashboard, Earth Engine map, report export | **Implemented prototype** | [frontend](../../frontend/src/pages/Dashboard.jsx), [reporting](../../src/services/reporting.py), [live map evidence](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md). User usability untested. |
| Email/Telegram external dispatch | **Partially implemented** | [notifications](../../src/services/notifications.py); external notifications disabled, SMTP recipients absent and model approval false in [config](../../.env.example)/[manifest](../../models/ndvi_forecast_rf.manifest.json). No delivered official email evidenced. |
| Cell-level anomaly/loss map | **Not started as ML pipeline** | [grid](../../src/services/grid.py) generates geometry only; single AOI in [validation](../../reports/dataset_validation.json). |
| Ground-truth incident validation | **Not started** | No labels, adjudication protocol or field results in repository. |
| Operator user testing / partner pilot | **Not started** | No recruitment, observations, signed pilot or quote evidence. |
| Ecological impact evaluation | **Proposed** | No measured change in loss, survival, carbon or community outcome. |

**Overall TRL recommendation: 4.** The integrated software can ingest real EO data, run inference and produce outputs in a controlled deployment, but its conservation decision function has not been validated with independent real-world incidents or operators. A component-level TRL 5 argument could be made for the EO/API pipeline; do not apply that to the whole system. To claim TRL 5 overall, complete a relevant-environment analyst pilot with field/high-resolution reference and documented performance. TRL 6 would need a sustained operational demonstration and reliability evidence.

**Verification performed for this review:** the React frontend production build passed and `python -m pytest -q` passed **19 tests** on 12 Nov 2026. The Docker Desktop engine was unavailable during this review, so no fresh authenticated Earth Engine run was performed today; see [live evidence](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md) for the last recorded authenticated run. A passed code suite does not establish field accuracy or service uptime.
