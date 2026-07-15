# heatmap_table

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/heatmap_table.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/heatmap_table.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/heatmap_table.py`
- R spec: `foundations/visual_library/charts/heatmap_table/heatmap_table_spec.md`
- R question coverage: `foundations/visual_library/charts/heatmap_table/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_heatmap_table.R`
- R render: `foundations/visual_library/shared/render/render_heatmap_table.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `render`
- Recommended fix order: render parity first, spec parity second, export parity third

## Spec Parity
- Match: Python keeps the main matrix field contract.
- Gaps: the generated spec does not preserve the R methodology, ordering, and variant guidance.

## Prep Parity
- Match: Python has a prep path and regression coverage.
- Gaps: R prep owns row ordering, highlight ordering, notes, and normalized/diverging fill conventions that are only partially reflected in Python.

## Render Parity
- Match: Python renders a matrix with text labels.
- Gaps: `render/heatmap_table.py` hardcodes a blue scale and omits the R renderer's highlight rows, diverging scale path, legend-title logic, and methodology note behavior.

## Theme / Defaults Parity
- Match: base font and dimension hooks exist.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: export path exists.
- Gaps: caption/source/vintage remain hidden in `usermeta`.

## Question Coverage Parity
- Supported: simple KPI profile matrix
- Partial: shortlist and peer-profile scans
- Missing: highlight-row and methodology-heavy review outputs

## Gap Register
- [major] [render] Python heatmap table omits several R visual semantics
  Evidence: `render/heatmap_table.py` always uses `scheme="blues"` and simple text overlays; `shared/render/render_heatmap_table.R` supports diverging fills, row highlight outlines, legend-title logic, and automatic methodology notes.
  Why it matters: the same matrix can tell a materially different story in Python.
  Fix location: `chart_engine_py/chart_engine/render/heatmap_table.py`
- [major] [spec] Generated heatmap spec loses the R methodology and QA contract
  Evidence: `chart_specs/heatmap_table.md` is a compressed artifact, while `charts/heatmap_table/heatmap_table_spec.md` documents more review rules and example question patterns.
  Why it matters: parity validation has too little contract surface in Python.
  Fix location: `chart_engine_py/scripts/generate_chart_specs.py`

## Recommended Follow-Up
- First: port the R diverging/highlight/methodology render semantics.
- Second: widen the generated spec artifact.
- Later: close the shared Altair caption/export gap.

## Progress Update 2026-07-12
- Closed in code:
  - `prep/heatmap_table.py` now supports variant-aware matrix completion, polarity-aware percentile normalization, explicit row/column ordering, and richer cell-label preparation
  - `render/heatmap_table.py` now supports diverging percentile fills, highlight outlines, better legend defaults, and improved cell-label handling
  - regression and orchestrator coverage now exercise row ordering and highlight-row semantics
- Still open:
  - the shared spec generator remains the source of any remaining methodology/detail compression, so contract richness still depends on the chart-spec regeneration path
