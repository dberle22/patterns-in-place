# Data Dictionary: silver LEHD LODES OD county flows

- **Table**: `silver.lehd_lodes_od_county`
- **Purpose**: Directional 2023 county home-to-work flow surface for all available workplace states.
- **Grain**: one observed `home_county_geoid + work_county_geoid + year + source_state + source_part` flow.
- **Measures**: `jobs_all` (`JT00`) and `jobs_private` (`JT02`). Private jobs are included in all jobs.
- **Coverage**: `silver.lehd_lodes_od_coverage` is required when interpreting an absent flow. Alaska and Michigan are explicitly provider-unavailable for 2023.
- **Geography**: Virginia workplaces must match the managed county backbone. Auxiliary external homes are retained even when their provider county is outside that backbone and are labeled with `home_county_geography_status`.
- **Validation**: every job-type/part aggregate reconciles to the Census source-file `S000` total before publication.
