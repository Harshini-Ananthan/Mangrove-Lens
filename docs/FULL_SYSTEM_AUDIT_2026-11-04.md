# Mangrove Lens full-system audit — 2026-11-04

## Audit outcome

The deployed stack was audited against live Google Earth Engine acquisition, PostgreSQL persistence, model inference/retraining, deterministic agent decisions, map synchronization, PDF reporting, official-email delivery, scheduling, Docker deployment, and UI truthfulness.

Satellite data is dynamic but not instantaneous: Sentinel collections become available on their publication cadence, and Mangrove Lens analyzes completed monthly windows. The UI polls system state every 15 seconds and refreshes the matching Earth Engine layer when the selected observation changes.

## Gaps found before this audit

- Sidebar displayed the internal Earth Engine readiness string.
- Product heading said “Sundarbans” instead of “Mangrove Lens.”
- Sidebar could not be collapsed.
- Menu, News, language, Help, search, notification/settings and measurement controls were nonfunctional or legacy.
- The trend card contained a hard-coded `+0.01` statement.
- The map legend did not match the live Earth Engine visualization range or palette.
- Statistics used the latest row while the map used the selected year, so periods could diverge.
- The dashboard did not poll for server-side changes.
- Export Report had no action.
- No detailed PDF or high-resolution Earth Engine evidence images were generated.
- SMTP delivery did not attach reports and approved alerts were not automatically dispatched.
- The scheduler required an optional Compose profile and only monitored; it did not reconcile history or retrain.
- Retraining was manual and model artifact replacement was not atomic.
- Legacy dummy search/navigation components remained in the repository.

## Changes implemented

### UI and synchronization

- Renamed the visible product title and document title to **Mangrove Lens**.
- Added the Mangrove Lens SVG favicon and theme metadata.
- Removed the provider/readiness banner, search bar, fake navigation and unused legacy components.
- Removed the hard-coded trend delta; the chart now reports the number of live months.
- Added close/open controls for a responsive collapsible sidebar.
- Kept only controls with implemented behavior.
- Bound map tile, measurements, prediction, risk and report to the same selected June period.
- Added 15-second polling for observations, decisions and alerts; tile regeneration follows observation `updated_at` changes.
- Corrected the NDVI legend to Earth Engine range `-0.2` through `0.9` and the exact seven-color palette.
- Renamed the boundary legend to “Operational AOI boundary,” avoiding a false mangrove-extent claim.

### Reporting and official email

- Added a server-generated A4 PDF for every completed monitoring decision.
- Reports include AOI/period, source provenance, collection IDs, quality and image counts, NDVI/NDMI/SAR/CO measurements, model version/output/uncertainty, risk evidence, recommendations and safety context.
- Added 1,800-pixel Earth Engine true-color and NDVI evidence images.
- Added `GET /api/v1/reports/{decision_id}` and connected the dashboard Export Report button.
- Added PDF attachment support to SMTP notifications.
- Added automatic monthly low-risk report email support and automatic alert/report dispatch when external notifications are enabled, the validated model is approved, and per-alert approval is disabled.

### Autonomous operations

- Scheduler now starts in the normal Compose stack, performs startup reconciliation, and runs at 03:00 UTC on the fifth day of each month.
- Cycle order is leakage-safe: backfill missing completed months → monitor/infer/report/alert → retrain for the following month.
- Backfill now raises on failed periods instead of printing a false-success completion.
- Scheduler and API jobs remain idempotent for completed region/period/provider combinations.
- Retraining still rejects any Random Forest that does not beat persistence.
- Model artifact and manifest replacement is atomic.
- Optional `AUTO_APPROVE_VALIDATED_MODELS` enables automatic operational promotion after the observational/baseline gates; it is disabled by default.

## Live verification evidence

- Earth Engine project: `nex-sync`
- Historical live dataset: 94 months, 90 valid, 4 low coverage, no gaps/duplicates/null features.
- Scheduler startup reconciliation skipped all existing months correctly.
- Latest completed monitoring job was detected and not duplicated.
- Scheduler retrained and promoted model `rf-20261104152349-8bf04d2e` for inference.
- Retrained MAE: `0.0305559`; persistence MAE: `0.0484141`; observational gate passed.
- Fresh June 2025 live job: `aefb822e-02db-4ad6-b66c-0d0908f20e58`, provider `earth_engine`, checkpoint `reported`.
- Generated decision 3 report: HTTP 200, `application/pdf`, 4 A4 pages, 1,992,027 bytes.
- Embedded source images verified directly from Earth Engine:
  - true-color: 1,800 × 1,118 pixels, 875,369 bytes;
  - NDVI: 1,800 × 1,118 pixels, 686,371 bytes.
- SMTP attachment behavior is covered by a fake-server integration test that verifies recipient, TLS/login, and attached PDF filename.
- Final backend suite: 19 passed, 71.11% coverage (70% gate passed).
- Frontend lint and production build passed; Docker Compose validation and final live readiness passed.

## Autonomous external-email activation

External delivery is intentionally inactive until SMTP recipients and deployment policy are configured. For automatic official delivery set:

```env
ENABLE_EXTERNAL_NOTIFICATIONS=true
AUTO_EMAIL_REPORTS=true
AUTO_APPROVE_VALIDATED_MODELS=true
REQUIRE_ALERT_APPROVAL=false
SMTP_HOST=...
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
ALERT_EMAIL_TO=...
```

Then restart API/scheduler and allow one successful retraining cycle. Keeping `REQUIRE_ALERT_APPROVAL=true` preserves operator approval for external high-impact alerts while dashboard monitoring remains automatic.
