# waterfall

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/waterfall.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/waterfall.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/waterfall.py`
- R spec: `foundations/visual_library/charts/waterfall/waterfall_spec.md`
- R question coverage: `foundations/visual_library/charts/waterfall/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_waterfall.R`
- R render: `foundations/visual_library/shared/render/render_waterfall.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `render`
- Recommended fix order: benchmark/facet parity first, cumulative-path parity second, export parity third

## Spec Parity
- Match: Python preserves the main waterfall field contract, including benchmark and sort metadata.
- Gaps: the generated spec does not preserve the R benchmark-comparison and negative-offset guidance.

## Prep Parity
- Match: Python has a prep path and regression coverage.
- Gaps: the R prep/test path carries more explicit cumulative-path and benchmark-panel logic than the Python parity surface documents.

## Render Parity
- Match: Python renders a waterfall with positive/negative coloring.
- Gaps: R render supports the benchmark faceting path used in `waterfall_income_mix_compare`, plus richer caption/note behavior; Python does not expose those semantics.

## Theme / Defaults Parity
- Match: diverging colors are aligned in spirit.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: export path exists.
- Gaps: caption/source/vintage remain hidden in `usermeta`.

## Question Coverage Parity
- Supported: simple component decomposition
- Partial: negative-offset decomposition
- Missing: benchmark-faceted comparison workflows

## Gap Register
- [major] [render] Python waterfall does not cover the benchmark-faceted R workflow
  Evidence: `charts/waterfall/test_waterfall_render.R` explicitly renders `facet_by = "benchmark_label"` for the benchmark comparison case; `render/waterfall.py` has no facet path.
  Why it matters: one of the canonical R waterfall questions cannot be told the same way in Python.
  Fix location: `chart_engine_py/chart_engine/render/waterfall.py`
- [major] [spec] Generated waterfall spec loses the R question-pattern guidance
  Evidence: `chart_specs/waterfall.md` is compressed, while `charts/waterfall/waterfall_spec.md` and `question_coverage.md` call out benchmark-comparison and negative-offset patterns.
  Why it matters: parity review loses the distinction between supported and unsupported waterfall stories.
  Fix location: `chart_engine_py/scripts/generate_chart_specs.py`

## Recommended Follow-Up
- First: port benchmark-faceted comparison semantics.
- Second: carry fuller benchmark/question guidance into the generated spec.
- Later: close the shared Altair caption/export gap.

## Progress Update 2026-07-12
- Closed in code:
  - `prep/waterfall.py` now supports grouped cumulative-path prep, total-row generation, additive metadata, and benchmark comparison grouping
  - `render/waterfall.py` now supports benchmark comparison panels, connector lines, and value labels rather than a single unfaceted bar layer
  - regression and orchestrator coverage now exercise total-row and benchmark-panel workflows
- Still open:
  - the richer question-pattern guidance still depends on the generated spec artifact, so the implementation is ahead of the compressed contract file
