# proportional_symbol_map

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/proportional_symbol_map.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/proportional_symbol_map.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/proportional_symbol_map.py`
- R spec: `foundations/visual_library/charts/proportional_symbol_map/proportional_symbol_map_spec.md`
- R question coverage: `foundations/visual_library/charts/proportional_symbol_map/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_proportional_symbol_map.R`
- R render: `foundations/visual_library/shared/render/render_proportional_symbol_map.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `render`
- Recommended fix order: legend/group parity first, prep parity second, tests third

## Spec Parity
- Match: Python preserves size, optional color-group, highlight, and label fields.
- Gaps: the generated spec does not preserve the R size-legend and label-strategy guidance.

## Prep Parity
- Match: Python keeps coordinates, size values, highlight flags, and labels.
- Gaps: R prep carries more explicit label-strategy separation and mapping defaults.

## Render Parity
- Match: Python renders scaled bubbles and optional labels.
- Gaps: R render includes size legends, color-group legends, and richer note treatment; Python render does not.

## Theme / Defaults Parity
- Match: matplotlib title/subtitle/caption helpers exist.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: matplotlib export renders visible captions.
- Gaps: tests remain structural-only.

## Question Coverage Parity
- Supported: simple bubble concentration maps
- Partial: labeled highlight maps
- Missing: fully legend-driven color-group comparisons

## Gap Register
- [major] [render] Python proportional-symbol render omits important legend semantics
  Evidence: `render/proportional_symbol_map.py` draws circles and labels only; `proportional_symbol_map_spec.md` and the R render path expect size and color legends to explain bubble area and groups.
  Why it matters: readers get less guidance in Python on how to interpret size and color.
  Fix location: `chart_engine_py/chart_engine/render/proportional_symbol_map.py`
- [major] [tests] Geo render coverage is structural-only
  Evidence: `tests/test_geo_render.py` checks only that `proportional_symbol_map` returns a `Figure`.
  Why it matters: symbol-scaling and legend regressions would not be caught.
  Fix location: `chart_engine_py/tests/test_geo_render.py`

## Recommended Follow-Up
- First: port size/color legend behavior.
- Second: add stronger geo regression coverage.
- Later: widen the generated spec artifact.

## Progress Update 2026-07-12
- Closed in code: prep now supports Top-N filtering, rank/share metadata, and label strategies.
- Closed in code: render now supports explicit size and color legends rather than unlabeled bubbles only.
- Closed in code: geo prep coverage now asserts ranking metadata.
- Still open: there is still no committed image or golden-style regression surface for matplotlib maps.
