# Product strategy

## User and job hypothesis

Primary proposed user: West Bengal forest/coastal monitoring analyst who must triage a potential stress signal and prepare a defensible briefing. Secondary: Bangladesh counterpart, research lab and restoration-program assessor. These are **proposed segments**, not interview-verified customers. The India–Bangladesh Sundarbans is shared (UNESCO, *The Sundarbans*, **2024**, [source](https://www.unesco.org/en/articles/sundarbans?hub=70318)); MISHTI creates a plausible monitoring context (MoEFCC/PIB, **2025**, [source](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2159295&lang=2&reg=3)).

## Product boundary

The product should be a **decision-support and evidence workflow**, not an automatic enforcement system. The alert says “review this anomaly”; a domain expert or field team decides what happened. Keep GMW visible as an external benchmark rather than pretending it does not exist (Global Mangrove Alliance, *GMW 4.1 Launch*, **2026**, [source](https://www.mangrovealliance.org/news/global-mangrove-watch-4-launch)). For the current prototype, surface data age, coverage, model version, mask year and explanation on every report. Never show “realtime” without the completed-month date.

## Sequenced roadmap and decision gates

| Stage | Deliverable | Exit evidence |
|---|---|---|
| 0: Prototype (now) | Monthly area summary, forecast, dashboard, report, scheduler and audit | Repo run and test evidence; [live evidence](../../reports/LIVE_SYSTEM_EVIDENCE_2026-11-04.md) |
| 1: Scientific validity | Tide/orbit-aware composites; per-cell records; independent incident labels; comparison with GMW | Held-out spatial/temporal metrics and false-alarm burden, independently reviewed |
| 2: Workflow validity | 5–10 analyst interviews; 3–5 observed task trials; report revisions | Task completion, review time, comprehension and usefulness recorded; no quotes invented |
| 3: Controlled pilot | Named agency agreement, human review, delivery policy, uptime/freshness monitoring | Signed pilot, alert acceptance and field follow-up log |
| 4: Scale | Multi-agency governance, SLA, costed Earth Engine plan | Paid or funded deployment, independently measured outcomes |

**North-star metric proposal:** percentage of reviewed candidates that lead to a documented, timely field or desk decision, reported with denominator and false-alarm cost. Supporting metrics: validated event recall, precision, median alert delay from image availability, data coverage, report completion, operator minutes and recurring cost. No metric is claimed as achieved.
