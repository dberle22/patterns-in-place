# Publisher

`publisher/` is one product area with two different workflows inside it:

- the automated Chatbot-to-publishing workflow
- the manual editorial Content workflow

Those two workflows share the same upstream assets in `foundations/`, but they do not work the same way.

## Mental Model

The cleanest way to think about this folder is:

- `chatbot/` is the analysis engine
- `publisher/` is the production wrapper around that engine
- `frontend/` is the review and interaction layer
- `qa/` is the validation layer
- `content/` is a separate manual editorial workflow

So:

- `chatbot/ + publisher/ + frontend/ + qa/` form one system
- `content/` is intentionally separate and higher-touch

Another useful shorthand:

- If the question is "How does the system think?" go to `chatbot/`
- If the question is "How do we queue, save, and package outputs?" go to `publisher/`
- If the question is "How do humans develop a story manually?" go to `content/`

## Folder Overview

### `chatbot/`

The NL-to-SQL backend shared by the Insights Generator and the future public chatbot.

Main responsibilities:

- parse natural-language questions
- map them to approved metrics, geographies, and query templates
- generate and validate SQL
- execute queries against DuckDB
- select a chart type
- render charts through the shared R visual library
- assemble concise answer text

Important files:

- [chatbot/orchestrator.py](publisher/chatbot/orchestrator.py)
- [chatbot/intent/parser.py](publisher/chatbot/intent/parser.py)
- [chatbot/query/catalogs.py](publisher/chatbot/query/catalogs.py)
- [chatbot/query/planner.py](publisher/chatbot/query/planner.py)
- [chatbot/query/generator.py](publisher/chatbot/query/generator.py)
- [chatbot/query/validator.py](publisher/chatbot/query/validator.py)
- [chatbot/query/executor.py](publisher/chatbot/query/executor.py)
- [chatbot/charts/selector.py](publisher/chatbot/charts/selector.py)
- [chatbot/charts/renderer.py](publisher/chatbot/charts/renderer.py)
- [chatbot/response/assembler.py](publisher/chatbot/response/assembler.py)
- [chatbot/scripts/ask.py](publisher/chatbot/scripts/ask.py)

### `publisher/`

The queue-based production wrapper around the Chatbot engine.

Main responsibilities:

- hold the content question queue
- pick the next ready question
- run parse / sql / chart steps
- save artifacts to a consistent folder structure
- track question status as work moves through the pipeline

Important files:

- [publisher/run_publisher.py](publisher/publisher/run_publisher.py)
- [publisher/queue_manager.py](publisher/publisher/queue_manager.py)
- [publisher/packager.py](publisher/publisher/packager.py)
- [publisher/summarizer.py](publisher/publisher/summarizer.py)
- [publisher/question_queue.yaml](publisher/publisher/question_queue.yaml)
- [publisher/examples/question_library.yml](publisher/publisher/examples/question_library.yml)
- [publisher/output/](publisher/publisher/output)

### `frontend/`

The Streamlit review and inspection layer for saved artifacts.

Main responsibilities:

- let you inspect saved runs
- preview saved SQL, query plans, CSV outputs, and chart PNGs
- support QA and review without digging through folders manually

Important files:

- [frontend/streamlit_app.py](publisher/frontend/streamlit_app.py)
- [frontend/qa_utils.py](publisher/frontend/qa_utils.py)
- [frontend/qa_review.py](publisher/frontend/qa_review.py)

### `qa/`

The testing and evaluation layer for the Chatbot and Publisher workflow.

Main responsibilities:

- define QA cases
- track tuning and quality issues
- support repeatable evaluation runs

Important files:

- [qa/qa_prompt_library.yml](publisher/qa/qa_prompt_library.yml)
- [qa/QA_FRAMEWORK.md](publisher/qa/QA_FRAMEWORK.md)
- [qa/QA_TUNING_LOG.md](publisher/qa/QA_TUNING_LOG.md)
- [qa/testing_strategy.md](publisher/qa/testing_strategy.md)

### `content/`

The manual editorial workspace.

This is not the same as the Chatbot flow. It is deliberately manual and exploratory.

