# Publisher — Product Roadmap

*Last updated: 2026-07-11. This roadmap is referenced from `PLATFORM_ROADMAP.md` → Track G and Track H. It covers three distinct products that share the same foundations layer (DuckDB warehouse, `chart_engine_py`, semantic layer, Gold tables) but have different execution models, outputs, and distribution channels.*

*Revision notes: Added CE task breakdowns (2026-07-11). Added chart type coverage analysis, q016–q028 backlog expansion, decision gate log, backlog format spec, and chart-selection design (2026-07-11). Added Python rendering architecture direction after the Phase 5 manual-run review (2026-07-12).*

---

## Context for Agents

Read this section before starting any milestone work. It records decisions already made and pointers that would otherwise require rediscovery.

### Orientation docs

- [`PUBLISHER_ROADMAP.md`](PUBLISHER_ROADMAP.md) — this file; canonical plan; authoritative on structure even where `publisher/README.md` describes the old layout
- [`publisher/README.md`](README.md) — current folder orientation; note it predates this roadmap and will be updated as milestones complete
- [`foundations/visual_library/chart_engine_py/PLAN.md`](../foundations/visual_library/chart_engine_py/PLAN.md) — Phases 1–4 complete; Phases 5–6 are what CE-2 and CE-3 accomplish as a byproduct of Chart Engine manual runs
- [`AGENTS.md`](../AGENTS.md) — shared behavioral guidelines for all agents in this monorepo; read before writing any code

### Decisions already made — do not re-litigate

1. **Chart Engine bypasses the chatbot's NL→SQL pipeline entirely.** Questions in `backlog.yaml` are pre-defined; the agent writes SQL directly against the Gold schema. This is an agentic coding task, not a natural language understanding task.
2. **`publisher/publisher/` inner folder is being retired at CE-0, not deferred.** `queue_manager.py` and the CLI structure from `run_publisher.py` migrate into `chart_a_day/runner/`; `summarizer.py` (never implemented) and `skills/` stubs are retired; `packager.py` logic folds into `run_next.py`. Keeping both alive creates import ambiguity.
3. **`shared/chart_bridge.py` is the rendering seam for both Chart Engine and Chatbot.** Neither product imports `chart_engine_py` directly — both go through the bridge. The bridge is built in CE-3 once the Python render path is confirmed stable via CE-2's manual run. The bridge accepts an explicit `chart_type` string from the caller — it does not do template-to-chart-type mapping internally. Mapping logic lives in `chart_request.md` and `run_next.py`.
4. **The manual run (CE-2) comes before the runner (CE-4).** Draft skills first (CE-1), run one question manually end-to-end (CE-2), fix what broke and build `chart_bridge.py` (CE-3), then build `run_next.py` (CE-4). The runner is built around proven behavior, not guessed behavior.
5. **`content/` → `data_stories/` is a folder rename only.** The artifact contract and 9-step workflow are unchanged.
6. **Skills in CE-1 are human-invokable prompts, not SDK calls.** For CE-1 and CE-2, each skill file is a markdown prompt you paste into Claude. `mode: prompt` in front matter. CE-4 converts them to SDK calls; do not wire the SDK before CE-2's manual run is complete and the prompts are proven.
7. **The first CE-2 question is q003 (cost-burdened renters, `ranking`, `cbsa`).** If q003's data is missing from the Gold tables, fall back to q006 (national vacancy trend — a single-row aggregate, simplest possible SQL). Decide before starting CE-2, not mid-run.
8. **`backlog.yaml` carries a `produce_alternatives` boolean per entry.** When `true`, `chart_request.md` builds a second `ChartRequest` using the first fallback from `chart_rules.yml` and saves `chart_alt.png` alongside `chart_py.png`. During Phase 5, the explicit Python parity artifact is `chart_py.png`; if a convenience `chart.png` is kept for review tooling, it is a copy of the approved Python candidate. Default is `false`. Set to `true` on the first few `trend` and `distribution` questions to collect format comparison data for CE-8.
9. **Chart type selection follows `chart_rules.yml`, not ad hoc agent judgment.** The agent reads `template_id + result shape → approved_chart_types` from `foundations/semantic_layer/chart_rules.yml`, applies selection constraints, and uses the first approved type. The `backlog.yaml` `notes` field can override with an explicit chart type directive (e.g., "use slopegraph not line"). The agent does not guess.
10. **`backlog.yaml` `template_id` set is extended to cover all 16 chart types.** Original six (`ranking`, `trend`, `compare_selected`, `distribution`, `benchmark`, `growth`) only mapped to 5 chart types. Five new template IDs added: `correlation`, `composition`, `map`, `demographic`, `rank_change`. These are registered in `chart_rules.yml` in CE-1. See chart type coverage table below.
11. **CE-8 format decision uses a pre-defined threshold.** If one format has ≥25% higher average engagement across ≥10 posts, it wins. If neither clears the bar, default to standalone (simpler to produce). Write the threshold before looking at data (CE-8.1) — do not set it after seeing the numbers.
12. **Automated posting starts with Bluesky only (CE-9).** Bluesky API is free. X API v2 Basic costs ~$100/month. Evaluate X only after 30+ posts live and the pipeline is proven. Document the evaluation at `chart_a_day/runner/X_API_EVAL.md` before adding X posting code.
13. **During CE-1 and CE-2, `chart_rules.yml` stays chatbot-compatible.** The shared catalog still uses legacy `bar` / `line` names for the R-backed chatbot path. Manual Chart Engine prompts normalize those to `bar_chart` / `line_chart` only when calling `chart_engine_py`. Do not rewrite the shared catalog names until CH-1 swaps the chatbot renderer.
14. **Chart A Day does not need to wait for Python publishing parity.** If the R render is clearly stronger, it is acceptable to use the R visual for near-term Chart A Day production while Python keeps improving in parallel.
15. **Long-term Python rendering converges on `matplotlib`.** The current mixed Python backend is acceptable during the transition, but the target architecture is a shared matplotlib-based design system with reusable classes/helpers for composition, colors, fonts, legends, labels, and map framing.

### Milestone-specific pointers

**CE-0 (folder structure):**
- Source for `backlog.yaml`: `publisher/publisher/question_queue.yaml`
- Source for `chart_a_day/runner/queue_manager.py`: `publisher/publisher/queue_manager.py` — migrate as-is, it's solid
- Source for `chart_a_day/runner/run_next.py`: `publisher/publisher/run_publisher.py` — strip the NL→SQL step calls (`run_parse_step`, `run_sql_step`, `run_chart_step`), keep the CLI structure, artifact checking, and note-appending logic
- Also add q016–q028 to `backlog.yaml` at CE-0 time — see chart type coverage table below

**CE-1 (draft skills):**
- `ChartRequest` surface: [`foundations/visual_library/chart_engine_py/SPEC.md`](../foundations/visual_library/chart_engine_py/SPEC.md)
- Chart selection rules: `foundations/semantic_layer/chart_rules.yml` — extend with `correlation`, `composition`, `map`, `demographic`, `rank_change` rule blocks in CE-1
- Gold table schema context for the SQL skill: `foundations/semantic_layer/`
- Worked example of good SQL + chart output: `publisher/content/vacancy_rates/`
- Skills are `mode: prompt` (human-invokable) in CE-1; wired to SDK in CE-4

**CE-2 (first manual run):**
- This run IS `chart_engine_py` Phase 5. Each artifact produced simultaneously proves the SQL skill and exercises the chart type against real content.
- For every CE manual run, render the same result through both stacks: `chart_r.png` is the reference implementation from the existing R visual library, and `chart_py.png` is the Python parity candidate from `chart_engine_py`.
- The parity question is explicit on every run: does the Python output match the analytical intent and the current R visual contract closely enough to replace it?
- Default question: q003. Fallback if Gold data missing: q006.
- The Phase 5 review now tells us two things at once:
  - R can remain the practical Chart A Day renderer for now when it is materially stronger.
  - Python still matters because the chatbot path benefits from a native Python renderer and shared runtime control.

### Backlog entry format

Every entry in `backlog.yaml` uses this schema. Read this before adding questions.

