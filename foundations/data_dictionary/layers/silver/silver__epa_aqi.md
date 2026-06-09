# Data Dictionary: silver.epa_aqi

## Overview
- **Table**: `silver.epa_aqi`
- **Purpose**: Standardized EPA annual AQI table combining county and CBSA rows into the canonical analytical geography contract.
- **Row count**: 15,145
- **Time coverage**: 2016 through 2025

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
- **Observed geo coverage**:
  - `county`: 10,057 rows
  - `cbsa`: 5,088 rows
- **Key QA**: live duplicate check on `geo_level + geo_id + year` returned zero duplicates.

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **AQI bucket counts**: `days_with_aqi`, `good_days`, `moderate_days`, `usg_days`, `unhealthy_days`, `very_unhealthy_days`, `hazardous_days`
- **AQI summary metrics**: `max_aqi`, `aqi_p90`, `aqi_median`
- **Pollutant attribution metrics**: `days_ozone`, `days_pm25`

## Data Quality Notes
- County rows are normalized from EPA `state_name + county_name` strings into canonical county GEOIDs using a deterministic county crosswalk join in Silver.
- County identification uses normalized source names rather than a source-published county FIPS:
  - start from EPA `state_name` + `county_name`
  - normalize case, punctuation, saint/st variants, and common county-equivalent suffixes
  - join to county crosswalk aliases built from `silver.xwalk_county_state`
  - supplement with a very small manual alias layer for known source/crosswalk mismatches such as Connecticut legacy county names
- CBSA rows use the source-published `cbsa_code` directly and backfill display names from `silver.xwalk_cbsa_county` where available.
- Any county rows that still fail canonical GEOID assignment after that normalization path are dropped from Silver rather than carried with ambiguous geography.
- AQI bucket totals are validated upstream in staging, so the category-day fields sum to `days_with_aqi` before rows reach Silver.
- EPA AQI is a partial-coverage environmental source rather than a full national geography census.
  - Counties and CBSAs only appear when EPA has sufficient AQI summary coverage for that year.
- This first-pass Silver contract intentionally keeps the highest-signal AQI summary fields and leaves lower-priority pollutant attribution columns such as CO, NO2, and PM10 in staging only.

## Lineage
1. `foundations/etl/staging/get_epa_aqi.R` downloads and lands the annual EPA county and CBSA AQI ZIP files for 2016 through 2025 into `staging.epa_aqi`.
2. `foundations/etl/silver/epa_aqi_silver.R` reads the county and CBSA staging slices, normalizes county GEOIDs from source names, uses the native CBSA codes directly, selects the approved AQI metrics, row-binds both geography levels, and writes `silver.epa_aqi`.

## Known Gaps / To-Dos
- Silver currently preserves source coverage as-is and does not derive any additional geographies beyond county and CBSA.
- County name normalization depends on the current geography crosswalk metadata and may need a small exception list if EPA introduces new naming variants in future annual files.
- The next downstream step is `gold.environment_wide`, where AQI will be combined with EJScreen and FEMA risk fields as those tracks land.
