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
  - chart_py.png
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
- Prefer `.venv312` for manual runs because that environment is where `chart_engine`, export dependencies, and `vl-convert` have been validated together.

# Environment Guardrails

Before rendering, make the execution environment explicit instead of assuming the shell is already correct.

- Use `.venv312` or another environment that definitely has the editable `chart_engine_py` install plus its image export dependencies.
- For Matplotlib-backed geo renders, set `MPLBACKEND=Agg`.
- For Matplotlib-backed geo renders, set a writable `MPLCONFIGDIR` such as `/tmp/mpl_cache_q024` so static export does not fail on cache writes.
- If the local machine does not have `Inter`, override the theme font family to a safe installed fallback such as `Arial` for the manual run.
- Keep these environment choices in the render snippet or shell command so the run is reproducible from `step_notes.md`.

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
- choropleth: include `{"geometry": "geometry"}` after parsing a serialized geometry payload into an in-memory geometry column

For dense multi-series trend charts, readability matters as much as correctness:

- If full CBSA names make the Python legend or direct labels unreadable, create concise display labels in-memory before rendering.
- Treat this as presentation polish, not a data transformation: keep the same series membership and ordering, just shorten the shown label text.
- If the fallback `slopegraph` becomes more crowded than the primary `line_chart`, keep `chart_alt.png` as comparison evidence rather than forcing it to be the preferred artifact.

# Worked Example

Reference artifacts:

- `publisher/content/vacancy_rates/metro_rankings/chart_config.json`
- `publisher/content/vacancy_rates/metro_rankings/result.csv`

Representative Python shape:

```python
df = pd.read_csv("publisher/content/vacancy_rates/metro_rankings/result.csv")

theme = Theme.default()
theme.fonts["family"] = "Arial"

request = ChartRequest(
    data=df,
    chart_type="bar_chart",
    theme=theme,
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
        path=Path("publisher/chart_a_day/output/metro_rankings/chart_py.png"),
        format="png",
    ),
    interactive=False,
)

result = render(request)
```

# Result-Set Contract Checks

Before building the request, inspect the CSV and make the measurement semantics explicit.

- If the question is a percent or share, determine whether `metric_value` is stored as a fraction (`0.587`) or percentage points (`58.7`).
- Match the `NumberFormat` choice to the stored values. Do not pass percentage-point values into a formatter that expects fractions unless you deliberately convert them first.
- If the result includes `benchmark_value`, add the matching benchmark config or other benchmark instructions instead of leaving the reference unlabeled.
- When the run is part of R-vs-Python parity review, preserve metadata fields such as `source`, `vintage`, `metric_label`, `time_window`, and `note` if the R reference stack needs them.
- For geo questions, prefer carrying both an R-friendly geometry field such as `geom_wkt` and a Python-friendly serialized geometry field that you can parse into `geometry`.

# Output Steps

1. Activate `.venv312` or confirm the chosen environment has `chart_engine` and export dependencies.
2. For geo renders, set `MPLBACKEND=Agg` and a writable `MPLCONFIGDIR` before launching Python.
3. Build the resolved `ChartRequest` with `Theme.default()`, then override the font family locally if the machine does not have `Inter`.
4. Set `OutputConfig(save=True, path=Path("publisher/chart_a_day/output/{{q_id}}/chart_py.png"), format="png")`.
5. If the CSV stores percentage-point values, either convert them before render or avoid a percent formatter that assumes fractions.
6. For geo renders, parse the serialized geometry payload into a `geometry` column before constructing the request.
7. If the result carries a benchmark, add the benchmark config or equivalent chart instructions deliberately.
8. Call `render(request)`.
9. If `ChartResult.warnings` is non-empty, print the warnings.
10. Confirm `chart_py.png` exists at `publisher/chart_a_day/output/{{q_id}}/`.
11. For multi-series trend charts with long metro names, consider a concise display-label pass and a slightly wider canvas before accepting the first export.

If `produce_alternatives` is `true`:

1. Build a second request with `fallback_chart_types[0]`.
2. Save it to `publisher/chart_a_day/output/{{q_id}}/chart_alt.png`.
3. Print which fallback chart type was used.
4. If the fallback is clearly less readable than `chart_py.png`, keep it for review context but do not treat it as the preferred publishable artifact by default.

# Geo Render Pattern

Use this pattern when the SQL exports serialized geometry for the Python path.

```python
import json

df = pd.read_csv("publisher/chart_a_day/output/q024/result.csv")
df["geometry"] = df["geometry_json"].apply(json.loads)

theme = Theme.default()
theme.fonts["family"] = "Arial"

request = ChartRequest(
    data=df,
    chart_type="choropleth",
    theme=theme,
    column_mapping={
        "geometry": "geometry",
    },
    output=OutputConfig(
        save=True,
        path=Path("publisher/chart_a_day/output/q024/chart_py.png"),
        format="png",
    ),
    interactive=False,
)
```

# Review Checklist

- The chart matches the analytical intent in `backlog_notes`.
- Ranking order or time ordering is correct.
- Labels are readable.
- A benchmark is present when the result includes one or the question implies one.
- The chosen `column_mapping` matches the axes and legend orientation you intended.
- The Python artifact is saved as `chart_py.png`, not `chart.png`.
- For parity runs, compare subtitle text, note text, benchmark labeling, and overall readability directly against `chart_r.png`.
- For percent/share questions, the rendered labels reflect the underlying storage semantics correctly.
- For geo renders, verify the map actually used the parsed Python geometry field and did not silently drop shapes.
- For dense trend charts, check whether display labels need shortening before concluding the Python renderer itself is the problem.
