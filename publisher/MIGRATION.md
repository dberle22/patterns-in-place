# Publisher Migration Plan

Migration of `metro_deep_dive_chatbot` into `publisher/` within the `patterns-in-place` monorepo.

**Source repo:** `<local-projects-root>/metro_deep_dive_chatbot`
**Destination:** `<monorepo-root>/publisher/`
**Rule:** Copy files in; do not modify or delete the source repo until all verification gates pass.

---

## What this folder is

`publisher/` is the home of four distinct but tightly coupled components:

| Component | Folder | What it does |
|---|---|---|
| **Chatbot backend** | `chatbot/` | NL-to-SQL engine: intent parsing → LLM → SQL generation → chart rendering → response assembly. The shared brain behind both the Insights Generator and the public Chatbot. |
| **Publisher batch runner** | `publisher/` | CLI workflow that manages `question_queue.yaml`, runs questions step-by-step through the engine, packages output artifacts (SQL + CSV + chart + post draft), and tracks publish status. Includes `examples/` — question library and sample SQL. |
| **Chatbot frontend** | `frontend/` | Streamlit UI for interactive Q&A and reviewing saved run artifacts. Not yet publicly deployed. |
| **Content workspace** | `content/` | Manual, topic-driven content production. Hand-written SQL, direct R calls, and post drafts organized by topic series (e.g. vacancy rates). The entry point and output of the publisher — explicitly does not use the `chatbot/` pipeline. |

### Why `examples/` lives inside `publisher/` and not at the root

`examples/` contains the question library (`question_library.yml`) and sample SQL showing what the publisher pipeline produces — it is publisher-specific content, not shared across all components. The chatbot's equivalent reference lives in `foundations/semantic_layer/query_templates.yml`, which encodes the canonical question→SQL patterns per template type. There is no separate chatbot examples folder.

### Why `content/` is not inside `publisher/`

`content/` is the editorial workspace where topic series are built by hand: you write the question brief, explore the data, hand-craft the SQL, call R directly, and produce the post. The source repo README explicitly says "do not use the chatbot pipeline here — this is a manual workflow by design." It is the *entry point* of the publishing workflow (question briefs are written here before entering the queue) and the *output* (post drafts and rendered charts live here). It sits alongside the publisher machinery, not inside it.

---

## What does NOT go in `publisher/` — already in `foundations/`

This migration is different from stoop. Two major assets from the source repo are already in `foundations/` and must **not** be copied into `publisher/`:

| Asset | Source location | Already in |
|---|---|---|
| Semantic layer YAML catalogs | `metro_deep_dive_chatbot/semantic_layer/` | `foundations/semantic_layer/` |
| Visual library | `metro_deep_dive_chatbot/visual_library/` | `foundations/visual_library/` |
| ETL pipeline | `metro_deep_dive_chatbot/etl/` | `foundations/etl/` (pending migration) |
| Data dictionary | `metro_deep_dive_chatbot/data_dictionary/` | `foundations/data_dictionary/` |

Because the app code points at `semantic_layer/` and `visual_library/` relative to its repo root, **two source files need path fixes on day one** — the app will not run without them. See Phase 2.

---

## Target folder structure

