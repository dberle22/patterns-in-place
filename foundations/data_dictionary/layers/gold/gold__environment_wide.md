# Data Dictionary: gold.environment_wide

## Overview
- **Table**: `gold.environment_wide`
- **Purpose**: Curated environment mart for the county + CBSA environmental risk surface, combining source-native AQI with tract-derived EJScreen rollups.
- **Row count**: 15,145
- **KPI applicability**: Gold output table for air-quality analysis and the future climate/environment risk topic.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
  - Live uniqueness check on June 8, 2026: rows=15,145; duplicate keys=0
- **Time coverage**: `year` min=2016, max=2025
- **Geo coverage**: 2 geo levels; 1,626 distinct `geo_id`
  - `county`: 10,057
  - `cbsa`: 5,088
  - EJScreen-enriched rows currently appear only for `2024` AQI backbone rows: `977` county rows and `482` CBSA rows
  - FEMA-enriched rows currently appear only for `2025` AQI backbone rows: `959` county rows and `478` CBSA rows

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **AQI bucket counts**: `days_with_aqi`, `good_days`, `moderate_days`, `usg_days`, `unhealthy_days`, `very_unhealthy_days`, `hazardous_days`
- **AQI summary metrics**: `max_aqi`, `aqi_p90`, `aqi_median`
- **Pollutant attribution metrics**: `days_ozone`, `days_pm25`
- **EJScreen rollup coverage**: `ejs_population_covered`
- **EJScreen population-weighted indicators**: `ejs_pm25`, `ejs_ozone`, `ejs_diesel_pm`, `ejs_traffic_proximity`, `ejs_superfund_proximity`, `ejs_rmp_proximity`, `ejs_wastewater_discharge`, `ejs_drinking_water_noncompliance`
- **EJScreen population-weighted national percentiles**: `ejs_pctile_pm25_us`, `ejs_pctile_ozone_us`, `ejs_pctile_diesel_pm_us`, `ejs_pctile_traffic_us`, `ejs_pctile_superfund_us`, `ejs_pctile_rmp_us`, `ejs_pctile_wastewater_us`, `ejs_pctile_drinking_water_us`
- **EJScreen exposure summary metrics**: `ejs_avg_high_exposure_indicators`, `ejs_avg_high_exposure_supplemental`
- **FEMA composite risk metrics**: `fema_risk_score`, `fema_eal_score`, `fema_alr_national_pctile`, `fema_alr_vra_national_pctile`, `fema_social_vulnerability_score`, `fema_community_resilience_score`
- **FEMA hazard risk scores**: `fema_avalanche_risk_score`, `fema_coastal_flooding_risk_score`, `fema_cold_wave_risk_score`, `fema_drought_risk_score`, `fema_earthquake_risk_score`, `fema_hail_risk_score`, `fema_heat_wave_risk_score`, `fema_hurricane_risk_score`, `fema_ice_storm_risk_score`, `fema_inland_flooding_risk_score`, `fema_landslide_risk_score`, `fema_lightning_risk_score`, `fema_strong_wind_risk_score`, `fema_tornado_risk_score`, `fema_tsunami_risk_score`, `fema_volcanic_activity_risk_score`, `fema_wildfire_risk_score`, `fema_winter_weather_risk_score`

## Data Quality Notes
- Live query checks confirm the intended `geo_level + geo_id + year` grain with zero duplicate keys.
- AQI remains the source-faithful county + CBSA backbone of the table.
- County rows inherit the documented Silver county-identification rule:
  - start from EPA `state_name + county_name`
  - normalize the source strings
  - match to canonical county GEOIDs through geography crosswalk aliases
  - apply a very small manual alias fallback for known edge cases
- CBSA rows inherit the source-published `cbsa_code` directly as `geo_id`.
- Ten county rows were intentionally dropped upstream in Silver because they could not be matched to a canonical county GEOID after normalization.
- EJScreen metrics are rolled up from tract to county / CBSA with population-weighted averages using tract population as the weight.
- Because the Gold table keeps AQI as the backbone, EJScreen values are currently non-null only where the 2024 EJScreen rollup intersects an AQI county / CBSA row.
- The EJScreen tract archive excludes Puerto Rico and territorial rows from the canonical Silver layer, so Gold inherits that same supported-geography boundary.
- FEMA NRI now joins from `silver.fema_nri` at the shared `geo_level + geo_id + year` grain.
- Because FEMA is currently a single-release `2025` surface, the FEMA columns are non-null only for `2025` AQI rows that intersect the FEMA county / CBSA contract.
- FEMA Silver retains more county-equivalent rows than the monitored AQI backbone, so the Gold table intentionally shows the AQI-overlapping subset rather than every staged FEMA geography.

## Lineage
1. **Primary build script**: [gold_environment_wide.sql](/Users/danberle/Documents/projects/patterns_in_place/foundations/etl/gold/gold_environment_wide.sql)
2. **Primary upstreams**:
   - `silver.epa_aqi`
   - `silver.ejscreen`
   - `silver.fema_nri`
   - `gold.dim_geo`

## Known Gaps / To-Dos
- County normalization remains dependent on current geography crosswalk coverage and a small manual alias list for legacy-name cases.
- EJScreen is currently a population-weighted tract rollup. If we later need alternative aggregation logic, such as simple tract averages or threshold shares, that should be added as new derived columns rather than by replacing the current contract.
- FEMA tract rows are staged but intentionally excluded from this first-pass Gold mart. If we later want tract-level or tract-derived FEMA exposure, that should be added through a separate documented extension rather than by changing the current county + CBSA contract in place.
- If we decide later that AQI is more useful as a composite score or normalized percentile surface, that should happen in a downstream analytical layer rather than by changing this source-faithful Gold mart.
