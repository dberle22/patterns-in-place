# Area Explorer Mart Sketch

*Drafted: 2026-06-21. This is a v1 product-read mart sketch for the Streamlit Area Explorer apps. It is intentionally narrower than `gold/` and should be treated as an app-serving layer, not a replacement semantic layer.*

---

## Why this mart exists

Area Explorer is a **metric-first** product with a fixed UI shape:

- sidebar hierarchy: `Theme -> Subject -> Topic -> Metric`
- main surface: choropleth + ranking table + profile panel
- context tabs: `Scatter`, `Trend`, `Distribution`, and `Intelligence` for the internal CBSA app

Today the app has to assemble that surface by joining:

- one Gold fact table per selected metric
- `gold.dim_geo` for benchmark context and place labels
- `mart_intelligence.*` for frame scores and clusters when available
- phase parquets as fallback when `mart_intelligence` is absent

That is workable for development, but it is not the right long-term contract for a product surface. A dedicated app mart should:

- stabilize the fields the UI reads
- reduce query-time joins and source-specific branching
- make internal/public variants easy to gate
- let us materialize benchmark fields once instead of recomputing them ad hoc
- simplify future app builds beyond Area Explorer, especially the Deep Dive Research Tool

---

## Design stance

This should be a **thin, denormalized, product-serving mart** in a new schema:

```text
mart_area_explorer
```

It should not try to precompute every possible chart or metric combination. The right split is:

- `gold/` remains the canonical analytical layer
- `mart_intelligence/` remains the canonical scored-model layer
- `mart_area_explorer/` becomes the **UI-serving read layer**

That means:

- keep one row per geography-year for the main explorer surfaces
- carry only the fields that the apps repeatedly need
- leave rare or exploratory joins in `gold/` until they prove they belong here

---

## Proposed v1 tables

### 1. `mart_area_explorer.cbsa_profile_year`

**Purpose:** canonical row store for the CBSA internal and public apps.

**Grain:** one row per `cbsa_code, year`

**Feeds:**

- map
- ranking table
- profile panel
- scatter tab
- Intelligence tab
- most benchmark lookups

**Core fields**

```text
cbsa_code
cbsa_name
year
state_fips_primary
state_name_primary
division_id
division_name
region_id
region_name
primary_city_name
cbsa_type
pop_total
```

**KPI payload**

This table should carry the KPI columns we actually intend to expose in the explorer, not the full warehouse. The v1 rule should be:

- include all CBSA-valid metrics that appear in `theme_catalog.yml`
- include the public/default scatter pair
- include the internal/default Intelligence pair
- exclude county-only metrics, tract-only metrics, and metrics not exposed in the picker

That means the KPI payload comes primarily from:

- `gold.population_demographics`
- `gold.housing_core_wide`
- `gold.economics_income_wide`
- `gold.affordability_wide`
- `gold.economics_labor_wide`
- `gold.economics_industry_wide`
- `gold.environment_wide`
- `gold.health_wide`
- `gold.transport_wide`
- `gold.social_fabric_wide`
- `gold.social_infra_wide`
- `gold.food_access_wide`
- any other Gold marts already referenced by CBSA-valid metrics in `metric_catalog.yml`

**Intelligence payload**

These should be flattened onto the same row so the internal app does not need frame-by-frame joins.

From `mart_intelligence.intelligence_character`:

```text
character_percentile_rank
character_cluster
demographics_score
social_fabric_score
```

From `mart_intelligence.intelligence_livability`:

```text
livability_percentile_rank
livability_cluster
affordability_score
health_and_safety_score
access_and_infrastructure_score
physical_environment_score
```

From `mart_intelligence.intelligence_opportunity`:

```text
opportunity_percentile_rank
opportunity_cluster
resident_opportunity_score
market_opportunity_score
business_and_industry_score
```

From `mart_intelligence.intelligence_cross_frame`:

