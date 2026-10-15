# Intelligence Framework — build record

**Status:** Done. Phases 0–7 are complete, calibrated, and promoted to `mart_intelligence` by `foundations/loaders/`.

This folder is the working record of how the framework was built: phase notebooks, outputs and working notes. It isn't where the method is documented. Start from [docs/methodology/intelligence_framework/](../../docs/methodology/intelligence_framework/README.md), which holds the overview, the locked architecture, the metric map and selections, and the zone methodology.

| Folder | What it holds |
|---|---|
| `phase_1_variable_selection/` | Variance, correlation and PCA passes per frame |
| `phase_2_character_calibration/` – `phase_5_cross_frame_integration/` | Frame calibration and the combined model |
| `phase_6_trajectory/` | Momentum and divergence over time |
| `phase_7_zone_methodology/` | Tract and ZCTA zone model, EDA, cluster review, review app |
| `phase_8_catalog/` | Catalog finalization (empty) |
| `docs/` | Working notes: calibration notes, clustering notes, audits, plans and memos |
| `R/`, `outputs/` | Shared helpers and phase outputs (outputs are gitignored) |

New Intelligence work doesn't start here. Method changes need a decision record (see `docs/decisions/`); consumer work belongs in the Metro Deep Dive program.
