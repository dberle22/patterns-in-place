# Content Workspace

This folder is the manual editorial and analytical workspace for Publisher.

It is separate from the automated Chatbot and queue workflow. The work here is deliberately manual and exploratory: we choose the angle, write the SQL by hand, decide the visual, render the chart, and write the copy ourselves.

The goal is twofold:

1. produce polished publishable content
2. act as a leading indicator for where the automated Chatbot and Publisher pipeline should improve

## Where This Fits

Inside `publisher/`, there are two different workflows:

- `chatbot/ + publisher/ + frontend/ + qa/` are the automated question-to-artifact system
- `content/` is the manual editorial workflow

That distinction matters:

- the Chatbot path decides much of the analysis flow automatically
- the Content path expects a human or agent to make the core analytical and editorial decisions

Do not treat this folder as "just another frontend for the Chatbot." It is its own workflow by design.

## What This Folder Is

A topic-based content system. Each topic folder contains multiple insights, and each insight produces one publishable output or post concept.

Typical use cases:

- build a short series around one theme such as vacancy rates or affordability
- test a new story angle before trying to automate it
- develop a more nuanced version of an analysis than the current Chatbot path can produce

## Folder Structure

```text
content/
├── README.md                        ← this file
├── daily_data_publisher_spec.md     ← product spec: workflow, artifact contract, scope, future automation
├── publisher_backlog.md             ← cross-topic post tracker and question bank
└── {topic}/
    ├── README.md                    ← topic overview: story, key numbers, planned insights, publish order
    ├── TASKS.md                     ← checklist tracking progress across the topic
    └── {insight}/
        ├── question.md              ← editorial brief written before EDA
        ├── findings.md              ← confirmed angle, key numbers, surprises
        ├── query.sql                ← hand-written, chart-ready SQL
        ├── result.csv               ← query output
        ├── chart_config.json        ← render config: title, subtitle, dimensions, formatting
        ├── chart.png                ← rendered chart
        ├── summary.md               ← 2–3 sentence data-first interpretation
        └── post_draft.md            ← X post, thread, caption, or related draft copy
```

## Workflow Per Insight

```text
1. QUESTION   — write question.md before touching the data
2. EDA        — explore the data and test the hypothesis
3. FINDINGS   — write findings.md: key numbers, confirmed angle, surprises
4. SQL        — write query.sql to match the intended chart contract
5. EXECUTE    — run SQL and save result.csv
6. CONFIG     — write chart_config.json
7. RENDER     — call the shared R visual library and save chart.png
8. SUMMARY    — write summary.md
9. SOCIAL     — write post_draft.md
```

`question.md` should always come first. It captures the editorial hypothesis so you can compare what you expected to what the data actually showed in `findings.md`.

## Active Topics

| Topic | Folder | Insights Planned | Status |
|---|---|---:|---|
| Vacancy Rates | `vacancy_rates/` | 4 | In progress |

## Data

This workflow uses the shared monorepo data platform in `foundations/`.

- **Canonical warehouse location:** `foundations/etl/data/duckdb/patterns_in_place.duckdb`
- **Schema prefix:** `gold.` such as `gold.housing_core_wide`, `gold.population_demographics`, and `gold.economics_income_wide`
- **Common tables:** `housing_core_wide`, `population_demographics`, `economics_income_wide`
- **Geo levels available:** `us`, `region`, `division`, `state`, `cbsa`, `county`, `tract`, `zcta`, `place`
- **Years:** generally 2012–2024, depending on table and metric coverage

Recommended connection pattern:

```python
import duckdb

con = duckdb.connect("foundations/etl/data/duckdb/patterns_in_place.duckdb", read_only=True)
```

If you prefer environment-based configuration, align it with the rest of Publisher:

- `FOUNDATIONS_PATH=<monorepo-root>/foundations`
- `DB_CONNECTION=<monorepo-root>/foundations/etl/data/duckdb/patterns_in_place.duckdb`

## Shared Assets

This folder uses shared assets from `foundations/`, not local copies:

- semantic layer: `foundations/semantic_layer/`
- visual library: `foundations/visual_library/`
- warehouse: `foundations/etl/data/duckdb/patterns_in_place.duckdb`

If you need to update semantic catalogs or render scripts, edit them in `foundations/`, not in `content/`.

## Chart Rendering

Charts are rendered through the shared R visual library in `foundations/visual_library/`.

One important post-migration detail:

- the `render_*.R` files in `foundations/visual_library/shared/render/` are library-style render functions
- they are not standalone CLI entrypoints on their own

That means the manual Content workflow should use a small R wrapper script or interactive R session that:

1. sources the relevant `render_{chart_type}.R`
2. reads `chart_config.json`
3. reads `result.csv`
4. calls `render_{chart_type}(data, config = config)`
5. saves `chart.png` with `ggplot2::ggsave()`

Conceptually the flow is:

```text
question.md
   ↓
findings.md
   ↓
query.sql ──(run against DuckDB)──> result.csv
                                      │
chart_config.json ────────────────────┤
                                      ↓
R wrapper script / R session
  ├─ source foundations/visual_library/shared/render/render_{chart_type}.R
  ├─ load chart_config.json
  ├─ load result.csv
  ├─ call render_{chart_type}(data, config)
  └─ save chart.png
```

Available chart types include:

- `bar`
- `line`
- `scatter`
- `choropleth`
- `slopegraph`
- `bump_chart`
- `heatmap_table`
- `boxplot`
- `bivariate_choropleth`

and others defined under `foundations/visual_library/`.

Each chart type has a required data contract. The SQL must output the fields expected by the selected chart type. The render scripts are for rendering, not reshaping the analysis.

## Relationship To The Automated Flow

This workflow should not use the automated Chatbot path as its main execution model.

In practice:

- do not route this work through `chatbot/orchestrator.py`
- do not rely on `publisher/run_publisher.py` for topic development
- do use the same shared data and visual standards
- do use insights from this folder as signal for future pipeline improvements

The manual workflow is where you decide:

- what the real story is
- what SQL best answers it
- which chart is best
- how the interpretation should be written

## For Agents

When helping inside this folder:

- read the topic `README.md` first
- read `TASKS.md` to see what is done and what is next
- read `question.md` before proposing SQL or chart direction
- keep the workflow manual unless explicitly asked to automate part of it
- write SQL directly against `gold.*` tables in the shared warehouse
- check the relevant chart contract in `foundations/visual_library/` before writing chart-ready SQL
- do not reuse the automated Chatbot pipeline unless the task specifically asks for comparison or migration work

## Rule Of Thumb

Use `content/` when the question is:

- "What story should we tell?"
- "What is the best angle here?"
- "What is the right hand-built chart and interpretation?"

Use the automated Chatbot and Publisher flow when the question is:

- "Can the system answer this repeatably?"
- "Can we queue this and generate standard artifacts?"
- "Can we operationalize this into a reusable pipeline?"
