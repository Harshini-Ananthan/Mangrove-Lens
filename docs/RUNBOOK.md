# Mangrove Lens operations runbook

## Safety defaults

- `SATELLITE_PROVIDER=demo` unless live Earth Engine mode is deliberately enabled.
- `ENABLE_EXTERNAL_NOTIFICATIONS=false` until observational validation and shadow monitoring pass.
- `REQUIRE_ALERT_APPROVAL=true`; high-impact alerts require a named operator.
- Set `API_KEY` in deployed environments. Never commit API, SMTP, Telegram, Google, or database secrets.

## Start and verify

```powershell
docker compose up --build -d db api frontend
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-RestMethod http://localhost:8000/api/v1/readiness
```

The dashboard is served at `http://localhost:5173`. API documentation is at `http://localhost:8000/docs`.

## Historical acquisition and model training

```powershell
.venv\Scripts\python -m scripts.backfill_earth_engine --start 2019-01-01 --workers 4
.venv\Scripts\python -m scripts.train_model
```

Do not approve the generated model merely because training completed. Review `reports/model_evaluation.json`; the Random Forest must beat persistence on held-out time periods and the report must identify observational data.

## Monthly workflow

Run the scheduler profile only after the model and readiness checks pass:

```powershell
docker compose --profile scheduler up -d scheduler
```

It runs the latest complete month on the fifth day of each month. Jobs are idempotently deduplicated by region, period, and provider at the API boundary.

## Alert lifecycle

1. Moderate or higher decisions enter `alert_outbox`.
2. Dashboard alerts are immediately visible.
3. Email/Telegram alerts remain `pending_review`.
4. An authenticated operator approves an alert.
5. Dispatch sends it only when `ENABLE_EXTERNAL_NOTIFICATIONS=true`.
6. Failures remain retryable with an attempt count and error message.

## Recovery

- Failed Earth Engine month: rerun the backfill; existing rows are skipped.
- Failed monitoring job: inspect `/api/v1/monitoring/jobs`, correct the cause, and submit the period again.
- Failed notification: inspect `/api/v1/alerts/outbox?status_filter=failed`, then redispatch after correcting channel configuration.
- Database: use PostgreSQL volume snapshots in deployment. Restore into a separate instance and run readiness checks before promotion.

## Production promotion checklist

- observational model beats declared baseline;
- temporal/seasonal error slices reviewed;
- at least one conservation/domain expert approves risk rules and recommendations;
- field/reference samples validate representative high/low-risk locations;
- shadow alerts run without duplicate or spurious escalation;
- API key and secret manager configured;
- PostgreSQL backup/restore drill passes;
- notification test recipients approve email/Telegram formatting;
- external notifications explicitly enabled only after all previous gates.
