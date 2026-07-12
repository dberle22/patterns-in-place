# boxplot

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/boxplot.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/boxplot.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/boxplot.py`
- R spec: `foundations/visual_library/charts/boxplot/boxplot_spec.md`
- R question coverage: `foundations/visual_library/charts/boxplot/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_boxplot.R`
- R render: `foundations/visual_library/shared/render/render_boxplot.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `prep`
- Recommended fix order: prep parity first, render parity second, export parity third

## Spec Parity
- Match: Python keeps the main boxplot field contract, including `group`, `highlight_flag`, `label_flag`, and `weight_value`.
- Gaps: the generated Python spec drops the R narrative around benchmark and weighted distribution usage.

## Prep Parity
- Match: Python coerces values, keeps group labels, and preserves highlight/label flags.
- Gaps: R prep handles benchmark values, weights, and more opinionated distribution shaping; Python prep does not use `weight_value` or benchmark semantics.

## Render Parity
- Match: Python produces a readable boxplot with highlighted points.
- Gaps: R render supports richer benchmark/distribution semantics and more configured labeling than the Python `mark_boxplot` wrapper.

## Theme / Defaults Parity
- Match: neutral palette use is aligned.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: export path exists.
- Gaps: caption/source/vintage remain hidden in `usermeta`.

## Question Coverage Parity
- Supported: unweighted single-group distribution with highlighted outliers
- Partial: grouped distribution comparisons
- Missing: weighted and benchmark-aware distribution views

## Gap Register
- [major] [prep] Python boxplot prep ignores weighted and benchmark-aware behavior
  Evidence: `prep/boxplot.py` creates `box_group` and highlight flags only; `shared/prep/prep_boxplot.R` validates and uses `benchmark_value` and `weight_value`.
  Why it matters: R question patterns that depend on weighted tails or benchmark comparisons are not truly portable.
  Fix location: `chart_engine_py/chart_engine/prep/boxplot.py`
- [major] [render] Python boxplot render is a thin wrapper over Altair defaults
  Evidence: `render/boxplot.py` uses `mark_boxplot` plus a highlight point layer; `shared/render/render_boxplot.R` carries the richer caption, benchmark, and comparison treatment expected by the R library.
  Why it matters: the same distribution question will be analytically thinner in Python.
  Fix location: `chart_engine_py/chart_engine/render/boxplot.py`

## Recommended Follow-Up
- First: port weight and benchmark handling in prep.
- Second: port the richer comparison semantics in render.
- Later: close the shared Altair caption/export gap.

## Progress Update 2026-07-12
- Closed in code:
  - `prep/boxplot.py` now supports request-driven filtering, benchmark propagation, trimmed display handling, and group median/count metadata for ordering
  - `render/boxplot.py` now supports benchmark overlays plus richer highlight/label behavior instead of only a bare `mark_boxplot` wrapper
  - regression and orchestrator coverage now exercise ordered groups and benchmark overlays
- Still open:
  - `weight_value` is preserved but not yet used for weighted distribution logic, so the weighted R question path should still be treated as partial parity
