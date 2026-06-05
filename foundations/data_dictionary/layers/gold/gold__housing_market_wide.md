# Data Dictionary: gold.housing_market_wide

## Overview
- **Table**: `gold.housing_market_wide`
- **Purpose**: Curated housing market mart that annualizes Zillow home-value and rent series into comparable geo-year records and enriches them with annual FHFA house-price appreciation metrics.
- **Row count**: 289,585
- **KPI applicability**: Gold output table with annual level and YoY change fields for both yearly-average and December market references.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
  - Live uniqueness check on June 4, 2026: rows=289,585; distinct PK=289,585; duplicates=0
- **Time coverage**: `year` min=2016, max=2025
- **Geo coverage**: 3 geo levels; 28,811 distinct `geo_id`
  - `zcta` 250,155
  - `county` 30,253
  - `cbsa` 9,177

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **FHFA appreciation references**: `hpi_level`, `hpi_yoy_pct`, `hpi_5yr_pct`, `hpi_10yr_pct`
- **Home value references**: `zhvi_annual_avg`, `zhvi_december`, `zhvi_annual_avg_yoy_pct`, `zhvi_december_yoy_pct`
- **Rent references**: `zori_annual_avg`, `zori_december`, `zori_annual_avg_yoy_pct`, `zori_december_yoy_pct`

## Data Quality Notes
- Live query checks confirm the intended `geo_level + geo_id + year` grain with zero duplicate keys.
- FHFA enrichment follows the Zillow market surface rather than the full FHFA Silver surface, so `state` and `us` rows remain available in `silver.fhfa_hpi` but do not appear in this Gold mart.
- FHFA coverage is substantial but not universal on the Zillow market surface: `hpi_level` is populated for 209,732 rows and null for 79,853 rows in the current profile.
- By geography, FHFA currently fills `9,141` CBSA rows, `27,217` county rows, and `173,374` ZCTA rows. The ZCTA coverage uses the approved ZIP5-as-ZCTA proxy from FHFA Silver.
- Annual average fields are computed over observed monthly Zillow values only after Silver trims null rows and limits history to 2016 forward.
- December fields are sparser than annual averages because they require a year-end monthly observation; 2025 December fields are mostly null in the current snapshot because Zillow Silver currently stops at October 2025.
- ZORI coverage remains much narrower than ZHVI: `zori_annual_avg` is null in 241,292 rows, while `zhvi_annual_avg` is null in only 83 rows.

## Lineage
1. **Primary build script**: [gold_housing_market_wide.sql](/Users/danberle/Documents/projects/patterns_in_place/foundations/etl/gold/gold_housing_market_wide.sql)
2. **Primary upstreams**:
   - `silver.fhfa_hpi`
   - `silver.zillow_zhvi`
   - `silver.zillow_zori`

## Known Gaps / To-Dos
- The Gold row surface is still anchored to Zillow availability, so FHFA's broader `us` and `state` annual coverage remains Silver-only for now.
- Because Silver drops null months, annual averages are based on observed months rather than forced 12-month panels.
- City and state Zillow slices remain intentionally excluded pending the separate post-Gold contract review.