```
publisher/
├── chatbot/                   ← was app/ in source repo
│   ├── charts/
│   │   ├── profiler.py
│   │   ├── renderer.py        ← requires path fix (visual_library reference)
│   │   └── selector.py
│   ├── intent/
│   │   ├── parser.py
│   │   └── prompts/
│   ├── llm/
│   │   └── provider.py
│   ├── query/
│   │   ├── catalogs.py        ← requires path fix (semantic_layer reference)
│   │   ├── executor.py
│   │   ├── generator.py
│   │   ├── planner.py
│   │   └── validator.py
│   ├── response/
│   │   └── assembler.py
│   ├── scripts/
│   │   ├── ask.py
│   │   ├── create_benchmark_view.py
│   │   ├── create_runtime_duckdb.py
│   │   └── qa_batch.py
│   ├── main.py
│   └── orchestrator.py
├── publisher/
│   ├── skills/
│   ├── docs/
│   │   └── orchestrator_user_guide.md
│   ├── examples/              ← moved from root; publisher-specific question bank + sample SQL
│   │   ├── question_library.yml
│   │   └── sample_sql/
│   ├── output/
│   │   └── q001/              ← committed reference artifact
│   │       ├── answer.txt
│   │       ├── chart.png
│   │       ├── query_plan.json
│   │       ├── result.csv
│   │       ├── result.sql
│   │       └── step_notes.md
│   ├── packager.py
│   ├── queue_manager.py
│   ├── run_publisher.py
│   ├── summarizer.py
│   └── question_queue.yaml
├── frontend/
│   ├── streamlit_app.py
│   ├── qa_review.py
│   └── qa_utils.py
├── qa/
│   ├── QA_FRAMEWORK.md
│   ├── QA_TUNING_LOG.md
│   ├── qa_prompt_library.yml
│   └── testing_strategy.md
├── content/                   ← was analysis/ in source repo
│   ├── vacancy_rates/
│   └── README.md
├── requirements.txt
├── CLAUDE.md
├── AGENTS.md
└── MIGRATION.md               ← this file
```

---

## Phase 0 — Pre-migration checklist

- [ ] `metro_deep_dive_chatbot/app/orchestrator.py` runs a question end-to-end in the source repo without errors
- [x] `foundations/semantic_layer/` contains all YAML catalogs referenced by `app/query/catalogs.py` (`table_catalog.yml`, `metric_catalog.yml`, `join_catalog.yml`, `geography_catalog.yml`, `chart_rules.yml`, `query_templates.yml`)
- [x] `foundations/visual_library/shared/render/` exists and contains the R render scripts
- [x] You know the local absolute path to the `foundations/` folder — you will set this as `FOUNDATIONS_PATH` in your environment

Verify the foundations semantic layer has all required files:

```bash
ls <monorepo-root>/foundations/semantic_layer/
# Expected: table_catalog.yml, metric_catalog.yml, join_catalog.yml,
#           geography_catalog.yml, chart_rules.yml, query_templates.yml

ls <monorepo-root>/foundations/visual_library/shared/render/
# Expected: R render scripts (render_bar.R, render_line.R, etc.)
```

---

## Phase 1 — File copy

### 1.1 Automated copy

Run from `<monorepo-root>`:

```bash
SRC=<local-projects-root>/metro_deep_dive_chatbot
DEST=<monorepo-root>/publisher

# Chatbot backend (was app/ in source repo)
cp -r $SRC/app/charts/     $DEST/chatbot/charts/
cp -r $SRC/app/intent/     $DEST/chatbot/intent/
cp -r $SRC/app/llm/        $DEST/chatbot/llm/
cp -r $SRC/app/query/      $DEST/chatbot/query/
cp -r $SRC/app/response/   $DEST/chatbot/response/
cp -r $SRC/app/scripts/    $DEST/chatbot/scripts/
cp    $SRC/app/main.py         $DEST/chatbot/
cp    $SRC/app/orchestrator.py $DEST/chatbot/

# Publisher batch runner
cp -r $SRC/publisher/skills/       $DEST/publisher/skills/
cp -r $SRC/publisher/docs/         $DEST/publisher/docs/
cp    $SRC/publisher/packager.py      $DEST/publisher/
cp    $SRC/publisher/queue_manager.py $DEST/publisher/
cp    $SRC/publisher/run_publisher.py $DEST/publisher/
cp    $SRC/publisher/summarizer.py    $DEST/publisher/
cp    $SRC/publisher/question_queue.yaml $DEST/publisher/

# Publisher output — q001 committed as reference; future outputs gitignored
cp -r $SRC/publisher/output/q001/  $DEST/publisher/output/q001/

# Examples — publisher-specific; moved into publisher/
cp -r $SRC/examples/  $DEST/publisher/examples/

# Chatbot frontend
cp $SRC/frontend/streamlit_app.py  $DEST/frontend/
cp $SRC/frontend/qa_review.py      $DEST/frontend/
cp $SRC/frontend/qa_utils.py       $DEST/frontend/

# QA framework
cp $SRC/qa/QA_FRAMEWORK.md        $DEST/qa/
cp $SRC/qa/QA_TUNING_LOG.md       $DEST/qa/
cp $SRC/qa/qa_prompt_library.yml   $DEST/qa/
cp $SRC/qa/testing_strategy.md    $DEST/qa/

# Content workspace (was analysis/ in source repo)
cp -r $SRC/analysis/  $DEST/content/

# Requirements
cp $SRC/requirements.txt $DEST/
```

