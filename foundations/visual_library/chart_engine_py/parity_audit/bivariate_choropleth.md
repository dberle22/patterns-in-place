# bivariate_choropleth

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/bivariate_choropleth.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/bivariate_choropleth.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/bivariate_choropleth.py`
- R spec: `foundations/visual_library/charts/bivariate_choropleth/bivariate_choropleth_spec.md`
- R question coverage: `foundations/visual_library/charts/bivariate_choropleth/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_bivariate_choropleth.R`
- R render: `foundations/visual_library/shared/render/render_bivariate_choropleth.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `render`
- Recommended fix order: facet/legend parity first, tests second, spec parity third

## Spec Parity
- Match: Python preserves x/y value and bin fields.
- Gaps: the generated spec does not preserve the R faceting, composition, and legend guidance.

## Prep Parity
- Match: Python computes bivariate classes and keeps highlight flags.
- Gaps: R prep has more explicit binning controls and group/facet considerations than the Python surface documents.

## Render Parity
- Match: Python renders a map and inset 3x3 legend key.
- Gaps: R render supports faceting and a more configurable composed legend/layout path; Python render is single-map only.

## Theme / Defaults Parity
- Match: matplotlib title/subtitle/caption helpers exist.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: matplotlib export renders visible captions.
- Gaps: tests remain structural-only.

## Question Coverage Parity
- Supported: single-universe overlap map
- Partial: highlighted local overlap views
- Missing: faceted growth-window comparison maps

## Gap Register
- [major] [render] Python bivariate choropleth lacks the R facet/composition surface
  Evidence: `shared/render/render_bivariate_choropleth.R` supports `facet_by` and a configurable legend composition path; `render/bivariate_choropleth.py` renders one map and one fixed inset legend.
  Why it matters: canonical R bivariate comparison questions are only partially portable.
  Fix location: `chart_engine_py/chart_engine/render/bivariate_choropleth.py`
- [major] [tests] Geo render coverage is structural-only
  Evidence: `tests/test_geo_render.py` checks only that `bivariate_choropleth` returns a `Figure`.
  Why it matters: bivariate binning and legend regressions would not be caught.
  Fix location: `chart_engine_py/tests/test_geo_render.py`

## Recommended Follow-Up
- First: port faceting and more configurable legend composition.
- Second: add stronger geo regression coverage.
- Later: widen the generated spec artifact.

## Progress Update 2026-07-12
- Closed in code: prep now supports grouped bin metadata and request-driven bin recomputation.
- Closed in code: render now supports faceted comparison panels and a more flexible bivariate key surface.
- Closed in code: geo prep coverage now asserts grouped comparison prep behavior.
- Still open: matplotlib render coverage is stronger structurally but still not a golden image parity surface.
