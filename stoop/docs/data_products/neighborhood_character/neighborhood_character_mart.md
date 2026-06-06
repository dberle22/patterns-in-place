# Neighborhood Character Mart

Last updated: 2026-05-05

## Purpose

This mart pre-computes neighborhood-level POI concentration signals for use in
the Stoop Explore and Stoop Search apps.

It answers two questions the app needs at runtime:

- **"Top neighborhoods for X"** — rank all NYC NTAs by curated POI density for a
  selected category (the Stoop Explore intelligence panel).
- **"What is this neighborhood known for?"** — surface the categories an NTA
  over-indexes on relative to the NYC baseline (the neighborhood character panel).

It also provides lightweight livability signals from public POI counts (transit,
grocery, parks) for the Stoop Search Phase 1 surface.

---

## What it is not

- A composite score rolled up to a single number. Character and livability signals
  stay in separate, explainable columns.
- A real-time query. Everything is pre-computed at pipeline run time. The app
  reads from mart output tables directly.
- A substitute for the full neighborhood character framework. This mart
  implements the MVP analytics layer only. Composite scoring, label taxonomy,
  and natural-language profiles are future work.

---

## Schema

`neighborhood_character_mart`

---

## Table inventory

### 1. `nta_boundaries`

**Grain**: one row per NTA (262 rows for NYC).

**Source**: NYC Open Data NTA 2020 boundaries GeoJSON. Loaded by the Python
pipeline step before SQL mart runs.

**Key columns**:

| Column | Type | Notes |
|---|---|---|
| `nta_id` | varchar | matches `dim_tract_to_nta.nta_id` |
| `nta_name` | varchar | |
| `borough` | varchar | |
| `area_sqkm` | double | NTA area in km², derived from geometry |
| `centroid_lat` | double | NTA centroid latitude |
| `centroid_lon` | double | NTA centroid longitude |
| `geometry_wkt` | varchar | WKT polygon for spatial joins |

This table is populated by the Python pipeline, not the SQL mart. It is rebuilt
on each full pipeline run from the source GeoJSON.

---

### 2. `nta_poi_assignments`

**Grain**: one row per POI (curated + public) with its assigned NTA.

**Source**: spatial join of lat/lon from `dim_user_poi_v2` and `dim_public_poi`
against `nta_boundaries` geometry. Point-in-polygon using geopandas, executed
in the Python pipeline before SQL mart runs.

**Key columns**:

| Column | Type | Notes |
|---|---|---|
| `poi_id` | varchar | matches source table |
| `poi_source` | varchar | `curated` or `public` |
| `nta_id` | varchar | assigned NTA |
| `category` | varchar | from source table |
| `subcategory` | varchar | from source table, curated only |
| `lat` | double | |
| `lon` | double | |

POIs outside NTA boundaries (outside the five boroughs) are excluded. POIs
with NULL lat/lon are excluded. These are populated by the Python pipeline,
not the SQL mart.

---

### 3. `nta_curated_poi_counts`

**Grain**: one row per (nta_id, category, subcategory).

**Source**: `nta_poi_assignments` filtered to `poi_source = 'curated'`.

**Key columns**:

| Column | Type | Notes |
|---|---|---|
| `nta_id` | varchar | |
| `nta_name` | varchar | |
| `borough` | varchar | |
| `category` | varchar | |
| `subcategory` | varchar | |
| `poi_count` | integer | number of curated POIs in this NTA × category × subcategory |
| `nyc_category_total` | integer | total curated POIs for this category across all NYC NTAs |

`nyc_category_total` is used downstream to apply the minimum evidence threshold.

---

### 4. `nta_public_poi_counts`

**Grain**: one row per (nta_id, category).

**Source**: `nta_poi_assignments` filtered to `poi_source = 'public'`.

**Key columns**:

| Column | Type | Notes |
|---|---|---|
| `nta_id` | varchar | |
| `nta_name` | varchar | |
| `borough` | varchar | |
| `category` | varchar | |
| `poi_count` | integer | |

Livability signal families drawn from this table:

- **Transit**: `subway_station`, `bus_stop`, `citi_bike`, `ferry_terminal`
- **Daily needs**: `grocery_store`, `pharmacy`, `laundromat`
- **Green space**: `park`, `playground`, `dog_run`
- **Civic**: `public_library`, `public_school`, `hospital`, `urgent_care`

---

### 5. `nta_category_density` ← core ranking table

**Grain**: one row per (nta_id, source, category). Source is `curated` or
`public`.

This is the primary table the app reads for the "Top neighborhoods for X"
ranking surface.

**Key columns**:

