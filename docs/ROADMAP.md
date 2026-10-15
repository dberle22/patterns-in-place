# Roadmap

**Status:** Active
**Updated:** 2026-09-29
**Supersedes:** `ROADMAP.md` and `PLATFORM_ROADMAP.md` (archived in [archive/2026-09_platform_roadmaps/](archive/2026-09_platform_roadmaps/))

Strategy and sequencing across areas. Two products are active: the **Metro Deep Dive**, the destination, and the **public CBSA panel**, the first thing shipped. Foundations supports both. Everything else is paused and can resume on the same shared core. Current state per area is in [STATUS.md](STATUS.md); task lists live in each area's own plan.

---

## Strategic frame

- **Foundations is infrastructure.** It's complete enough for current work. New sources and promotions happen when a consumer pulls them ([foundations/ROADMAP.md](../foundations/ROADMAP.md)).
- **Metro Deep Dive is the destination product**: long-form, comparable market work, starting with a [series on New York State](decisions/2026-09_ny-series-first.md). The program works backward from the issue to analyses to engines, and the Intelligence Framework routes which analyses a market gets ([program](../metro-deep-dive-program/metro_deep_dive_program.md)).
- **The public panel makes the platform's harmonization work visible and citable.** It's the first public artifact, and future releases grow from Gold in narrow, validated steps.
- **Exploration is where discovery starts.** Finished work gets promoted out rather than living there.
- **Area Explorer, Publisher and Stoop are paused**, not abandoned. Each can resume without rebuilding its data. Publishing strategy for when Publisher resumes is in [strategy/PUBLISHING.md](strategy/PUBLISHING.md).

The Intelligence Framework (phases 0–7) is finished: CBSA frames, Cross-Frame, trajectory and tract/ZCTA zones are promoted to `mart_intelligence`. What remains is consumer-side review, which happens through the Deep Dive's Position analyses.

## Now

1. **Metro Deep Dive: define the New York series and point the program at it.** Settle the series outline and set up `issues/new_york/`. Review Profile, Peers and Trajectory interactively for New York CBSAs. Continue the Explanation analyses already in flight (Q2, Q3, Q4, Q1).
2. **Public panel: finish v2026.1.** Release hygiene (Epic 5), then the first analysis and outreach (Epic 6). This runs alongside the Deep Dive, not after it: Deep Dive issues cite the panel as their public data source.

## Next

- **First New York pieces.** The state primer first, then regional and metro deep dives and rankings, with New York City as the finale.
- **Public panel v2 scope** (Epic 7), pulling the held-back sources through Foundations.
- **Promotions into Foundations** as engines reach two unchanged consumers, starting with POI.

## Later

- **Resume Publisher.** Chart a day as the heartbeat, fed by Deep Dive pieces; technical posts as their gates clear.
- **Resume Area Explorer.** Verify the internal app; a public deploy needs the semantic layer alignment pass and a cloud-hosted warehouse.
- **Resume Stoop.** v2 planning; Stoop Search waits on a product decision and listings data.
- **Richmond** (paused), and formalizing what proved reusable across the New York series.

## Resuming a paused area

| Area | First step on return | Blocked on | Plan |
|---|---|---|---|
| Publisher | Restart chart a day from the backlog | Nothing; it's a priority call | [PUBLISHER_ROADMAP.md](../publisher/PUBLISHER_ROADMAP.md), [PUBLISHING.md](strategy/PUBLISHING.md) |
| Chatbot (in Publisher) | Wire the theme, intelligence and question catalogs into the query pipeline | Cloud warehouse and an auth decision before any public deploy | [PUBLISHER_ROADMAP.md](../publisher/PUBLISHER_ROADMAP.md) |
| Area Explorer | End-to-end verification run of the internal CBSA app | Semantic layer alignment pass and cloud warehouse for the public app | [AREA_EXPLORER_ROADMAP.md](../area-explorer/AREA_EXPLORER_ROADMAP.md) |
| Stoop | v2 planning | A shared Points pipeline for new markets; a product decision for Search | [current_backlog.md](../stoop/docs/planning/current_backlog.md) |

## Open strategic questions

- **When does Publisher resume:** with the first New York piece, with panel outreach, or independently?
- **Chatbot access:** open to the public, or shared link only? (Open since July.)
