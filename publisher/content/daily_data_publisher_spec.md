# Daily Data Publisher
### Product Spec — `metro_deep_dive_chatbot/analysis/`

**Last updated:** 2026-05-13
**Status:** Active
**Goal:** Publish 3x/week data posts to X and Substack. Build the manual workflow first — understand what good looks like before automating anything.

---

## What This Is

A manual, editorial-first publishing workflow. We pick a topic, explore the data, write the SQL by hand, render the chart through the R visual library, and write the copy ourselves. No automated runners, no queue managers, no pipeline orchestration.

The work is organized by topic. One topic yields multiple insights and multiple posts. This keeps related analyses together, makes the editorial arc visible, and lets us publish a coherent series rather than disconnected one-offs.

---

## Why Manual First

The chatbot pipeline (intent parser → SQL generator → chart renderer → assembler) is built and works. But running questions through it before we understand the editorial workflow would produce outputs we can't evaluate properly. We need to know what a good post looks like — what SQL produces the right shape, what chart type earns its place, what copy actually lands — before we can judge whether the pipeline produces it.

Every post in this folder is a lesson. The lessons feed back into the pipeline directly: better SQL templates, sharper chart selection rules, a clearer picture of what post-ready language looks like vs. analytical language.

---

## The Model: Topic → Insights → Posts

```
Topic (e.g. Vacancy Rates)
├── Insight 1: National trend          → 1 post
├── Insight 2: Metro rankings          → 1 post
├── Insight 3: State map               → 1 post
└── Insight 4: Regional breakdown      → 1 post
```

A topic is a data area with a unifying thesis. Insights are distinct angles on that thesis — each answerable with one chart and one piece of copy. One topic typically yields 3–5 posts that can be published as a series or spaced across weeks.

---

## Workflow (Per Insight)

```
1. QUESTION   — write question.md before touching the data
2. EDA        — explore the data; establish what's actually there
3. FINDINGS   — write findings.md: key stats, confirmed angle, surprises
4. SQL        — write query.sql in the chart's required column contract format
5. EXECUTE    — run SQL → result.csv
6. CONFIG     — write chart_config.json: title, subtitle, dimensions, label style
7. RENDER     — Rscript → chart.png; review and iterate on config
8. SUMMARY    — write summary.md: 2–3 sentences, data-first
9. SOCIAL     — write post_draft.md: X post + thread + Substack caption
```

**The critical rule:** `question.md` is always written before EDA. It captures the editorial hypothesis cold — what you expect the data to show and why it's worth a post. `findings.md` captures what the data actually showed. The gap between the two is where the learning is.

---

## Artifact Contract

Every insight folder contains the same set of files:

| File | Written by | Written when | Purpose |
|------|-----------|--------------|---------|
| `question.md` | Me | Before EDA | Editorial brief: question, angle, visual hypothesis, audience |
| `findings.md` | Both | After EDA | Key stats, confirmed angle, surprises, data notes |
| `query.sql` | Agent | After findings | Hand-written SQL in the chart's column contract format |
| `result.csv` | Agent | After SQL | Query output — the data the chart is built from |
| `chart_config.json` | Agent | After result | R renderer config: title, subtitle, dimensions, label style |
| `chart.png` | Agent | After config | Rendered chart — reviewed and iterated until publish-ready |
| `summary.md` | Both | After chart | 2–3 sentence analytical interpretation |
| `post_draft.md` | Both | After summary | X post + optional thread + Substack caption |

---

## Topic Structure

Each topic lives in its own folder under `analysis/`:

```
analysis/
└── {topic}/
    ├── README.md      ← story, key numbers, planned insights, publish order
    ├── TASKS.md       ← checklist tracking build progress across all insights
    └── {insight}/
        ├── question.md
        ├── findings.md
        ├── query.sql
        ├── result.csv
        ├── chart_config.json
        ├── chart.png
        ├── summary.md
        └── post_draft.md
```

The topic `README.md` is written after initial EDA on the topic as a whole. It captures the unifying thesis, key numbers across all planned insights, the publish order, and any cross-cutting data notes. It is the first thing an agent should read when picking up work on a topic.

`TASKS.md` is the working checklist. It tracks the 9-step sequence for each insight with owner labels (Me / Agent / Both). Check tasks off as they complete.

---

## Scope

**In scope:**
- Topic-based analysis folders with the standard artifact set
- Hand-written SQL against the gold-layer DuckDB tables
- Chart rendering via the R visual library
- Post copy for X and Substack
- Skill writing: `question.md` and `findings.md` as a prompt engineering practice ground
- Pipeline signal: insights that reveal gaps in the chatbot's SQL templates, chart selection, or response assembly

**Out of scope (for now):**
- Automated runners or queue managers
- Direct API posting to X or Substack
- Engagement tracking
- Modifying the `app/` pipeline based on findings here (tracked separately)

---

## Publishing Cadence

**Target:** 3x/week  
**Unit of work:** one insight = one post  
**Review buffer:** at least one day between `chart.png` approval and posting  
**Trigger:** fully manual — no scheduling

Keep the topic queue at least one full topic (3–5 insights) ahead of the current publish week.

---

## Relationship to the Chatbot Pipeline

This workflow runs alongside the chatbot, not through it. But everything learned here feeds back in:

| What we learn here | Where it feeds back |
|---|---|
| Which SQL patterns produce clean chart-ready output | `semantic_layer/query_templates.yml` |
| Which chart types work for which question shapes | `semantic_layer/chart_rules.yml` |
| What post-ready language sounds like | `app/response/assembler.py` tone |
| Which question phrasings cause ambiguity | `app/intent/parser.py` examples |
| Real questions that worked end-to-end | `examples/` question library |

---

## Future Automation

Once the manual workflow is proven across 10–15 posts, revisit:

- **Queue manager:** YAML-based editorial backlog with status tracking (`ready → ran → reviewed → posted`)
- **Runner:** thin wrapper around `app/scripts/ask.py` that reads from the queue and saves artifacts to the topic folder structure
- **Summarizer:** template mode first (reformats `assembler.py` output), then an optional Groq LLM call for social-native copy
- **Skill files:** `question.md` and `findings.md` templates evolve into runtime-loadable prompt files with YAML front matter

The automation should conform to the proven manual workflow — not define it.