```yaml
- id: q016                      # sequential, never reused, never reassigned
  question: "Plain-language question as you'd say it out loud."
  template_id: correlation      # see template IDs below
  geo_level: cbsa               # cbsa | state | national | county
  status: ready                 # ready | ran | reviewed | posted
  platform: both                # both | x | bluesky | substack
  produce_alternatives: false   # true = also render fallback chart type as chart_alt.png
  notes: |
    Agent hints go here. Specify: population filters, named geographies for
    compare_selected, benchmark value/source, preferred chart variant when
    template maps to multiple types, any known data caveats.
  scheduled: null
  ran_at: null
  posted_at: null
```

**Template IDs and their primary chart types** (from `chart_rules.yml`; fallbacks in parentheses):

| `template_id` | Primary chart | Fallback | When to use |
|---|---|---|---|
| `ranking` | `bar_chart` | `heatmap_table` | Top-N ordered list at a single point in time |
| `trend` | `line_chart` | `slopegraph` | One or more series over time; use `rank_change` if exactly two time points |
| `compare_selected` | `bar_chart` | `slopegraph` | Small named set of geographies, point-in-time or two-point comparison |
| `distribution` | `boxplot` | `heatmap_table` | Spread of a metric across all geographies at a common grain |
| `benchmark` | `bar_chart` | `strength_strip` | One geography vs. a reference value or peer set |
| `growth` | `bar_chart` | `heatmap_table` | Top-N by rate of change over a window |
| `correlation` | `scatter` | `hexbin` | Two quantitative metrics across many geographies; use `hexbin` if N > 200 |
| `composition` | `waterfall` | `heatmap_table` | Multi-metric scorecard or component breakdown for one or a few geographies |
| `map` | `choropleth` | `highlight_context_map` | Any geographic distribution where spatial pattern is the story |
| `demographic` | `age_pyramid` | `heatmap_table` | Age/sex population structure; requires age bins and sex breakdown |
| `rank_change` | `bump_chart` | `slopegraph` | How rankings have shifted over time; requires 3+ time points for bump, 2 for slope |

**Chart type → Phase 5 coverage:**

| Chart type | Template(s) | Backlog question(s) covering it |
|---|---|---|
| `bar_chart` | ranking, benchmark, growth, compare_selected | q001–q003, q011–q015 |
| `line_chart` | trend, compare_selected | q004–q008 |
| `boxplot` | distribution | q009–q010 |
| `scatter` | correlation | q016 |
| `slopegraph` | rank_change, trend (2-pt) | q017 |
| `bump_chart` | rank_change | q018 |
| `heatmap_table` | composition | q019 |
| `waterfall` | composition | q020 |
| `strength_strip` | composition, benchmark | q021 |
| `correlation_heatmap` | correlation (multi-metric) | q022 |
| `age_pyramid` | demographic | q023 |
| `choropleth` | map | q024 |
| `highlight_context_map` | map | q025 |
| `proportional_symbol_map` | map | q026 |
| `bivariate_choropleth` | map (two-metric) | q027 |
| `hexbin` | correlation (dense) | q028 |

Running q016–q028 through the pipeline closes `chart_engine_py` Phase 5 for all 16 chart types. Update `PLAN.md` Phase 5 verification criteria after each run: "Python chart matches analytical intent in backlog `notes`; benchmark present where specified; column mapping produced the correct axis orientation; material differences from the R reference are logged and classified."

**Broad parity audit first:**
- Before using CE manual runs as the main parity-discovery mechanism, run the broad Python-vs-R audit defined in `foundations/visual_library/chart_engine_py/PARITY_AUDIT_FRAMEWORK.md`.
- That audit should produce a master parity register, a fix execution order, and one chart-by-chart audit file for all 16 chart types.
- After that audit exists, CE runs shift from "find what is broken" to "validate that the audited gaps are actually closed on real questions."

**Phase 5 manual-run tracker:**
- [x] `q001` — `bar_chart` parity run (`ranking`)
- [x] `q002` — `bar_chart` parity run (`ranking`)
- [x] `q003` — `bar_chart` parity run (`ranking`)
- [x] `q004` — `line_chart` parity run (`trend`)
- [x] `q005` — `line_chart` parity run (`trend`)
- [x] `q006` — `line_chart` parity run (`trend`)
- [x] `q007` — `bar_chart` parity run (`compare_selected`)
- [x] `q008` — `line_chart` parity run (`compare_selected`)
- [x] `q009` — `boxplot` parity run (`distribution`)
- [x] `q010` — `boxplot` parity run (`distribution`)
- [x] `q011` — `bar_chart` parity run (`benchmark`)
- [x] `q012` — `bar_chart` parity run (`benchmark`)
- [x] `q013` — `bar_chart` parity run (`growth`)
- [x] `q014` — `bar_chart` parity run (`growth`)
- [x] `q015` — `bar_chart` parity run (`ranking`)
- [x] `q016` — `scatter` parity run (`correlation`)
- [x] `q017` — `slopegraph` parity run (`rank_change`)
- [x] `q018` — `bump_chart` parity run (`rank_change`)
- [x] `q019` — `heatmap_table` parity run (`composition`)
- [x] `q020` — `waterfall` parity run (`composition`)
- [x] `q021` — `strength_strip` parity run (`benchmark` / `composition`)
- [x] `q022` — `correlation_heatmap` parity run (`correlation`)
- [x] `q023` — `age_pyramid` parity run (`demographic`)
- [x] `q024` — `choropleth` parity run (`map`)
- [x] `q025` — `highlight_context_map` parity run (`map`)
- [x] `q026` — `proportional_symbol_map` parity run (`map`)
- [x] `q027` — `bivariate_choropleth` parity run (`map`)
- [x] `q028` — `hexbin` parity run (`correlation`)

Treat this checklist as stricter than the backlog status alone. A question only counts here once the CE dual-render workflow has produced `chart_r.*`, `chart_py.*`, and a written parity verdict in `step_notes.md`.

**Initial manual tranche:**
- Start with `q003` (`ranking`) as the first ranked bar-chart proof point.
- If `q003` is blocked on Gold coverage, run `q006` (`trend`) immediately as the fallback line-chart proof point.
- In the same initial tranche, run `q024` (`map`) to force one early geo/manual parity check before the workflow hardens around Altair-first charts.
- After those three runs, tighten prompts and workflow notes before scaling through the remaining backlog.
- The long-run goal remains unchanged: work through all questions in the tracker, not just the first tranche.

**Manual run artifact contract:**
- Every Phase 5 / CE manual run writes artifacts to `publisher/chart_a_day/output/{q_id}/`.
- Required files for a parity-complete run:
  - `question.md`
  - `result.sql`
  - `result.csv`
  - `chart_py.png`
  - `chart_r.png`
  - `post.md`
  - `step_notes.md`
- Optional files:
  - `chart_alt.png` when `produce_alternatives: true`
  - helper scripts or temporary notebooks used to generate the R reference, if they are useful for reproducibility
- `chart.png` is not the parity source-of-truth filename during Phase 5. If a convenience `chart.png` is kept for downstream review tools, it should be a copy of the approved Python candidate after `chart_py.png` exists.

**Manual run log:**
- Canonical log path: `publisher/chart_a_day/MANUAL_RUN_LOG.md`
- Each run appends one dated section with:
  - `q_id`
  - run date
  - question type / chart type
  - whether the run covered `python`, `r`, or both
  - artifact status (`complete`, `partial`, `blocked`)
  - parity verdict (`match`, `match_with_minor_drift`, `blocked`, `not_reviewed`)
  - gap class for every issue: `spec`, `prep`, `render`, `theme`, `export`, `sql`, `agent_prompt`, or `review_process`
  - the concrete fix or instruction change required
  - whether the fix belongs in `chart_engine_py`, `chart_a_day` skills, backlog notes, or reviewer guidance
- `step_notes.md` remains the per-question scratchpad. `MANUAL_RUN_LOG.md` is the cross-run learning record we use to improve prompts and workflow instructions.

### How the agent decides chart type

The decision chain, in order:

