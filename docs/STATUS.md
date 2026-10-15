# Status

**Updated:** 2026-09-29

One row per area. Update this when an area changes status or finishes a milestone. Agents: read this before starting work in an area. Strategy and sequencing are in [ROADMAP.md](ROADMAP.md).

| Area | Status | Where it stands | Next | Plan |
|---|---|---|---|---|
| `metro-deep-dive-program/` | Active | First published work is the [New York series](decisions/2026-09_ny-series-first.md), `issues/new_york/`, still being defined. Richmond is paused; its work proved the engines and analyses. Position (Profile, Peers, Trajectory) is implemented, with interactive review pending. Explanation: Q6, Regional Role and Catchment are complete; Q2, Q3 and Q4 are mid-build; Q1 has finished its audit. Thematic A1–A10 are scaffolds. | Define the NY series and set up `issues/new_york/`; review the Position notebooks; Q2 national-pattern review; Q3 Epic 5 review; Q1 mart design | [build_sequence.md](../metro-deep-dive-program/docs/build_sequence.md), per-analysis READMEs |
| `public-cbsa-panel/` | Active | **v2026.1 published on Zenodo, 2026-09-28** ([DOI 10.5281/zenodo.23020706](https://doi.org/10.5281/zenodo.23020706)). | Epic 5 release hygiene (GitHub tag, citation checks); Epic 6 first analysis and outreach; Epic 7 v2 candidates | [BUILD_PLAN.md](../public-cbsa-panel/BUILD_PLAN.md) |
| `foundations/` | Active | 22 Gold tables, governed geography marts, Intelligence Framework promoted. Work is pulled by consumers. | Promotions from the MDD program; panel v2 sources when Epic 7 pulls them | [foundations/ROADMAP.md](../foundations/ROADMAP.md) |
| `exploration/` | Active | Intelligence Framework phases 0–7 complete and promoted to `mart_intelligence`; national EDA; TX school districts. | Framework method now lives in [methodology/intelligence_framework/](methodology/intelligence_framework/README.md); the folder is its build record | [README.md](../exploration/README.md) |
| `metro-deep-dive/` | Legacy | Retiring into the program. Still live: the research tool, and `metro-area-explorer/` code the program depends on. | Nothing now. Reviewing and archiving it is a separate future project; its README lists what's still depended on | [README.md](../metro-deep-dive/README.md) |
| `area-explorer/` | Paused since 2026-07 | Internal CBSA app (Phase 1) fully built but never verified end to end. Public app, county explorer and zone layer not started. | On return: one end-to-end verification run of the internal app | [AREA_EXPLORER_ROADMAP.md](../area-explorer/AREA_EXPLORER_ROADMAP.md) |
| `publisher/` | Paused since 2026-07 | Chart a day ran 28 questions (q001–q028). Chatbot works locally, not deployed. Housing and vacancy content drafted, not published. | On return: restart chart a day from [PUBLISHING.md](strategy/PUBLISHING.md) | [PUBLISHER_ROADMAP.md](../publisher/PUBLISHER_ROADMAP.md) |
| `stoop/` | Paused since 2026-06 | Stoop Explore v1 is live (NYC). Stoop Search is scaffolded only. | On return: v2 planning | [current_backlog.md](../stoop/docs/planning/current_backlog.md) |

## Open status questions

- `metro-deep-dive-program/docs/build_sequence.md` "Where we are" lags the per-analysis READMEs. Refresh it the next time the program is planned.
