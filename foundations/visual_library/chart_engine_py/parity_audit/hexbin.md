# hexbin

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/hexbin.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/hexbin.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/hexbin.py`
- R spec: `foundations/visual_library/charts/hexbin/hexbin_spec.md`
- R question coverage: `foundations/visual_library/charts/hexbin/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_hexbin.R`
- R render: `foundations/visual_library/shared/render/render_hexbin.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `prep`
- Recommended fix order: weighting/facet parity first, render parity second, tests third

## Spec Parity
- Match: Python preserves the base x/y/weight/highlight contract.
- Gaps: the generated spec does not preserve the R weighting and faceted comparison guidance.

## Prep Parity
- Match: Python coerces coordinates and weights and drops rows missing `x` or `y`.
- Gaps: R prep validates non-negative weights and supports more opinionated density shaping; Python prep does not enforce the non-negative weight rule or facet-oriented setup.

## Render Parity
- Match: Python renders a hexbin with optional highlight points.
- Gaps: the R render/test surface includes reference medians, legends, and faceted region comparisons that Python does not expose.

## Theme / Defaults Parity
- Match: map-side title/subtitle/caption helpers exist.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: matplotlib export renders visible captions.
- Gaps: tests remain structural-only.

## Question Coverage Parity
- Supported: simple density tradeoff view
- Partial: highlighted local density view
- Missing: faceted region comparisons and weighted-population hexbin variants

## Gap Register
- [major] [prep] Python hexbin prep misses part of the R density contract
  Evidence: `shared/prep/prep_hexbin.R` explicitly validates non-negative weights and carries more density-shaping options; `prep/hexbin.py` only coerces and drops missing coordinates.
  Why it matters: weighted and faceted hexbin stories are not parity-safe.
  Fix location: `chart_engine_py/chart_engine/prep/hexbin.py`
- [major] [tests] Geo render coverage is structural-only
  Evidence: `tests/test_geo_render.py` checks only that `hexbin` returns a `Figure`.
  Why it matters: visually important density and legend regressions would go uncaught.
  Fix location: `chart_engine_py/tests/test_geo_render.py`

## Recommended Follow-Up
- First: port the weight-validation and faceted prep surface.
- Second: add stronger map snapshot or structural-visual regression coverage.
- Later: widen the generated spec artifact.

## Progress Update 2026-07-12
- Closed in code: prep now supports request-driven filtering, non-negative weight validation, runtime config capture, and quantile-trimming hooks.
- Closed in code: render now supports weighted density labeling, faceted comparison panels, optional reference lines, and highlighted-point overlays with labels.
- Closed in code: geo coverage now asserts weighted/faceted prep metadata and structural reference-line rendering rather than only "returns a Figure."
- Still open: matplotlib geo parity still lacks committed golden-image regression, so final visual QA belongs in the Chart a Day refinement loop.
