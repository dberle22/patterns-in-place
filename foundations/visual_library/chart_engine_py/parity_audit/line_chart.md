# line_chart

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/line_chart.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/line.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/line.py`
- R spec: `foundations/visual_library/charts/line/line_spec.md`
- R question coverage: `foundations/visual_library/charts/line/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_line.R`
- R render: `foundations/visual_library/shared/render/render_line.R`

## Verdict
- Overall parity status: `blocking`
- Primary missing layer: `prep`
- Recommended fix order: prep parity first, render parity second, test coverage third

## Spec Parity
- Match: Python has a generated spec and a default benchmark marker.
- Gaps: the generated spec does not preserve the R line variants or the documented county small-multiples extension.

## Prep Parity
- Match: Python renames columns, keeps contract fields, and sorts by period.
- Gaps: R prep handles filtering, complete-period expansion, indexed and rolling variants, highlight flags, and benchmark fields; Python prep does not.

## Render Parity
- Match: Python renders multi-series lines with optional vertical annotations.
- Gaps: R render supports facets, benchmark series, highlight-aware color modes, indexed labeling, and richer subtitle/caption defaults that Python lacks.

## Theme / Defaults Parity
- Match: Python uses shared palette keys and basic point/line defaults.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: export path exists.
- Gaps: Python exports do not visibly render the caption/source/vintage treatment that R includes.

## Question Coverage Parity
- Supported: simple single-series trend, simple multi-series trend
- Partial: peer comparison trend
- Missing: indexed trend, rolling trend, planned county small-multiples extension

## Gap Register
- [blocking] [prep] Python line prep is materially narrower than the R prep contract
  Evidence: `prep/line.py` only renames, filters columns, and sorts; `shared/prep/prep_line.R` supports `variant`, `base_period`, `rolling_k`, `complete_periods`, benchmark data, and highlight handling.
  Why it matters: Python cannot tell the same indexed, rolling, or benchmark stories that the R line chart is designed for.
  Fix location: `chart_engine_py/chart_engine/prep/line.py`
- [major] [render] Python line render misses benchmark and facet semantics
  Evidence: `render/line.py` has no facet path and no benchmark-line branch, while `shared/render/render_line.R` supports `facet_by`, `add_benchmark`, variant-aware y labeling, and richer subtitle/caption generation.
  Why it matters: canonical R line questions are only partially portable to Python.
  Fix location: `chart_engine_py/chart_engine/render/line.py`
- [major] [tests] Planned line regression coverage is still absent
  Evidence: `PLAN.md` Phase 4 leaves `line_chart golden test` unchecked, and `tests/test_regression.py` has no `line_chart` case.
  Why it matters: the thinnest high-volume parity candidate is also missing the strongest regression guardrail.
  Fix location: `chart_engine_py/tests/test_regression.py`

## Recommended Follow-Up
- First: port the R prep surface for indexed, rolling, and complete-period logic.
- Second: port benchmark and facet behavior in the renderer.
- Later: add the missing golden regression and resolve the shared export caption gap.

## Progress Update 2026-07-12
- Closed in code:
  - the Python prep layer now handles indexed and rolling variants, complete-period expansion, duplicate guards, benchmark values, and highlight-aware series handling
  - the Python renderer now supports benchmark lines, highlight-aware series coloring, visible caption text, and optional faceting
  - Phase 4 regression coverage now includes a committed `line_chart` golden
- Residual parity risk:
  - the generated Python spec still does not fully encode every narrative nuance from the R docs, including the planned county small-multiples extension
  - manual CE parity runs are still needed before this chart should be treated as fully validated in publisher workflows
