# Data Dictionary: gold.transport_built_form_sld

## Overview
- **Table**: `gold.transport_built_form_sld`
- **Purpose**: County-level EPA Smart Location Database baseline mart for walkability, transit access, jobs accessibility, and built-form context.
- **KPI applicability**: Gold output table for the one-time EPA SLD baseline rather than the recurring ACS transport panel.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
- **Current scope**:
  - `geo_level = county`
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
- The current Gold contract is county-only.
- The `2021` Connecticut rows use the legacy county GEOIDs (`09001` through `09015`) via an explicit manual fallback so the SLD baseline aligns with the `2021` county ACS transport contract.
- Alaska county-equivalent `02261` remains excluded because the current county crosswalk no longer carries that retired geography.
- Tract-level SLD recovery remains deferred pending a stronger 2010/2020 tract relationship strategy or a geodatabase-based ingest path.

## Lineage
1. `foundations/etl/staging/get_epa_sld.R` downloads the direct EPA Smart Location CSV, reconstructs canonical block-group GEOIDs, keeps the approved compact indicator set plus `TotEmp`, and writes `staging.epa_sld`.
2. `foundations/etl/silver/epa_sld_silver.R` aggregates block groups to counties using exact recomputation where possible and documented weighted means elsewhere, then writes `silver.epa_sld`.
3. `foundations/etl/gold/gold_transport_built_form_sld.sql` promotes the modeled county baseline directly into `gold.transport_built_form_sld`.

## Known Gaps / To-Dos
- No CBSA or tract rows are included in the current Gold contract.
- If we later recover tract-level SLD cleanly, we should revisit whether this table stays county-only or adds a parallel tract baseline.