1. Read `template_id` from `backlog.yaml`
2. Look up `template_id` in `foundations/semantic_layer/chart_rules.yml` → `approved_chart_types[0]`
3. Check selection constraints in `chart_rules.yml` (e.g., `slopegraph_requires_two_time_points`) against the actual result shape
4. If a constraint blocks the primary type, use `fallback_chart_types[0]`
5. If `backlog.yaml` `notes` contains an explicit chart type directive (e.g., "use slopegraph not line"), that overrides steps 2–4
6. Pass the resolved `chart_type` string explicitly to `chart_bridge.render_chart()` — the bridge does not select

The agent does not guess or improvise chart types. If `template_id` is not in `chart_rules.yml`, the skill raises and halts — do not add a default fallback. Fix the `chart_rules.yml` gap instead.

**When to produce alternatives (`produce_alternatives: true`):**

Set this on questions where the approved and fallback types tell meaningfully different stories — not on every question. Use it for data collection; decide the default at CE-8.

| Scenario | Produce alternative? | Why |
|---|---|---|
| `ranking` → `bar_chart` | No | Bar is unambiguously right for ranked lists |
| `trend` with 2 time points | Yes | `line_chart` shows trajectory; `slopegraph` shows rank change |
| `distribution` with large N | Yes | `boxplot` compresses; `heatmap_table` shows individual metros |
| `correlation` with N > 200 | Yes | `scatter` shows outliers; `hexbin` shows density clusters |
| `map` questions | No | Map or not-map is a binary call on data availability |

**CH-0 (catalog wiring):**
- File to edit: `publisher/chatbot/query/catalogs.py`
- Missing catalogs to wire: `theme_catalog.yml`, `intelligence_catalog.yml`, `question_catalog.yml` — all live in `foundations/semantic_layer/`
- Follow the existing loading pattern in `catalogs.py` for the three catalogs already wired

### Python Renderer Direction

The current manual-run review changed the architecture emphasis:

- For **Chart A Day**, keep using the stronger R renderer for near-term production artifacts when Python is visibly weaker.
- For the **chatbot**, keep native Python rendering as the strategic target because it simplifies packaging, deployment, and runtime behavior.
- For **Python renderer development**, do not keep solving polish one chart at a time forever. Build reusable visual classes/helpers that own:
  - composition presets
  - semantic color tokens
  - font and caption hierarchy
  - legend placement
  - annotation / label behavior
  - map framing and context layers
- Treat the current Altair analytical renderers as acceptable transition infrastructure, not necessarily as the final steady state.
- The long-term target is a Python renderer that is fully `matplotlib`-based for final presentation quality.

**DS-0 (folder rename):**
- `git mv publisher/content publisher/data_stories`
- Also update references in: `publisher/README.md`, `publisher/CLAUDE.md`, `PLATFORM_ROADMAP.md` → Track G section

### Environment

- `FOUNDATIONS_PATH` must be set to `<monorepo-root>/foundations/` before running anything in the publisher
- Python environment: `.venv312` with the editable `chart_engine_py` install plus `publisher/requirements.txt`
- DuckDB: `foundations/etl/data/duckdb/patterns_in_place.duckdb` (read-only for all publisher work)

---

## The Three Products

| Product | What it is | Execution model | Primary output | Distribution |
|---|---|---|---|---|
| **Data Stories** | Editorial content — long-form analyses, listicles, data takes | Human-led; agent executes against your direction | Substack posts, articles | Substack |
| **Chart Engine** | Chart-a-day social publishing pipeline | Agent-driven; human review gate before posting | Chart + social copy (X, Bluesky) | X, Bluesky |
| **Chatbot** | NL→SQL interactive product | User-driven; query in, chart + answer out | In-app chart and text response | Public Streamlit demo |

They are not the same workflow routed through the same code. They share foundations; they do not share a pipeline.

---

## Folder Structure

```
publisher/
├── CLAUDE.md
├── README.md                       ← overview of three products + shared foundations
├── PUBLISHER_ROADMAP.md            ← this file
│
├── data_stories/                   ← replaces content/; human-led editorial workflow
│   ├── README.md
│   ├── backlog.md                  ← cross-topic post tracker + story angles
│   └── {topic}/
│       ├── README.md               ← topic thesis, planned insights, publish order
│       └── {insight}/
│           ├── question.md
│           ├── findings.md
│           ├── query.sql
│           ├── result.csv
│           ├── chart_config.json
│           ├── chart.png
│           ├── summary.md
│           └── post_draft.md
│
├── chart_a_day/                    ← new; agent-driven chart-a-day pipeline
│   ├── README.md
│   ├── backlog.yaml                ← question backlog with status tracking
│   ├── skills/
│   │   ├── sql_agent.md            ← skill: question + schema → SQL → result.csv
│   │   ├── chart_request.md        ← skill: result.csv → ChartRequest → chart_py.png
│   │   └── social_copy.md          ← skill: chart + finding → canonical social draft, plus optional platform variants
│   ├── runner/
│   │   ├── run_next.py             ← CLI: read next ready question, run skill chain
│   │   └── queue_manager.py        ← status machine: ready → ran → reviewed → posted
│   └── output/
│       └── {q_id}/
│           ├── question.md
│           ├── result.sql
│           ├── result.csv
│           ├── chart_py.png
│           ├── chart_r.png
│           ├── post.md
│           ├── post_x.md           ← optional, only when X needs different copy
│           └── post_bluesky.md     ← optional, only when Bluesky needs different copy
│
├── shared/                         ← shared by chart_a_day/ and chatbot/
│   ├── db.py                       ← DuckDB connection helper
│   └── chart_bridge.py             ← result.csv + config → chart_engine_py → chart_py.png
│
├── chatbot/                        ← NL→SQL product; stays largely as-is
│   ├── orchestrator.py
│   ├── intent/
│   ├── query/
│   ├── charts/
│   ├── response/
│   ├── llm/
│   └── scripts/
│
├── frontend/                       ← review app for chatbot artifacts
└── qa/                             ← QA framework for chatbot
```

**Migration notes for `publisher/publisher/` (inner folder, to be retired):**
- `queue_manager.py` → migrates to `chart_a_day/runner/queue_manager.py` as-is (solid code, keep it)
- `run_publisher.py` → migrates to `chart_a_day/runner/run_next.py` (strip the NL→SQL step calls, keep CLI structure and artifact logic)
- `packager.py` → retire; artifact checking logic folds into `run_next.py`
- `summarizer.py` → retire; was never implemented (raises `NotImplementedError`)
- `skills/` stub files → retire; replace with real skill files in `chart_a_day/skills/`
- `output/q001/, q002/` → keep as reference artifacts; move to `chart_a_day/output/` or leave in place

---

## Track DS — Data Stories

**What it is:** Editorial content developed topic-first with a human driving all key decisions. Agent executes: writes SQL, renders charts, drafts social copy. You decide: angle, metric, chart type, interpretation. Output goes to Substack. Format (long-form, listicle, data take) is learned by doing — not prescribed.

**Current state:** Infrastructure is complete. Four housing topics with real SQL, renders, and post drafts exist under `content/housing/`. The `vacancy_rates/` series has completed artifacts for multiple insights. The folder rename is the only structural change needed. Zero posts published.

**The single biggest gap:** Nothing has shipped. Everything else is secondary.

### Milestones

| ID | Milestone | Description | Status | Depends on |
|---|---|---|---|---|
| DS-0 | Folder rename | `content/` → `data_stories/`; update CLAUDE.md + README | Ready | — |
| DS-1 | First published piece | Pick one completed insight from housing or vacancy backlog; full artifact set; post to Substack | Unblocked after DS-0 | DS-0 |
| DS-2 | Second topic complete | Validate artifact contract holds across topics; note what took time | After DS-1 | DS-1 |
| DS-3 | L/O scatter flagship | The Livability/Opportunity four-quadrant piece — first piece that earns Lane 1 outreach (Kolko, Cortright) | After Area Explorer Phase 1 verified | DS-2, Track E Phase 1 |
| DS-4 | Set publishing cadence | Based on measured time per post, not aspiration; commit to a frequency after two data points | After DS-2 | DS-2 |
| DS-5 | Content pipeline skill | Encode the 9-step workflow as a Claude skill for consistent scaffolding | After DS-4 | DS-4 |

### Non-technical work (parallel, no build dependency)

