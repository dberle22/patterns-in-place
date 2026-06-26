# Area Explorer — Roadmap & Spec

*Last updated: 2026-06-19. This document is the product spec and build roadmap for all Area Explorer apps. It supersedes the brief notes in `README.md`. Tactical Intelligence Layer work lives in `INTELLIGENCE_LAYER_ROADMAP.md`.*

---

## What this product is

Area Explorer is the metric-first analytical surface for the Patterns in Place data platform. It answers the question: **given a metric, how do all places rank?** It is not a place-first product (that is the Deep Dive Research Tool, see `metro-deep-dive/RESEARCH_TOOL_ROADMAP.md`), and it is not a question-first product (that is the Chatbot/Publisher flow).

The entry point is always: pick a theme → pick a subject → pick a topic → pick a metric. The map, ranking table, scatter, and trend charts all update around that selection.

---

## Product scope

Three independent Streamlit apps, connected by a landing page. Each app is self-contained — cross-links open in a new tab via URL. No shared navigation state between apps.

| App | Audience | Intelligence frames | Grain | Priority |
|---|---|---|---|---|
| `cbsa_internal` | Dan (analytical) | Yes — clusters, scores, peers | CBSA | 1 |
| `cbsa_public` | Readers / clients | No — metrics and benchmarks only | CBSA | 2 |
| `county_explorer` | Both | No | County | 3 |
| `landing` | Both | — | — | 4 |

The two CBSA apps share a codebase via `shared/` but are separate Streamlit entry points with separate configs. The county app is fully independent. The landing page links them all together.

---

## Repository structure

```
area-explorer/
  AREA_EXPLORER_ROADMAP.md        ← this file
  README.md                       ← quick-start and running instructions
  landing/
    index.py                      ← Streamlit landing page (links to each app)
  apps/
    cbsa_internal/
      app.py                      ← entry point
      config.py                   ← internal-specific feature flags and constants
    cbsa_public/
      app.py                      ← entry point
      config.py                   ← public-specific label overrides, no Intel flags
    county_explorer/
      app.py                      ← entry point
      config.py
  shared/
    db.py                         ← DuckDB connection + all cached query functions
    catalog.py                    ← loads metric_catalog.yml, theme_catalog.yml at startup
    geo_utils.py                  ← GeoJSON loader, geometry helpers
    chart_utils.py                ← Plotly map + chart factory functions
    benchmark.py                  ← national + division percentile rank helpers
    components/
      sidebar.py                  ← metric-first sidebar (theme → subject → topic → metric)
      map_panel.py                ← choropleth panel component
      ranking_table.py            ← ranking table component
      profile_panel.py            ← clicked-place profile card component
      scatter_tab.py              ← scatter plot tab
      trend_tab.py                ← trend line tab
      distribution_tab.py         ← distribution histogram tab
      intelligence_tab.py         ← L/O four-quadrant + cluster view (internal only)
  data/
    cbsa_boundaries.geojson       ← pre-baked simplified CBSA boundaries (Census TIGER 2023)
    county_boundaries.geojson     ← pre-baked simplified county boundaries
    state_boundaries.geojson      ← state outlines for reference layer
  tests/
    test_db.py
    test_catalog.py
    test_benchmark.py
```

The existing `app/data_explorer.py` and `app/explorer_utils.py` are migration-state reference. They become the skeleton for `shared/db.py` and `apps/cbsa_public/app.py`. Once the new structure is built they can be removed.

---

## Metric-first navigation hierarchy

The sidebar always follows this hierarchy, derived directly from the semantic layer catalogs:

```
Theme  →  Subject  →  Topic  →  Metric
```

**Theme** maps to the three Intelligence frames plus a Raw catch-all:
- Character (public label: "Community Profile")
- Livability (public label: "Quality of Life")
- Opportunity (public label: "Economic Conditions")
- Raw / All Metrics (advanced picker, bypasses hierarchy)

**Subject** is the second level within each theme (e.g., Livability → Affordability / Health & Safety / Access & Infrastructure / Physical Environment).

**Topic** is the third level (e.g., Affordability → Housing Burden / Price Pressure / Poverty Context).

**Metric** is the leaf — a single column from a Gold table.

Selecting at any level above Metric is valid: selecting a Subject maps the subject score (internal app) or a representative metric (public app). The sidebar renders whichever level the user stopped at. The `catalog.py` module builds the full hierarchy tree at startup from `metric_catalog.yml` and `theme_catalog.yml`, filtered by `valid_geo_levels` for the current app's grain.

