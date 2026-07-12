# highlight_context_map

## Source Map
- Python spec: `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/highlight_context_map.md`
- Python prep: `foundations/visual_library/chart_engine_py/chart_engine/prep/highlight_context_map.py`
- Python render: `foundations/visual_library/chart_engine_py/chart_engine/render/highlight_context_map.py`
- R spec: `foundations/visual_library/charts/highlight_context_map/highlight_context_map_spec.md`
- R question coverage: `foundations/visual_library/charts/highlight_context_map/question_coverage.md`
- R prep: `foundations/visual_library/shared/prep/prep_highlight_context_map.R`
- R render: `foundations/visual_library/shared/render/render_highlight_context_map.R`

## Verdict
- Overall parity status: `major`
- Primary missing layer: `prep`
- Recommended fix order: variant/benchmark parity first, render parity second, tests third

## Spec Parity
- Match: Python preserves highlight, neighbor, and optional metric fields.
- Gaps: the generated spec does not preserve the R `focus_only`, `continuous`, `binned`, and `diverging` variant guidance.

## Prep Parity
- Match: Python preserves `highlight_flag`, `neighbor_flag`, and optional `metric_value`.
- Gaps: R prep handles variant selection, optional benchmark deltas, and a hard `require_highlight` rule; Python prep does not.

## Render Parity
- Match: Python draws highlighted and neighbor outlines with a legend.
- Gaps: render fidelity is bounded by the thinner prep surface, so the full R variant set cannot be expressed.

## Theme / Defaults Parity
- Match: matplotlib title/subtitle/caption helpers exist.
- Gaps: font-family drift remains.

## Export / Runtime Parity
- Match: matplotlib export renders visible captions.
- Gaps: tests remain structural-only.

## Question Coverage Parity
- Supported: simple locator and neighbor-context maps
- Partial: metric-colored local outlier maps
- Missing: diverging benchmark-relative highlight maps

## Gap Register
- [major] [prep] Python highlight-context prep omits the R variant and benchmark logic
  Evidence: `shared/prep/prep_highlight_context_map.R` supports `variant`, `benchmark_field`, and `require_highlight`; `prep/highlight_context_map.py` preserves only flags and optional metric coercion.
  Why it matters: several canonical R highlight-context stories are unavailable in Python.
  Fix location: `chart_engine_py/chart_engine/prep/highlight_context_map.py`
- [major] [tests] Geo render coverage is structural-only
  Evidence: `tests/test_geo_render.py` checks only that `highlight_context_map` returns a `Figure`.
  Why it matters: variant-specific map behavior can drift without visual regression checks.
  Fix location: `chart_engine_py/tests/test_geo_render.py`

## Recommended Follow-Up
- First: port variant and benchmark delta logic in prep.
- Second: add stronger geo regression coverage.
- Later: widen the generated spec artifact.

## Progress Update 2026-07-12
- Closed in code: prep now supports focus-only vs analytical variants, benchmark-relative fill metadata, and explicit highlight requirements.
- Closed in code: render now supports role-aware fills plus faceted panels.
- Closed in code: geo prep coverage now asserts role metadata.
- Still open: geo render checks are improved but still not snapshot-style parity tests.
