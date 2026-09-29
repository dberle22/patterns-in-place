# Intelligence Framework methodology

The canonical explanation of the Intelligence Framework: what the three frames (Character, Livability, Opportunity) and the Cross-Frame, trajectory and zone models mean, how they were built, and which metrics feed them. The framework is complete: phases 0–7 are calibrated and promoted to `mart_intelligence`.

This folder owns the **strategy and methods**. The semantic layer owns the **machine-readable definitions** agents query; its catalogs link back here.

## Read in this order

| Doc | What it covers |
|---|---|
| [intelligence_framework_overview.md](intelligence_framework_overview.md) | Start here: why the framework exists, shared architecture, per-frame results, trajectory, zones, known limitations |
| [ARCHITECTURE.md](ARCHITECTURE.md) | The locked scoring and clustering architecture; changes need a decision record |
| [frame_questions.md](frame_questions.md) | The questions each frame answers, from high level to direct lookups |
| [metric_map.md](metric_map.md) | Phase 0: every candidate KPI mapped to Gold, with gaps |
| [metric_selections.md](metric_selections.md) | Phase 1: final KPI selections per frame and the reasons |
| [zone_methodology_notes.md](zone_methodology_notes.md) | The tract-level zone model and its seven zone types |
| [zone_methodology_literature_review.md](zone_methodology_literature_review.md) | The literature the zone labels are anchored to |

## Where everything else lives

| What | Where |
|---|---|
| Model definitions (KPIs, polarity, roles, weights) | `foundations/semantic_layer/intelligence_catalog.yml` |
| Topic groupings for products | `foundations/semantic_layer/theme_catalog.yml` |
| Published outputs | DuckDB schema `mart_intelligence`, built by `foundations/loaders/` |
| Downstream contract for the Metro Deep Dive | `metro-deep-dive-program/engines/intelligence_framework/` |
| Phase notebooks, outputs and working notes (the build record) | `exploration/intelligence_framework/` |
| Phase-by-phase roadmap (history) | `docs/archive/2026-09_intelligence_layer_roadmap/` |
| Decision | [Three Intelligence frames, one shared method](../../decisions/2026-06_three-intelligence-frames.md) |