### 1.2 Leave behind (do not copy)

| File / folder | Reason |
|---|---|
| `semantic_layer/` | Already in `foundations/semantic_layer/` — canonical home |
| `visual_library/` | Already in `foundations/visual_library/` — canonical home |
| `etl/` | Lives in `foundations/etl/` |
| `data_dictionary/` | Lives in `foundations/data_dictionary/` |
| `chatbot/` | Old spec scaffold and planning doc — not live code |
| `runs/` | Local run artifacts — gitignored, generated by the pipeline |
| `data/` | Local DuckDB and data files — gitignored |
| `reference_dashboard/` | Stale |
| `BUILD_PLAN.md`, `DASHBOARD_BACKLOG.md`, `DASHBOARD_SPEC.md` | Stale planning docs |
| `PROJECT_CONTEXT.md`, `USER_GUIDE.md` | Replaced by monorepo docs |
| `Rplots.pdf` | Generated artifact |
| `model_test.md` | Scratch notes |

---

## Phase 2 — Required code changes

These are not optional cleanup — the app will not run without them.

### 2.1 Fix `chatbot/query/catalogs.py` — semantic layer path

**Current code:**
```python
REPO_ROOT = Path(__file__).resolve().parents[2]
SEMANTIC_DIR = REPO_ROOT / "semantic_layer"
DATA_DICTIONARY_GOLD_DIR = REPO_ROOT / "data_dictionary" / "layers" / "gold"
```

`REPO_ROOT` resolves to `publisher/` in the new location. `semantic_layer/` no longer lives there — it's in `foundations/`.

**New code:**
```python
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# foundations/ is a sibling of publisher/ in the monorepo.
# Set FOUNDATIONS_PATH env var to the absolute path of foundations/.
# Example: export FOUNDATIONS_PATH=/path/to/patterns-in-place/foundations
_foundations = Path(os.environ["FOUNDATIONS_PATH"])

SEMANTIC_DIR = _foundations / "semantic_layer"
DATA_DICTIONARY_GOLD_DIR = _foundations / "data_dictionary" / "layers" / "gold"
```

### 2.2 Fix `chatbot/charts/renderer.py` — visual library path

**Current code:**
```python
from app.query.catalogs import REPO_ROOT, load_semantic_catalogs

RENDER_SCRIPT_DIR = REPO_ROOT / "visual_library" / "shared" / "render"
```

**New code:**
```python
import os
from pathlib import Path
from chatbot.query.catalogs import load_semantic_catalogs

_foundations = Path(os.environ["FOUNDATIONS_PATH"])
RENDER_SCRIPT_DIR = _foundations / "visual_library" / "shared" / "render"
```

Note: the import also changes from `app.query.catalogs` to `chatbot.query.catalogs` to reflect the renamed folder.

### 2.3 Update all internal `app.` imports to `chatbot.`

Because `app/` is renamed to `chatbot/`, every `from app.` or `import app.` reference inside the copied files must be updated. Find them all:

```bash
grep -r "from app\." <monorepo-root>/publisher/chatbot/
grep -r "import app\." <monorepo-root>/publisher/chatbot/
grep -r "from app\." <monorepo-root>/publisher/publisher/
grep -r "from app\." <monorepo-root>/publisher/frontend/
```