---

## Benchmark context

Every metric value is shown with three benchmark lines, consistently formatted. This applies to both CBSA apps and the county app.

| Benchmark | Example display |
|---|---|
| Raw value | `$1,450 / month` |
| National | `62nd percentile nationally (among 401 CBSAs)` |
| Census Division | `48th percentile in South Atlantic Division` |

Percentile ranks are computed as window functions over the data at query time — no precomputed rank columns needed until Intelligence Phase 8 promotes the scored parquets to Gold tables (at which point the internal app uses the pre-computed frame percentile ranks directly).

---

## Layout — CBSA Internal app

The analytical surface. Intelligence frames, cluster labels, and similarity peers are first-class. This is the tool for building and verifying the Intelligence work, and for selecting Deep Dive markets.

### Sidebar

- Theme picker (Character / Livability / Opportunity / Raw)
- Subject picker (filtered by theme)
- Topic picker (filtered by subject — optional, can select at subject level)
- Metric picker (filtered by topic — filtered by `valid_geo_levels: cbsa`)
- Year selector (slider, defaults to latest available)
- State filter (multi-select, optional)
- Color scale toggle: Auto / Quantile / Raw

### Main area

```
┌──────────────────────────────────────┬──────────────────────────────┐
│  Choropleth map                      │  Ranking table               │
│                                      │                              │
│  Plotly choropleth_mapbox            │  All 401 CBSAs, sorted by    │
│  Token-free (geojson= local file)    │  selected metric             │
│  Simplified CBSA boundaries          │  Top / Bottom toggle         │
│                                      │  Click row → profile panel  │
│  Hover tooltip:                      │                              │
│    CBSA name                         ├──────────────────────────────┤
│    Metric value + units              │  Profile panel               │
│    National percentile               │  (appears on click)          │
│    Census Division percentile        │                              │
│    Cluster label + type              │  Selected CBSA:              │
│    (Intelligence frames only)        │  - KPI value + benchmarks    │
│                                      │  - Character cluster label   │
│  Click → locks profile panel         │  - Livability cluster label  │
│                                      │  - Opportunity cluster label │
│                                      │  - GMM soft membership       │
│                                      │    (top 2 cluster affinities)│
│                                      │  - Top 5 cosine-similarity   │
│                                      │    peers (per selected frame)│
└──────────────────────────────────────┴──────────────────────────────┘
┌────────────────────────────────────────────────────────────────────┐
│  Context row — four tabs                                           │
│                                                                    │
│  [Scatter]  [Trend]  [Distribution]  [Intelligence]               │
└────────────────────────────────────────────────────────────────────┘
```

### Context tabs — internal app

**Scatter tab**
- X-axis metric picker, Y-axis metric picker (independent of sidebar selection)
- 401 CBSAs as points
- Color by: Character cluster / Livability cluster / Opportunity cluster / Census Division
- Selected CBSA highlighted with a larger marker and label
- Hover shows CBSA name, X value, Y value, cluster label
- Default view: Livability percentile (X) vs. Opportunity percentile (Y) — Article 1 view

**Trend tab**
- Line chart for selected metric over available years
- Selected CBSA as the primary line
- Add up to 3 comparison CBSAs (searchable multi-select)
- National median and Census Division median as reference lines (dashed)

**Distribution tab**
- Histogram of selected metric across 401 CBSAs
- Selected CBSA annotated with a vertical line and label
- Bin count auto-tuned to data range; outlier handling via quantile clip option

**Intelligence tab** *(internal only)*
- Primary view: L/O four-quadrant scatter
  - X = Livability percentile rank, Y = Opportunity percentile rank
  - Color = Character cluster label (default) or Census Division
  - Quadrant labels: Unicorns (high/high) / Pleasant but Stagnant (high L / low O) / High-Growth Expensive (low L / high O) / Distressed (low/low)
  - "Highlight state" filter: dims all metros outside selected state(s)
  - Selected CBSA pinned with label
- Secondary view: Cluster membership table — all 401 CBSAs with their three cluster labels, GMM top-2 probabilities, and cross-frame divergence flag from Phase 5
- Toggle between primary and secondary views within the tab

---

## Layout — CBSA Public app

Same structural skeleton as the internal app, with content and framing adjusted for a reader or client audience.