- [ ] Set up Substack publication: name, tagline, welcome post placeholder — before or alongside DS-1
- [ ] Set up PiP X account: handle, bio, profile image, pinned post slot
- [ ] Set up PiP Bluesky account: same
- [ ] Build urban-econ follow list on X: Parsons, Stone, Kolko, Cortright, EIG, Armlovich, Gray, Darrell Owens, M. Nolan Gray
- [ ] Daily X engagement habit: 10 min/day; replies with charts or analysis before original posts
- [ ] Submit Substack RSS to R-bloggers after first R-adjacent post
- [ ] Engagement tracker: YAML or spreadsheet — post date, platform, likes, replies, follows gained, notes. One row per post. Reviewed weekly.

### Distribution activations (artifact-gated)

- After DS-1: r/dataisbeautiful (strongest single chart), #rstats Bluesky
- After DS-3: email Jed Kolko + Joe Cortright; FlowingData submission
- After methodology piece: Brookings Metro, Regional Feds email

---

## Track CE — Chart Engine

**What it is:** A lightweight agent-driven pipeline for chart-a-day social posting. A question backlog (`backlog.yaml`) feeds an agent that writes SQL, executes it, passes the result through `chart_engine_py`, and generates a canonical social draft (standalone post plus thread opener), with platform-specific variants only when they meaningfully differ. Human reviews and posts manually. Long-term target: fully autonomous posting once the concept is proven and X API cost is justified.

**Key design decision:** This pipeline bypasses the chatbot's NL→SQL intent parser entirely. Questions are pre-defined; the agent writes SQL directly against the Gold schema. This is an agentic coding task, not a natural language understanding task — simpler, more reliable, and decoupled from the chatbot's complexity.

**How this relates to `chart_engine_py` Phase 5:** The Chart Engine manual proving runs *are* Phase 5. They are the same work, not sequential steps. Each question run through the pipeline simultaneously proves the SQL skill, exercises a `chart_engine_py` chart type against real content, and validates the social copy skill. CE-1 through CE-4 complete Phase 5 as a byproduct. `shared/chart_bridge.py` (Phase 6) is built once the manual runs confirm the Python render path is stable — at that point, the Chatbot can swap its R bridge for the same seam.

**What migrates from `publisher/publisher/`:** `queue_manager.py` migrates as-is. `run_publisher.py` migrates with the NL→SQL step calls stripped. Everything else is retired or rewritten.

### Milestones

| ID | Milestone | Description | Status | Depends on |
|---|---|---|---|---|
| CE-0 | Folder structure | Create `chart_a_day/`; migrate `question_queue.yaml` → `backlog.yaml`; write README; retire `publisher/publisher/` inner folder | Complete | — |
| CE-1 | First skill drafts | Write initial `sql_agent.md`, `chart_request.md`, `social_copy.md` skill files; each is a Claude skill with YAML front matter; intentionally rough — they get refined through use | Complete | CE-0 |
| CE-2 | First manual run | Pick one question from backlog; run each skill manually in sequence; save the full artifact set plus R/Python comparison charts to `output/{q_id}/`; record what broke, what was off, what worked | Ready | CE-1 |
| CE-3 | Skill iteration + `shared/chart_bridge.py` | Fix skill gaps surfaced by CE-2; build `chart_bridge.py` once the Python render path is confirmed stable; this completes `chart_engine_py` Phase 5–6 as a byproduct | After CE-2 | CE-2 |
| CE-4 | `run_next.py` runner | Thin CLI that reads next `ready` question from backlog, invokes skill chain, saves artifact set; replaces the manual step-by-step from CE-2 | After CE-3 | CE-3 |
| CE-5 | First 5 posts end-to-end | Run 5 questions through the full pipeline via `run_next.py`; review artifacts; iterate on social copy quality; each run produces one X post and one Bluesky post draft | After CE-4 | CE-4 |
| CE-6 | Reviewer tab in frontend | Add a tab to `frontend/streamlit_app.py` for reviewing chart_engine output (chart preview + social copy + approve/reject status update) | After CE-5 | CE-5 |
| CE-7 | Engagement telemetry | Track post performance: date, platform, URL, likes, replies, reposts, follows gained. Start as a YAML append-log; move to DuckDB table once the format stabilizes | After CE-5 | CE-5 |
| CE-8 | Single post vs thread decision | Run both formats across 10+ posts; review engagement data; establish default format | After ~10 posts live | CE-7 |
| CE-9 | Automated posting via API | X API + Bluesky API integration; evaluate cost vs value once concept is proven; consider Bluesky-first since its API is free | After CE-8 | CE-8 |

### Task Breakdown by Milestone

---

#### CE-0 — Folder Structure

**Goal:** Create the `chart_a_day/` directory layout and migrate the existing queue artifacts. Nothing new is built here — this is a pure structural move. When done, the old `publisher/publisher/` inner folder is retired and the new folder layout from the roadmap spec exists on disk.

**Audit note:** `publisher/publisher/queue_manager.py` is solid — migrate as-is. `run_publisher.py` strips the three NL→SQL step functions (`run_parse_step`, `run_sql_step`, `run_chart_step`), which belong to the chatbot pipeline, not Chart Engine. `packager.py` and `summarizer.py` are retired (the artifact check logic folds into `run_next.py` later; `summarizer.py` was never implemented). The `skills/` stubs are retired; real skills replace them in CE-1.

- [x] **CE-0.1** Create `publisher/chart_a_day/` with subdirectories: `skills/`, `runner/`, `output/`
- [x] **CE-0.2** Copy `publisher/publisher/question_queue.yaml` to `publisher/chart_a_day/backlog.yaml` — update the path constant in the file header comment; keep all 15 entries intact
- [x] **CE-0.3** Copy `publisher/publisher/queue_manager.py` to `publisher/chart_a_day/runner/queue_manager.py` — update `DEFAULT_QUEUE_PATH` to point to `chart_a_day/backlog.yaml` (two levels up from `runner/`)
- [x] **CE-0.4** Create `publisher/chart_a_day/runner/run_next.py` by stripping `publisher/publisher/run_publisher.py` — remove `run_parse_step`, `run_sql_step`, `run_chart_step`, and the `--step` CLI argument; keep `--next`, `--status`, `--note`, `--id`, `print_status`, `append_note`, `resolve_entry`, `ensure_output_dir`; update `OUTPUT_ROOT` to point at `chart_a_day/output/`; the step-running logic will be filled in CE-4
- [x] **CE-0.5** Move `publisher/publisher/output/q001/` and `output/q002/` to `publisher/chart_a_day/output/` as reference artifacts (these are already-ran examples)
- [x] **CE-0.6** Write `publisher/chart_a_day/README.md` — two paragraphs: what Chart Engine is (agent-driven chart-a-day pipeline, bypasses chatbot NL→SQL) and how to use it (`--next`, `--status`, `--note`); list the three skill files and what each does
- [x] **CE-0.7** Retire `publisher/publisher/` inner folder: delete `packager.py`, `summarizer.py`, `skills/` stub files; leave `question_queue.yaml` with a comment pointing to `chart_a_day/backlog.yaml`; update `publisher/CLAUDE.md` command table to replace the old `run_publisher.py` command with the new `run_next.py` path

**Verification:** `python -c "from chart_a_day.runner.queue_manager import QueueManager; print(QueueManager().status_counts())"` prints counts from `backlog.yaml` without error. `python chart_a_day/runner/run_next.py --status` prints the queue status table.

---

#### CE-1 — First Skill Drafts

**Goal:** Write three Claude skill files — `sql_agent.md`, `chart_request.md`, `social_copy.md` — that an agent (or you running Claude manually) can execute step by step against a single backlog question. These are intentionally rough first drafts; they get sharpened through CE-2's manual run. The existing `publisher/publisher/skills/` stubs have no real content — treat them as blank slates, not starting points.

**What a skill file must contain:** YAML front matter (`name`, `version`, `description`, `inputs`, `outputs`) followed by a prompt body that gives Claude enough context to act without requiring extra files to be open.

