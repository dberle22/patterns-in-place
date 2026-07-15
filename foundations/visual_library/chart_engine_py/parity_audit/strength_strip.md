# strength_strip

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/strength_strip.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/strength_strip.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/strength_strip.py`
- R spec: `foundations/visual_library/charts/strength_strip/strength_strip_spec.md`
- R question coverage: `foundations/visual_library/charts/strength_strip/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_strength_strip.R`
- R render: `foundations/visual_library/shared/render/render_strength_strip.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `render`
- Recommended fix order: benchmark semantics first, facet parity second, export parity third

## Spec Parity
- Match: Python keeps the base field contract and optional benchmark metadata.
- Gaps: the generated spec does not preserve the R benchmark-delta and composition guidance.

## Prep Parity
- Match: Python has a prep path and regression coverage.
- Gaps: R prep carries more explicit benchmark-delta shaping and normalization logic.

## Render Parity
- Match: Python renders a strip chart with a legend.
- Gaps: R render supports richer benchmark and comparison semantics than the Python surface expresses.

## Theme / Defaults Parity
- Match: shared palette intent is aligned.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: export path exists.
- Gaps: caption/source/vintage remain hidden in `usermeta`.

## Question Coverage Parity
- Supported: simple KPI profile strip
- Partial: peer comparison
- Missing: benchmark-delta and comparison-heavy strip stories

## Gap Register
- [major] [render] Python strength strip is materially thinner than the R benchmark/comparison contract
  Evidence: `charts/strength_strip/strength_strip_spec.md` explicitly documents delta-vs-benchmark behavior, while `render/strength_strip.py` renders a much simpler strip form.
  Why it matters: the core benchmark story for this chart type is under-specified in Python.
  Fix location: `chart_engine_py/chart_engine/render/strength_strip.py`
- [major] [spec] Generated strength-strip spec loses benchmark-focused guidance
  Evidence: `chart_specs/strength_strip.md` omits the richer benchmark and QA guidance present in the R spec and question coverage docs.
  Why it matters: Python's runtime contract is too thin for a benchmark-led chart type.
  Fix location: `chart_engine_py/scripts/generate_chart_specs.py`

## Recommended Follow-Up
- First: port benchmark-delta render semantics.
- Second: widen the generated spec artifact.
- Later: close the shared Altair caption/export gap.

## Progress Update 2026-07-12
- Closed in code:
  - `prep/strength_strip.py` now preserves benchmark inputs beyond the thin generated spec, computes normalized values and benchmark-normalized positions, and exposes `benchmark_delta` for comparison-heavy stories.
  - `render/strength_strip.py` now supports benchmark markers, richer peer/highlight coloring, and multi-window stacked composition for comparison workflows.
  - regression fixtures and orchestrator coverage now exercise benchmark-led and multi-window strip paths.
- Verification:
  - `python3 -m unittest foundations.visual_library.chart_engine_py.tests.test_orchestrator.OrchestratorTests.test_strength_strip_supports_benchmark_and_window_facet_prep foundations.visual_library.chart_engine_py.tests.test_regression.RegressionTests.test_strength_strip_matches_golden` passed on 2026-07-12.
- Remaining caution:
  - this chart still depends on the generated-spec gap for formally documenting benchmark-focused runtime fields, and it still inherits the shared Altair export/runtime caption limitation.