```text
cross_frame_percentile_rank
combined_cluster
peer_1_code
peer_1_name
peer_1_similarity
peer_2_code
peer_2_name
peer_2_similarity
peer_3_code
peer_3_name
peer_3_similarity
peer_4_code
peer_4_name
peer_4_similarity
peer_5_code
peer_5_name
peer_5_similarity
```

If cross-frame divergence becomes a stable field later, add it here. Do not block the mart on it.

**Benchmark payload**

The internal/public apps repeatedly need:

- national percentile
- Census Division percentile

We should precompute these for the fields we actually expose frequently. Two options:

1. Materialize benchmark columns only for:
   - frame percentile scores
   - subject-level scores
   - a curated set of “hero” KPIs used most often in the UI
2. Keep percentile computation query-time for arbitrary leaf KPIs

Recommendation for v1:

- materialize benchmark fields for Intelligence outputs
- keep arbitrary KPI percentile ranks query-time until usage stabilizes

This keeps the mart from exploding in width too early.

---

### 2. `mart_area_explorer.cbsa_metric_long`

**Purpose:** lightweight long-form metric table for the picker, rankings, map, and distribution workflows.

**Grain:** one row per `cbsa_code, year, metric_id`

**Feeds:**

- sidebar metric selection
- choropleth metric values
- ranking table metric values
- distribution tab
- flexible benchmark logic for arbitrary metrics

**Fields**

```text
cbsa_code
cbsa_name
year
metric_id
metric_display_name
theme_id
subject_id
topic_id
source_table
source_column
unit_format
metric_value
state_fips_primary
state_name_primary
division_id
division_name
region_id
region_name
national_pct_rank
division_pct_rank
```

This is the most important table for simplifying the app. It lets the UI query a single relation for nearly every metric-first action.

This table should be built from the semantic layer, not hand-curated SQL. The build should:

- start from active CBSA-valid metrics in `metric_catalog.yml`
- map those metrics into `theme/subject/topic` using `theme_catalog.yml` and `intelligence_catalog.yml`
- union them into one standardized long table

This table does **not** need Intelligence-only metrics as leaf picker options in v1 unless we explicitly decide to expose them.

---

### 3. `mart_area_explorer.cbsa_metric_trend`

**Purpose:** trend-ready long table optimized for the line chart tab.

**Grain:** one row per `cbsa_code, metric_id, year`

This can be the same physical data as `cbsa_metric_long` if performance is fine. If not, treat it as a separate materialized projection.

**Fields**

```text
cbsa_code
cbsa_name
metric_id
year
metric_value
national_median
division_median
```

This exists because the trend tab wants comparison lines and reference medians over time, which are slightly different from the ranking/map use case.

---

### 4. `mart_area_explorer.county_profile_year`

**Purpose:** county-serving equivalent for Phase 3.

**Grain:** one row per `county_fips, year`

Do not build this until the CBSA mart shape is stable. The county app has different comparator logic and slower geometry constraints, so it should be a follow-on table, not part of the first sprint.

---

## Alignment to visuals

### Choropleth map

Needs:

- one metric value per geography
- place labels
- benchmark context for hover
- optional Intelligence labels in the internal app

Best source:

- `cbsa_metric_long` for the selected metric
- join-free or nearly join-free access to `cbsa_name`, `division_name`, and `national_pct_rank`

### Ranking table

Needs:

- same selected metric value as the map
- fast sorting across all CBSAs
- optional top/bottom toggles

Best source:

- `cbsa_metric_long`

### Profile panel

Needs:

- selected KPI raw value
- national and division benchmarks
- Character / Livability / Opportunity cluster labels
- frame percentile ranks
- peer list

Best source:

- metric-specific row from `cbsa_metric_long`
- place-level row from `cbsa_profile_year`

### Scatter tab

Needs:

- two selected metrics on the same CBSA-year row
- optional cluster color

Best source:

- self-join `cbsa_metric_long` by `cbsa_code, year`
- or read both metrics from `cbsa_profile_year` if the KPI is already present there

Recommendation:

- use `cbsa_metric_long` as the canonical scatter input
- reserve `cbsa_profile_year` for fixed/default scatter views and profile enrichment

### Trend tab

Needs:

