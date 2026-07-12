# age_pyramid

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/age_pyramid.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/age_pyramid.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/age_pyramid.py`
- R spec: `foundations/visual_library/charts/age_pyramid/age_pyramid_spec.md`
- R question coverage: `foundations/visual_library/charts/age_pyramid/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_age_pyramid.R`
- R render: `foundations/visual_library/shared/render/render_age_pyramid.R`

## Verdict
- Overall parity status: `blocking`
- Primary missing layer: `render`
- Recommended fix order: benchmark/facet render parity first, prep parity second, export parity third

## Spec Parity
- Match: Python preserves the base age/sex field contract.
- Gaps: the generated spec does not preserve the R benchmark-outline and facet-heavy usage guidance.

## Prep Parity
- Match: Python computes population shares and signed left/right values.
- Gaps: Python defaults `highlight_flag` to `True` for all rows, which is a different default posture from the R chart family and can mask intentional highlight semantics.

## Render Parity
- Match: Python renders mirrored bars by sex.
- Gaps: the canonical R age-pyramid questions use benchmark outlines and multiple faceted comparison layouts; `render/age_pyramid.py` renders a single bar pyramid with no benchmark overlay or facet path.

## Theme / Defaults Parity
- Match: base dimensions and bar form are present.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: export path exists.
- Gaps: caption/source/vintage remain hidden in `usermeta`.

## Question Coverage Parity
- Supported: simple single-entity age structure
- Partial: single-entity benchmark comparison by title/subtitle only
- Missing: benchmark-outline and faceted county/peer/ZCTA comparison workflows

## Gap Register
- [blocking] [render] Python age pyramid cannot tell the canonical R benchmark/facet stories
  Evidence: `charts/age_pyramid/test_age_pyramid_render.R` repeatedly uses benchmark outlines and `facet_by`; `render/age_pyramid.py` only draws one mirrored bar chart plus a zero rule.
  Why it matters: several primary R age-pyramid use cases are unavailable in Python.
  Fix location: `chart_engine_py/chart_engine/render/age_pyramid.py`
- [major] [prep] Python prep defaults `highlight_flag` to `True`
  Evidence: `prep/age_pyramid.py` sets `highlight_flag` to `True` when the column is absent.
  Why it matters: that default can blur intentional distinction between selected and comparison structures.
  Fix location: `chart_engine_py/chart_engine/prep/age_pyramid.py`

## Recommended Follow-Up
- First: port benchmark-outline and facet behavior from the R render path.
- Second: revisit highlight/default semantics in prep.
- Later: close the shared Altair caption/export gap.

## Progress Update 2026-07-12
- Closed in code:
  - the Python prep layer now defaults benchmark rows and highlight semantics more explicitly instead of treating all rows as selected
  - the Python renderer now supports benchmark outlines, automatic faceting, richer default titles/subtitles, and visible caption text
  - the regression golden was refreshed against the expanded selected-versus-benchmark fixture
- Residual parity risk:
  - the generated spec still compresses some of the R usage guidance around benchmark-heavy and facet-heavy storytelling
  - this chart still needs a manual parity pass against real publisher content before it can be treated as production-validated
