# Data Dictionary: silver.ejscreen

## Overview
- **Table**: `silver.ejscreen`
- **Purpose**: Curated tract-level EJScreen environmental indicator table built from the archived 2024 tract file.
- **Time coverage**: 2024 only in the current first-pass archive contract.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
- **Observed geo coverage**: tract only
- **Key QA**: Silver runs a live duplicate check on `geo_level + geo_id + year` after the tract-vintage audit passes.

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Weighting / population**: `total_population`
- **Core environmental indicators**: `pm25`, `ozone`, `diesel_pm`, `traffic_proximity`, `superfund_proximity`, `rmp_proximity`, `wastewater_discharge`, `drinking_water_noncompliance`
- **National percentile fields**: `pctile_pm25_us`, `pctile_ozone_us`, `pctile_diesel_pm_us`, `pctile_traffic_us`, `pctile_superfund_us`, `pctile_rmp_us`, `pctile_wastewater_us`, `pctile_drinking_water_us`
- **Summary counts**: `count_high_exposure_indicators`, `count_high_exposure_supplemental`

## Data Quality Notes
- Before Silver writes any rows, it checks whether archived tract IDs exist in both `silver.xwalk_tract_county` and `gold.dim_geo`.
- The archive includes Puerto Rico plus territorial tracts for American Samoa, Guam, Northern Mariana Islands, and the U.S. Virgin Islands. Those rows are retained in staging but excluded from the first-pass Silver contract because the current Foundations tract backbone does not model them canonically.
- After excluding those unsupported archive geographies, Silver requires at least a 99 percent tract-key match rate against both canonical references. If supported-state coverage falls below that threshold, the script stops and forces a reassessment of archive compatibility.
- In the current archived 2024 pass, Silver drops `1,667` unsupported Puerto Rico / territory tracts and `294` additional supported-state tracts that do not resolve cleanly to the current tract spine.
- The first-pass modeled contract keeps only the tract-level environmental indicators we identified as most important for the environment-risk topic.
- Demographic context fields, bucketized helper columns, and text percentile labels remain staging-only for now.

## Lineage
1. `foundations/etl/staging/get_ejscreen.R` downloads and lands the archived EJScreen tract CSV into `staging.ejscreen`.
2. `foundations/etl/silver/ejscreen_silver.R` audits tract-key compatibility with canonical geography references, selects the approved core indicators, and writes `silver.ejscreen`.

## Known Gaps / To-Dos
- This first pass is tract-only. County and CBSA rollups should happen only after tract-key match quality is confirmed acceptable.
- The current tract table is analytically strong for the canonical U.S. tract backbone, but it is not yet a full all-geographies archive reproduction because Puerto Rico and territorial tracts fall outside the current geo reference system.
- If a future archive version materially worsens supported-state tract coverage, the next step is not to force a partial Silver table; it is to document the gap and decide whether to use a different archive version or a more permissive matching strategy.
- Additional indicators such as `no2`, `pre1960_housing`, and broader EJScreen burden composites remain available upstream in staging if we decide they belong in a later modeled contract.
