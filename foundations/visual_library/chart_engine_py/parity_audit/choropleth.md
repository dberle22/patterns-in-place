# choropleth

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/choropleth.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/choropleth.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/choropleth.py`
- R spec: `foundations/visual_library/charts/choropleth/choropleth_spec.md`
- R question coverage: `foundations/visual_library/charts/choropleth/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_choropleth.R`
- R render: `foundations/visual_library/shared/render/render_choropleth.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `render`
- Recommended fix order: variant parity first, facet/legend parity second, tests third

## Spec Parity
- Match: Python keeps the base map field contract, including `benchmark_value`, `bin`, and `highlight_flag`.
- Gaps: the generated spec does not preserve the R continuous/binned/diverging map guidance.

## Prep Parity
- Match: Python coerces values and preserves geometry/highlight/bin columns.
- Gaps: R prep computes variant-specific `fill_value` logic from `benchmark_value`; Python prep does not.

## Render Parity
- Match: Python renders a continuous choropleth with highlight outlines and a colorbar.
- Gaps: R render supports continuous, binned, diverging, and faceted map workflows; Python render is continuous-only and does not expose those branches.

## Theme / Defaults Parity
- Match: map title/subtitle/caption helpers exist on the matplotlib side.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: matplotlib export renders visible captions.
- Gaps: current tests do not verify visual parity beyond "returns a Figure."

## Question Coverage Parity
- Supported: simple continuous geographic distribution
- Partial: highlight-focused local maps
- Missing: diverging benchmark-relative and faceted growth-window comparison maps

## Gap Register
- [major] [render] Python choropleth is continuous-only
  Evidence: `render/choropleth.py` always normalizes `metric_value` into a continuous `Blues` colorbar; `shared/render/render_choropleth.R` supports multiple variants and faceting.
  Why it matters: several canonical R choropleth questions cannot be expressed with the same semantics.
  Fix location: `chart_engine_py/chart_engine/render/choropleth.py`
- [major] [tests] Geo render coverage is structural-only
  Evidence: `tests/test_geo_render.py` asserts only that `choropleth` returns a matplotlib `Figure`.
  Why it matters: map parity can drift without any snapshot-style regression signal.
  Fix location: `chart_engine_py/tests/test_geo_render.py`

## Recommended Follow-Up
- First: port binned/diverging/facet map semantics.
- Second: strengthen geo render regression coverage.
- Later: align the generated spec with the fuller R map contract.

## Progress Update 2026-07-12
- Closed in code: prep now supports request-driven filtering, benchmark-relative fill values, and binned/diverging variant metadata.
- Closed in code: render now supports continuous, binned, and diverging fills plus faceted map panels.
- Closed in code: geo prep coverage now asserts fill metadata rather than only preserved columns.
- Still open: geo render coverage is stronger than before but still structural compared with the richer golden-style parity surface used elsewhere.