### What is removed vs. internal

- No cluster labels anywhere — not in the hover tooltip, not in the profile panel
- No Intelligence tab in the context row
- No GMM soft memberships
- No cosine-similarity peer panel
- No "frame percentile" language — all ranks are described as "X% of comparable metro areas"

### What is different vs. internal

**Theme labels (public-facing):**
- "Community Profile" instead of "Character"
- "Quality of Life" instead of "Livability"
- "Economic Conditions" instead of "Opportunity"

**Benchmark language:**
- "Better than 62% of comparable metro areas nationally" instead of "62nd percentile"
- "Similar to the South Atlantic region average" instead of a raw division rank

**Profile panel:**
- Shows KPI values and the two benchmark lines (national, division)
- Does not show cluster labels or frame scores
- Shows a "similar metros" list based on size and geography rather than cosine similarity (to avoid surfacing model internals before the methodology is published)

**Scatter tab defaults:**
- Default to median household income (X) vs. rent-to-income ratio (Y) — a reader-friendly pair — rather than the L/O frame scatter

**Deployment:**
- Deployed on Streamlit Cloud
- Shareable URL for embedding in Substack or a landing page
- No local DuckDB — connects to MotherDuck only

---

## Layout — County Explorer

Independent app. No Intelligence frames. County-level metrics from `gold.population_demographics`, `gold.housing_core_wide`, `gold.economics_income_wide`, `gold.affordability_wide`, `gold.economics_labor_wide`.

### Differences from CBSA apps

- State filter is **required** as the first selection (national county map at 3,100+ polygons is too slow for a default view; state-filtered view is fast and useful)
- "Show all states" is available as a toggle for users who want the national view and accept the slower render
- No Intelligence tab
- Profile panel shows county KPI values + national and state-level benchmark (not Census Division — state is the more natural comparator for county)
- Ranking table defaults to within-state ranking; toggle to national ranking available

### Layout

```
┌──────────────────────────────────────┬──────────────────────────────┐
│  State-filtered choropleth           │  Ranking table               │
│  (defaults to state filter required) │  Within-state or national    │
│                                      │  toggle                      │
│  Hover: county name, metric value,   │                              │
│  national pct, state pct             ├──────────────────────────────┤
│                                      │  Profile panel               │
│                                      │  KPI values + benchmarks     │
└──────────────────────────────────────┴──────────────────────────────┘
┌────────────────────────────────────────────────────────────────────┐
│  [Scatter]  [Trend]  [Distribution]                                │
└────────────────────────────────────────────────────────────────────┘
```

No drill-down from CBSA → County in this phase. The two apps are independent views. The county app links to the CBSA app via the landing page nav.

---

## Technical decisions

### Map rendering

`plotly.express.choropleth_mapbox` with `geojson=` pointing to a local pre-baked GeoJSON. No Mapbox token required for the token-free approach. The `mapbox_style="white-bg"` or `"carto-positron"` tile base works without a token.

CBSA boundaries: Census TIGER 2023 cartographic boundary files (20m resolution), simplified to ~5% detail using `mapshaper`. Stored in `area-explorer/data/`. Loaded once at startup via `@st.cache_data(hash_funcs=...)` — do not re-read the GeoJSON on every rerender.

For the county app, state-filtered GeoJSON slices are faster to load than the full national file. Pre-bake one file per state and load on state selection, or load the full file and filter in Python.

### Query layer

`duckdb.connect(db_path)` where `db_path` is `DB_CONNECTION` env var (local DuckDB) or `MOTHERDUCK_CONNECTION` (MotherDuck for the public app). All SQL in `shared/db.py` — no inline SQL in app files or component files.

All data queries wrapped in `@st.cache_data(ttl=3600)`. Cache key includes geo_level, metric, year, and state filter so changing any selector triggers a fresh query.

### Catalog-driven metric menus

Sidebar pickers read from `metric_catalog.yml` and `theme_catalog.yml` via `shared/catalog.py`. The KPI options dict in `data_explorer.py` is hardcoded — replace it with a catalog-driven build that reads `valid_geo_levels`, `themes`, and `subject_areas` per metric. Adding a metric to the catalog makes it available in the app automatically.

### Benchmark percentile computation

For the public app and the county app, national and division percentile ranks are computed at query time as a window function:

