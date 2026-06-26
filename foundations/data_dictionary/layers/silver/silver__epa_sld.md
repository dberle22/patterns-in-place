# Data Dictionary: silver.epa_sld

## Overview
- **Table**: `silver.epa_sld`
- **Purpose**: EPA Smart Location Database table carrying county, CBSA, and state built-form, walkability, transit-access, and accessibility indicators aggregated from census block groups.
- **Time coverage**: 2021 only

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
- **Observed geo coverage**:
  - `county`: `3,232`
  - `cbsa`: `928`
  - `state`: `56`
- **Key QA**: the Silver script stops if any staged county GEOID fails to resolve to `silver.xwalk_county_state`, and it then checks for duplicate `geo_level + geo_id + year` rows before writing.

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Geography helpers**: `state_abbr`
- **Denominator and coverage fields**: `total_population`, `total_employment`, `housing_units`, `households`, `land_acres_unprotected`, `block_group_count`, `block_group_count_transit_non_null`, `transit_population_coverage_share`, `walkability_population_coverage_share`
- **Built-form and accessibility metrics**: `walkability_index`, `employment_housing_mix`, `employment_mix`, `street_intersection_density`, `auto_oriented_intersection_share`, `transit_service_density`, `transit_frequency_peak`, `distance_to_transit`, `jobs_access_45min_transit`, `workers_access_45min_transit`, `jobs_access_45min_auto`, `workers_access_45min_auto`
- **Recomputed density metrics**: `employment_density_gross`, `population_density_gross`, `housing_density_gross`

## Aggregation Rules
- The source is published at census block-group grain.
- Silver builds counties directly from block groups, then derives CBSA and state rows from that county base so tract recovery can remain deferred.
- Aggregation is metric-specific rather than one-size-fits-all:
  - `total_population`, `total_employment`, `housing_units`, `households`, and `land_acres_unprotected` are summed across block groups.
  - `employment_density_gross`, `population_density_gross`, and `housing_density_gross` are recomputed from summed numerators and summed land-area denominators at each modeled geography.
  - `walkability_index`, destination accessibility, and distance-style metrics use population-weighted means.
  - `employment_housing_mix` uses a household-weighted mean.
  - `employment_mix` uses an employment-weighted mean.
  - `street_intersection_density` and `auto_oriented_intersection_share` use land-area-weighted means.
- This means the three density fields are exact recomputations from retained components, while several other metrics are documented approximations aggregated from lower-grain values.

## Data Quality Notes
- The live EPA CSV writes `GEOID10` and `GEOID20` in scientific notation.
  - Staging does not trust those raw fields as keys.
  - Instead, it reconstructs the canonical 12-digit block-group GEOID from `STATEFP + COUNTYFP + TRACTCE + BLKGRPCE`.
- Silver derives county GEOIDs directly as `state_fips + county_fips` and validates them against `silver.xwalk_county_state`.
- CBSA rows are derived by joining the county base to `silver.xwalk_cbsa_county`.
  - The current build assumes one county maps to at most one CBSA in that crosswalk snapshot.
- State rows are derived from the county base through `silver.xwalk_state_region`.
- The first-pass county contract keeps the 8 legacy Connecticut county GEOIDs through an explicit manual lookup.
  - This is intentional because the 2021 ACS county transport contract also uses the legacy Connecticut county GEOIDs.
  - Alaska county-equivalent `02261` remains excluded because the current county crosswalk no longer carries that retired geography.
- Transit-related metrics are only available where EPA has GTFS-based coverage, so nulls are expected in some block groups.
  - The table keeps population-coverage helper fields so downstream users can distinguish low-service places from low-coverage source areas.
- Multi-state CBSAs intentionally leave `state_abbr` null rather than implying a single-state identity.
- This first-pass Silver contract is intentionally tract-free.
  - The direct CSV staging path reconstructs tract identity from `STATEFP + COUNTYFP + TRACTCE`, but the live tract match rate to the governed tract backbone is too incomplete to support production tract rows.
  - Tract-level recovery therefore remains a future follow-on that likely requires the official Census 2010/2020 tract relationship files or the geodatabase-based SLD delivery rather than the current CSV-only path.

## Lineage
1. `foundations/etl/staging/get_epa_sld.R` downloads the direct EPA Smart Location CSV, reconstructs canonical block-group GEOIDs from component geography parts, keeps the agreed compact indicator set plus `TotEmp`, and materializes `staging.epa_sld`.
2. `foundations/etl/silver/epa_sld_silver.R` derives county GEOIDs, validates canonical county coverage against `silver.xwalk_county_state`, aggregates block-group rows to county using metric-specific rules, derives CBSA and state rows from that county base, recomputes exact density metrics, and writes `silver.epa_sld`.

## Known Gaps / To-Dos
- `walkability_index` remains a weighted county approximation of EPA's block-group score rather than a true county-level EPA re-estimation.
- If downstream Gold work needs tract transportation summaries, the next step should be to add a tract relationship bridge or move to a source artifact that preserves tract identity reliably enough for the governed tract backbone rather than re-aggregating block groups in multiple places.
