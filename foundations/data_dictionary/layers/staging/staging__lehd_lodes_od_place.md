# Data Dictionary: staging LEHD LODES OD Place flows

- **Table**: `staging.lehd_lodes_od_place`
- **Scope**: 2023 LODES 8.4 `S000` flows for `JT00` and `JT02`. Raw block OD
  files are transient inputs; this managed staging table is already aggregated.
- **Grain**: `home_place_geoid + home_place_status + work_place_geoid +
  work_place_status + year + source_state + source_part + job_type + segment`.
- **Direction**: home is the worker-residence `h_geocode`; work is the job
  location `w_geocode`; `source_state` is the workplace state.
- **Measures**: `jobs` is the sum of source `S000`; `source_block_row_count`
  provides the contributing native-flow count.
- **Endpoint status**: `matched`, `no_census_place`, and `unmapped_block` are
  distinct outcomes. The two non-Place statuses are retained, never dropped.
- **Matched identity**: matched endpoint IDs are seven-digit Census Place
  GEOIDs (`state_fips + place_fips`), consistent with Geography and not the
  provider's state-local five-digit Place code.
- **Provenance**: release/transformation versions and source filename/date stay
  with the aggregated row. Asset-level accounting is in the coverage table.

`staging.lehd_lodes_od_place_coverage` has one row per expected source asset.
It records source and mapped totals, no-Place/unmapped counts, pair counts,
reconciliation, and provider-unavailable status. Alaska and Michigan are not
zero-flow states in 2023; they have explicit coverage records.
