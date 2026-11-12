# Differentiation: claim only what can be defended

## Positioning statement

**Mangrove Lens is a Sundarbans-focused satellite condition review workspace**: it turns completed monthly Earth Engine observations into a quality-tagged NDVI forecast deviation, contextual signals, an auditable decision record and a report for expert review. The current result is a prototype of that workflow, not a verified conservation outcome. Evidence: [live run](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md), [orchestrator](../../src/agents/orchestrator.py), [reporting code](../../src/services/reporting.py).

| Claim | Verdict | Why |
|---|---|---|
| “First real-time mangrove alert system” | Reject | GMW 4.1 publishes monthly loss alerts; see Global Mangrove Alliance, *GMW 4.1 Launch*, **27 Jul 2026**, [source](https://www.mangrovealliance.org/news/global-mangrove-watch-4-launch). Lens itself uses completed monthly windows. |
| “First Earth Engine/NDVI mangrove tool” | Reject | McNulty et al., *Blue Carbon Explorer*, **5 Sep 2025**, [source](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1641301/full); Yancho et al., *GEEMMM*, **16 Nov 2020**, [source](https://www.mdpi.com/2072-4292/12/22/3758); The Mangrove Lab's [CGMD canopy-cover product](https://developers.google.com/earth-engine/datasets/catalog/projects_mangrovedatahub2_assets_CGMD-AFCC30). |
| “Detects Sundarbans mangrove loss accurately” | Reject | No independent loss labels or loss-classification confusion matrix; current error is AOI NDVI regression MAE, [evaluation](../../reports/model_evaluation.json). |
| “Combines multi-sensor condition evidence with reviewable actions” | Supported as implementation; usefulness unvalidated | [Earth Engine provider](../../src/providers/earth_engine.py), [decision rules](../../src/services/decision.py), [live evidence](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md). |
| “Saves operator time / has unique data / has partnerships” | Not established | No user trial, exclusive dataset or signed partnership in repository. |

## Testable differentiation hypothesis

For a Sundarbans conservation analyst, condition deviations plus a provenance-rich report may shorten first review of potential stress compared with manually combining GMW and separate Sentinel layers. Test on 20–30 known and non-event months, with blinded incident adjudication, time-to-review, precision at a fixed alert burden and reviewer confidence. If it does not beat the existing workflow, integrate GMW as a baseline/overlay and focus on reporting interoperability instead. This is a proposed experiment, not an achieved result.