| Column | Type | Notes |
|---|---|---|
| `nta_id` | varchar | |
| `nta_name` | varchar | |
| `borough` | varchar | |
| `area_sqkm` | double | NTA area |
| `source` | varchar | `curated` or `public` |
| `category` | varchar | |
| `poi_count` | integer | POIs in this NTA for this category |
| `poi_density_per_sqkm` | double | `poi_count / area_sqkm` |
| `subcategory_diversity` | integer | distinct curated subcategories within the category for this NTA; null for public rows |
| `nyc_category_total` | integer | total POIs for this category across NYC |
| `nyc_percentile` | double | PERCENT_RANK() of this NTA for this category within NYC |
| `concentration_tier` | varchar | see tier definitions below |
| `meets_evidence_threshold` | boolean | false if `nyc_category_total` falls below the active category threshold |

**Concentration tier definitions** (applied only when `meets_evidence_threshold = true`):

| Tier | Threshold | App label |
|---|---|---|
| `destination` | top 10% (`nyc_percentile >= 0.90`) | "known for" |
| `strong` | top 25% (`nyc_percentile >= 0.75`) | "strong scene" |
| `present` | top 50% (`nyc_percentile >= 0.50`) | surfaced, unlabeled |
| `limited` | bottom 50% | not surfaced |

The `destination` tier is the "known for" threshold. A category only earns this
label if the NTA is genuinely in the top decile of NYC neighborhoods for that
category based on POI count.

**Minimum evidence threshold**: categories should support a configurable minimum
evidence threshold rather than a permanently fixed one. In the first draft, if
`nyc_category_total` falls below the active threshold, `concentration_tier` is
set to `null` and `meets_evidence_threshold = false`. This prevents labels from
looking more certain than the underlying coverage supports while still allowing
the threshold to loosen or tighten during Sprint 2 validation.

**Normalization note**: ranking uses raw `poi_count`, not `poi_density_per_sqkm`,
as the primary sort signal in the current MVP. Density is stored for future use
when NTA area variation matters more. Large residential NTAs may get penalized
by density normalization even when they have strong absolute POI counts. Revisit
this when the data supports it.

**Tie-breaker note**: for curated categories, ties should break first on
`subcategory_diversity` and then on `nta_name` for deterministic ordering. This
is especially important for restaurant-heavy categories, where category depth
matters more than raw count alone.

---

### 5a. `nta_category_controls` ← app inclusion and threshold control table

**Grain**: one row per curated Explore category.

This table lets Stoop lock the MVP Explore category set without hard-coding
those decisions inside app logic or ranking SQL.

**Key columns**:

| Column | Type | Notes |
|---|---|---|
| `category` | varchar | curated category name |
| `include_in_explore_v1` | boolean | whether the category is selectable in Explore |
| `known_for_enabled` | boolean | whether the category can power "known for" labels |
| `min_nyc_category_total` | integer | active evidence threshold for this category |
| `display_label` | varchar | user-facing category label |
| `notes` | varchar | rationale or temporary caveat |

**Recommended MVP seed state**:

| Category | Include | Known for enabled | Notes |
|---|---|---|---|
| `restaurants` | true | true | first-class Explore input |
| `museums` | true | true | strong cultural anchor |
| `bookstores` | true | true | strong editorial and destination signal |
| `shopping` | true | true | broad but useful destination signal |
| `hotels` | true | true | visitor-oriented anchor and useful control category |
| `bakeries` | true | true | food-adjacent, good editorial signal |
| `food_markets` | true | true | strong browse-and-eat signal |
| `specialty_grocery` | true | true | useful in food stories |
| `record_stores` | true | true | niche but high-character when present |
| `bars` | true | true | include now even if under-covered; validation should show gaps |
| `music_venues` | false | false | hold until coverage is more trustworthy |
| `movie_theaters` | false | false | hold for now |
| `coffee` | false | false | hide until evidence improves |

---

### 6. `nta_character_profile` ← final output per NTA

**Grain**: one row per NTA.

This is the primary table the app reads for the neighborhood character panel
when a user selects an NTA on the map.

**Key columns**:

| Column | Type | Notes |
|---|---|---|
| `nta_id` | varchar | |
| `nta_name` | varchar | |
| `borough` | varchar | |
| `area_sqkm` | double | |
| `total_curated_poi_count` | integer | all curated POIs assigned to this NTA |
| `destination_categories` | varchar | pipe-delimited list of `destination`-tier categories |
| `strong_categories` | varchar | pipe-delimited list of `strong`-tier categories |
| `top_category` | varchar | single highest-ranking curated category by poi_count |
| `top_subcategory` | varchar | single highest-ranking subcategory within top_category |
| `subway_station_count` | integer | public POI count |
| `bus_stop_count` | integer | |
| `grocery_store_count` | integer | |
| `pharmacy_count` | integer | |
| `park_count` | integer | |
| `public_library_count` | integer | |
| `public_school_count` | integer | |
| `built_at` | timestamp | mart build time |

