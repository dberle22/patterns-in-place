# Data Dictionary: staging LEHD LODES OD county flows

- **Table**: `staging.lehd_lodes_od_county`
- **Scope**: 2023 national available-workplace-state surface; `JT00` all jobs and `JT02` private jobs, `S000` total jobs. Alaska and Michigan are explicit provider-unavailable coverage records.
- **Grain**: `home_county_geoid + work_county_geoid + year + source_state + source_part`.
- **Direction**: `home_county_geoid` is worker residence; `work_county_geoid` is job location.
- **Measures**: `jobs_all` and `jobs_private` are overlapping job universes and must not be summed together.
- **Provenance**: Each measure retains source file, source creation date, and contributing block-row count. `source_part` distinguishes in-state `main` from out-of-state-home `aux` files.
- **Transformation**: Source blocks are validated and aggregated directly to county pairs; block flows are not persisted.

The companion `staging.lehd_lodes_od_coverage` records every expected source part/job-type asset, source and aggregate totals, geography-match rate, and reconciliation result. Consumers must use it to distinguish unavailable coverage from a zero flow.
