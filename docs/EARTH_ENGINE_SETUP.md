# Earth Engine setup

The live provider uses Google Cloud project `nex-sync`. Development defaults to the deterministic demo provider so a missing credential can never silently become synthetic "live" data.

## Interactive development

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\earthengine set_project nex-sync
.venv\Scripts\earthengine authenticate
```

Set the following in `.env` after authentication:

```dotenv
EE_PROJECT_ID=nex-sync
SATELLITE_PROVIDER=earth_engine
```

Verify readiness at `GET /api/v1/health`. A live provider failure returns an explicit unavailable state and never falls back to demo observations.

## Unattended deployment

Use a dedicated Google Cloud service account belonging to `nex-sync`:

1. register the project for noncommercial Earth Engine access and enable the Earth Engine API;
2. grant the service account only the Earth Engine and storage permissions the deployment needs;
3. provide credentials through the deployment platform's secret manager, never through Git;
4. test a small AOI/one-month smoke query before enabling the scheduler.

The operational envelope is `data/aoi/sundarbans_transboundary_envelope.geojson`. Live calculations are intersected with the 2023 CGMD mangrove extent (`projects/mangrovedatahub2/assets/CGMD-Extent30`). This is an analysis boundary, not a political boundary.