Replace `from app.` → `from chatbot.` and `import app.` → `import chatbot.` across all results. The `orchestrator.py` imports are the main ones; `run_publisher.py` and the frontend may also reference `app.*`.

### 2.4 Set the `FOUNDATIONS_PATH` env var

Add to your shell profile (`.zshrc` or `.zprofile`):

```bash
export FOUNDATIONS_PATH="<absolute-path-to-monorepo>/foundations"
```

Or pass it inline when running:

```bash
FOUNDATIONS_PATH=<monorepo-root>/foundations python -m chatbot.scripts.ask "Which metros have the highest rent?"
FOUNDATIONS_PATH=<monorepo-root>/foundations python publisher/run_publisher.py --next
```

Document the required env var in `publisher/README.md` (to be written after migration).

### 2.5 Verify no remaining references to old paths

```bash
grep -r "REPO_ROOT / \"semantic_layer\"" <monorepo-root>/publisher/
grep -r "REPO_ROOT / \"visual_library\"" <monorepo-root>/publisher/
grep -r "REPO_ROOT / \"data_dictionary\"" <monorepo-root>/publisher/
grep -r "from app\." <monorepo-root>/publisher/
```

All should return zero results. If any remain, apply the `FOUNDATIONS_PATH` pattern (for path references) or the `chatbot.` rename (for import references).

Status: complete. The migration also needed two follow-up fixes discovered during verification:

- `chatbot/query/catalogs.py` now normalizes the current `foundations/semantic_layer/` schema (`subject_areas`, `non_standard_joins`) instead of assuming the older standalone repo field names.
- `chatbot/charts/renderer.py` now uses a generated R wrapper to call the shared render functions in `foundations/visual_library/`, because those files are library-style `render_*` functions rather than standalone CLI scripts.

---

## Phase 3 — `.gitignore` updates

Add to `<monorepo-root>/.gitignore`:

```
publisher/publisher/output/q002/
publisher/publisher/output/q003/
# ... or use a glob:
publisher/publisher/output/q[0-9][0-9][0-9]/
# then explicitly un-ignore q001:
!publisher/publisher/output/q001/
```

Alternatively, add a `publisher/publisher/output/.gitignore`:

```
# Ignore all question output folders except q001 (committed reference)
*
!q001/
!q001/**
!.gitignore
```

Also add `publisher/content/` generated artifacts (CSV outputs, rendered PNGs) to `.gitignore` if they become large. The `content/` folder structure and markdown files (question briefs, findings, post drafts) should be committed; raw data outputs and charts are optional based on size.

- [x] Output folders other than `q001` are ignored via `.gitignore`
- [x] `publisher/content/` chart and result artifacts are ignored via `.gitignore`

---

## Phase 4 — Verification gate

### 4.1 Engine smoke test

Run a question end-to-end through the engine from `publisher/`:

```bash
cd <monorepo-root>/publisher
export FOUNDATIONS_PATH=<monorepo-root>/foundations
PYTHONPATH=. python chatbot/scripts/ask.py "Which metros have the highest rent-to-income ratio in 2023?"
```

Expected: intent parsed → SQL generated → query executed → chart rendered → answer text returned. No import errors, no path errors.

- [x] Intent parser returns a `ParseResult` without errors
- [x] SQL generator produces valid DuckDB SQL
- [x] Query executes against the foundations DuckDB and returns rows
- [x] Chart renderer calls the R visual library at `foundations/visual_library/shared/render/` and produces a `.png`
- [x] Response assembler returns answer text

### 4.2 Publisher workflow test

Run one queue step through the publisher:

```bash
cd <monorepo-root>/publisher
export FOUNDATIONS_PATH=<monorepo-root>/foundations
PYTHONPATH=. python publisher/run_publisher.py --next --step parse
```

- [x] `run_publisher.py` finds the next `ready` question in `question_queue.yaml` (should be q002)
- [x] `parse` step completes and writes `query_plan.json` to the output folder
- [x] Run `--step sql` and confirm `result.sql` and `result.csv` are written
- [x] Run `--step chart` and confirm `chart.png` is written

