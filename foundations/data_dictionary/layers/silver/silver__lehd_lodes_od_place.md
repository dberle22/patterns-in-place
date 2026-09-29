# Data Dictionary: silver LEHD LODES OD Place flows

- **Table**: `silver.lehd_lodes_od_place`
- **Purpose**: directional 2023 Census Place home-to-work relationship surface
  for relationship analysis, including external and unincorporated endpoints.
- **Grain**: the staging grain is retained without combining job types or OD
  parts. `JT02` is a subset of `JT00` and the two measures must not be summed.
- **Identity**: matched home/work endpoint IDs are seven-digit Census Place
  GEOIDs. `no_census_place` and `unmapped_block` remain explicit endpoint
  statuses rather than Place IDs.
- **Coverage**: always consult `silver.lehd_lodes_od_place_coverage` before
  interpreting an absent flow as zero.
- **Use boundary**: supports matrices and ranked connections; it describes
  work relationships and cannot establish anchor status, access, or travel time.
- **Validation**: every available source asset reconciles its aggregated jobs
  to source `S000`; keys are unique and measures nonnegative.
