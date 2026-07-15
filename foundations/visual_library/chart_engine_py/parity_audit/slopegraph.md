# slopegraph

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/slopegraph.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/slopegraph.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/slopegraph.py`
- R spec: `foundations/visual_library/charts/slopegraph/slopegraph_spec.md`
- R question coverage: `foundations/visual_library/charts/slopegraph/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_slopegraph.R`
- R render: `foundations/visual_library/shared/render/render_slopegraph.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `prep`
- Recommended fix order: prep selection logic first, render labeling second, export parity third

## Spec Parity
- Match: Python keeps the core two-period slopegraph contract.
- Gaps: the generated Python spec does not preserve the R value/indexed/rank variant surface.

## Prep Parity
- Match: Python keeps metric values, optional rank, highlight flags, and two-endpoint selection.
- Gaps: R prep supports explicit period selection, top-N trimming, highlight inclusion, indexed and rank variants, endpoint completeness checks, and display ordering; Python drops most of that.

## Render Parity
- Match: Python renders comparison/highlight/benchmark lines with endpoint labels.
- Gaps: R render owns richer endpoint labels, delta labels, truncation, and rank/indexed y-axis behavior.

## Theme / Defaults Parity
- Match: overall palette intent is aligned.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: export path exists.
- Gaps: caption/source/vintage remain hidden in `usermeta`.

## Question Coverage Parity
- Supported: simple two-period value change
- Partial: highlighted or benchmarked two-period change
- Missing: indexed slopegraph and rank slopegraph variants

## Gap Register
- [major] [prep] Python slopegraph prep drops the R selection and variant logic
  Evidence: `prep/slopegraph.py` always takes earliest and latest periods and sets `plot_value = metric_value`; `shared/prep/prep_slopegraph.R` supports `variant`, `top_n`, `include_highlighted`, endpoint validation, and display ordering.
  Why it matters: Python cannot faithfully reproduce the R chart's canonical rank/indexed and curated-entity slopegraphs.
  Fix location: `chart_engine_py/chart_engine/prep/slopegraph.py`
- [major] [render] Python slopegraph labels are much simpler than the R reference
  Evidence: `render/slopegraph.py` labels only the last-period names; `shared/render/render_slopegraph.R` includes endpoint/delta label modes, label truncation, and variant-aware axes.
  Why it matters: the same chart can tell a materially weaker story in Python even when the data is equivalent.
  Fix location: `chart_engine_py/chart_engine/render/slopegraph.py`

## Recommended Follow-Up
- First: port the R prep surface for curated entity selection and variant handling.
- Second: port endpoint/delta label semantics.
- Later: close the shared Altair caption/export gap.

## Progress Update 2026-07-12
- Closed in code:
  - `prep/slopegraph.py` now accepts request-driven prep config through shared runtime spec plumbing, including explicit period selection, indexed/rank variants, endpoint completeness checks, curated `top_n` selection, highlighted-entity retention, and display ordering.
  - `render/slopegraph.py` now adds variant-aware subtitles and y-axis titles plus richer endpoint label behavior with delta labels and benchmark/highlight styling.
  - regression coverage now exercises the richer slopegraph fixture, and orchestrator tests cover indexed and rank request paths.
- Verification:
  - `python3 -m unittest foundations.visual_library.chart_engine_py.tests.test_orchestrator.OrchestratorTests.test_slopegraph_supports_rank_variant_and_top_n_selection foundations.visual_library.chart_engine_py.tests.test_orchestrator.OrchestratorTests.test_slopegraph_supports_explicit_periods_and_indexed_variant foundations.visual_library.chart_engine_py.tests.test_regression.RegressionTests.test_slopegraph_matches_golden` passed on 2026-07-12.
- Remaining caution:
  - this chart still inherits the shared Altair export/runtime caption limitation noted in the master register, so exported static artifacts should not yet be treated as full parity for caption placement.