```sql
PERCENT_RANK() OVER (
    PARTITION BY geo_level, year
    ORDER BY {metric_column}
) * 100 AS national_pct_rank

PERCENT_RANK() OVER (
    PARTITION BY geo_level, census_division, year
    ORDER BY {metric_column}
) * 100 AS division_pct_rank
```

For the internal CBSA app, these are supplemented by the pre-computed frame percentile ranks from `mart_intelligence.intelligence_livability`, `mart_intelligence.intelligence_opportunity`, `mart_intelligence.intelligence_character` once those tables are populated (Intelligence Phase 8).

### State management

Streamlit `session_state` tracks:
- `selected_geo_id` — the CBSA or county currently pinned in the profile panel (set by map click or table row click; cleared by clicking elsewhere)
- `selected_metric` — the current leaf metric in the sidebar
- `selected_year` — from the year slider
- `active_context_tab` — which of the four context tabs is open
- `state_filter` — list of selected state FIPS
- `scatter_x`, `scatter_y` — independent metric selectors for the scatter tab
- `trend_comparisons` — list of comparison geo_ids for the trend tab

### Performance targets

- Initial load (cold): < 5 seconds
- Metric switch (cached): < 1 second
- Map re-render on metric change: < 2 seconds
- Profile panel open on click: < 500ms
- County app state switch (new state GeoJSON): < 3 seconds

### Deployment

| App | Deployment | Connection |
|---|---|---|
| `cbsa_internal` | Local only | Local DuckDB |
| `cbsa_public` | Streamlit Cloud | MotherDuck |
| `county_explorer` | Streamlit Cloud (Phase 3) | MotherDuck |
| `landing` | Streamlit Cloud | None |

---

## Build phases

### Phase 1 — Shared foundation + CBSA Internal

**Goal:** Replace `data_explorer.py` with the new architecture. Ship a working internal CBSA app with Intelligence frame support.

**Prerequisites:**
- Intelligence Phases 3, 4, 2 complete (all CBSA frame models built) ✓
- `mart_intelligence.intelligence_livability`, `mart_intelligence.intelligence_opportunity`, `mart_intelligence.intelligence_character` populated in DuckDB (Intelligence Phase 8)
- Pre-baked CBSA GeoJSON in `area-explorer/data/`

**Work:**

1. **`shared/db.py`** — refactor `explorer_utils.py` into a clean query module. Functions: `get_connection()`, `query_metric(geo_level, metric, year, state_filter)`, `query_benchmark_ranks(geo_level, metric, year)`, `query_intelligence_scores(cbsa_code)`, `query_similarity_peers(cbsa_code, frame)`, `query_available_years(table, geo_level)`.

2. **`shared/catalog.py`** — load `metric_catalog.yml` and `theme_catalog.yml` at startup. Build the theme → subject → topic → metric hierarchy tree. Expose `get_metrics_for_geo_level(geo_level)`, `get_hierarchy()`, `get_metric_meta(metric_id)`.

3. **`shared/geo_utils.py`** — load and cache GeoJSON files. Merge metric data onto GeoJSON features for Plotly rendering. Expose `load_cbsa_geojson()`, `merge_data_onto_geojson(geojson, df, geo_id_col, value_col)`.

4. **`shared/benchmark.py`** — compute national and Census Division percentile ranks. Expose `add_benchmark_ranks(df, metric_col, division_col)`.

5. **`shared/components/`** — build each UI component as a standalone function that takes data and returns rendered Streamlit output. Components do not query the DB — they receive pre-loaded DataFrames.

6. **`apps/cbsa_internal/app.py`** — wire the sidebar, map, ranking table, profile panel, and four context tabs. Internal config enables: cluster labels in hover, Intelligence tab, GMM memberships, peer panel.

7. **Pre-bake GeoJSON** — download Census TIGER 2023 CBSA shapefile, simplify with `mapshaper`, export to `data/cbsa_boundaries.geojson`.

**Deliverable:** `cbsa_internal` running locally against local DuckDB, with all four context tabs working and Intelligence frame data visible.

---

### Phase 2 — CBSA Public app

**Goal:** Ship the reader-facing CBSA app on Streamlit Cloud.

**Prerequisites:**
- Phase 1 shared foundation complete
- MotherDuck connection tested
- Public-facing label review done (theme names, benchmark language)

**Work:**

1. **`apps/cbsa_public/config.py`** — feature flags: `show_intelligence = False`, public theme label overrides, public benchmark language strings.

