# bump_chart

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/bump_chart.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/bump_chart.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/bump_chart.py`
- R spec: `foundations/visual_library/charts/bump_chart/bump_chart_spec.md`
- R question coverage: `foundations/visual_library/charts/bump_chart/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_bump_chart.R`
- R render: `foundations/visual_library/shared/render/render_bump_chart.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `prep`
- Recommended fix order: entity-selection parity first, render-label parity second, export parity third

## Spec Parity
- Match: Python preserves the base field contract, including `rank`, `highlight_flag`, and `peer_flag`.
- Gaps: the generated spec does not preserve the R entity-selection strategies or rank-method notes.

## Prep Parity
- Match: Python computes ranks when absent and preserves highlights.
- Gaps: R prep supports fixed-top-N, rolling-top-N, peer-set, and all-entity strategies plus endpoint fields and rank metadata; Python prep does not.

## Render Parity
- Match: Python draws rank lines with end labels and highlight color.
- Gaps: R render includes richer endpoint labeling, peer/context styling, rank-band semantics, and caption notes.

## Theme / Defaults Parity
- Match: highlight/comparison color intent is aligned.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: export path exists.
- Gaps: caption/source/vintage remain hidden in `usermeta`.

## Question Coverage Parity
- Supported: simple rank-over-time view
- Partial: target-rank and stability questions
- Missing: rolling-top-N and peer-set selection behavior

## Gap Register
- [major] [prep] Python bump prep lacks the R entity-selection and rank metadata surface
  Evidence: `prep/bump_chart.py` computes a basic rank and sorts; `shared/prep/prep_bump_chart.R` supports `entity_strategy`, `selection_period`, `include_highlighted`, `peer_flag`, and endpoint metadata.
  Why it matters: canonical R bump questions are curated views, not just raw rank lines.
  Fix location: `chart_engine_py/chart_engine/prep/bump_chart.py`
- [major] [render] Python bump render is materially simpler than the R reference
  Evidence: `render/bump_chart.py` draws a single comparison/highlight line layer; `shared/render/render_bump_chart.R` includes peer/context separation, endpoint-label planning, and rank-band treatment.
  Why it matters: the same rank-change story is less interpretable in Python.
  Fix location: `chart_engine_py/chart_engine/render/bump_chart.py`

## Recommended Follow-Up
- First: port entity-selection and endpoint metadata from the R prep.
- Second: port peer/context and endpoint-label semantics in render.
- Later: close the shared Altair caption/export gap.

## Progress Update 2026-07-12
- Closed in code:
  - `prep/bump_chart.py` now supports request-driven entity selection strategies including fixed-top-N, rolling-top-N, peer-set, and all-entity views, plus endpoint metadata and rank-source fields.
  - `render/bump_chart.py` now distinguishes context, peer, and highlight lines and adds richer end labels plus subtitle metadata for selection and rank method.
  - regression fixtures and orchestrator coverage now exercise peer-set selection and endpoint metadata.
- Verification:
  - `python3 -m unittest foundations.visual_library.chart_engine_py.tests.test_orchestrator.OrchestratorTests.test_bump_chart_supports_peer_set_and_endpoint_metadata foundations.visual_library.chart_engine_py.tests.test_regression.RegressionTests.test_bump_chart_matches_golden` passed on 2026-07-12.
- Remaining caution:
  - rank-band semantics and the shared Altair export/runtime caption limitation still remain outside this tranche.
