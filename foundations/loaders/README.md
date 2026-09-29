# foundations/loaders

**Status:** Active
**Updated:** 2026-09-29

Scripts that publish the Intelligence Framework's outputs into the `mart_intelligence` schema: frame scores (Character, Livability, Opportunity, Cross-Frame) and tract and ZCTA zone assignments. The outputs come from the phase work in `exploration/intelligence_framework/`; the method is documented in `docs/methodology/intelligence_framework/`.

## How to run it

From the repo root:

```bash
Rscript foundations/loaders/build_intelligence_framework_datamart.R
```

It runs each loader in order: character, livability, opportunity and cross-frame scores, then zone assignments, then ZCTA zone scores. `_shared_intelligence_loader.R` holds the helpers they share.

Trajectory tables in `mart_intelligence` are written by the Metro Deep Dive time-series engine, not by these loaders.
