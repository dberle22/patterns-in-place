# Skill: Question → Chart Request

**File:** `chart_engine/skills/question_to_chart_request.py`
**Status:** Spec — implement against your actual `chart_rules.yml` / `metric_catalog.yml`

---

## What It Does

Takes the output of a completed query (a `ResultProfile` + the executed
DataFrame + the question's metadata) and produces a fully-formed
`ChartRequest` — ready to hand to `chart_engine.render()`.

This is the seam between the *analytics* world (question_type, metric_id,
geo_level, result shape) and the *chart engine* world (chart_type,
column_mapping, benchmark config). Neither side should know about the
other directly. This skill is the only thing that does.

**Concretely, it decides:**
1. Which `chart_type` answers this question, given its `question_type`
   and the shape of the result (row count, has_time_series, dimension_count)
2. How the result DataFrame's actual column names map onto that chart
   type's `required_fields` / `optional_fields`
3. Whether a benchmark belongs on the chart, and if so, what value/label
4. What title and subtitle to generate from the question text
5. What number format applies, from the metric's `unit_format`

---

## Inputs

| Input | Type | Source |
|---|---|---|
| `question_type` | `str` | `QueryPlan.question_type` (ranking, trend, compare_selected, distribution, benchmark, growth) |
| `result_df` | `pd.DataFrame` | `QueryExecutor` output |
| `result_profile` | `ResultProfile` | `app/charts/profiler.py` — row_count, has_time_series, dimension_count, inferred_shape |
| `question_text` | `str` | the original NL question or `question_queue.yaml` entry |
| `metric_id` | `str` | `QueryPlan.metric_id` |
| `geo_level` | `str` | `QueryPlan.geo_level` |
| `chart_rules` | `dict` | loaded `semantic_layer/chart_rules.yml` |
| `metric_catalog` | `dict` | loaded `semantic_layer/metric_catalog.yml` — for `unit_format`, display name |
| `theme` | `Theme` | caller-supplied, per-repo |
| `run_context` | `RunContext \| None` | question_id + source, for provenance |

## Outputs

A single `ChartRequest`, unrendered. This skill **never calls `render()`**
— it only builds the request. Keeping it a pure function (inputs in,
`ChartRequest` out, no side effects) is what makes it independently
testable and reusable from the publisher, the chatbot, and the Deep
Dive builder without any of them being coupled to each other.

---

## Logic

```
1. CHART TYPE SELECTION
   chart_type = chart_rules[question_type][result_profile.inferred_shape]
   → if no entry exists, raise (do not guess a fallback chart type —
     an unmapped question_type + shape combination is a chart_rules.yml
     gap, not something to paper over silently)

2. FIELD RESOLUTION
   spec = chart_engine.specs.load_spec(chart_type)
   column_mapping = infer_column_roles(result_df, result_profile, spec)
   → dimension column (e.g. cbsa_name) maps to spec's "entity" or "series"
     role depending on chart_type
   → metric column maps to "value"
   → time column (if result_profile.has_time_series) maps to "period"
   → raise if any of spec.required_fields has no resolvable source column

3. BENCHMARK RESOLUTION
   if question_type == "benchmark" or spec.default_benchmark is not None:
       benchmark = build_benchmark_config(metric_id, geo_level, chart_rules)
   else:
       benchmark = None

4. NUMBER FORMAT
   number_format = NumberFormat(**metric_catalog[metric_id]["unit_format"])

5. TEXT
   title = title_template(question_type).format(metric=metric_catalog[metric_id]["display_name"])
   subtitle = geo_level.title() + " grain" if geo_level != "cbsa" else None

6. ASSEMBLE
   return ChartRequest(
       data=result_df, chart_type=chart_type, theme=theme,
       column_mapping=column_mapping, benchmark=benchmark,
       number_format=number_format, title=title, subtitle=subtitle,
       run_context=run_context,
   )
```

---

## Reuses

- `app/charts/profiler.py` — `ResultProfile` (do not reimplement shape inference here)
- `semantic_layer/chart_rules.yml` — question_type + shape → chart_type mapping (already exists)
- `semantic_layer/metric_catalog.yml` — `unit_format`, display names
- `chart_engine.specs.load_spec()` — to read a candidate chart's required/optional fields before committing to it

## Key Constraint

**This skill must fail loudly, not guess.** Two specific cases:

- If `chart_rules.yml` has no entry for a `question_type` + `inferred_shape`
  pair, raise — don't default to `bar_chart`. An unmapped combination is
  a real gap that should surface in QA, not get silently papered over
  with a chart type that happens to not crash.
- If column-role inference can't confidently map a `required_field` to
  a source column (e.g. two equally-plausible dimension columns), raise
  with both candidates named, rather than picking one arbitrarily.

This mirrors the chatbot's existing design principle: **clarify rather
than improvise.**

## Optimization Levers

- Column-role inference heuristics — start with dtype + position rules
  (first non-numeric column = dimension, numeric column matching
  `metric_id` = value, datetime/year column = period); expand as edge
  cases surface in the QA batch runner
- Benchmark source expansion — national median today; regional/peer
  cluster benchmarks once `intelligence_catalog.yml` benchmark_strategy
  entries are calibrated (see `INTELLIGENCE_LAYER_ROADMAP.md` Phase 7)
- Title phrasing templates — one per `question_type`, tuned against
  actual publisher output review, same feedback loop as the existing
  Insight Summary skill
