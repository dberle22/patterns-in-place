---
name: sql_agent
mode: prompt
version: 0.1
description: Write DuckDB SQL for a Chart-A-Day backlog question, execute it read-only, and save SQL plus CSV artifacts.
inputs:
  - q_id
  - question
  - template_id
  - geo_level
  - backlog_notes
outputs:
  - result.sql
  - result.csv
---

# Purpose

You are writing DuckDB SQL against the Gold warehouse for a Chart-A-Day backlog entry. Questions are pre-defined in `publisher/chart_a_day/backlog.yaml`; do not use the chatbot NL-to-SQL pipeline.

Inputs:

- `q_id`: `{{q_id}}`
- `question`: `{{question}}`
- `template_id`: `{{template_id}}`
- `geo_level`: `{{geo_level}}`
- `backlog_notes`: `{{backlog_notes}}`

# Data Context

- Warehouse file: `foundations/etl/data/duckdb/patterns_in_place.duckdb`
- Connect read-only.
- Semantic catalogs live in `foundations/semantic_layer/`.
- Consult `metric_catalog.yml` for metric definitions and unit clues before writing SQL.
- Consult `table_catalog.yml` for canonical table names before writing SQL.
- Stay in Gold unless `backlog_notes` explicitly requires a crosswalk or supporting Silver table.

# Working Rules

1. Match the backlog question exactly. Do not broaden the scope.
2. Prefer one query file that is easy to read over clever SQL.
3. Include provenance columns when they help downstream charting or review: `metric_label`, `benchmark_value`, `note`, `period`, `rank`, `series`, `highlight_flag`.
4. Name columns intentionally so the chart step can map them to canonical chart fields without guesswork.
5. If the needed metric or table is missing from the semantic layer, stop and say what is missing instead of guessing.

# Template Guidance

- `ranking`: one row per geography, ordered by the primary metric.
- `trend`: one row per period, optionally repeated by `series`.
- `compare_selected`: small named geography set; keep the selected entities explicit in the SQL.
- `distribution`: many peer geographies at one common grain; preserve the raw values rather than pre-aggregating them away.
- `benchmark`: include both the focal geography value and a reference value the chart step can render.
- `growth`: calculate a clearly labeled change window and return the growth metric ready for ordering.
- `correlation`: return the two comparison measures in separate numeric columns.
- `composition`: return the component rows or metric matrix required by the requested scorecard.
- `map`: keep the supported geography identifier required for joins or geometry lookups.
- `demographic`: preserve age bins and sex columns.
- `rank_change`: return the ranked entities across comparable time points.

For `geo_level: national`, expect a single aggregate row or a national time series rather than a ranked geography list. The SQL shape should change with the question.

# Worked Example

Reference pair:

- SQL: `publisher/content/vacancy_rates/metro_rankings/query.sql`
- Result: `publisher/content/vacancy_rates/metro_rankings/result.csv`

What makes it good:

- It filters to the intended geography universe before ranking.
- It carries a benchmark column (`benchmark_value`) for the later chart step.
- It emits readable metadata columns like `metric_label`, `time_window`, and `note`.
- It orders the final output in the same order the bar chart should render.

# Execution Steps

1. Read the relevant metric and table definitions from the semantic layer.
2. Write SQL to `publisher/chart_a_day/output/{{q_id}}/result.sql`.
3. Execute the query against DuckDB in read-only mode.
4. Save the result to `publisher/chart_a_day/output/{{q_id}}/result.csv`.
5. Print the row count and the output column names as a sanity check.

# Done When

- `result.sql` runs without error.
- `result.csv` exists and is non-empty unless the task is explicitly blocked by missing source data.
- The result columns are named clearly enough for the chart step to map them without editing the CSV by hand.
