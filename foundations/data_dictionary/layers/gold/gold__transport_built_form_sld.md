# Data Dictionary: gold.transport_built_form_sld

## Overview
- **Table**: `gold.transport_built_form_sld`
- **Purpose**: EPA Smart Location Database baseline mart for county, CBSA, and state walkability, transit access, jobs accessibility, and built-form context.
- **KPI applicability**: Gold output table for the one-time EPA SLD baseline rather than the recurring ACS transport panel.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
- **Current scope**:
  - `geo_level = tract`, `county`, `cbsa`, `state`
  - `year = 2021`

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Geography helper**: `state_abbr`
- **Denominator and coverage fields**: `total_population`, `total_employment`, `housing_units`, `households`, `land_acres_unprotected`, `block_group_count`, `block_group_count_transit_non_null`, `block_group_count_walkability_non_null`, `transit_population_coverage_share`, `walkability_population_coverage_share`
- **EPA Smart Location metrics**: `walkability_index`, `employment_housing_mix`, `employment_mix`, `street_intersection_density`, `auto_oriented_intersection_share`, `transit_service_density`, `transit_frequency_peak`, `distance_to_transit`, `jobs_access_45min_transit`, `workers_access_45min_transit`, `jobs_access_45min_auto`, `workers_access_45min_auto`
- **Recomputed density context**: `employment_density_gross`, `population_density_gross`, `housing_density_gross`

## Data Quality Notes
- This table is intentionally separate from `gold.transport_built_form_wide`.
  - SLD is a sparse, single-vintage (`2021`) baseline source.
  - Keeping it separate avoids implying that the SLD fields are recurring annual transport series.
- The Gold contract includes tract, county, CBSA, and state rows promoted directly from `silver.epa_sld`.
- Tract rows use the Census Bureau 2010→2020 block group relationship file (`staging.census_bg_xwalk_2010_2020`) to map SLD's 2010 BG boundaries onto 2020 tract GEOIDs. Each split BG contributes proportionally via land-area weights, and the resulting 2020 tract GEOIDs align with the TIGRIS 2023 tract backbone in `silver.xwalk_tract_county`. Coverage is 83,220 tracts (99.7% have a walkability index).
- Tracts not resolved: Puerto Rico, US territories, and Connecticut's 2022 planning district restructuring — the same geographic edge cases excluded at county level.
- The `2021` Connecticut rows use the legacy county GEOIDs (`09001` through `09015`) via an explicit manual fallback so the SLD baseline aligns with the `2021` county ACS transport contract.
- Alaska county-equivalent `02261` remains excluded because the current county crosswalk no longer carries that retired geography.
- Multi-state CBSAs intentionally keep `state_abbr` null rather than implying a single-state identity.

## Lineage
1. `foundations/etl/staging/get_epa_sld.R` downloads the direct EPA Smart Location CSV, reconstructs canonical block-group GEOIDs, keeps the approved compact indicator set plus `TotEmp`, and writes `staging.epa_sld`.
2. `foundations/etl/staging/get_census_bg_crosswalk.R` downloads the Census Bureau 2010→2020 block group relationship file and writes `staging.census_bg_xwalk_2010_2020` with land-area weights.
3. `foundations/etl/silver/epa_sld_silver.R` aggregates block groups to tracts (via the BG crosswalk), counties, CBSAs, and states using population-weighted means, and writes `silver.epa_sld`.
4. `foundations/etl/gold/gold_transport_built_form_sld.sql` promotes the modeled baseline directly into `gold.transport_built_form_sld`.

## Known Gaps / To-Dos
- Tract rows for Puerto Rico, US territories, and CT planning districts are excluded by design — the same boundary edge cases excluded at county level.
- The Census BG crosswalk uses land-area weights as a proxy for population distribution within split BGs. NHGIS target-density weights would be more precise but require an account; land-area weights are a well-accepted fallback for most use cases.
