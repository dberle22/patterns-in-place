# correlation_heatmap

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/correlation_heatmap.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/correlation_heatmap.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/correlation_heatmap.py`
- R spec: `foundations/visual_library/charts/correlation_heatmap/correlation_heatmap_spec.md`
- R question coverage: `foundations/visual_library/charts/correlation_heatmap/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_correlation_heatmap.R`
- R render: `foundations/visual_library/shared/render/render_correlation_heatmap.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `prep`
- Recommended fix order: facet/grouping parity first, render parity second, export parity third

## Spec Parity
- Match: Python has a generated spec and regression coverage.
- Gaps: the generated spec does not preserve the R faceting and comparison question guidance.

## Prep Parity
- Match: Python produces a minimal correlation matrix contract.
- Gaps: `prep/correlation_heatmap.py` explicitly notes it preserves only a minimal contract, while `shared/prep/prep_correlation_heatmap.R` handles `facet_by` and split-universe workflows.

## Render Parity
- Match: Python renders a diverging correlation matrix.
- Gaps: R render carries more title/subtitle/methodology handling and comparison workflows.

## Theme / Defaults Parity
- Match: diverging correlation palette is directionally aligned.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: export path exists.
- Gaps: caption/source/vintage remain hidden in `usermeta`.

## Question Coverage Parity
- Supported: single-universe KPI correlation scan
- Partial: within-CBSA metric scan
- Missing: faceted universe comparison workflows

## Gap Register
- [major] [prep] Python correlation-heatmap prep is intentionally minimal relative to R
  Evidence: `prep/correlation_heatmap.py` comments that it preserves only a minimal contract; `shared/prep/prep_correlation_heatmap.R` includes `facet_by` and single-vs-faceted validation logic.
  Why it matters: Python cannot yet reproduce the full R comparison surface.
  Fix location: `chart_engine_py/chart_engine/prep/correlation_heatmap.py`
- [major] [spec] Generated correlation-heatmap spec loses comparison guidance
  Evidence: the generated spec is compressed, while the R spec and question coverage docs document multiple analytical comparison patterns.
  Why it matters: parity review lacks enough contract detail for one of the more interpretation-heavy chart types.
  Fix location: `chart_engine_py/scripts/generate_chart_specs.py`

## Recommended Follow-Up
- First: port the faceting/grouping prep logic.
- Second: widen the generated spec and render notes.
- Later: close the shared Altair caption/export gap.

## Progress Update 2026-07-12
- Closed in code:
  - `prep/correlation_heatmap.py` now supports group-split/faceted comparison prep, weak-correlation masking, ordering metadata, and richer matrix output fields
  - `render/correlation_heatmap.py` now supports comparison panel composition plus method/missingness/order subtitles instead of a single minimal matrix
  - regression and orchestrator coverage now exercise faceted comparison workflows
- Still open:
  - the spec artifact is still lighter than the R source docs, so comparison guidance remains more compressed in the generated markdown than in the implementation
