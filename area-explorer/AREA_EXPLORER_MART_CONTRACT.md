# Area Explorer Mart Contract

*Drafted: 2026-06-22. This document turns the earlier mart sketch into a concrete v1 contract for the CBSA explorer surfaces.*

---

## Scope

This contract covers the first two app-serving tables in:

```text
mart_area_explorer
```

V1 includes:

1. `mart_area_explorer.cbsa_profile_year`
2. `mart_area_explorer.cbsa_metric_long`

V1 does **not** try to carry every CBSA-valid metric in the semantic layer. It carries a curated set aligned to the current explorer visuals and KPI exposure.

---

## Assumptions

- The mart serves the **CBSA** apps first.
- `gold.*` remains the canonical facts layer.
- `mart_intelligence.*` remains the canonical scored-model layer.
- Intelligence fields are current-snapshot outputs and will be repeated across each `cbsa_code, year` row in `cbsa_profile_year` for easier app joins.
- Benchmark ranks in `cbsa_metric_long` are **raw-value percentile ranks**, not polarity-adjusted “better/worse” scores.

---

## Table 1: `mart_area_explorer.cbsa_profile_year`

**Purpose**

This is the place-first read model behind:

- profile panel
- Intelligence tab
- fixed/default scatter views
- app-level selected-place context

**Grain**

One row per `cbsa_code, year`

### Core geography fields

| Output column | Source table | Source column |
|---|---|---|
| `geo_level` | derived | literal `cbsa` |
| `cbsa_code` | `gold.dim_geo` | `geo_id` |
| `cbsa_name` | `gold.dim_geo` | `geo_name` |
| `cbsa_display_name` | `gold.dim_geo` | `display_name` |
| `year` | `gold.population_demographics` | `year` |
| `state_fips_primary` | `gold.dim_geo` | `state_fips` |
| `state_name_primary` | `gold.dim_geo` | `state_name` |
| `state_abbr_primary` | `gold.dim_geo` | `state_abbr` |
| `division_id` | `gold.dim_geo` | `division_id` |
| `division_name` | `gold.dim_geo` | `division_name` |
| `region_id` | `gold.dim_geo` | `region_id` |
| `region_name` | `gold.dim_geo` | `region_name` |
| `primary_city_name` | `gold.dim_geo` | `primary_city_name` |
| `cbsa_type` | `gold.dim_geo` | `cbsa_type` |
| `cbsa_type_short` | `gold.dim_geo` | `cbsa_type_short` |
| `is_metro` | `gold.dim_geo` | `is_metro` |
| `is_micro` | `gold.dim_geo` | `is_micro` |
| `state_count` | `gold.dim_geo` | `state_count` |
| `county_count` | `gold.dim_geo` | `county_count` |

### KPI payload

These are the v1 leaf metrics we want directly available on the profile-year row.

