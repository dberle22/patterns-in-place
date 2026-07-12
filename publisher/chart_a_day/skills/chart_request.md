---
name: chart_request
mode: prompt
version: 0.1
description: Turn a Chart-A-Day result CSV into a chart_engine_py ChartRequest and render chart artifacts.
inputs:
  - q_id
  - question
  - template_id
  - backlog_notes
  - produce_alternatives
  - result_csv_path
outputs:
  - chart.png
  - chart_alt.png
---

# Purpose

You are rendering a Chart-A-Day backlog result through `chart_engine_py`. This is the CE-1/CE-2 manual path, so call `chart_engine.render()` directly. `publisher/shared/chart_bridge.py` does not exist until CE-3.

Run the Python render snippet from the monorepo root, or from another shell context where the editable `chart_engine_py` package resolves first. Do not run the snippet from inside `publisher/` with `PYTHONPATH=.` because that local path also contains a `chart_a_day/` directory for backlog assets.

Inputs:

- `q_id`: `{{q_id}}`
- `question`: `{{question}}`
- `template_id`: `{{template_id}}`
- `backlog_notes`: `{{backlog_notes}}`
- `produce_alternatives`: `{{produce_alternatives}}`
- `result_csv_path`: `{{result_csv_path}}`

# Load Context

- Read `foundations/semantic_layer/chart_rules.yml`.
- Read the CSV at `{{result_csv_path}}` into a DataFrame.
- Import from the editable Python package under `foundations/visual_library/chart_engine_py/`.

Suggested import surface:

```python
from pathlib import Path

import pandas as pd
from chart_engine import BenchmarkConfig, ChartRequest, OutputConfig, Theme, render
```

# Chart Type Resolution

Use this decision chain in order:

1. Read `template_id`.
2. Look up the matching rule in `chart_rules.yml`.
3. Start from `approved_chart_types[0]`.
4. Check the relevant selection constraints against the actual result shape.
5. If a constraint blocks the primary type, use `fallback_chart_types[0]`.
6. If `backlog_notes` explicitly says to use a named chart type, that overrides the rule lookup.
7. If no rule exists, stop and report the gap instead of guessing.

Compatibility note:

- `chart_rules.yml` still uses legacy shared names `bar` and `line` for chatbot compatibility.
- When building a Python `ChartRequest`, normalize `bar -> bar_chart` and `line -> line_chart`.
- All other chart type names should pass through unchanged.

# Template Reference Table

Use this only as a human cross-check. The source of truth is still `chart_rules.yml`.

| `template_id` | Primary | Fallback |
|---|---|---|
| `ranking` | `bar_chart` | `heatmap_table` |
| `trend` | `line_chart` | `slopegraph` |
| `compare_selected` | `bar_chart` | `slopegraph` |
| `distribution` | `boxplot` | `heatmap_table` |
| `benchmark` | `bar_chart` | `strength_strip` |
| `growth` | `bar_chart` | `heatmap_table` |
| `correlation` | `scatter` | `hexbin` |
| `composition` | `waterfall` | `heatmap_table` |
| `map` | `choropleth` | `highlight_context_map` |
| `demographic` | `age_pyramid` | `heatmap_table` |
| `rank_change` | `bump_chart` | `slopegraph` |

# Column Mapping Guidance

`chart_engine_py` expects canonical field names such as:

- `entity`
- `value`
- `period`
- `series`
- `benchmark_value`

Use `column_mapping` on the request to map the CSV's real column names onto those canonical names. Do not rename the CSV on disk just to satisfy the chart API.

Common examples:

- ranking bar chart: `{"geo_name": "entity", "metric_value": "value"}`
- line chart: `{"year": "period", "metric_value": "value", "geo_name": "series"}`
- benchmark chart: include the benchmark column mapping if the result carries it

# Worked Example

Reference artifacts:

- `publisher/content/vacancy_rates/metro_rankings/chart_config.json`
- `publisher/content/vacancy_rates/metro_rankings/result.csv`

Representative Python shape:

```python
df = pd.read_csv("publisher/content/vacancy_rates/metro_rankings/result.csv")

request = ChartRequest(
    data=df,
    chart_type="bar_chart",
    theme=Theme.default(),
    column_mapping={
        "geo_name": "entity",
        "metric_value": "value",
        "rank": "rank",
        "benchmark_value": "benchmark_value",
    },
    title="The Tightest Major Metro Housing Markets in 2024",
    subtitle="Top 20 CBSAs by lowest vacancy rate | Population filter: 250k+ | US benchmark shown for reference",
    benchmark=BenchmarkConfig(kind="custom", value=10.1, label="US: 10.1%"),
    output=OutputConfig(
        save=True,
        path=Path("publisher/chart_a_day/output/metro_rankings/chart.png"),
        format="png",
    ),
    interactive=False,
)

result = render(request)
```

# Output Steps

1. Build the resolved `ChartRequest` with `Theme.default()`.
2. Set `OutputConfig(save=True, path=Path("publisher/chart_a_day/output/{{q_id}}/chart.png"), format="png")`.
3. Call `render(request)`.
4. If `ChartResult.warnings` is non-empty, print the warnings.
5. Confirm `chart.png` exists at `publisher/chart_a_day/output/{{q_id}}/`.

If `produce_alternatives` is `true`:

1. Build a second request with `fallback_chart_types[0]`.
2. Save it to `publisher/chart_a_day/output/{{q_id}}/chart_alt.png`.
3. Print which fallback chart type was used.

# Review Checklist

- The chart matches the analytical intent in `backlog_notes`.
- Ranking order or time ordering is correct.
- Labels are readable.
- A benchmark is present when the result includes one or the question implies one.
- The chosen `column_mapping` matches the axes and legend orientation you intended.
