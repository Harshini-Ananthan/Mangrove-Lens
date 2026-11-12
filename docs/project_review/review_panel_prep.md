# Project review panel preparation

The following answers are deliberately bounded by the repository and primary sources. Core references: [live-system evidence](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md), [dataset validation](../../reports/dataset_validation.json), [model evaluation](../../reports/model_evaluation.json), [model manifest](../../models/ndvi_forecast_rf.manifest.json), Global Mangrove Alliance’s [GMW 4.1 launch](https://www.mangrovealliance.org/news/global-mangrove-watch-4-launch) (27 Jul 2026), Yancho et al.’s [GEEMMM](https://www.mdpi.com/2072-4292/12/22/3758) (16 Nov 2020), and Bangladesh Forest Department’s [BFIS](https://bfis.bforest.gov.bd/bfis/) (date not stated).

## Five strongest arguments for the project

1. **Real EO data path:** authenticated Earth Engine acquisitions and map tiles were recorded for a fresh Oct 2026 run, with collection names and timestamps in the [audit](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md).
2. **Reviewable scientific signal:** the pipeline retains quality, provenance, a model version, expected-vs-observed NDVI and a rule explanation, rather than a bare colour on a map ([monitoring service](../../src/services/monitoring.py)).
3. **A measured baseline:** the 12-month temporal holdout MAE 0.0306 beats persistence MAE 0.0484 for AOI NDVI on that split; this is a narrow but real experiment ([evaluation](../../reports/model_evaluation.json)).
4. **Operational integration:** API, dashboard, scheduler, reports and audit log exist as one workflow ([run evidence](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md)).
5. **Relevant scope:** the transboundary Sundarbans is ecologically important and has public program/agency monitoring contexts (UNESCO, [Sundarbans](https://www.unesco.org/en/articles/sundarbans?hub=70318), 2024; MoEFCC/PIB, [MISHTI](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2159295&lang=2&reg=3), 2025).

## Five strongest objections a judge may raise

1. **“GMW already does this.”** It already maps extent and monthly loss alerts globally; any novelty claim must be about validated workflow value, which has not yet been proven ([GMW 4.1](https://www.mangrovealliance.org/news/global-mangrove-watch-4-launch)).
2. **“Your model does not detect local loss.”** Correct: it predicts one AOI-wide monthly NDVI mean. Local loss maps and event precision are future work ([dataset validation](../../reports/dataset_validation.json)).
3. **“NDVI changes may be tide/season/cyclone.”** Correct: the current pipeline needs tide-aware validation and incident adjudication; GEEMMM shows this is a known, addressable issue ([Yancho et al., 2020](https://www.mdpi.com/2072-4292/12/22/3758)).
4. **“Who wants or pays for it?”** No customer interviews, signed pilot, tender or price are documented. The B2G case is a hypothesis ([user validation](user_validation.md), [market analysis](market_analysis.md)).
5. **“Are the agents autonomous and real-time?”** They are scheduled deterministic stages operating on completed monthly imagery, with a 15-second UI refresh. They are not independent LLM agents or instant satellite sensing ([scheduler](../../scripts/run_scheduler.py), [dashboard](../../frontend/src/pages/Dashboard.jsx)).

## Answers to 15 difficult questions

1. **What exactly is novel?** The current integration and audit workflow for Sundarbans condition review is a locally focused combination; scientific or commercial novelty is unproven. GMW, GEEMMM and Blue Carbon Explorer already cover substantial related capability ([competitor analysis](competitor_analysis.md)).
2. **How do you know data are real?** The recorded fresh Oct 2026 job used `earth_engine`, source collection IDs, `nex-sync`, acquisition timestamp and a fetched tile; its run evidence is [here](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md). Re-run during the demo and inspect the timestamp; the prior record is not proof the service is online today.
3. **Is it truly real-time?** No. It refreshes the screen frequently but analyses completed monthly windows; source acquisition/processing and cloud availability create delay ([scheduler](../../scripts/run_scheduler.py), [dashboard](../../frontend/src/pages/Dashboard.jsx)).
4. **What does the Random Forest output?** Expected AOI mean NDVI for a month from prior-month indices and season; it does not output mangrove area, loss probability or a pixel mask ([training](../../scripts/train_model.py)).
5. **What is the model accuracy?** A single 12-month temporal holdout has MAE 0.0306 NDVI, RMSE 0.0413 and R² 0.488. There is no validated loss-detection accuracy, precision or recall ([evaluation](../../reports/model_evaluation.json)).
6. **How many training samples?** 66 train and 12 test rows after lag construction, from 94 monthly records, 90 valid. These are monthly **AOI observations**, not millions of independent satellite pixels ([dataset validation](../../reports/dataset_validation.json), [evaluation](../../reports/model_evaluation.json)).
7. **Why use CO?** It is coarse atmospheric-column context; the Google [S5P CO catalog](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_CO) lists ~1.1 km grid pixels. It cannot establish local pollution source or cause of mangrove stress. We should ablate it if it adds no validated value.
8. **Could the static mask bias results?** Yes. The 2023 CGMD extent mask conditions what pixels are averaged, so later gains/losses can be omitted or misrepresented. Update/reference-check it and distinguish “condition of 2023-masked pixels” from current extent ([provider](../../src/providers/earth_engine.py)).
9. **Can you compare with GMW?** Not yet on matched incidents. GMW targets loss/extent and Lens currently targets condition deviations, so a fair study needs common geography, dates, independent reference and alert-budget thresholds ([GMW 4.1](https://www.mangrovealliance.org/news/global-mangrove-watch-4-launch)).
10. **Do the AI agents use an LLM?** No. “Agents” are named deterministic pipeline steps coordinated by code; that is an honest orchestration description ([orchestrator](../../src/agents/orchestrator.py)).
11. **Are automatic alerts sent to officials?** Dashboard review records are generated. External notification adapters exist but are disabled/unconfigured and the model is not approved for production dispatch. No delivered official email is evidenced ([notifications](../../src/services/notifications.py), [manifest](../../models/ndvi_forecast_rf.manifest.json)).
12. **What have users said?** No external operator trial or quote is documented. Planned testing is detailed in [user validation](user_validation.md).
13. **What is the TRL?** Overall TRL 4 conservatively: integrated prototype and real EO run, without validated conservation decisions in a relevant user setting. NASA’s [TRL definitions](https://esto.nasa.gov/trl/) distinguish laboratory from relevant-environment validation.
14. **What is the market size?** We can identify up to 13 Indian MISHTI activity jurisdictions as opportunity geography and the Bangladesh segment, but no defensible ₹ TAM without agency count, verified procurement price and demand ([MoEFCC/PIB](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2159295&lang=2&reg=3), 2025; [market analysis](market_analysis.md)).
15. **What would prove real impact?** Independently verified incidents leading to timely agency action, and later measured ecological results using a defensible counterfactual. Alerts, NDVI and PDF counts alone do not prove avoided loss ([SDG mapping](sdg_mapping.md)).

## Two-minute pitch (approximately 250 words)

“The Sundarbans is a shared India–Bangladesh mangrove ecosystem. Monitoring it matters, and strong tools already exist. India publishes official mangrove inventories; Global Mangrove Watch gives global extent history and monthly loss alerts. We are not claiming to replace them.

Mangrove Lens asks a narrower question: when satellite measurements of the Sundarbans look unusual, can a local analyst review the signal quickly, see its provenance and uncertainty, and prepare an evidence-based briefing?

We have built a working prototype. It queries Sentinel-2, Sentinel-1 and Sentinel-5P through Google Earth Engine, checks data quality, stores monthly observations, forecasts expected NDVI from earlier months and generates a reviewable alert and report. A recorded fresh run for October 2026 retrieved real Earth Engine observations and map tiles. Our Random Forest was tested on the last 12 months; its mean absolute error was 0.0306 NDVI, compared with 0.0484 for a persistence baseline.

That result has a clear limit. It is one area-level NDVI forecast, not a validated map of mangrove loss. Tides, clouds, seasons and a static extent mask can affect the signal. The system’s agents are deterministic pipeline stages, and external notifications remain gated until validation and authorized recipients are in place.

Our next step is an independent comparison with Global Mangrove Watch and field or high-resolution reference cases, followed by observed trials with forest and restoration analysts. We will measure false alerts, time to a defensible review and whether the report changes decisions. If those tests succeed, Mangrove Lens can become a useful local evidence layer within existing conservation workflows.”

## Final positioning recommendation

**Modify the current positioning.** “Autonomous real-time AI system that detects mangrove degradation” overstates latency, spatial detail and validation. Use: **“A working, Earth Engine-powered Sundarbans condition-monitoring prototype that produces auditable monthly review candidates; independent ecological and user validation is the next milestone.”** That is credible today and leaves a clear route to a stronger product claim.
    