# Mangrove Lens: evidence-led project review

**As of 12 November 2026.** Scope: full India–Bangladesh Sundarbans operational envelope. This document distinguishes repository evidence from external evidence and from proposals. The full paper is [`Mangrove_Guardian_Research_Paper_final.pdf`](../../Mangrove_Guardian_Research_Paper_final.pdf); its architecture is a proposal, while code and recorded runs show what exists now.

**Snapshot caveat:** the inspected checkout is branch `staging`; the model manifest, model-evaluation JSON, SQLite database and `.env.example` already had uncommitted changes before this research work. Their values describe the inspected working tree, not necessarily a merged release or active container. The review did not alter those four files.

## Executive judgment

Mangrove Lens is a functioning **monthly, area-level satellite condition and audit prototype**, not a validated loss-detection or conservation-impact system. Its strongest defensible use is to turn Earth Engine observations into reproducible Sundarbans condition summaries, forecast deviations, reviewable alerts and evidence reports. The main scientific gap is ground-truth validation of whether NDVI anomalies correspond to harmful mangrove change. The main product gap is a named institutional user who has tested and adopted the workflow.

The problem is material: India's 2023 mangrove cover was **4,991.68 km²**, of which **2,119.16 km²** was in West Bengal (Forest Survey of India, *India State of Forest Report 2023*, vol. 1, 2023, [official report](https://fsi.nic.in/uploads/isfr2023/isfr_book_eng-vol-1_2023.pdf)). The Sundarbans are shared by India and Bangladesh (UNESCO, *The Sundarbans*, 19 July 2024, [article](https://www.unesco.org/en/articles/sundarbans?hub=70318)). These figures establish ecosystem importance, **not** detection performance or a customer market.

## What the repository demonstrates

The [live-system evidence](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md) records an authenticated Earth Engine run in `nex-sync`, a 94-month observational store (90 valid, four low-coverage), a fresh October 2026 run, Earth Engine map tiles and a March 2026 critical **screening** alert. The [model evaluation](../../reports/model_evaluation.json) records a single 12-month temporal holdout: 66 train rows, 12 test rows, MAE 0.0306 NDVI, RMSE 0.0413, R² 0.488, compared with persistence MAE 0.0484. This is **forecast error on monthly AOI NDVI**, not mangrove-classification accuracy or field-verified alert precision. Current [manifest](../../models/ndvi_forecast_rf.manifest.json) has `production_approved: false`.

Processing is monthly over one AOI; the grid endpoint does not create cell-level forecasts. A running [scheduler](../../scripts/run_scheduler.py) can reconcile and retrain, but continuous real-time sensing is physically constrained by satellite acquisition, clouds, OFFL processing and monthly aggregation. External notification code exists, while [configuration](../../.env.example) disables external dispatch and lacks SMTP credentials/recipients. The dashboard is a working prototype; no documented operator user test, field truth, paid pilot or ecological outcome was found.

## Strategic finding

Avoid claiming to be the first mangrove monitor or first alert system. [Global Mangrove Watch 4.1](https://www.mangrovealliance.org/news/global-mangrove-watch-4-launch) already provides annual extent history and monthly loss alerts (Global Mangrove Alliance, 27 July 2026). [Blue Carbon Explorer](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1641301/full) already uses Earth Engine and NDVI for mangrove condition and restoration decisions (McNulty et al., 5 September 2025). [NCSCM](https://ncscm.res.in/mza-2/) and [FSI](https://fsi.nic.in/uploads/isfr2023/isfr_book_eng-vol-1_2023.pdf) already map Indian mangroves. The potentially useful niche is **Sundarbans-focused, reviewable condition anomalies with local operational evidence**, if independent validation proves added value over these tools. This is a hypothesis, not a moat.

## Evidence standard for the pitch

Show the actual October 2026 provenance, one NDVI/forecast/decision record, the 12-month holdout and the explicit “not externally approved” gate. Label maps “satellite-derived condition” and alerts “review candidates.” Do not label them confirmed degradation. See the other documents in this folder for source-level research, market logic, TRL, risks and slide copy.
