# Chart Engine — Build Spec

**Status:** Reference implementation complete for 2 of ~15 chart types (bar, line). This spec covers the full intended surface; extend chart-by-chart using the pattern established here.

**Design principle:** `render()` takes a single `ChartRequest` object, not a flat function signature. Every optional capability (benchmark, annotation, facet, output persistence, run provenance) is a sub-config on that object. A render function only needs to read the sub-configs it actually supports — unsupported configs are silently ignored by that chart type, not required by all of them. This is what lets the request surface grow to 15+ chart types without any individual chart type's render function needing to handle every config.

---

## 1. Architecture

```
ChartRequest (full input surface)
    │
    ▼
render(request) -> ChartResult
    │
    ├── 1. registry lookup:      chart_type -> (spec_path, prep_fn, render_fn)
    ├── 2. spec load:            .md front-matter -> ChartSpec
    ├── 3. spec override:        column_mapping + field_values merged in
    ├── 4. prep:                 prep_fn(request.data, spec) -> prepped df
    ├── 5. contract validation:  validate_contract(prepped, spec) -> raises or passes
    ├── 6. facet size check:     warn if facet cardinality exceeds max_panels
    ├── 7. [validate_only?]      return early, chart=None
    ├── 8. render:               render_fn(prepped, spec, request) -> chart object
    ├── 9. [output.save?]        persist to disk, dispatch on .save/.savefig
    └── 10. wrap:                ChartResult(chart, output_path, warnings, ...)
```

**Two entry points, one code path:**
- `render(request: ChartRequest) -> ChartResult` — the real API. Use for anything with a benchmark, annotation, facet, output config, or run context.
- `render_chart(data, chart_type, theme, **overrides) -> chart_object` — thin convenience wrapper for simple ad hoc calls. Builds a `ChartRequest` internally and calls `render()`. Never add logic here that doesn't also apply to `render()` — this must stay sugar, not a second implementation.

---

## 2. `ChartRequest` — full schema

See `chart_engine/request.py` for the authoritative dataclasses. Summary:

| Field | Type | Purpose |
|---|---|---|
| `data` | `pd.DataFrame` | required |
| `chart_type` | `str` | required — registry key |
| `theme` | `Theme` | required |
| `column_mapping` | `dict` | source column → canonical field name |
| `field_values` | `dict` | chart-specific optional field *values* (e.g. `highlight_entity="Jacksonville"`), distinct from column renaming |
| `title` / `subtitle` / `alt_text` | `str \| None` | overrides spec-derived defaults |
| `benchmark` | `BenchmarkConfig \| None` | reference line/shape — national median, regional, peer cluster, or custom value |
| `annotations` | `list[Annotation]` | point/vline/hline/range/text callouts |
| `facet` | `FacetConfig \| None` | small multiples — facet field, column count, max panels |
| `dimensions` | `DimensionOverride \| None` | width/height override beyond theme defaults |
| `number_format` | `NumberFormat \| None` | unit, decimals, compact notation — sourced from `metric_catalog.yml` in production |
| `output` | `OutputConfig` | save flag, path, format, social crop preset, DPI scale |
| `run_context` | `RunContext \| None` | question_id, source, run_id — provenance only, never affects rendering |
| `interactive` | `bool` | Altair interactive vs static |
| `validate_only` | `bool` | run steps 1–6 only, skip render — for QA batch runner |
| `return_prepped_data` | `bool` | attach the prepped df to `ChartResult` for debugging |

**Rule for adding a new sub-config in the future:** it must be optional, default to `None` or an inert value, and existing render functions must continue to work unchanged if they don't read it. Never make an existing render function's signature depend on a new required field.

---

## 3. `ChartSpec` — per chart type contract

Lives as YAML front-matter inside generated `chart_specs/<chart_type>.md` files. The human-authored source remains `visual_library/charts/<type>/<type>_spec.md`; package-local spec files are machine-readable artifacts derived from those docs so consumers have a stable runtime contract without creating a second hand-maintained spec layer.

```yaml
---
chart_type: bar_chart
backend: altair              # or matplotlib
required_fields: [entity, value]
optional_fields: [subtitle]
column_mapping: {}
default_benchmark: null      # or e.g. "national_median" if this chart type usually wants one
---
# markdown docs below — question coverage, usage notes, constraints
```

`ChartSpec.default_benchmark` is what the skill (Section 5) checks to decide whether to auto-attach a benchmark even when the question wasn't explicitly `question_type: benchmark`.

---

## 4. Adding a new chart type — checklist

