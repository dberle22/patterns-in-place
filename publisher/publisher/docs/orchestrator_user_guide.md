# Orchestrator User Guide

This document explains how the automated Publisher backend works after the monorepo migration.

The canonical implementation now lives in:

- [chatbot/orchestrator.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/orchestrator.py)
- [chatbot/intent/parser.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/intent/parser.py)
- [chatbot/query/](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/query)
- [chatbot/charts/](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/charts)
- [chatbot/response/assembler.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/response/assembler.py)

## What The Orchestrator Is

The orchestrator is the automated question-to-artifact pipeline.

It takes a natural-language question and coordinates the steps required to produce:

- a structured query plan
- generated SQL
- validated query logic
- query results
- chart selection
- rendered chart output
- answer text

It is the core of the automated Chatbot and Publisher workflow.

## Mental Model

The orchestrator does not "think" in one monolithic step. It coordinates several smaller layers:

1. parse the question
2. normalize the analytical plan
3. generate approved SQL
4. validate the SQL semantically
5. execute the query
6. profile the result shape
7. choose a chart type
8. render the chart
9. write a short answer

The main coordinating class is [chatbot/orchestrator.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/orchestrator.py).

## High-Level Flow

```text
question
  ↓
IntentParser
  ↓
QueryPlan
  ↓
QueryPlanner
  ↓
PlannedQuery
  ↓
QueryGenerator
  ↓
RenderedQuery (SQL + metadata)
  ↓
QueryValidator
  ↓
QueryExecutor
  ↓
DataFrame result
  ↓
ResultProfiler
  ↓
ChartSelector
  ↓
ChartRenderer
  ↓
Rendered chart
  ↓
ResponseAssembler
  ↓
Answer text
```

## Main Entry Points

### Interactive or CLI question flow

Use [chatbot/scripts/ask.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/scripts/ask.py).

This script can:

- run parser-only mode
- run the full backend flow
- optionally render a chart
- optionally save artifacts

### Queue-based publishing flow

Use [publisher/run_publisher.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/publisher/run_publisher.py).

This script wraps the same backend logic in a queue-driven production workflow.

## Core Files And Responsibilities

### [chatbot/orchestrator.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/orchestrator.py)

Main responsibilities:

- instantiate the parser, planner, generator, validator, executor, profiler, selector, renderer, and assembler
- run them in sequence
- return a single `OrchestrationResult`

Important object:

- `OrchestrationResult`

This bundles the major outputs of the run:

- `parse_result`
- `query_plan`
- `planned_query`
- `rendered_query`
- `validation`
- `dataframe`
- `result_profile`
- `chart_selection`
- `rendered_chart`
- `response`

### [chatbot/intent/parser.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/intent/parser.py)

Main responsibilities:

- classify the question type
- identify metric, geography, and time fields
- decide whether clarification is needed
- optionally use example matching, heuristics, or an LLM provider

Important objects:

- `ParseResult`
- `QueryPlan`
- `ClarificationRequest`

Important decision order:

1. exact example match from [publisher/examples/question_library.yml](/Users/danberle/Documents/projects/patterns_in_place/publisher/publisher/examples/question_library.yml)
2. heuristic parse
3. LLM parse if configured
4. clarification if required slots are still missing

### [chatbot/query/catalogs.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/query/catalogs.py)

Main responsibilities:

- load the semantic layer from `FOUNDATIONS_PATH/semantic_layer/`
- load the data dictionary from `FOUNDATIONS_PATH/data_dictionary/`
- normalize current monorepo catalog schema details so the migrated backend can use them consistently

This file is where the migrated backend connects to shared `foundations/` assets.

### [chatbot/query/planner.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/query/planner.py)

Main responsibilities:

- fill deterministic defaults after parsing
- infer missing `source_table` from the metric catalog
- normalize benchmark and growth defaults

Output:

- `PlannedQuery`

### [chatbot/query/generator.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/query/generator.py)

Main responsibilities:

- convert a structured plan into executable DuckDB SQL
- choose the correct template implementation
- emit both SQL and semantic metadata

Output:

- `RenderedQuery`

Key template paths:

- `ranking`
- `trend`
- `compare_selected`
- `distribution`
- `benchmark`
- `growth`

### [chatbot/query/validator.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/query/validator.py)

Main responsibilities:

- ensure SQL is read-only
- check approved tables, joins, fields, and metrics
- verify the selected geography level is valid for the requested table and metric

Output:

- `ValidationResult`

### [chatbot/query/executor.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/query/executor.py)

Main responsibilities:

- execute validated SQL against DuckDB
- return a pandas DataFrame

This layer reads from `DB_CONNECTION` if set, otherwise from its default runtime database path.

### [chatbot/charts/profiler.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/charts/profiler.py)

Main responsibilities:

- inspect the result shape
- determine whether the output looks like a ranking, time series, distribution, or other structure

The profiler is important because chart selection depends on the actual result shape, not just the original question type.

### [chatbot/charts/selector.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/charts/selector.py)

Main responsibilities:

- read chart rules from the semantic layer
- choose the most appropriate approved chart type
- apply constraint checks such as minimum row count or time-point count

Output:

- `ChartSelection`