| Theme | Subject | Topic | Output column | Source table | Source column |
|---|---|---|---|---|---|
| `character` | `demographics` | `population_size_and_growth` | `pop_total` | `gold.population_demographics` | `pop_total` |
| `character` | `demographics` | `population_size_and_growth` | `pop_growth_5yr` | `gold.population_demographics` | `pop_growth_5yr` |
| `character` | `demographics` | `age_structure` | `median_age` | `gold.population_demographics` | `median_age` |
| `character` | `demographics` | `race_and_ethnicity` | `diversity_index` | `gold.population_demographics` | `diversity_index` |
| `character` | `demographics` | `educational_attainment` | `pct_ba_plus` | `gold.population_demographics` | `pct_ba_plus` |
| `character` | `demographics` | `nativity_and_citizenship` | `pct_foreign_born` | `gold.migration_wide` | `pct_foreign_born` |
| `character` | `demographics` | `nativity_and_citizenship` | `pct_non_citizen` | `gold.migration_wide` | `pct_non_citizen` |
| `character` | `social_fabric` | `residential_stability` | `irs_net_migration_rate` | `gold.migration_wide` | `irs_net_migration_rate` |
| `livability` | `affordability` | `price_pressure` | `rent_to_income` | `gold.housing_core_wide` | `rent_to_income` |
| `livability` | `affordability` | `price_pressure` | `value_to_income` | `gold.housing_core_wide` | `value_to_income` |
| `livability` | `affordability` | `housing_burden` | `pct_rent_burden_30plus` | `gold.housing_core_wide` | `pct_rent_burden_30plus` |
| `livability` | `affordability` | `housing_supply` | `permits_per_1000_housing_units` | `gold.housing_core_wide` | `permits_per_1000_housing_units` |
| `livability` | `affordability` | `housing_supply` | `vacancy_rate` | `gold.housing_core_wide` | `vacancy_rate` |
| `livability` | `health_and_safety` | `health_outcomes` | `life_expectancy` | `gold.health_wide` | `life_expectancy` |
| `livability` | `health_and_safety` | `health_outcomes` | `premature_death_rate` | `gold.health_wide` | `premature_death_rate` |
| `livability` | `access_and_infrastructure` | `commute_and_mode` | `pct_commute_transit` | `gold.transport_built_form_wide` | `pct_commute_transit` |
| `livability` | `access_and_infrastructure` | `vehicle_access` | `pct_hh_0_vehicles` | `gold.transport_built_form_wide` | `pct_hh_0_vehicles` |
| `livability` | `access_and_infrastructure` | `digital_access` | `pct_no_internet_access` | `gold.social_infra_wide` | `pct_no_internet_access` |
| `livability` | `physical_environment` | `air_pollution` | `aqi_median` | `gold.environment_wide` | `aqi_median` |
| `livability` | `physical_environment` | `climate_hazard_risk` | `fema_risk_score` | `gold.environment_wide` | `fema_risk_score` |
| `opportunity` | `resident_opportunity` | `wage_levels` | `median_hh_income` | `gold.economics_income_wide` | `median_hh_income` |
| `opportunity` | `resident_opportunity` | `poverty_and_inclusion` | `pov_rate` | `gold.economics_income_wide` | `pov_rate` |
| `opportunity` | `resident_opportunity` | `income_growth` | `income_pc_growth_5yr` | `gold.economics_income_wide` | `income_pc_growth_5yr` |
| `opportunity` | `resident_opportunity` | `labor_market_tightness` | `lfpr` | `gold.economics_labor_wide` | `lfpr` |
| `opportunity` | `resident_opportunity` | `labor_market_tightness` | `pct_unemployment_rate` | `gold.economics_labor_wide` | `pct_unemployment_rate` |
| `opportunity` | `market_opportunity` | `home_price_appreciation` | `hpi_5yr_pct` | `gold.housing_market_wide` | `hpi_5yr_pct` |
| `opportunity` | `market_opportunity` | `rent_growth` | `zori_annual_avg_yoy_pct` | `gold.housing_market_wide` | `zori_annual_avg_yoy_pct` |
| `opportunity` | `business_and_industry_opportunity` | `gdp_growth` | `productivity_growth_5yr` | `gold.economics_gdp_wide` | `productivity_growth_5yr` |
| `opportunity` | `business_and_industry_opportunity` | `business_formation` | `bfs_business_application_rate_per_1000_establishments` | `gold.economics_industry_wide` | `bfs_business_application_rate_per_1000_establishments` |
| `opportunity` | `business_and_industry_opportunity` | `establishment_density` | `cbp_estabs_per_1000_residents` | `gold.economics_industry_wide` | `cbp_estabs_per_1000_residents` |
| `opportunity` | `business_and_industry_opportunity` | `industry_concentration` | `industry_concentration_hhi` | `gold.economics_industry_wide` | `industry_concentration_hhi` |

### Intelligence payload

| Output column | Source table | Source column |
|---|---|---|
| `character_percentile_rank` | `mart_intelligence.intelligence_character` | `character_percentile_rank` |
| `character_cluster` | `mart_intelligence.intelligence_character` | `character_cluster` |
| `demographics_score` | `mart_intelligence.intelligence_character` | `demographics_score` |
| `social_fabric_score` | `mart_intelligence.intelligence_character` | `social_fabric_score` |
| `livability_percentile_rank` | `mart_intelligence.intelligence_livability` | `livability_percentile_rank` |
| `livability_cluster` | `mart_intelligence.intelligence_livability` | `livability_cluster` |
| `affordability_score` | `mart_intelligence.intelligence_livability` | `affordability_score` |
| `health_and_safety_score` | `mart_intelligence.intelligence_livability` | `health_and_safety_score` |
| `access_and_infrastructure_score` | `mart_intelligence.intelligence_livability` | `access_and_infrastructure_score` |
| `physical_environment_score` | `mart_intelligence.intelligence_livability` | `physical_environment_score` |
| `opportunity_percentile_rank` | `mart_intelligence.intelligence_opportunity` | `opportunity_percentile_rank` |
| `opportunity_cluster` | `mart_intelligence.intelligence_opportunity` | `opportunity_cluster` |
| `resident_opportunity_score` | `mart_intelligence.intelligence_opportunity` | `resident_opportunity_score` |
| `market_opportunity_score` | `mart_intelligence.intelligence_opportunity` | `market_opportunity_score` |
| `business_and_industry_score` | `mart_intelligence.intelligence_opportunity` | `business_and_industry_score` |
| `cross_frame_percentile_rank` | `mart_intelligence.intelligence_cross_frame` | `cross_frame_percentile_rank` |
| `combined_cluster` | `mart_intelligence.intelligence_cross_frame` | `combined_cluster` |
| `peer_1_code` | `mart_intelligence.intelligence_cross_frame` | `peer_1_code` |
| `peer_1_name` | `mart_intelligence.intelligence_cross_frame` | `peer_1_name` |
| `peer_1_similarity` | `mart_intelligence.intelligence_cross_frame` | `peer_1_similarity` |
| `top10_peer_1_cbsa_code` ... `top10_peer_10_cbsa_code` | `mart_intelligence.intelligence_cross_frame` | matching wide peer code columns |
| `top10_peer_1_cbsa_name` ... `top10_peer_10_cbsa_name` | `mart_intelligence.intelligence_cross_frame` | matching wide peer name columns |
| `top10_peer_1_similarity` ... `top10_peer_10_similarity` | `mart_intelligence.intelligence_cross_frame` | matching wide peer similarity columns |

