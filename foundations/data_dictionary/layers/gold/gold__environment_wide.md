# Data Dictionary: gold.environment_wide

## Overview
- **Table**: `gold.environment_wide`
- **Purpose**: Curated environment mart for the tract + county + CBSA environmental risk surface, combining source-native AQI with tract-level EJScreen and FEMA overlays.
- **KPI applicability**: Gold output table for air-quality analysis and the future climate/environment risk topic.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
  - Live uniqueness check should remain zero-duplicate after tract promotion.
- **Time coverage**: `year` min=2016, max=2025
- **Geo coverage**: tract rows are now included alongside county and CBSA rows
  - tract `EJScreen` rows inherit the `2024` tract Silver coverage
  - tract `FEMA` rows inherit the `2025` tract Silver coverage
  - county and CBSA behavior remains aligned to the prior Gold contract

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **AQI bucket counts**: `days_with_aqi`, `good_days`, `moderate_days`, `usg_days`, `unhealthy_days`, `very_unhealthy_days`, `hazardous_days`
- **AQI summary metrics**: `max_aqi`, `aqi_p90`, `aqi_median`
- **Pollutant attribution metrics**: `days_ozone`, `days_pm25`
- **EJScreen coverage**: `ejs_population_covered`
- **EJScreen direct-or-rolled indicators**: `ejs_pm25`, `ejs_ozone`, `ejs_diesel_pm`, `ejs_traffic_proximity`, `ejs_superfund_proximity`, `ejs_rmp_proximity`, `ejs_wastewater_discharge`, `ejs_drinking_water_noncompliance`
- **EJScreen direct-or-rolled national percentiles**: `ejs_pctile_pm25_us`, `ejs_pctile_ozone_us`, `ejs_pctile_diesel_pm_us`, `ejs_pctile_traffic_us`, `ejs_pctile_superfund_us`, `ejs_pctile_rmp_us`, `ejs_pctile_wastewater_us`, `ejs_pctile_drinking_water_us`
- **EJScreen exposure summary metrics**: `ejs_avg_high_exposure_indicators`, `ejs_avg_high_exposure_supplemental`
- **FEMA composite risk metrics**: `fema_risk_score`, `fema_eal_score`, `fema_alr_national_pctile`, `fema_alr_vra_national_pctile`, `fema_social_vulnerability_score`, `fema_community_resilience_score`
- **FEMA hazard risk scores**: `fema_avalanche_risk_score`, `fema_coastal_flooding_risk_score`, `fema_cold_wave_risk_score`, `fema_drought_risk_score`, `fema_earthquake_risk_score`, `fema_hail_risk_score`, `fema_heat_wave_risk_score`, `fema_hurricane_risk_score`, `fema_ice_storm_risk_score`, `fema_inland_flooding_risk_score`, `fema_landslide_risk_score`, `fema_lightning_risk_score`, `fema_strong_wind_risk_score`, `fema_tornado_risk_score`, `fema_tsunami_risk_score`, `fema_volcanic_activity_risk_score`, `fema_wildfire_risk_score`, `fema_winter_weather_risk_score`

## Data Quality Notes
- Live query checks confirm the intended `geo_level + geo_id + year` grain with zero duplicate keys.
- AQI remains the source-faithful county + CBSA slice of the table.
- Tract rows come from the union of tract-ready environmental sources rather than from AQI.
- County rows inherit the documented Silver county-identification rule:
  - start from EPA `state_name + county_name`
  - normalize the source strings
  - match to canonical county GEOIDs through geography crosswalk aliases
  - apply a very small manual alias fallback for known edge cases
- CBSA rows inherit the source-published `cbsa_code` directly as `geo_id`.
- Ten county rows were intentionally dropped upstream in Silver because they could not be matched to a canonical county GEOID after normalization.
- EJScreen tract rows are promoted directly from `silver.ejscreen`.
- EJScreen county and CBSA rows are still rolled up from tract to county / CBSA with population-weighted averages using tract population as the weight.
- Because AQI has no tract contract, AQI columns remain null on tract rows.
- The EJScreen tract archive excludes Puerto Rico and territorial rows from the canonical Silver layer, so Gold inherits that same supported-geography boundary.
- FEMA NRI now joins from `silver.fema_nri` at the shared `geo_level + geo_id + year` grain for tract, county, and CBSA rows.
- Because FEMA is currently a single-release `2025` surface, the FEMA columns are non-null only for `year = 2025`.
- County and CBSA FEMA rows still show the AQI-overlapping subset of the broader FEMA county-equivalent coverage, while tract FEMA rows come directly from the governed tract Silver contract.

## Lineage
1. **Primary build script**: [gold_environment_wide.sql](/Users/danberle/Documents/projects/patterns_in_place/foundations/etl/gold/gold_environment_wide.sql)
2. **Primary upstreams**:
- `silver.epa_aqi`
- `silver.ejscreen`
- `silver.fema_nri`
- `gold.dim_geo`

## Known Gaps / To-Dos
- County normalization remains dependent on current geography crosswalk coverage and a small manual alias list for legacy-name cases.
- EJScreen tract rows are source-direct, while county and CBSA rows are population-weighted tract rollups. If we later need alternative aggregation logic, such as threshold shares, that should be added as new derived columns rather than by replacing the current contract.
- Tract AQI and tract SLD are still outside this Gold mart. If we later want a more complete tract environment surface, that should be added through a documented follow-on rather than by silently approximating those sources.
- If we decide later that AQI is more useful as a composite score or normalized percentile surface, that should happen in a downstream analytical layer rather than by changing this source-faithful Gold mart.