The livability columns in this table are raw counts, not scores. Scoring and
weighting are applied at the app layer or deferred to the Livability framework.

---

## Analytics logic summary

```
dim_user_poi_v2 (lat/lon)  ─┐
                              ├─► [Python: geopandas point-in-polygon]
dim_public_poi  (lat/lon)  ─┘        ↓
                              nta_poi_assignments
                                      ↓
                 ┌──────────────────────────────────┐
                 ▼                                  ▼
   nta_curated_poi_counts          nta_public_poi_counts
                 ↓                                  ↓
         nta_category_density               (feeds livability
          (PERCENT_RANK per                  columns in profile)
           category × NTA)
                 ↓
        nta_category_controls
         (Explore inclusion,
          label eligibility,
          threshold tuning)
                 ↓
         nta_character_profile
         (one row per NTA,
          top categories,
          raw livability counts)
```

---

## Pipeline

**Entry point**: `pipelines/build_neighborhood_character_mart.py`

**SQL build order**:

```
sql/ddl/004_neighborhood_character_mart.sql
sql/marts/neighborhood_character/nta_curated_poi_counts.sql
sql/marts/neighborhood_character/nta_public_poi_counts.sql
sql/marts/neighborhood_character/nta_category_density.sql
sql/marts/neighborhood_character/nta_category_controls.sql
sql/marts/neighborhood_character/nta_character_profile.sql
```

**Python steps** (executed before SQL mart):

1. Load NTA 2020 boundary GeoJSON from a bundled or downloaded source.
2. Compute NTA area in km² from geometry.
3. Spatial join curated POIs (lat/lon) → NTA, write `nta_poi_assignments` rows
   with `poi_source = 'curated'`.
4. Spatial join public POIs (lat/lon) → NTA, write `nta_poi_assignments` rows
   with `poi_source = 'public'`.
5. Execute SQL mart in order.
6. Print build summary (row counts, evidence threshold failures, top-tier NTAs
   per category).

**Rebuild behavior**: all mart tables are rebuilt from scratch on each run. The
mart has no durable state — source tables (`dim_user_poi_v2`, `dim_public_poi`)
are the authoritative layer. Rebuild whenever either source changes.

---

## NTA boundary source

NYC Planning publishes NTA 2020 boundaries as GeoJSON via NYC Open Data and
the DCP GitHub repository. Either can serve as the source.

The boundary file should be committed to `data/raw/boundaries/nta_2020.geojson`
so the pipeline is reproducible without a network dependency at run time.

---

## App consumption pattern

**Stoop Explore — "Top neighborhoods for [category]"**:

```sql
select nta_id, nta_name, borough, poi_count, nyc_percentile, concentration_tier
from neighborhood_character_mart.nta_category_density
where source = 'curated'
  and category = :selected_category
  and meets_evidence_threshold = true
order by nyc_percentile desc
```

**Stoop Explore — neighborhood character panel for selected NTA**:

```sql
select *
from neighborhood_character_mart.nta_character_profile
where nta_id = :selected_nta_id
```

**Stoop Search — lightweight livability panel**:

```sql
select
    subway_station_count,
    grocery_store_count,
    pharmacy_count,
    park_count,
    public_library_count,
    public_school_count
from neighborhood_character_mart.nta_character_profile
where nta_id = :selected_nta_id
```

---

## Current data coverage notes

As of 2026-05-05, curated POI coverage is uneven. Categories with enough
coverage to meet the evidence threshold (≥ 20 NYC-wide POIs):

- `restaurants` (930)
- `bakeries` (93)
- `shopping` (69)
- `hotels` (67)
- `food_markets` (53)
- `specialty_grocery` (51)
- `bookstores` (50)
- `movie_theaters` (37)
- `record_stores` (27)

Categories currently below threshold (rankings deferred):

- `bars` (26 — borderline, may cross threshold soon)
- `museums` (25)
- `music_venues` (22)
- `coffee_shops` (12)

The threshold is a configuration parameter and should be tuned as coverage grows.
Bars and museums are close enough that a small scraping push would unlock them.

---

## Future extensions

These are out of scope for the MVP mart but should be kept in mind as the
schema evolves.

| Extension | When |
|---|---|
| Subcategory-level rankings (e.g. top neighborhoods for ramen, not just restaurants) | When curated subcategory coverage justifies it |
| Walking-radius counts (0.5mi around NTA centroid) instead of within-NTA counts | When walkability framing is needed for Stoop Search |
| Composite livability score per NTA | After crime and school quality land in Sprint 1 |
| NTA-relative ranking within borough (not just citywide) | When app needs borough-scoped filters |
| Label taxonomy / controlled vocabulary assignment | After validation pass against known neighborhoods |
| Cross-market normalization | Post-NYC expansion |
