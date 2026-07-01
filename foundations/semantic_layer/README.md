# Patterns in Place — Semantic Layer

The semantic layer is the contract between the data warehouse and every product that queries it: the Chatbot, Area Explorer, and the Publisher pipeline. It lives entirely in this directory as a set of YAML files. Nothing downstream hardcodes table names, column names, or metric definitions — it reads them from here.

---

## What it does

The warehouse holds facts. The semantic layer answers three questions that facts alone can't answer:

1. **What does this column mean?** (`metric_catalog.yml`) — display name, unit format, which themes it belongs to, whether it can be used in growth calculations, and any caveats about coverage or interpretation.
2. **How do metrics combine into scores?** (`intelligence_catalog.yml`) — the full scoring and clustering models for the three Intelligence frames (Character, Livability, Opportunity) plus the Cross-Frame combined model, including KPI polarity, model roles, subject weights, and calibration status.
3. **How does the product surface this to a user?** (`theme_catalog.yml`, `question_catalog.yml`, `query_templates.yml`, `chart_rules.yml`) — topic groupings, pre-built question patterns, SQL execution templates, and chart selection rules.

---

## File map

```
semantic_layer/
│
│  ── Tier 1: Infrastructure ──────────────────────────────────────────────
│
├── table_catalog.yml          What Gold tables exist, their grain, primary key,
│                              supported geo levels, and column list.
│
├── metric_catalog.yml         Every queryable metric: source table, source column,
│                              unit format, theme membership, geo coverage, and caveats.
│                              Must be updated before any other catalog can reference
│                              a new metric.
│
├── join_catalog.yml           How Gold tables join to each other and to the CBSA/tract
│                              spine. Join keys, join type, grain-change notes.
│
├── geography_catalog.yml      The geographic levels the platform supports (us, region,
│                              division, state, cbsa, county, place, zcta, tract) and
│                              the dimension tables that anchor them.
│
├── points_catalog.yml         Points layer source families (POI, parcels, neighborhood
│                              boundaries). Sparse — fills in during Deep Dive work.
│
│  ── Tier 2: Intelligence ─────────────────────────────────────────────────
│
├── intelligence_catalog.yml   The scoring and clustering models for the three
│                              Intelligence frames. Subject → topic → KPI hierarchy
│                              with polarity flags, model roles (core / sensitivity /
│                              descriptive / dropped), reliability tiers, coverage
│                              rates, and calibration status per frame, plus the
│                              Cross-Frame combined surface.
│
│  ── Tier 3: Navigation and Presentation ──────────────────────────────────
│
├── theme_catalog.yml          User-facing topic groupings for Chatbot and Area Explorer.
│                              Organized by theme (Character / Livability / Opportunity).
│                              Reflects the calibrated Phase 2–4 topic structure.
│
├── question_catalog.yml       Canonical question definitions for the Chatbot and Publisher
│                              pipeline. Each entry carries semantic metadata AND a
│                              structured_query_plan used as a few-shot example by the
│                              LLM intent parser. Single source of truth for questions.
│
├── query_templates.yml        Named SQL execution templates. The parser resolves a
│                              question to a template_id; the generator builds SQL from
│                              the template's required and optional slots.
│
├── chart_rules.yml            Rules for auto-selecting chart type given metric type,
│                              geo level, and question intent.
│
│  ── Generated ────────────────────────────────────────────────────────────
│
└── artifacts/                 Derived graph outputs (mermaid, JSON). Regenerated from
                               the YAML catalogs — never hand-edited.
```

---

## The three-tier dependency rule

Tiers flow in one direction. Never reference something in a downstream tier before it exists in the tier above it.

```
Tier 1 — Infrastructure
    ↓  (metric_catalog.yml must have the metric before...)
Tier 2 — Intelligence
    ↓  (intelligence_catalog.yml must be calibrated before...)
Tier 3 — Navigation and Presentation
```

In practice: if you add a new Gold column, update `metric_catalog.yml` first. Then reference it in `intelligence_catalog.yml` if it belongs in a frame model. Then add it to `theme_catalog.yml` topics and any relevant `question_catalog.yml` entries.

---

## How a user question becomes a SQL result

```
User question (natural language)
    ↓
IntentParser (publisher/chatbot/intent/parser.py)
    — loads question_catalog.yml as few-shot examples
    — loads metric_catalog.yml and table_catalog.yml to validate metric/table references
    — resolves to a QueryPlan (question_type, metric_id, source_table, geo_level, etc.)
    ↓
QueryPlanner (publisher/chatbot/query/planner.py)
    — fills deterministic defaults from query_templates.yml required/optional slots
    ↓
SQLGenerator
    — builds SQL using the template shape and catalog-resolved field names
    ↓
Result → Chart (chart_rules.yml selects chart type)
```

For Intelligence frame questions (score lookups, archetype queries, peer comparisons), the `question_type` is `frame_lookup` and the template routes to a row lookup against the appropriate `mart_intelligence.intelligence_*` table rather than an aggregation query.

---

## Intelligence frame architecture

The three frames — Character, Livability, Opportunity — each produce the same artifact set from a shared architecture:

**Scoring hierarchy**
```
KPI z-score (sign-flipped for negative polarity)
    → Topic score      (mean of KPI z-scores within topic)
        → Subject score    (weighted mean of topic scores)
            → Frame composite  (weighted mean of subject scores)
                → Percentile rank  (0–100 within the published CBSA universe)
```

