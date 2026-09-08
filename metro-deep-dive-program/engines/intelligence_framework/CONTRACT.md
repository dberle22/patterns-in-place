# Contract

This contract defines the narrow downstream query surface for the current
Intelligence Framework engine.

It is intentionally smaller than the full mart column inventory.

## Source

- DuckDB schema: `mart_intelligence`
- Long-form method reference:
  `exploration/intelligence_framework/docs/intelligence_framework_overview.md`

## Current Promoted Tables

| Table | Grain | Current role |
|---|---|---|
| `intelligence_character` | `1 row per CBSA` | Character scores, labels, peers, topic and subject scores |
| `intelligence_livability` | `1 row per CBSA` | Livability scores, labels, peers, topic and subject scores |
| `intelligence_opportunity` | `1 row per CBSA` | Opportunity scores, labels, peers, topic and subject scores |
| `intelligence_cross_frame` | `1 row per CBSA` | Combined labels, percentile context, overlap and divergence fields, cross-frame peers |
| `intelligence_zones` | `1 row per tract` | Phase 7 tract zone assignments and percentile context |
| `intelligence_zones_zcta` | `1 row per ZCTA` | ZCTA rollup of tract zone composition |

## Primary Keys

| Table | Primary key |
|---|---|
| `intelligence_character` | `cbsa_code` |
| `intelligence_livability` | `cbsa_code` |
| `intelligence_opportunity` | `cbsa_code` |
| `intelligence_cross_frame` | `cbsa_code` |
| `intelligence_zones` | `tract_geoid` |
| `intelligence_zones_zcta` | `zip_geoid` |

## Shared Join Keys

- `cbsa_code`
- `cbsa_name`
- `county_geoid`
- `tract_geoid`
- `zip_geoid`

## Core Documented Fields

### 1. Identity Labels

Use these for headline Act 1 identity and light interpretation:

- `character.character_cluster_name`
- `livability.livability_cluster_name`
- `opportunity.opportunity_cluster_name`
- `cross_frame.combined_cluster`
- `cross_frame.top_frame`
- `cross_frame.bottom_frame`
- `cross_frame.overlap_profile`
- `cross_frame.signature`

### 2. Percentile Surface

Use these for ranking and frame-comparison context:

- `character.character_percentile_rank`
- `livability.livability_percentile_rank`
- `opportunity.opportunity_percentile_rank`
- `cross_frame.cross_frame_percentile_rank`
- `cross_frame.frame_percentile_gap`
- `cross_frame.frame_percentile_sd`
- `cross_frame.mean_frame_percentile`

### 3. Topic And Subject Scores

These are the preferred building blocks for early fingerprint work because they
are more stable and interpretable than exposing every raw KPI equally.

Recommended Character fields:

- `topic_score_population_density`
- `topic_score_educational_attainment`
- `topic_score_social_capital`
- `subject_score_demographics`
- `subject_score_social_fabric`

Recommended Livability fields:

- `topic_score_price_pressure`
- `topic_score_housing_burden`
- `topic_score_health_outcomes`
- `topic_score_walkability_baseline`
- `subject_score_affordability`
- `subject_score_health_and_safety`
- `subject_score_access_and_infrastructure`
- `subject_score_physical_environment`

Recommended Opportunity fields:

- `topic_score_income_growth`
- `topic_score_population_growth`
- `topic_score_wage_levels`
- `topic_score_business_formation`
- `subject_score_resident_opportunity`
- `subject_score_market_opportunity`
- `subject_score_business_and_industry_opportunity`

### 4. Raw KPI Starter Fields

These are useful for a first-pass Act 1 fingerprint query, but they are not yet
locked as the final fingerprint asset:

Character:

- `pop_total`
- `pct_ba_plus`
- `pct_foreign_born`
- `pop_weighted_density_sqmi`
- `social_associations_per_10k`

Livability:

- `value_to_income`
- `pct_rent_burden_30plus`
- `walkability_index`
- `aqi_median`
- `fema_risk_score`

Opportunity:

- `pop_growth_5yr`
- `income_pc_growth_5yr`
- `qcew_private_avg_wkly_wage`
- `hpi_5yr_pct`
- `bfs_business_application_rate_per_1000_establishments`

### 5. Peer Surface

The current promoted peer surface is top `10` only.

Documented fields:

- `top10_peer_1_cbsa_code` through `top10_peer_10_cbsa_code`
- `top10_peer_1_cbsa_name` through `top10_peer_10_cbsa_name`
- `top10_peer_1_similarity` through `top10_peer_10_similarity`

Applies to:

- `intelligence_character`
- `intelligence_livability`
- `intelligence_opportunity`
- `intelligence_cross_frame`

### 6. Zone Surface

Use these later for Act 4 bridge work:

Tract-level:

- `tract_geoid`
- `cbsa_code`
- `cbsa_name`
- `county_geoid`
- `county_name`
- `zone_type`
- `composite_score`
- `national_composite_percentile`
- `cbsa_composite_percentile`
- `zone_peer_composite_percentile`

ZCTA-level:

- `zip_geoid`
- `primary_zone_type`
- `dominant_zone_type`
- `dominant_zone_share`
- `secondary_zone_type`
- `secondary_zone_share`
- `tract_count`

## Explicit Non-Contract Surfaces

These outputs exist, but are not yet part of the DuckDB contract:

- `exploration/intelligence_framework/phase_6_trajectory/outputs/trajectory_scores.parquet`
- `exploration/intelligence_framework/phase_6_trajectory/outputs/phase6_candidate_list.csv`
- `exploration/intelligence_framework/phase_6_trajectory/outputs/phase6_opp_turn_signals.csv`
- `exploration/intelligence_framework/phase_6_trajectory/outputs/phase6_kpi_trajectory_long.csv`

## Known Caveats

- Current promoted CBSA universe is `396`, not `401`.
- Cross-frame divergence fields are promoted and queryable now.
- The current cross-frame table still exposes many prefixed fields like
  `character__...`, `livability__...`, and `opportunity__...`.
- A full trajectory mart has not been promoted yet, so `Trajectory` remains
  file-backed for now.
- The current promoted peer contract is top `10`; broader similarity retrieval
  would require a new promoted surface.