Main responsibilities:

- define topic areas
- develop story angles
- run hand-written SQL
- render charts manually
- draft summaries and social copy

Important files:

- [content/README.md](publisher/content/README.md)
- topic folders such as [content/vacancy_rates/](publisher/content/vacancy_rates)

## How The System Fits Together

The automated flow is:

1. `chatbot/` answers a question
2. `publisher/` turns that answer into tracked artifacts
3. `frontend/` lets you review those artifacts
4. `qa/` helps validate the system over time

The manual flow is:

1. `content/` defines a topic and editorial question
2. analysis is done manually
3. SQL, chart config, chart, summary, and post draft are created by hand

The key distinction is:

- the Chatbot flow decides most of the analysis steps automatically
- the Content flow expects a human to make most of the analytical and editorial decisions

## Product Flow 1: Question Into The Chatbot

This is the automated question-answering flow.

### Entry points

- CLI: [chatbot/scripts/ask.py](publisher/chatbot/scripts/ask.py)
- Programmatic pipeline: [chatbot/orchestrator.py](publisher/chatbot/orchestrator.py)

### Step-by-step

1. A question comes in.
   Example: "Which states have the highest median household income in 2023?"

2. The parser decides what kind of question it is.
   File: [chatbot/intent/parser.py](publisher/chatbot/intent/parser.py)

   Decisions made:

   - Is this `ranking`, `trend`, `comparison`, `distribution`, `benchmark`, or `growth`?
   - Which metric does it map to?
   - Which geography level is implied?
   - Which year or date range is implied?
   - Does the user need to clarify anything?

3. The parser chooses how to produce the plan.
   File: [chatbot/intent/parser.py](publisher/chatbot/intent/parser.py)

   Order of operations:

   - exact example match against [publisher/examples/question_library.yml](publisher/publisher/examples/question_library.yml)
   - heuristic parsing
   - LLM parsing if a provider is available
   - clarification request if required fields are still missing

4. Semantic catalogs are loaded.
   File: [chatbot/query/catalogs.py](publisher/chatbot/query/catalogs.py)

   Inputs:

   - `FOUNDATIONS_PATH/semantic_layer/`
   - `FOUNDATIONS_PATH/data_dictionary/`

   Output:

   - approved tables, metrics, joins, templates, and geography definitions

5. The plan is normalized and defaults are filled in.
   File: [chatbot/query/planner.py](publisher/chatbot/query/planner.py)

   Decisions made:

   - default `source_table`
   - default `sort_direction`
   - default `limit`
   - benchmark defaults
   - growth defaults

6. SQL is generated from the approved query template.
   File: [chatbot/query/generator.py](publisher/chatbot/query/generator.py)

   Decisions made:

   - which SQL template to use
   - which table to query
   - which metric column to select
   - which filters and ordering to apply

   Main template paths:

   - ranking
   - trend
   - compare_selected
   - distribution
   - benchmark
   - growth

7. SQL is validated.
   File: [chatbot/query/validator.py](publisher/chatbot/query/validator.py)

   Checks include:

   - read-only SQL only
   - approved tables only
   - approved joins only
   - approved fields only
   - valid metrics and geo levels

8. SQL is executed against DuckDB.
   File: [chatbot/query/executor.py](publisher/chatbot/query/executor.py)

   Output:

   - pandas DataFrame

9. The result is profiled.
   File: [chatbot/charts/profiler.py](publisher/chatbot/charts/profiler.py)

   Decisions made:

   - row count
   - number of measures
   - whether this is time series
   - whether the shape supports certain chart types

10. A chart type is selected.
    File: [chatbot/charts/selector.py](publisher/chatbot/charts/selector.py)

    Inputs:

    - question type
    - result profile
    - `foundations/semantic_layer/chart_rules.yml`

    Output:

    - selected chart type and fallback logic

11. The chart is rendered.
    File: [chatbot/charts/renderer.py](publisher/chatbot/charts/renderer.py)

    Steps:

    - write temp chart CSV
    - write temp chart config JSON
    - call the shared R visual library in `foundations/visual_library/`
    - save a temp PNG

