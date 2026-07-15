# scatter

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/scatter.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/scatter.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/scatter.py`
- R spec: `foundations/visual_library/charts/scatter/scatter_spec.md`
- R question coverage: `foundations/visual_library/charts/scatter/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_scatter.R`
- R render: `foundations/visual_library/shared/render/render_scatter.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `render`
- Recommended fix order: render parity first, prep guards second, export parity third

## Spec Parity
- Match: Python preserves the core scatter field contract, including `group`, `size_value`, and `label_flag`.
- Gaps: the generated Python spec does not preserve the R decision notes around highlight modes, reference lines, and density-vs-scatter scope.

## Prep Parity
- Match: numeric coercion and dropping missing `x`/`y` rows align with the R prep baseline.
- Gaps: R prep can require a single `geo_level`; Python prep does not enforce that guardrail.

## Render Parity
- Match: grouping, bubble sizing, trend line, labels, and simple guide annotations exist in Python.
- Gaps: R render has explicit `highlight_mode`, `add_reference_line`, and `add_quadrants` controls; Python only partially covers those semantics.

## Theme / Defaults Parity
- Match: shared palette keys and point alpha are broadly aligned.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: export path exists.
- Gaps: caption/source/vintage remain hidden in `usermeta`.

## Question Coverage Parity
- Supported: CBSA tradeoff scan, county valuation outlier scan, within-CBSA labeled outlier scan
- Partial: reference-line and quadrant-style analytical scans
- Missing: none from the current question bank, but some R render controls are unported

## Gap Register
- [major] [render] Python scatter omits part of the R narrative-control surface
  Evidence: `render/scatter.py` supports trend lines and h/v annotations, but `shared/render/render_scatter.R` also includes explicit reference-line, quadrant, and highlight-mode switches.
  Why it matters: Python can render the core shape, but not always with the same analytical framing as R.
  Fix location: `chart_engine_py/chart_engine/render/scatter.py`
- [minor] [prep] Python scatter prep does not enforce the single-geo-level guardrail
  Evidence: `shared/prep/prep_scatter.R` can stop on mixed `geo_level` input; `prep/scatter.py` does not.
  Why it matters: mixed-grain scatter inputs are easier to pass through silently in Python.
  Fix location: `chart_engine_py/chart_engine/prep/scatter.py`

## Recommended Follow-Up
- First: port the missing reference-line / quadrant / highlight-mode semantics.
- Second: add the `geo_level` guardrail from the R prep path.
- Later: close the shared Altair caption/export gap.

## Progress Update 2026-07-12
- Closed in code:
  - the Python prep layer now rejects mixed `geo_level` inputs like the R reference path
  - the Python renderer now supports opt-in reference-line, quadrant, and color-highlight controls through `field_values`
  - targeted orchestrator coverage now asserts those controls and the mixed-grain guardrail
- Residual parity risk:
  - the Python scatter path still exposes a smaller narrative-control surface than the full R implementation
  - manual parity review is still needed for quadrant/reference-line presentation quality on real publisher questions