Use `bar_chart` as the template. Per chart type:

1. `chart_specs/<name>.md` — front-matter + docs
2. `prep/<name>.py` — `prep_<name>(df, spec) -> df`, driven by `spec.column_mapping` / `spec.required_fields`, not hardcoded column names
3. `render/<name>.py` — `render_<name>(df, spec, request) -> chart_object`
   - Read `request.theme` for all styling — never hardcode colors/fonts
   - Only implement the sub-configs (`benchmark`, `annotations`, `facet`) that are meaningful for this chart type; ignore the rest
   - Backend choice is per chart type — geospatial types (choropleth, hexbin, bivariate choropleth, proportional symbol map, highlight context map) should use `matplotlib` + `geopandas`; everything else defaults to `altair`
4. One line in `registry.py`'s `CHART_REGISTRY`
5. Nothing else changes — no consuming repo needs an update, no orchestrator edit

**Priority order for the remaining 13 types** (from `visual_library`): choropleth, scatter, slopegraph, bump chart, heatmap table, boxplot next (highest reuse across Deep Dive sections 1, 3, 4, 6, 8); age pyramid, hexbin, highlight context map, proportional symbol map, bivariate choropleth, correlation heatmap, strength strip last (single-purpose, lower reuse).

---

## 5. Skill: Question → Chart Request

**Spec:** `chart_engine/skills/question_to_chart_request.md`
**Implementation:** `chart_engine/skills/question_to_chart_request.py`

Pure function: `(question_type, result_df, result_profile, metric_id, geo_level, chart_rules, metric_catalog, theme) -> ChartRequest`. Never calls `render()` itself.

This is the seam between your analytics pipeline (`app/charts/profiler.py`'s `ResultProfile`, `semantic_layer/chart_rules.yml`, `semantic_layer/metric_catalog.yml`) and the chart engine. It replaces what would otherwise be ad hoc, repeated field-mapping logic inside the publisher, the chatbot's `charts/selector.py`, and the Deep Dive builder.

**Must fail loud, not guess:**
- Unmapped `question_type` + `inferred_shape` in `chart_rules.yml` → raise, don't default to a chart type
- Ambiguous column-role inference (two equally-plausible dimension columns) → raise naming both candidates, don't pick arbitrarily

**Integration points once real `chart_rules.yml`/`metric_catalog.yml` are wired in:**
- Publisher: `packager.py` calls this skill after `QueryExecutor`, before `render()`
- Chatbot: replaces manual mapping currently implicit in `charts/selector.py` + `charts/renderer.py`
- Deep Dive builder: same skill, called once per section's chart, with `run_context.source="deep_dive"`

---

## 6. Output / persistence

`OutputConfig.social_crop` is a placeholder for the daily publisher's open question #2 ("What are the X-optimized chart dimensions?"). Once decided, implement as preset `DimensionOverride` values keyed by `social_crop`, applied in `render()` before `dimensions` is passed to `render_fn` — this keeps the crop decision out of every individual render function.

`_persist()` in `orchestrator.py` dispatches on `hasattr(chart, "save")` (Altair) vs `hasattr(chart, "savefig")` (matplotlib) — this is the seam that keeps render functions backend-agnostic about their own persistence.

---

## 7. Testing requirements (not yet implemented — add before extending past 2 chart types)

- `tests/test_contracts.py` — missing required field raises `ContractError` with correct message; empty df raises
- `tests/test_registry.py` — every registered chart_type has a loadable spec and matching prep/render function signatures
- `tests/test_orchestrator.py` — `validate_only=True` never calls a render function; `output.save=True` calls `_persist`; unknown `chart_type` raises `KeyError`
- `tests/test_skill_question_to_chart_request.py` — unmapped question_type/shape raises `ChartMappingError`; ambiguous column inference raises; happy path produces a request that `render()` accepts without error
- Golden-file tests per chart type: fixed input df + theme → saved `.json` (Altair's `to_dict()`) compared on each run, to catch unintended visual regressions

---

## 8. Explicitly out of scope for this spec

- Auto chart-type selection *inside* `render()` — selection is the skill's job (Section 5), not the engine's. `render()` always requires an explicit `chart_type`.
- R interop / `reticulate` bridge — this package assumes a full Python port; if bar/line charts need to ship before geospatial types are ported, that's a phased rollout of chart types within this package, not a hybrid R/Python runtime.
- Caching — `ChartRequest`/`ChartResult` are cache-key-able (mostly plain types) but no caching layer is implemented here.
