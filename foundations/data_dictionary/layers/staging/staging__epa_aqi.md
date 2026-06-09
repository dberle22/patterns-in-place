# Data Dictionary: staging EPA AQI

## Overview
- Schema: `staging`
- Family: `EPA AirData AQI`
- Contract scope: source-family staging contract for the unified annual county + CBSA AQI table produced by [`foundations/etl/staging/get_epa_aqi.R`](../../../etl/staging/get_epa_aqi.R)
- Documentation rule: AQI currently lands as one source-faithful table with a `geo_level` discriminator, so this file is the canonical staging contract for the entire AQI ingest

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| County annual AQI summaries | `epa_aqi` | County rows retain EPA `state_name` and `county_name` strings so Silver can own county GEOID crosswalking |
| CBSA annual AQI summaries | `epa_aqi` | CBSA rows retain EPA `cbsa_name` and `cbsa_code` directly from the source ZIPs |

## Contract Summary
- All staged AQI rows live in one table.
- Grain: one row per `geo_level + source geography key + year`
- Geography scope: EPA county annual summaries plus EPA CBSA annual summaries
- Current initial scope: `2016` through `2025`
- Shape expectation: approximately `15,171` total rows in the first 10-year load, made up of `10,083` county rows and `5,088` CBSA rows

## Shared Columns
- Geography discriminator: `geo_level`
- County source geography fields: `state_name`, `county_name`
- CBSA source geography fields: `cbsa_name`, `cbsa_code`
- Time field: `year`
- AQI bucket counts: `days_with_aqi`, `good_days`, `moderate_days`, `usg_days`, `unhealthy_days`, `very_unhealthy_days`, `hazardous_days`
- AQI summary metrics: `max_aqi`, `aqi_p90`, `aqi_median`
- Pollutant attribution counts: `days_co`, `days_no2`, `days_ozone`, `days_pm25`, `days_pm10`

## Lineage
- [`foundations/etl/staging/get_epa_aqi.R`](../../../etl/staging/get_epa_aqi.R) downloads the annual EPA county and CBSA AQI ZIP files for `2016:2025`, reads the single CSV inside each ZIP, row-binds the annual files within each geography family, normalizes the combined rows to the unified staging schema, validates AQI day-bucket totals, and writes `staging.epa_aqi`.
- The provider-level rationale, keep/drop column guidance, and downstream normalization plan live in [`../../sources/source__epa.md`](../../sources/source__epa.md).

## Data Quality Notes
- Verify uniqueness at `geo_level + source geography key + year`, where the source geography key is `state_name + county_name` for county rows and `cbsa_code` for CBSA rows.
- The AQI category-day columns should sum to `days_with_aqi`; the staging script enforces that contract before writing the table.
- County rows are intentionally source-faithful and do not yet carry county FIPS. Any canonical county GEOID assignment belongs in Silver.
- CBSA rows carry the provider-published `cbsa_code` directly and should remain zero-padded 5-digit strings. That source identifier is also the first-pass Silver `geo_id` for CBSA rows.
- Coverage is partial by design because EPA annual AQI summaries only exist for geographies with sufficient monitoring-based AQI data in a given year.

## Known Gaps / To-Dos
- The current staging contract keeps more pollutant attribution fields than the first-pass Silver table needs. Silver will intentionally narrow the modeled set.
- County rows still depend on a name-based crosswalk into canonical county GEOIDs downstream.
- Add landed year-by-year row counts if we want this staging contract to double as a refresh QA checklist.
