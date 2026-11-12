# Competitor and alternative analysis

These are alternatives users could actually use today. No row implies a product has failed a feature unless supported by published information. `Unknown` means no public proof was found, not that the feature is absent. Additional relevant alternatives are [GEEMMM](https://www.mdpi.com/2072-4292/12/22/3758) (Yancho et al., 2020; GEE classification and tidal calibration) and the [Bangladesh Forest Information System](https://bfis.bforest.gov.bd/bfis/) (Bangladesh Forest Department; existing national forest-management information system).

| Criterion | Mangrove Lens now | Global Mangrove Watch | FSI/NCSCM government products | Blue Carbon Explorer |
|---|---|---|---|---|
| Coverage | Sundarbans operational envelope; one AOI-level metric | Global annual extent and monthly alerts | India national inventory; India community atlas | Published Earth Engine restoration tool |
| Signal | Monthly NDVI/NDMI/SAR/CO; expected-vs-observed AOI NDVI | Mangrove extent/change/loss alerts | Extent and zonation | NDVI change, canopy/restoration prioritization |
| Evidence trail | Code-run provenance, quality gate, model version, report **implemented** | Public map and dataset metadata; per-alert audit comparison **not evaluated** | Official published methods/reports | Published methods and app; per-alert audit comparison **not evaluated** |
| Ground-verified performance | **None** for loss/alerts | Global extent F1 **0.9276**, not local alert accuracy | Official inventory methods; not same target | Study/application; not same target |
| Price / speed / ease | **No measured user cost or task timing** | Public access; operational pricing irrelevant to end users | Public reports | Public research app; task timing unknown |

Sources: repo [live evidence](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md), [model evaluation](../../reports/model_evaluation.json); Global Mangrove Alliance, *GMW 4.1 Launch*, **2026**, [source](https://www.mangrovealliance.org/news/global-mangrove-watch-4-launch); Bunting et al., *GMW v4.1.12 extent dataset*, **2026**, [record](https://zenodo.org/records/21346457); FSI, *ISFR 2023*, [source](https://fsi.nic.in/uploads/isfr2023/isfr_book_eng-vol-1_2023.pdf); NCSCM, *Zonation Atlas*, **2024**, [source](https://ncscm.res.in/mza-2/); McNulty et al., *Blue Carbon Explorer*, **2025**, [source](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1641301/full).

**Defensible distinction today:** an integrated, open-to-inspection *local review workflow* that combines multiple Earth Engine sources with a holdout-evaluated NDVI baseline and human-review gates. **Unfair advantage:** none yet. Data, APIs and algorithms are replicable. A durable advantage would require independently labelled incidents, institutional workflow integration, measured operator time savings and trusted local partnerships. A direct benchmark against GMW is a required next step.