- one metric over many years
- optional comparison metros
- national median and division median reference lines

Best source:

- `cbsa_metric_trend`

### Distribution tab

Needs:

- one metric across all CBSAs for a single year

Best source:

- `cbsa_metric_long`

### Intelligence tab

Needs:

- livability percentile rank
- opportunity percentile rank
- character cluster
- combined cluster
- peer set

Best source:

- `cbsa_profile_year`

---

## Alignment to KPI exposure

The mart should be driven by the KPIs we actually expose in the explorer, not by every field in `gold/`.

### V1 inclusion rule

Include KPIs that satisfy all three:

1. `status: active` in `metric_catalog.yml`
2. `cbsa` in `valid_geo_levels`
3. present in `theme_catalog.yml` or explicitly chosen as a default chart metric

This will capture:

- all theme-browsable Character / Livability / Opportunity metrics
- `median_hh_income`
- `rent_to_income`
- other default chart metrics we choose for the public/internal apps

### V1 exclusion rule

Exclude:

- metrics not exposed in the picker
- tract-only or county-only metrics
- provisional/dead metrics that exist in `gold/` but are not part of the current explorer contract
- raw modeling intermediates that are only useful inside notebooks

### Why this matters

If we use “all of Gold” as the KPI contract, the app mart becomes another warehouse. That defeats the purpose. The contract should reflect the **product surface**, not all possible analysis.

---

## Build approach

### Step 1

Build `mart_area_explorer.cbsa_profile_year` from:

- `gold.dim_geo`
- a curated CBSA metric bundle from Gold
- all four Intelligence marts

This gives us a stable internal-app row model quickly.

### Step 2

Build `mart_area_explorer.cbsa_metric_long` from semantic-layer-driven unions over active CBSA-valid metrics.

This is the real simplifier for the explorer.

### Step 3

Build `mart_area_explorer.cbsa_metric_trend` as either:

- a materialized projection from `cbsa_metric_long`, or
- a view if performance is already acceptable

### Step 4

After the CBSA app stabilizes, repeat the same pattern for counties.

---

## Recommended implementation choices

### Schema

Use:

```text
mart_area_explorer
```

Do not overload `mart_intelligence`. That schema should remain specifically about modeled score outputs.

### Physical form

Recommendation:

- materialize these as DuckDB tables, not views, for local app speed
- rebuild them sequentially as part of the app-serving ETL

### Builder language

Recommendation:

- SQL first where possible
- R only if the semantic-layer-driven union generation is much easier there

Given the metric union logic, a hybrid approach is reasonable:

- R script reads the semantic catalogs and emits the union SQL
- SQL does the actual materialization

### Naming

Prefer stable product names:

- `cbsa_profile_year`
- `cbsa_metric_long`
- `cbsa_metric_trend`
- `county_profile_year`

Avoid names that encode current implementation details like “wide_v2” or “explorer_flat”.

---

## What not to do

- Do not create one giant “everything app” mart for CBSA + county + tract.
- Do not duplicate the full warehouse into `mart_area_explorer`.
- Do not block the build on precomputing percentile ranks for every possible metric.
- Do not force public and internal apps into separate marts unless the contracts genuinely diverge.

One schema with shared base tables and app-level feature flags is the cleaner starting point.

---

## Suggested v1 deliverable

If we want the smallest useful first cut, it is this:

1. `mart_area_explorer.cbsa_profile_year`
2. `mart_area_explorer.cbsa_metric_long`

That pair is enough to support:

- internal CBSA app
- public CBSA app
- current map/ranking/profile/scatter/distribution workflows
- most Intelligence overlays

`cbsa_metric_trend` can come immediately after if trend performance or reference-line logic gets awkward.

---

## Recommendation

Yes, we should build an app-specific mart.

The right v1 is not “a special mart for every app.” The right v1 is:

- one shared `mart_area_explorer` schema
- one place-level CBSA profile table
- one long-form metric table
- trend as a projection if needed

That gives us a durable product-serving contract while keeping `gold/` and `mart_intelligence/` clean.