**Clustering sequence** (run on the same standardized KPI vectors)
1. Hierarchical agglomerative — discovers the natural cluster count (k) from the dendrogram
2. K-Means at natural k — hard cluster labels for publication
3. Gaussian Mixture Model at same k — soft membership probabilities that capture metros sitting between archetypes

**Similarity** — cosine distance on the standardized KPI vectors; top-10 peer CBSAs per frame per CBSA.

**Calibration status** — each frame entry in `intelligence_catalog.yml` carries a `status` field:
- `placeholder` — not yet started
- `specified` — architecture defined, not yet run
- `calibrated` — notebook complete, natural_k confirmed, outputs written

Current status: Livability (Phase 3), Opportunity (Phase 4), Character (Phase 2), and Cross-Frame combined model (Phase 5) are all `calibrated`.

---

## Intelligence DataMart tables

The scored outputs from each frame phase are promoted to DuckDB `mart_intelligence` tables via loader scripts in `foundations/loaders/`. These are the tables the Chatbot and Area Explorer query for Intelligence frame questions.

| Table | Frame | Status | Loader script |
|---|---|---|---|
| `mart_intelligence.intelligence_livability` | Livability | Active | `load_livability_scores.R` |
| `mart_intelligence.intelligence_opportunity` | Opportunity | Active | `load_opportunity_scores.R` |
| `mart_intelligence.intelligence_character` | Character | Active | `load_character_scores.R` |
| `mart_intelligence.intelligence_cross_frame` | Combined | Active | `load_cross_frame_scores.R` |
| `mart_intelligence.intelligence_zones` | Zone Methodology | Active | `load_zone_assignments.R` |
| `mart_intelligence.intelligence_zones_zcta` | Zone Methodology ZCTA Rollup | Active | `load_zone_scores_zcta.R` |

The Phase 2–5 intelligence tables are static CBSA-grain lookups — one row per CBSA, no year dimension. They contain normalized semantic aliases for cluster label, GMM soft membership probabilities, subject z-scores, frame composite percentile rank, and promoted top-10 peer columns. The Cross-Frame mart also carries overlap/divergence context such as `frame_percentile_gap`, `overlap_profile`, and frame leaders/laggards. `mart_intelligence.intelligence_zones` is the tract-grain Phase 7 output and carries the final `k = 7` zone type label, theme scores, percentile context, opportunity-zone flag, and standardized KPI columns used to interpret each tract assignment. `mart_intelligence.intelligence_zones_zcta` is the downstream ZCTA rollup built from HUD tract-to-ZCTA population weights; it keeps the dominant-vs-mixed assignment plus the full weighted zone-share vector for each ZCTA.

---

## Maintenance rules

### Adding a new Gold table or metric family

1. `table_catalog.yml` — add table entry
2. `metric_catalog.yml` — add all metric entries
3. `join_catalog.yml` — add join relationship
4. `intelligence_catalog.yml` — add metrics if they belong in a frame model
5. `theme_catalog.yml` — add to relevant topic (defer if Intelligence not yet calibrated)

### Completing an Intelligence phase notebook

1. `metric_catalog.yml` — add any derived metrics created during the notebook
2. `intelligence_catalog.yml` — set `status: calibrated`, populate `natural_k`, add `calibration_notes`, update `model_role` for any KPIs that changed
3. `theme_catalog.yml` — update topic membership to match calibrated structure
4. `question_catalog.yml` — add questions surfaced by hypothesis tests

### Adding a new question to the Chatbot

1. `question_catalog.yml` — add entry with `natural_language_question`, `structured_query_plan`, and semantic metadata
2. `query_templates.yml` — add a new template only if the question requires a new query shape not already covered
3. No other files need to change for new questions against existing tables and metrics

### Phase 8 — Catalog finalization and DuckDB promotion

1. Verify all `intelligence_catalog.yml` entries are `status: calibrated`
2. Verify all `metric_catalog.yml` entries referenced in Intelligence exist with correct `source_table`
3. Confirm `theme_catalog.yml` topic structure matches calibrated frames
4. Run `foundations/loaders/` R scripts to promote parquets to the `mart_intelligence` DataMart
5. Regenerate artifacts: `python3 -m semantic_layer.visualize --format artifacts`

---

## Generate artifacts

```bash
# Write graph artifacts to artifacts/
python3 -m semantic_layer.visualize --format artifacts

# Print a human-readable summary
python3 -m semantic_layer.visualize --format summary

# Print Mermaid diagram to stdout
python3 -m semantic_layer.visualize --format mermaid
```

## Explore in Python

```python
from semantic_layer.graph_builder import load_catalogs, build_semantic_graph

catalogs = load_catalogs()
graph = build_semantic_graph(catalogs)

# List all theme nodes
theme_nodes = [n for n, d in graph.nodes(data=True) if d["kind"] == "theme"]
```

---

## Source of truth

- YAML files in this directory are authoritative — not the warehouse, not any downstream product config.
- `artifacts/` is derived — regenerate, never hand-edit.
- The live warehouse (`metro_deep_dive.duckdb`) is the source for field names and coverage data when refreshing catalogs; the catalog is the source for everything the products consume.
