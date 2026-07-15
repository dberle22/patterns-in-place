# Parity Fix Execution Order

## 1. Shared Cross-Chart Fixes First
- Regenerate Python specs from the R source docs with more than the current front-matter-only contract. The present generator drops variants, QA rules, preprocessing notes, and example question patterns across the library.
- Make Altair exports carry visible captions, source, vintage, and note text instead of only storing caption text in `usermeta`.
- Align the packaged Python theme with the R standards font default or document the font fallback as an explicit intentional deviation.
- Upgrade the Python regression harness where the audit found thin coverage: add the missing `line_chart` golden and move geo charts beyond "returns a Figure" structural checks.

## 2. High-Volume Chart Families Second
- `bar_chart` and `line_chart`
  These are the highest-reuse analytical charts in the Phase 5 and CE backlog, and `line_chart` is the clearest blocker.
- `scatter`, `slopegraph`, `boxplot`, `bump_chart`
  These are the next-highest leverage charts for comparison, ranking-change, and distribution questions.
- `heatmap_table`, `waterfall`, `strength_strip`, `correlation_heatmap`, `age_pyramid`
  These are still important, but they follow naturally once the shared spec/caption/test problems and the core analytical chart family are stable.

## 3. Map And Single-Purpose Charts Third
- `choropleth` and `highlight_context_map`
  Fix the shared map variant, benchmark, and facet gaps before working the tail map types.
- `hexbin`, `proportional_symbol_map`, and `bivariate_choropleth`
  These charts have more specialized semantics and currently rely on structural tests rather than strong parity snapshots.

## 4. Validation Sequence Through CE Manual Runs Last
- Validate shared fixes first on the highest-volume CE backlog items: `q001` to `q015`.
- Validate the analytical tail next: `q016` to `q023`.
- Validate the map family last: `q024` to `q028`.
- Treat the CE/manual run phase as validation of audited fixes, not as the main gap-discovery mechanism. That matches the gate described in [PLAN.md](/foundations/visual_library/chart_engine_py/PLAN.md) Phase 5 and [PUBLISHER_ROADMAP.md](/publisher/PUBLISHER_ROADMAP.md).

## Why This Order
- Shared spec/export/test fixes unlock multiple charts at once.
- `bar_chart` and `line_chart` sit on the densest backlog coverage and are the first charts consuming apps are most likely to hit.
- Analytical charts come before maps because their shared surfaces are easier to validate and more central to the CE handoff.
- Maps last keeps specialized composition and runtime work from blocking the simpler, higher-leverage fixes.

## Progress Update 2026-07-12
- Completed from tranche 1:
  - shared spec generation now preserves substantive body content
  - shared font default now matches the R standard
  - `line_chart` prep/render/test blocker tranche is closed in code
- Completed from tranche 2:
  - visible Altair caption handling now covers the regression-backed analytical charts touched in this run
  - `age_pyramid` benchmark/facet blocker tranche is closed in code
- Completed from tranche 3:
  - `bar_chart` now covers diverging and stacked composition variants in addition to the ranked path
  - `scatter` now includes the R-style single-geo-level guardrail plus opt-in reference-line, quadrant, and color-highlight controls
- Completed from the infrastructure pivot:
  - shared prep helpers now centralize field selection, boolean coercion, numeric coercion, and single-geo-level guards
  - shared Altair render helpers now centralize repeated variant resolution plus common benchmark and reference-line layers
- Completed from the ranking/comparison family:
  - `slopegraph` now supports request-driven prep config, explicit periods, indexed/rank variants, curated entity selection, and richer endpoint subtitle/label behavior
  - `bump_chart` and `strength_strip` now share richer comparison-family selection/benchmark metadata and updated regression coverage
- Completed from the matrix/distribution family:
  - `boxplot` now supports request-driven filtering, group median ordering, benchmark overlays, richer highlight labeling, and updated regression coverage
  - `heatmap_table` now supports runtime row/column ordering, polarity-aware percentile fills, highlight outlines, and richer label/legend behavior
  - `waterfall` now supports grouped cumulative prep, terminal total rows, benchmark comparison panels, connector lines, and updated regression coverage
  - `correlation_heatmap` now supports group-split prep, comparison panel composition, method/missingness metadata, weak-correlation masking, and updated regression coverage
- Completed from the map family:
  - `choropleth` now supports request-driven continuous, binned, and diverging variants plus faceted map panels
  - `highlight_context_map` now supports focus-only and analytical fill variants plus explicit highlight/neighbor role semantics
  - `proportional_symbol_map` now supports request-driven Top-N filtering, label strategies, and explicit size/color legend behavior
  - `bivariate_choropleth` now supports grouped bin metadata, faceted comparison panels, and a more flexible bivariate key surface
- Completed from the specialized tail:
  - `hexbin` now supports request-driven filtering, non-negative weight validation, faceted comparison panels, weighted density labeling, and reference-line overlays
- Recommended next execution slice:
  - Chart a Day QA and refinement loop: `q001` to `q015` first, then `q016` to `q028`