### 4.3 Frontend smoke test

```bash
cd <monorepo-root>/publisher
PYTHONPATH=. streamlit run frontend/streamlit_app.py
```

- [x] Frontend boots without import errors
- [x] q001 artifact loads in the review interface
- [ ] Chart renders in the Streamlit UI

---

## Phase 5 — Post-migration cleanup

- [x] Update `<monorepo-root>/notes/patterns_in_place_notes/Migration.md` — check off the publisher migration step
- [x] Update `<monorepo-root>/notes/patterns_in_place_notes/Repos.md` — change `metro_deep_dive_chatbot` entry to note it is superseded by `publisher/`
- [x] Add `publisher/` entry to `Repos.md` with updated key paths
- [x] Write `publisher/README.md` documenting the `FOUNDATIONS_PATH` env var requirement, the three components, and how to run each

---

## Future Cleanup And Improvement Sprint

These are intentionally out of scope for the migration itself, but should be considered in a later cleanup and improvement sprint:

- [ ] Create a dedicated `content` skill so agents can reliably reproduce the manual editorial workflow in `content/`
- [ ] Evaluate renaming the inner `publisher/` folder to something clearer such as `production/` or `pipeline/` to reduce confusion between the top-level `publisher/` product area and the queue wrapper folder
- [ ] Complete a manual browser-level frontend QA pass to confirm saved charts render correctly inside the Streamlit UI, not just that the app boots and loads artifacts

---

## Agent docs

`metro_deep_dive_chatbot` does not have its own `AGENTS.md` or `CLAUDE.md`. The monorepo root `AGENTS.md` covers all general guidelines.

Write a minimal `publisher/CLAUDE.md` with publisher-specific orientation:

```markdown
# CLAUDE.md

See `<monorepo-root>/AGENTS.md` for full behavioral guidelines.

## Quick orientation

`publisher/` contains four components: the chatbot backend, the publisher batch
runner, the chatbot frontend, and the content workspace.

**Required env var:** `FOUNDATIONS_PATH` must point to `<monorepo-root>/foundations/`.
The chatbot will not start without it — `chatbot/query/catalogs.py` and
`chatbot/charts/renderer.py` both read this at import time.

| Task | Command |
|---|---|
| Run a question through the chatbot | `PYTHONPATH=. python chatbot/scripts/ask.py "<question>"` |
| Run the publisher queue | `PYTHONPATH=. python publisher/run_publisher.py --next` |
| Boot the chatbot frontend | `PYTHONPATH=. streamlit run frontend/streamlit_app.py` |

- Chatbot backend: `chatbot/` — orchestrator, intent parser, LLM, SQL pipeline, chart renderer
- Publisher: `publisher/` — queue, packager, summarizer, skills, examples, output artifacts
- Content workspace: `content/` — manual topic series; do not use the chatbot pipeline here
- Semantic layer: `foundations/semantic_layer/` — edit catalogs there, not here
- Visual library: `foundations/visual_library/` — edit render scripts there, not here
```

---

## Long-term: semantic layer ownership

The semantic layer YAML files (`table_catalog.yml`, `metric_catalog.yml`, etc.) live in `foundations/semantic_layer/`. The publisher reads them at runtime via `FOUNDATIONS_PATH`. This is the right long-term ownership model.

The remaining gap is that `foundations/semantic_layer/` currently has more files than `metro_deep_dive_chatbot/semantic_layer/` — it includes `intelligence_catalog.yml`, `theme_catalog.yml`, `points_catalog.yml`, and `question_catalog.yml` which don't exist in the source repo (they are planned additions from the roadmap). The publisher app does not load these yet. When they are written:

1. Write them in `foundations/semantic_layer/` — that is the canonical location
2. Wire them into `app/query/catalogs.py` `load_semantic_catalogs()` as additional catalog loads
3. No path changes needed — `FOUNDATIONS_PATH` already points there