**CE-1.1 — `sql_agent.md`**
- [x] **CE-1.1.1** Write YAML front matter: `name: sql_agent`, inputs: `[question, template_id, geo_level, backlog_notes]`, outputs: `[result.sql, result.csv]`
- [x] **CE-1.1.2** Write a prompt section that tells Claude: "You are writing DuckDB SQL against the Gold schema. The question is `{{question}}`. The template type is `{{template_id}}` (ranking / trend / compare_selected / distribution / benchmark / growth). The geography level is `{{geo_level}}` (cbsa / state / national). Relevant tables live in `foundations/etl/data/duckdb/patterns_in_place.duckdb`; connect read-only. The semantic layer is in `foundations/semantic_layer/` — consult `metric_catalog.yml` for column names and `table_catalog.yml` for table names before writing SQL."
- [x] **CE-1.1.3** Add a worked example section using the existing `publisher/content/vacancy_rates/metro_rankings/query.sql` and `result.csv` as a reference pair — show what good SQL looks like for a `ranking` + `cbsa` question
- [x] **CE-1.1.4** Add output instructions: write SQL to `chart_a_day/output/{q_id}/result.sql`; execute it against the DuckDB and write `result.csv`; print row count and column names as a sanity check
- [x] **CE-1.1.5** Add a note about the `geo_level: national` case — it queries a single aggregate row, not a ranked list; the SQL structure changes

**CE-1.0 — Extend `chart_rules.yml` before writing skills**
- [x] **CE-1.0.1** Open `foundations/semantic_layer/chart_rules.yml` and add five new rule blocks — one each for `correlation`, `composition`, `map`, `demographic`, `rank_change` — following the existing rule format (`rule_id`, `question_type`, `result_shape`, `approved_chart_types`, `fallback_chart_types`, `rationale`). Use the template IDs table in the backlog format section above as the spec. Also add constraints for `hexbin` (prefer when N > 200) and `bivariate_choropleth` (requires two binnable metrics).
- [x] **CE-1.0.2** Verify the extended `chart_rules.yml` is valid YAML: `python -c "import yaml; yaml.safe_load(open('foundations/semantic_layer/chart_rules.yml').read()); print('ok')"`

**CE-1.2 — `chart_request.md`**
- [x] **CE-1.2.1** Write YAML front matter: `mode: prompt`, inputs: `[question, template_id, produce_alternatives, result_csv_path, q_id]`, outputs: `[chart_py.png]` (and optionally `chart_alt.png`)
- [x] **CE-1.2.2** Write a prompt section explaining `ChartRequest`: "Import `chart_engine` from the editable install at `foundations/visual_library/chart_engine_py/`. Load `result.csv` as a DataFrame. Build a `ChartRequest` with `chart_type` resolved from `chart_rules.yml` using the decision chain: read `template_id` → look up `approved_chart_types[0]` → check selection constraints against result shape → apply any `notes` override → pass resolved type to the manual Python render path used before `chart_bridge.py` exists. Set `Theme.default()`. Set `OutputConfig(save=True, path='chart_a_day/output/{q_id}/chart_py.png')`."
- [x] **CE-1.2.3** Add the full template-to-chart-type resolution table (all 11 template IDs) — do not hardcode chart types in the skill; always derive from `chart_rules.yml`. The table in this skill is for human reference only.
- [x] **CE-1.2.4** Add `column_mapping` guidance: explain that `chart_engine_py` expects canonical field names (`entity`, `value`, `period`, etc.) and the agent must map CSV column names to those names using `column_mapping` on the request
- [x] **CE-1.2.5** Add a worked example using `publisher/content/vacancy_rates/metro_rankings/chart_config.json` and the corresponding `result.csv` — show what the `ChartRequest` Python code looks like for a ranked bar chart with a benchmark line
- [x] **CE-1.2.6** Add output instructions: call `render(request)`; if `ChartResult.warnings` is non-empty, print them; confirm `chart_py.png` was written to `output/{q_id}/`. If `produce_alternatives` is `true`, build a second `ChartRequest` using `fallback_chart_types[0]` from `chart_rules.yml` and save to `chart_a_day/output/{q_id}/chart_alt.png`; print which fallback type was used.

**CE-1.3 — `social_copy.md`**
- [x] **CE-1.3.1** Write YAML front matter: inputs: `[question, findings_summary, chart_path, platform]`, outputs: `[post.md]` plus optional `[post_x.md, post_bluesky.md]` when the copy needs to diverge by platform
- [x] **CE-1.3.2** Write a prompt section: "You are writing social copy for a data chart. The underlying question was: `{{question}}`. The key finding is: `{{findings_summary}}`. The chart is attached. Write one canonical draft first: a standalone post (fits in one post, ~240 chars for X) and a thread opener (hooks the finding, signals more below). Only split into platform files when there is a concrete reason."
- [x] **CE-1.3.3** Add platform-specific formatting notes: X posts have a 280-char hard limit; Bluesky supports 300 chars and renders links as cards; both should avoid hashtag spam (max 2); data accounts get better engagement with a specific number in the first line
- [x] **CE-1.3.4** Add a tone guide: plain language, no academic hedging, no "interesting to note"; lead with the finding, not the methodology; end with a question or invitation to reply
- [x] **CE-1.3.5** Add output instructions: write `post.md` to `chart_a_day/output/{q_id}/`; only add `post_x.md` or `post_bluesky.md` if a platform-specific variant is actually needed. Each file uses `## Standalone` and `## Thread opener` sections

**Verification:** All three skill files exist at `chart_a_day/skills/`. Each has valid YAML front matter parseable by `python -c "import yaml; yaml.safe_load(open('...').read().split('---')[1])"`.

---

#### CE-2 — First Manual Run