2. **`apps/cbsa_public/app.py`** — same structure as internal app, but config gates out cluster labels, the Intelligence tab, and the peer similarity panel. Scatter tab defaults to a reader-friendly metric pair.

3. **Streamlit Cloud deployment** — set `MOTHERDUCK_CONNECTION` secret in Streamlit Cloud settings. Confirm the public app reads from MotherDuck, not local file path.

4. **Landing page** — `landing/index.py`: title, one-line description per app, link to each. Deployed alongside the public app on Streamlit Cloud.

**Deliverable:** `cbsa_public` live on Streamlit Cloud with a shareable URL. Landing page live.

---

### Phase 3 — County Explorer

**Goal:** Ship a county-level metric explorer, state-filtered by default.

**Prerequisites:**
- Phase 1 shared foundation complete
- County GeoJSON pre-baked
- Confirm which Gold tables have county grain (population_demographics, housing_core_wide, economics_income_wide, affordability_wide, economics_labor_wide all have county grain per table_catalog.yml)

**Work:**

1. **Pre-bake county GeoJSON** — Census TIGER 2023 county cartographic boundaries. Option A: one large national file (~30MB simplified). Option B: one file per state (~0.5MB each). Decision: pre-bake by state, load on state selection.

2. **`apps/county_explorer/app.py`** — same shared components as CBSA apps. County-specific differences: state filter required as first step, profile panel uses state percentile instead of Census Division percentile, ranking table defaults to within-state.

3. **Link from CBSA apps to county app** — add a "Explore counties in [selected state]" link in the CBSA profile panel that opens the county app pre-filtered to that state.

**Deliverable:** `county_explorer` running locally and deployed to Streamlit Cloud.

---

### Phase 4 — Zone Layer (depends on Intelligence Phase 7)

**Goal:** Add a tract-level zone view to the CBSA internal app, using the zone cluster labels from Intelligence Phase 7.

**Prerequisites:**
- Intelligence Phase 7 (Zone Methodology) complete
- `mart_intelligence.intelligence_zones` populated in DuckDB
- Tract-level GeoJSON for the Deep Dive markets (Jacksonville, Richmond VA) — not full national at tract grain

**Scope:**
- Zone layer is a Deep Dive-specific view, not a national map
- Add a "Zone Map" view to the internal app that accepts a CBSA selection and renders the tract-level zone clusters for that market
- Populates from `mart_intelligence.intelligence_zones` joined to tract GeoJSON for the selected market
- Feeds the Deep Dive Research Tool (separate product) as a reference layer

---

## Open questions before building

1. **MotherDuck setup:** Is the public DuckDB database already published to MotherDuck, or does that need to happen as part of Intelligence Phase 8? The public CBSA app needs a MotherDuck connection string.

2. **GeoJSON simplification tooling:** `mapshaper` is the standard tool. Is it already installed, or does it need to be added to the setup? Alternative: use the pre-simplified Census cartographic boundary files (20m resolution) directly without additional simplification.

3. **Streamlit Cloud secrets:** The `MOTHERDUCK_CONNECTION` token needs to be set in Streamlit Cloud. Confirm the MotherDuck account and token before Phase 2 starts.

4. **Public theme labels:** "Community Profile," "Quality of Life," "Economic Conditions" are proposed. Review before deploying — do these feel right as the public-facing framing?

5. **"Similar metros" in public profile panel:** The internal app uses cosine similarity peers from the Intelligence models. The public app needs a simpler peer concept (size + geography) that doesn't surface model internals. Decision needed: use population-quartile + Census Division matching, or just omit peers from the public profile panel entirely until scores are published?

---

## What this product does not include

- **Place-first exploration:** That is the Deep Dive Research Tool (`metro-deep-dive/RESEARCH_TOOL_ROADMAP.md`). Area Explorer is metric-first.
- **Question-first exploration:** That is the Chatbot and Publisher pipeline.
- **Tract-level national map:** Full national tract choropleth is out of scope — too many polygons, no Intelligence frame data at that grain. Tract views are Deep Dive-specific (Phase 4 above).
- **Full Intelligence frame score breakdowns:** Subject scores, topic scores, GMM probability tables are available in the internal app's Intelligence tab but are not a Phase 1 deliverable for the public app. They surface in the public product after Article 2 ("A New Map of American Metros") establishes the framework in print.