12. The answer text is assembled.
    File: [chatbot/response/assembler.py](publisher/chatbot/response/assembler.py)

    Decisions made:

    - how to summarize a ranking
    - how to summarize a benchmark
    - how to summarize a trend
    - which metric label and values to emphasize

### Main runtime outputs

- `ParseResult`
- `QueryPlan`
- SQL string
- query result DataFrame
- chart selection
- rendered chart path
- answer text

### Saved artifacts when persisted

If the run is saved through `ask.py` or `publisher/run_publisher.py`, the artifact set looks like:

- `query_plan.json`
- `result.sql`
- `result.csv`
- `chart.png`
- `answer.txt`

These typically live under [publisher/output/](publisher/publisher/output).

## Product Flow 2: Area Of Analysis For The Content Workflow

This is the manual editorial flow. It does not go through `chatbot/orchestrator.py`.

### Entry point

- [content/README.md](publisher/content/README.md)

### Step-by-step

1. Choose a topic area.
   Example: vacancy rates, affordability, migration.

2. Work inside a topic folder.
   Example: [content/vacancy_rates/](publisher/content/vacancy_rates)

   Typical control files:

   - `README.md`
   - `TASKS.md`

3. Define the editorial question before analysis.
   Artifact:

   - `question.md`

   This is a human decision point. You decide:

   - what the angle is
   - what would make it publishable
   - what geography or metric is likely interesting

4. Do exploratory analysis manually.
   This is not automated through the Chatbot.

5. Record confirmed findings.
   Artifact:

   - `findings.md`

6. Write the SQL by hand.
   Artifact:

   - `query.sql`

   This is the biggest difference from the Chatbot flow.
   The human chooses:

   - exact table
   - exact filters
   - exact geography scope
   - exact output shape for the target chart

7. Execute the SQL.
   Artifact:

   - `result.csv`

8. Decide chart type and chart config manually.
   Artifact:

   - `chart_config.json`

9. Render the chart.
   Artifact:

   - `chart.png`

   This still uses the shared R visual library, but manually rather than through the automated Chatbot rendering flow.

10. Write the summary and social copy.
    Artifacts:

    - `summary.md`
    - `post_draft.md`

### Main content artifacts

Per insight, the expected artifact set is:

- `question.md`
- `findings.md`
- `query.sql`
- `result.csv`
- `chart_config.json`
- `chart.png`
- `summary.md`
- `post_draft.md`

## Where `publisher/` Adds Value

The inner `publisher/` folder is not the same thing as `content/`.

Its value is that it gives the Chatbot path an operational wrapper:

- a queue of publishable questions
- saved artifacts in a standard structure
- stepwise execution
- status tracking
- repeatable packaging and review

So:

- `chatbot/` answers a question
- `publisher/` operationalizes that answer into a managed workflow
- `content/` is where humans do more nuanced editorial development outside the automated path

`publisher/` would only be redundant if you decided that either:

- interactive Chatbot Q&A is enough on its own
- or fully manual editorial work is enough on its own

As long as you want a repeatable bridge between those two extremes, it still has a clear role.

## Required Environment

Set `FOUNDATIONS_PATH` to the monorepo `foundations/` folder before running the Chatbot or Publisher workflow.

```bash
export FOUNDATIONS_PATH=<monorepo-root>/foundations
```

The backend reads the semantic layer, data dictionary, and R chart render scripts from that shared folder at import time.

## Common Commands

Run from `publisher/` with `PYTHONPATH=.`

| Task | Command |
|---|---|
| Ask one question through the Chatbot | `PYTHONPATH=. python chatbot/scripts/ask.py "<question>"` |
| Run the next Publisher queue step | `PYTHONPATH=. python publisher/run_publisher.py --next --step parse` |
| Boot the review frontend | `PYTHONPATH=. streamlit run frontend/streamlit_app.py` |

## Ownership Boundaries

- Edit semantic catalogs in `foundations/semantic_layer/`, not here.
- Edit chart render scripts in `foundations/visual_library/shared/render/`, not here.
- Treat `content/` as a manual workflow unless the publishing model changes intentionally.