**Goal:** Run one question end-to-end through the three skills manually (not via the runner — that's CE-4). The purpose is to surface what actually breaks before building automation around it and to compare the Python output against the current R reference implementation on the exact same result set. Pick `q003` (cost-burdened renters ranking, template `ranking`, geo `cbsa`) — it's a simple ranked bar chart and the data is almost certainly in the Gold tables.

**What "manual" means here:** You open Claude, invoke each skill file in sequence, paste in the inputs, review the output, save artifacts by hand. The runner doesn't exist yet — you're proving the skills work before building the plumbing.

- [x] **CE-2.1** Verify `chart_engine_py` is installed in `.venv312`: `source .venv312/bin/activate && python -c "from chart_engine import render; print('ok')"` — if not, run `pip install -e foundations/visual_library/chart_engine_py`
- [x] **CE-2.2** Verify DuckDB connection works: `python -c "import duckdb; con = duckdb.connect('foundations/etl/data/duckdb/patterns_in_place.duckdb', read_only=True); print(con.execute('SHOW TABLES').fetchall())"` — confirm Gold tables are present
- [x] **CE-2.3** Create `chart_a_day/output/q003/` directory
- [x] **CE-2.3a** Create or update `chart_a_day/MANUAL_RUN_LOG.md` with a new section for `q003`
- [x] **CE-2.4** Run `sql_agent.md` for q003: open Claude, invoke the skill with `question="Which metros have the highest share of cost-burdened renters in 2023?"`, `template_id=ranking`, `geo_level=cbsa`; save output to `chart_a_day/output/q003/result.sql` and `result.csv`
- [x] **CE-2.5** Inspect `result.csv` before proceeding: confirm column names, row count (expect ~20–50 CBSAs), value range (share should be 0–100 or 0–1); note any surprises in a `step_notes.md`
- [x] **CE-2.6** Render the R reference chart for q003 from the same `result.csv`; save it as `chart_r.png` in `chart_a_day/output/q003/`
- [x] **CE-2.7** Run `chart_request.md` for q003: invoke the skill with the result CSV; produce the Python parity candidate as `chart_py.png` in `chart_a_day/output/q003/`
- [x] **CE-2.8** Visually review `chart_r.png` and `chart_py.png` side by side: does the Python output match the question, ranking order, labels, benchmark, and overall readability of the R output closely enough? Write findings in `step_notes.md` and classify each gap as `acceptable`, `minor`, or `blocking`
- [x] **CE-2.9** Run `social_copy.md` for q003: invoke the skill with the question, a one-sentence finding from the chart, and the approved chart image; save `post.md` and only create platform-specific files if they materially differ
- [x] **CE-2.10** Write `chart_a_day/output/q003/question.md` — one line: the question text, the q_id, the template, the geo level
- [x] **CE-2.11** Update `backlog.yaml`: set `q003.status = ran`, set `q003.ran_at` to today's date only if the parity review is not blocked
- [x] **CE-2.12** Write a post-run summary in `step_notes.md`: what worked, what broke, what needed manual correction, what the skill prompts got wrong, what took longer than expected, and whether the gap lives in Python `spec`, `prep`, `render`, `theme`, `export`, `sql`, `agent_prompt`, or `review_process`
- [x] **CE-2.13** Append the structured verdict to `chart_a_day/MANUAL_RUN_LOG.md`: artifact completeness, parity verdict, issue classes, and the exact prompt or code changes required before the next run

**Verification:** `chart_a_day/output/q003/` contains: `question.md`, `result.sql`, `result.csv`, `chart_r.png`, `chart_py.png`, `post.md`, `step_notes.md`, plus platform-specific social files only if needed. `step_notes.md` records the R-vs-Python parity verdict. `chart_a_day/MANUAL_RUN_LOG.md` contains the cross-run summary entry. `backlog.yaml` shows `q003` as `ran` only if the parity review is not blocked.

---

#### CE-3 — Skill Iteration + `shared/chart_bridge.py`

**Goal:** Fix the gaps surfaced by CE-2, then build `shared/chart_bridge.py` once the Python render path is confirmed stable. The bridge is the shared seam between Chart Engine and Chatbot — it lives in `publisher/shared/` so neither product imports `chart_engine_py` directly.

**Audit note:** `publisher/shared/` does not yet exist. `publisher/chatbot/charts/renderer.py` currently shells out to R — that is what `chart_bridge.py` replaces in CH-1. Build the bridge here based on what CE-2 confirmed works; CH-1 just swaps the renderer to use it.

**CE-3.1 — Fix skill gaps from CE-2**
- [x] **CE-3.1.1** Review `q003/step_notes.md` and list every gap: SQL errors, wrong column names, chart type mismatches, missing benchmarks, copy tone issues, and any Python-vs-R parity differences
- [x] **CE-3.1.2** Edit `sql_agent.md` to fix SQL issues: if the agent needed manual column name corrections, add those column names explicitly; if it queried the wrong table, add the correct table name to the prompt
- [x] **CE-3.1.3** Edit `chart_request.md` to fix chart issues: if `column_mapping` was wrong, fix the example; if a benchmark was missing, add instructions for when to add `BenchmarkConfig`; if parity was blocked, note whether the fix belongs in Python `spec`, `prep`, `render`, or `theme`
- [x] **CE-3.1.4** Edit `social_copy.md` to fix copy issues: if tone was off, sharpen the tone guide; if the character count was exceeded, add a hard-limit reminder
- [x] **CE-3.1.5** Run a second question (pick `q006` — national vacancy trend, template `trend`, geo `national`) as a spot check that the skill fixes hold for a different template type; save artifacts to `chart_a_day/output/q006/`
- [x] **CE-3.1.6** Add a second structured entry to `chart_a_day/MANUAL_RUN_LOG.md` for `q006`, then compare the `q003` and `q006` failures to identify reusable prompt fixes versus chart-specific code fixes

**CE-3.2 — Build `shared/chart_bridge.py`**
- [ ] **CE-3.2.1** Create `publisher/shared/` directory with an empty `__init__.py`
- [ ] **CE-3.2.2** Create `publisher/shared/db.py` — a thin DuckDB connection helper: `def get_connection(read_only=True) -> duckdb.DuckDBPyConnection` that reads the DB path from `FOUNDATIONS_PATH` env var (`<FOUNDATIONS_PATH>/etl/data/duckdb/patterns_in_place.duckdb`); raise a clear error if `FOUNDATIONS_PATH` is not set
- [ ] **CE-3.2.3** Create `publisher/shared/chart_bridge.py` with a single public function: `def render_chart(data: pd.DataFrame, chart_type: str, column_mapping: dict, title: str, subtitle: str | None, benchmark: dict | None, output_path: Path) -> Path` — internally builds a `ChartRequest` and calls `chart_engine_py.render()`; returns the path to the saved PNG
- [ ] **CE-3.2.4** Add `BenchmarkConfig` support in `chart_bridge.py`: if `benchmark` dict is provided (keys: `value`, `label`), build a `BenchmarkConfig` and attach it to the request
- [ ] **CE-3.2.5** Add `OutputConfig` in `chart_bridge.py`: always set `save=True` and route to `output_path`; always use `Theme.default()`
- [ ] **CE-3.2.6** Smoke test the bridge: write a 10-line test script that loads `q003/result.csv`, calls `render_chart()`, and confirms the PNG was written; run it and confirm it passes

**Verification:** `publisher/shared/` has `__init__.py`, `db.py`, `chart_bridge.py`. The smoke test script runs without error. The bridge function signature is documented with a one-line docstring.

---

#### CE-4 — `run_next.py` Runner

**Goal:** Wire `run_next.py` into a thin CLI that can run the full skill chain for the next `ready` question without manual steps. The CLI reads the backlog, picks the next `ready` entry, runs the three skills in sequence (SQL → chart → social copy), saves all artifacts, and updates the backlog status to `ran`. The skill steps call Claude via the SDK — this is agentic code, not a manual prompt invocation.

**Audit note:** The scaffold from CE-0.4 already has `--next`, `--status`, `--note`, `resolve_entry`, `print_status`, `append_note`. What CE-4 adds is the `run_skill_chain()` function and wires it into the `--next` flow.

- [ ] **CE-4.1** Add `run_skill_chain(entry: QueueEntry) -> Path` to `run_next.py`: orchestrates the three steps; creates `output/{q_id}/` if it doesn't exist; returns the output directory path
- [ ] **CE-4.2** Implement `run_sql_step(entry, output_dir)` in `run_next.py`: reads `backlog.yaml` entry fields, invokes `sql_agent.md` skill via the Claude SDK, saves `result.sql` and `result.csv`; raises on empty result set
- [ ] **CE-4.3** Implement `run_chart_step(entry, output_dir)` in `run_next.py`: reads `result.csv`, calls `shared.chart_bridge.render_chart()` with the appropriate chart type (derive from `template_id` using the same mapping as in `chart_request.md`), and saves the Python candidate as `chart_py.png`
- [ ] **CE-4.4** Implement `run_social_step(entry, output_dir)` in `run_next.py`: reads `result.csv` + `chart_py.png`, invokes `social_copy.md` skill via the Claude SDK, saves `post.md`, and only writes `post_x.md` / `post_bluesky.md` if the skill decides the copy should diverge by platform
- [ ] **CE-4.5** Write `question.md` at the end of `run_skill_chain()`: one-liner with question text, q_id, template, geo level, run timestamp
- [ ] **CE-4.6** Append a runner-generated partial entry to `chart_a_day/MANUAL_RUN_LOG.md` marking the Python portion `complete` and the R/parity portion `not_reviewed`
- [ ] **CE-4.7** After successful Python-side run, call `queue_manager.update_status(entry.id, "ran")` — this stamps `ran_at`; do not treat that status alone as parity completion
- [ ] **CE-4.8** Add artifact completeness check at the end of `run_skill_chain()`: verify the Python-side required files exist (`question.md`, `result.sql`, `result.csv`, `chart_py.png`, `post.md`); treat `post_x.md` and `post_bluesky.md` as optional platform-specific overlays; print which required files are missing if any
- [ ] **CE-4.9** Add `--dry-run` flag to `run_next.py`: prints which question would run and what steps would execute, but does not invoke Claude or write any files
- [ ] **CE-4.10** Add a follow-up reviewer step outside the runner: render `chart_r.png`, compare against `chart_py.png`, and update the existing `MANUAL_RUN_LOG.md` entry with the parity verdict before checking off the corresponding Phase 5 tracker item
- [ ] **CE-4.11** Test the runner end-to-end on `q004` (median gross rent trend): `python chart_a_day/runner/run_next.py --next`; confirm the Python-side artifact files are written and `backlog.yaml` shows `q004` as `ran`

**Verification:** `python run_next.py --status` shows correct counts. `python run_next.py --dry-run` prints the next ready question without side effects. `python run_next.py --next` on a clean `ready` entry produces the Python-side artifact set and updates the backlog. The corresponding Phase 5 checklist item is only checked off after `chart_r.png` and the final `MANUAL_RUN_LOG.md` parity verdict are added manually.

---

#### CE-5 — First 5 Posts End-to-End

**Goal:** Run five questions through the full `run_next.py` pipeline, review every artifact set, and produce five pairs of social copy ready to post. The emphasis is on quality review and iteration, not speed. By the end, you have five charts and ten post drafts (X + Bluesky for each) and a clear read on what the social copy still gets wrong.

- [ ] **CE-5.1** Run `run_next.py --next` for q004, q005, q007, q008, q013 — five questions across `trend`, `compare_selected`, and `growth` templates (mix of chart types)
- [ ] **CE-5.2** For each run: open the output folder; read `question.md`; review `chart_r.png` and `chart_py.png` side by side; read `post.md` plus any platform-specific variants that exist; write a one-paragraph verdict in `step_notes.md` and a structured verdict in `MANUAL_RUN_LOG.md` — is Python at parity, needs copy edit only, needs chart rework, or blocked?
- [ ] **CE-5.3** Fix any charts that failed or rendered poorly: note the specific `column_mapping`, `chart_type`, or Python parity gap that caused the issue; fix it in `chart_request.md` or `chart_engine_py` so the next run doesn't repeat it
- [ ] **CE-5.4** Edit social copy to post-ready quality for the best three of the five: keep edits minimal — fix factual errors, tighten the hook, cut to character limit
- [ ] **CE-5.5** Update `backlog.yaml`: any question whose copy is post-ready gets status `reviewed`; blocked questions get a `notes` update explaining the issue
- [ ] **CE-5.6** Write a brief skill iteration log at `chart_a_day/skills/ITERATION_LOG.md`: one section per skill, what changed after CE-5 runs and why
- [x] **CE-5.7** Summarize the first tranche (`q003`, `q006`, `q024`) at the top of `MANUAL_RUN_LOG.md`: recurring failure modes, instruction changes adopted, and what is now stable enough to scale across the rest of the backlog

**Verification:** Five output folders exist in `chart_a_day/output/`. At least three questions are at `reviewed` status in `backlog.yaml`. `ITERATION_LOG.md` exists with at least one entry per skill. `MANUAL_RUN_LOG.md` shows both per-run verdicts and a tranche-level summary.

---

#### CE-6 — Reviewer Tab in Frontend

**Goal:** Add a tab to `publisher/frontend/streamlit_app.py` that lets you review Chart Engine output without opening the file system. Shows the chart image, the two social copy drafts, approve/reject buttons that update `backlog.yaml` status.

**Audit note:** `frontend/streamlit_app.py` already exists with a QA tab for the chatbot. The Chart Engine tab is a new tab alongside it, reading from `chart_a_day/output/` instead of the chatbot pipeline. `chart_a_day/runner/queue_manager.py` already has `update_status()` — the frontend calls it directly.

- [ ] **CE-6.1** Add a `Chart Engine` tab to `streamlit_app.py` using `st.tabs()`
- [ ] **CE-6.2** In the tab: load `backlog.yaml` via `QueueManager`; display a `st.selectbox` of questions filtered to `ran` or `reviewed` status, showing `q_id + question text`
- [ ] **CE-6.3** On question select: show `st.image` of `chart_a_day/output/{q_id}/chart_py.png` by default, with a side-by-side option for `chart_r.png` when it exists; show `st.text_area` for `post.md` content (editable); if `post_x.md` or `post_bluesky.md` exist, expose them as optional override fields
- [ ] **CE-6.4** Add Save button: on click, write the edited text back to `post.md` and any platform-specific override files that were edited
- [ ] **CE-6.5** Add Approve button: calls `queue_manager.update_status(q_id, "reviewed")`; on success shows `st.success`
- [ ] **CE-6.6** Add Reject/Reset button: calls `queue_manager.update_status(q_id, "ready")`; clears the output folder (ask for confirmation first via `st.warning` + second click)
- [ ] **CE-6.7** Add a status summary sidebar in the tab: `st.metric` widgets showing counts by status (ready / ran / reviewed / posted)
- [ ] **CE-6.8** Test the tab locally: run `streamlit run frontend/streamlit_app.py`; confirm all five q003–q007 entries load, image shows, copy is editable, approve/reject updates the YAML

**Verification:** Tab renders without error. Approve/reject updates `backlog.yaml`. Edited copy is saved to disk. Character counts show on the text areas.

---

#### CE-7 — Engagement Telemetry

**Goal:** Add a lightweight log so every posted entry has a performance record. Start as a YAML append-log — one file, one entry per post. Graduate to DuckDB only after 20+ data points when the field set is stable.

- [ ] **CE-7.1** Create `chart_a_day/engagement_log.yaml` — empty list `[]` as initial state
- [ ] **CE-7.2** Define the log schema (document in file header comment): `q_id`, `posted_at`, `platform` (x / bluesky), `post_url`, `likes`, `replies`, `reposts`, `follows_gained`, `notes`
- [ ] **CE-7.3** Add a `log-engagement` subcommand to `run_next.py`: `python run_next.py --log-engagement --id q003 --platform x --url <url> --likes 12 --replies 3 --reposts 2`; appends to `engagement_log.yaml` and updates `backlog.yaml` status to `posted`
- [ ] **CE-7.4** Add engagement summary to the `--status` output: if `engagement_log.yaml` has entries, print average likes and total posts per platform
- [ ] **CE-7.5** Add an Engagement tab to `frontend/streamlit_app.py`: load `engagement_log.yaml`; show a table of all entries sorted by `posted_at`; show a bar chart of likes by `q_id` using `st.bar_chart`
- [ ] **CE-7.6** After 20+ entries, evaluate whether the field set is stable; if yes, write a migration script to move `engagement_log.yaml` into a DuckDB table at `chart_a_day/engagement.duckdb` (keep the YAML as a backup)

**Verification:** `run_next.py --log-engagement` appends to the YAML without overwriting prior entries. `--status` prints engagement summary when data exists. Engagement tab loads in the frontend.

---

#### CE-8 — Single Post vs Thread Decision

**Goal:** Analyze engagement data from 10+ posts across both formats; establish a default. This is a data task, not a build task — the deliverable is a decision recorded in the roadmap, not code.

- [ ] **CE-8.1** Ensure all canonical social drafts are tagged with format type (standalone vs thread opener), and only tag platform-specific files when they actually exist
- [ ] **CE-8.2** Filter `engagement_log.yaml` to 10+ posted entries; compute average likes + replies by format type and platform
- [ ] **CE-8.3** Write a one-page decision doc at `chart_a_day/FORMAT_DECISION.md`: the data, the conclusion, the default format going forward, and any exceptions (e.g. "threads for methodology-heavy charts")
- [ ] **CE-8.4** Update `social_copy.md` skill to default to the winning format; remove the "both formats" instruction

**Verification:** `FORMAT_DECISION.md` exists with numeric evidence. `social_copy.md` has a clear default format.

---

#### CE-9 — Automated Posting via API

**Goal:** Replace the manual copy-and-paste posting step with API calls. Start with Bluesky (free API) and evaluate X only after concept is proven and API cost is justified.

- [ ] **CE-9.1** Set up Bluesky API credentials: create an app password in Bluesky settings; store as environment variable `BLUESKY_APP_PASSWORD` and `BLUESKY_HANDLE`
- [ ] **CE-9.2** Install `atproto` Python client: `pip install atproto`; add to `requirements.txt`
- [ ] **CE-9.3** Create `chart_a_day/runner/post_bluesky.py`: `def post(q_id: str, copy_path: Path, image_path: Path) -> str` — authenticates, uploads image blob, creates post with text from the standalone section of `post_bluesky.md` when it exists, otherwise from `post.md`; returns the post URL
- [ ] **CE-9.4** Add `--post` flag to `run_next.py`: `python run_next.py --post --id q003 --platform bluesky` — calls `post_bluesky.post()`, logs engagement entry with the returned URL, updates status to `posted`
- [ ] **CE-9.5** Run a test post on a private/test Bluesky account before the real account; confirm image attaches correctly and character limit is not exceeded
- [ ] **CE-9.6** Evaluate X API: at this point, check the current X API v2 pricing for posting (it has changed multiple times); document the monthly cost for 30 posts/month at `chart_a_day/runner/X_API_EVAL.md`; decide whether to proceed
- [ ] **CE-9.7** If X API is justified: create `chart_a_day/runner/post_x.py` with the same interface as `post_bluesky.py`; use `tweepy` or the native `x-api-client`; store credentials as `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`
- [ ] **CE-9.8** Add rate limiting guard to both post functions: if `posted_at` for any entry in `engagement_log.yaml` has a timestamp within the last 2 hours, print a warning and require `--force` to override

**Verification:** Bluesky test post appears on the test account with image attached. `--post` updates `backlog.yaml` and appends to `engagement_log.yaml`. Rate limit guard blocks double-posting.

---

### Non-technical work (parallel)

- [ ] Finalize PiP X account handle and bio before CE-4 (posts need a destination)
- [ ] Finalize PiP Bluesky account — same
- [ ] Posting time decision: weekday mornings ET is the baseline for data content; adjust based on early engagement data
- [ ] Join: MotherDuck Slack, DuckDB Discord, Locally Optimistic, dbt Slack, BetaNYC Slack, ACS Data Users Group, Bluesky #rstats — chart posts land better in communities you're already in
- [ ] Engagement tracker setup: before CE-4 so you have data from the first posts

### Distribution activations (artifact-gated)

- After first X posts go live: reply to Jay Parsons with relevant housing charts (he engages independent analysts)
- After 5+ posts: r/dataisbeautiful, #rstats Bluesky, Lyman Stone replies
- After 10+ posts: evaluate X API cost for CE-8

---

## Track CH — Chatbot

**What it is:** An NL→SQL interactive product. User asks a plain-language question in a Streamlit UI; system parses intent, generates validated SQL against the semantic layer, executes it, renders a chart, and returns a text answer. Portfolio piece and demo of what the semantic layer enables. Also the technical vehicle for HIB-2 ("how we built a constrained NL-to-SQL chatbot").

**Current state:** The `Orchestrator`, intent parser, query pipeline, validator, executor, profiler, chart selector, and response assembler are all built and working locally against local DuckDB. The R subprocess renderer (`chatbot/charts/renderer.py`) is functional. Two gaps: (1) intelligence catalogs not wired into `catalogs.py`, (2) R renderer needs to be replaced with `shared/chart_bridge.py` before production deploy.

**Architecture note:** The `Orchestrator` is dependency-injected throughout — swapping `ChartRenderer` for a Python-backed renderer is a one-line constructor change once `shared/chart_bridge.py` exists. No rewrite.

### Milestones

| ID | Milestone | Description | Status | Depends on |
|---|---|---|---|---|
| CH-0 | Wire intelligence catalogs | Load `theme_catalog.yml`, `intelligence_catalog.yml`, `question_catalog.yml` into `chatbot/query/catalogs.py`; required before Intelligence frame queries work | Unblocked | — |
| CH-1 | Replace R renderer | Swap `chatbot/charts/renderer.py` to use `shared/chart_bridge.py` → `chart_engine_py`; R subprocess path retired | After CE-3 | CE-3 |
| CH-2 | Frontend QA | Confirm charts render in Streamlit browser UI (not just headlessly); verify full end-to-end flow locally | After CH-1 | CH-1 |
| CH-3 | Auth decision | Open public, shared-link, or email gate? Document the choice before any public deploy | Before CH-5 | — |
| CH-4 | MotherDuck promotion | Confirm `mart_intelligence` + Gold tables queryable from MotherDuck (shared dependency with Area Explorer Phase 2) | Track D item | Track D |
| CH-5 | Prod deploy | Streamlit Cloud + Groq; set `MOTHERDUCK_CONNECTION` + Groq API key as secrets; smoke test live URL | After CH-2, CH-3, CH-4 | CH-2, CH-3, CH-4 |
| CH-6 | QA tuning pass | Run representative questions through QA app; identify failure modes; tune prompts; document failure categories | After CH-5 | CH-5 |
| CH-7 | HIB-2 article | "How we built a constrained NL-to-SQL chatbot" — the technical article that turns the chatbot into a content asset; target: data engineering community, Show HN | After CH-5 | CH-5 |
| CH-8 | Benchmarking article | Compare semantic layer approaches (our constrained template approach vs. free-form LLM SQL generation) | After CH-7 | CH-7 |

### Non-technical work (parallel)

- [ ] Auth decision also involves: email list/waitlist gate? That's a Substack or Mailchimp list-building moment — think through before CH-3
- [ ] Show HN post framing: "Show HN: constrained NL-to-SQL for US metro data using a semantic layer instead of free-form LLM queries" — prep framing before CH-5 deploy
- [ ] Basic usage telemetry: log questions asked to an append-CSV or DuckDB table before going public — you'll want data on what people actually ask; set up at CH-5
- [ ] Join communities before CH-7: Hacker News account (post on the day of Show HN), MotherDuck Slack, dbt Slack semantic layer channels; the HIB-2 post lands better from a warm account

### Distribution activations (artifact-gated)

- After CH-5: Show HN post, MotherDuck devrel email, LinkedIn launch post
- After CH-7: dbt Slack semantic layer channels, DuckDB Discord, Locally Optimistic show-and-tell
- After CH-8: pitch MotherDuck for a community showcase post

---

## Sequencing Summary

```
NOW (no dependencies):
  DS-0    Rename content/ → data_stories/
  CE-0    Create chart_a_day/ structure, migrate backlog
  CH-0    Wire intelligence catalogs into chatbot
  —       Account setup: X, Bluesky, Substack
  —       Community joins: MotherDuck Slack, DuckDB Discord, BetaNYC, etc.
  —       Daily X engagement habit

NEXT (CE-0 done):
  CE-1    Draft three agent skills (sql_agent, chart_request, social_copy)
  DS-1    First published Data Story (pick from housing or vacancy backlog)

AFTER CE-1:
  CE-2    First manual run — one question end-to-end; this IS chart_engine_py Phase 5
  CE-3    Fix skill gaps; build shared/chart_bridge.py — completes Phase 5–6 as byproduct
  CE-4    run_next.py runner

AFTER CE-3 (chart_bridge stable):
  CH-1–CH-2   Chatbot chart rendering via chart_bridge; frontend QA

AFTER CH-2 + CH-3 + CH-4:
  CH-5        Chatbot prod deploy → Show HN
  CH-7        HIB-2 article

AFTER CE-4 (~5 posts live):
  CE-5        Reviewer tab in frontend
  CE-6        Engagement telemetry

AFTER ~10 posts:
  CE-7        Single post vs thread decision

AFTER CH-5 + DS-3 (L/O scatter):
  CE-8        Evaluate automated posting via API
  Lane 1      Email Kolko + Cortright
  —           posit::conf CFP watch (Jan 2027)
```

---

## Shared Foundations

Both Chart Engine and Chatbot call into the same shared layer. Neither product should import `chart_engine_py` directly — both go through `shared/chart_bridge.py`.

```
chart_a_day/runner/run_next.py  ──┐
                                    ├──► shared/chart_bridge.py ──► chart_engine_py.render()
chatbot/charts/renderer.py (CH-1) ─┘

Both products:
  shared/db.py ──► foundations/etl/data/duckdb/patterns_in_place.duckdb
  chatbot/query/catalogs.py ──► foundations/semantic_layer/
```

`shared/` does not import from `chatbot/` or `chart_a_day/`. It only imports from `foundations/`.

---

## Open Questions

- **First Data Story to publish:** Housing vacancy series has the most complete artifacts. L/O scatter (DS-3) is the flagship but needs Area Explorer Phase 1 verified first. Start with vacancy.
- **Social copy format:** Single post vs. thread — run both for first 10 Chart Engine posts, then decide. Don't prescribe before you have data.
- **Data Stories format:** Long-form vs. listicle vs. data take — learn by doing. The first three posts will define the format more than any spec.
- **Chatbot auth:** Open public, shared-link, or email gate? Decide at CH-3 before deploy.
- **Automated posting (CE-8):** X API requires payment. Bluesky API is free. Consider starting CE-8 with Bluesky only, then evaluating X when concept is proven and revenue justifies it.
- **Engagement telemetry:** Start manual (YAML log); graduate to DuckDB table once you have 20+ data points and know what fields matter.