---

## Table 2: `mart_area_explorer.cbsa_metric_long`

**Purpose**

This is the metric-first read model behind:

- choropleth map
- ranking table
- distribution tab
- scatter tab
- most query-time benchmark lookups

**Grain**

One row per `cbsa_code, year, metric_id`

### Output fields

| Output column | Source |
|---|---|
| `cbsa_code` | `mart_area_explorer.cbsa_profile_year.cbsa_code` |
| `cbsa_name` | `mart_area_explorer.cbsa_profile_year.cbsa_name` |
| `year` | `mart_area_explorer.cbsa_profile_year.year` |
| `state_fips_primary` | `mart_area_explorer.cbsa_profile_year.state_fips_primary` |
| `state_name_primary` | `mart_area_explorer.cbsa_profile_year.state_name_primary` |
| `division_id` | `mart_area_explorer.cbsa_profile_year.division_id` |
| `division_name` | `mart_area_explorer.cbsa_profile_year.division_name` |
| `region_id` | `mart_area_explorer.cbsa_profile_year.region_id` |
| `region_name` | `mart_area_explorer.cbsa_profile_year.region_name` |
| `theme_id` | curated literal mapping in SQL |
| `subject_id` | curated literal mapping in SQL |
| `topic_id` | curated literal mapping in SQL |
| `metric_id` | curated literal mapping in SQL |
| `metric_display_name` | curated literal mapping in SQL |
| `source_table` | curated literal mapping in SQL |
| `source_column` | curated literal mapping in SQL |
| `unit_format` | curated literal mapping in SQL |
| `metric_value` | selected KPI field from `cbsa_profile_year` |
| `national_pct_rank` | window function over `metric_value` by `metric_id, year` |
| `division_pct_rank` | window function over `metric_value` by `metric_id, year, division_name` |

### KPI contract carried into `cbsa_metric_long`

The long table carries the exact KPI set listed above under the `cbsa_profile_year` KPI payload. The difference is only shape:

- `cbsa_profile_year` is wide and place-serving
- `cbsa_metric_long` is long and metric-serving

---

## Deliberate exclusions

These are intentionally out of v1:

- full semantic-layer coverage for every CBSA-valid metric
- county-grain tables
- tract/zone-grain tables
- snapshot-only social-fabric leaf metrics such as `economic_connectedness`

That last exclusion is deliberate because `gold.social_fabric_wide` is not currently modeled at a clean `geo_level + geo_id + year` grain. We should not smear snapshot values across yearly rows until we explicitly decide that is acceptable.

The cross-frame datamart now exposes a wide top-10 peer bundle. V1 should carry those fields through as-is so the internal app can render a ranked peer panel without recomputing similarity relationships at query time.

---

## SQL build asset

The v1 SQL lives at:

[foundations/etl/mart_area_explorer/mart_cbsa_explorer.sql](../foundations/etl/mart_area_explorer/mart_cbsa_explorer.sql)

That script creates:

- `mart_area_explorer.cbsa_profile_year`
- `mart_area_explorer.cbsa_metric_long`

---

## Recommendation

This contract is intentionally smaller than the full semantic layer. That is a feature, not a bug.

If the current CBSA internal and public apps work well against this contract, the next expansion should be:

1. fill out the remaining theme-catalog CBSA metrics
2. add `cbsa_metric_trend` if trend-specific performance needs it
3. design `county_profile_year` after the CBSA app contract is stable