### [chatbot/charts/renderer.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/charts/renderer.py)

Main responsibilities:

- prepare chart-ready CSV data
- build chart config JSON
- call the shared R visual library in `foundations/visual_library/`
- save a rendered PNG in a temporary folder

Important migration detail:

- the shared `render_*.R` files are library-style render functions, not standalone CLI scripts
- the Python renderer now generates a small R wrapper script at runtime
- that wrapper loads config and data, calls the correct `render_{chart_type}` function, and saves the PNG via `ggplot2::ggsave()`

Output:

- `RenderedChart`

### [chatbot/response/assembler.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/response/assembler.py)

Main responsibilities:

- translate the analytical result into concise answer text
- tailor the summary based on question type and result shape

Output:

- `AssembledResponse`

## Detailed Step-By-Step Walkthrough

### 1. Question intake

The user asks a natural-language question.

Examples:

- "Which states have the highest median household income in 2023?"
- "How has median gross rent changed in the 10 largest metros since 2018?"
- "How does Miami compare to the national average?"

### 2. Intent parsing

Handled by [chatbot/intent/parser.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/intent/parser.py).

The parser decides:

- question type
- metric
- geography level
- target geography
- year or year range
- benchmark type
- whether clarification is needed

Possible outputs:

- successful `QueryPlan`
- `ClarificationRequest`

### 3. Plan normalization

Handled by [chatbot/query/planner.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/query/planner.py).

The planner fills in defaults such as:

- `source_table`
- `sort_direction`
- `limit`
- `target_geo_level` for benchmark questions
- `benchmark_geo_level` for benchmark questions

### 4. SQL generation

Handled by [chatbot/query/generator.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/query/generator.py).

The generator uses the semantic layer to produce template-specific SQL and semantic metadata such as:

- `tables_used`
- `fields_used`
- `joins_used`
- `metric_ids`

### 5. Validation

Handled by [chatbot/query/validator.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/query/validator.py).

If validation fails, the orchestration stops here with errors.

### 6. Query execution

Handled by [chatbot/query/executor.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/query/executor.py).

Output:

- DataFrame

### 7. Result profiling

Handled by [chatbot/charts/profiler.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/charts/profiler.py).

This inspects the shape of the result so the charting layer can make a good decision.

### 8. Chart selection

Handled by [chatbot/charts/selector.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/charts/selector.py).

The selector combines:

- question type
- profiled result shape
- approved chart rules

to choose a chart type.

### 9. Chart rendering

Handled by [chatbot/charts/renderer.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/charts/renderer.py).

Intermediate artifacts created in a temp directory:

- `chart_data.csv`
- `chart_config.json`
- `run_render.R`
- `chart_output.png`

### 10. Response assembly

Handled by [chatbot/response/assembler.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/chatbot/response/assembler.py).

This produces the short answer text shown to the user or saved into Publisher artifacts.

## Artifact Flow

### In-memory outputs from the orchestrator

- `ParseResult`
- `QueryPlan`
- `PlannedQuery`
- `RenderedQuery`
- `ValidationResult`
- query result DataFrame
- `ResultProfile`
- `ChartSelection`
- `RenderedChart`
- `AssembledResponse`

### Persisted outputs in the Publisher workflow

When the queue workflow uses the backend through [publisher/run_publisher.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/publisher/run_publisher.py), the main saved artifacts are:

- `query_plan.json`
- `result.sql`
- `result.csv`
- `chart.png`
- `answer.txt`

These are stored under [publisher/output/](/Users/danberle/Documents/projects/patterns_in_place/publisher/publisher/output).

## Relationship To The Queue Workflow

The orchestrator is the backend engine.

The queue workflow in [publisher/run_publisher.py](/Users/danberle/Documents/projects/patterns_in_place/publisher/publisher/run_publisher.py) wraps that engine in a production process:

- choose the next `ready` question
- run parse, sql, or chart steps
- persist artifacts to `publisher/output/{id}/`
- update queue status

So:

- `chatbot/` answers the question
- `publisher/` operationalizes that answer

## Required Environment

Before running the orchestrator-backed flows, set:

```bash
export FOUNDATIONS_PATH=<monorepo-root>/foundations
```

Optionally set a shared DB path:

```bash
export DB_CONNECTION=<monorepo-root>/foundations/etl/data/duckdb/patterns_in_place.duckdb
```

The orchestrator depends on:

- semantic layer catalogs in `foundations/semantic_layer/`
- data dictionary metadata in `foundations/data_dictionary/`
- chart rendering assets in `foundations/visual_library/`

## Common Commands

Run from `publisher/` with `PYTHONPATH=.`

| Task | Command |
|---|---|
| Parser-only test | `PYTHONPATH=. python chatbot/scripts/ask.py "<question>" --parser-only --json` |
| Full question flow | `PYTHONPATH=. python chatbot/scripts/ask.py "<question>" --render-chart --json` |
| Queue parse step | `PYTHONPATH=. python publisher/run_publisher.py --next --step parse` |
| Queue SQL step | `PYTHONPATH=. python publisher/run_publisher.py --id q002 --step sql` |
| Queue chart step | `PYTHONPATH=. python publisher/run_publisher.py --id q002 --step chart` |
