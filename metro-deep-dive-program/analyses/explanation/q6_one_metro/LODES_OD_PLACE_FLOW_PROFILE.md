# LODES OD Place Flow Publication Decision

**Decision date:** 2026-09-22  
**Scope:** 2023 LODES 8.4 `S000` OD files, profiled in Virginia (`VA`) for
`JT00` and `JT02`, both `main` and `aux` parts. This is a publication decision,
not a Q6 anchor-classification implementation.

## Decision

Build a durable national **Place-to-Place** Silver surface after the contract
below is reviewed. Do not persist block-to-block OD. Do not build a durable
tract-to-tract surface: it is roughly eight times the row count for no declared
shared consumer. A future tract consumer needs its own proposal; a
parameterized, sequential helper can aggregate a selected workplace-state or
metro scope when needed.

The durable Place surface is materially smaller than the temporary source files,
retains flows involving unincorporated territory, and supports Q6's matrix and
ranked-connection views. It describes work relationships only; it cannot decide
whether a Place is an anchor.

## Measured Virginia profile

Both endpoints joined to `silver.block_registry` at the block level. Every row
and every `S000` job count matched at the tract endpoint level. `no_census_place`
means a valid block that has no Census Place assignment, not a failed block join.

| Source asset | Rows | Jobs | Compressed / uncompressed | Rows with a no-Place endpoint | Jobs with a no-Place endpoint | Place pairs | Tract pairs |
|---|---:|---:|---:|---:|---:|---:|---:|
| `main JT00` | 3,062,302 | 3,548,645 | 17.4 / 178.2 MiB | 1,315,094 (42.9%) | 1,496,809 (42.2%) | 70,019 | 798,800 |
| `aux JT00` | 335,293 | 346,247 | 2.3 / 19.5 MiB | 125,322 (37.4%) | 129,296 (37.3%) | 51,424 | 216,690 |
| `main JT02` | 2,715,811 | 3,014,227 | 15.6 / 158.0 MiB | 1,153,261 (42.5%) | 1,259,973 (41.8%) | 67,028 | 762,759 |
| `aux JT02` | 301,586 | 310,271 | 2.1 / 17.5 MiB | 111,946 (37.1%) | 114,956 (37.1%) | 47,939 | 199,553 |
| **Total** | **6,414,992** | **7,219,390** | **37.4 / 373.2 MiB** | **2,705,623 (42.2%)** | **3,001,034 (41.6%)** | **236,410** | **1,977,802** |

Additional checks:

- There were zero duplicate block endpoint pairs and zero exact duplicate rows
  within each asset.
- There were zero shared block endpoint pairs between `main` and `aux`, for
  both job types.
- At Place grain, a `no_census_place` endpoint can otherwise make distinct
  source parts look like the same pair. `source_part` must therefore remain in
  the fact-table key rather than being collapsed away.
- Across the profiled job types, only 58.4% of Virginia flow counts have both
  endpoints in Census Places. Dropping the remaining 41.6% would bias a Place's external and
  unincorporated denominator.

## Scale estimate

The managed 2023 WAC staging surface contains 146.57 million all jobs across
the 49 available workplace states; Virginia contains 3.895 million. Applying
that 37.63× job-weighted multiplier to this profile gives an order-of-magnitude
national estimate. State heterogeneity, especially very large states, warrants
a planning range rather than treating this as a final count.

| Surface, both job types and both parts | Virginia rows | National estimate | Measured Virginia Parquet | Planning footprint |
|---|---:|---:|---:|---:|
| Temporary block-native source inputs | 6.41m | 241m source rows | 37 MiB gzip / 373 MiB CSV | about 1.4 GiB gzip / 14 GiB CSV, sequential and transient |
| Aggregated Place fact | 236k | 8.9m | 0.96 MiB ZSTD Parquet | roughly 40–100 MiB Parquet; allow 0.1–0.5 GiB in DuckDB with metadata and operational headroom |
| Aggregated tract fact | 1.98m | 74.4m | 8.4 MiB ZSTD Parquet | roughly 0.3–1 GiB Parquet; allow 1–3 GiB in DuckDB before indexes/working space |

The national input estimate is a capacity warning, not a persistence proposal:
read one asset, map both endpoints, aggregate, validate, write its compact
result, then discard the raw file. Alaska and Michigan retain explicit
`provider_unavailable_2023` coverage rows and do not contribute zero flows.

## Proposed contracts

### `staging.lehd_lodes_od_place`

The managed staging table is already aggregated; raw block rows are transient
within the sequential loader.

- **Grain/key:** `home_place_geoid + home_place_status + work_place_geoid +
  work_place_status + year + source_state + source_part + job_type + segment`.
- **Direction:** home is `h_geocode`; work is `w_geocode`. `source_state` is
  the workplace state.
- **Endpoint fields:** each endpoint has `*_place_geoid` and `*_place_status`.
  Matched IDs are seven-digit Census Place GEOIDs (`state_fips + place_fips`),
  never the state-local five-digit Place code.
  A matched endpoint has its Census Place GEOID; an unincorporated or otherwise
  unassigned registry block is `no_census_place` with the explicit sentinel
  GEOID `no_census_place`. An endpoint missing from the block registry is a
  distinct `unmapped_block` status and remains in reconciliation output.
- **Measures:** `jobs` (sum of `S000`) and `source_block_row_count`.
- **Provenance:** `release_format_version`, `transformation_version`, source
  filename, source created date, and load date. Asset-level row/job totals
  belong in coverage rather than being repeated on every fact row.

### `staging.lehd_lodes_od_place_coverage` and Silver counterpart

One row per expected `source_state + year + source_part + job_type + segment`
asset, including unavailable providers. Keep source rows/jobs, mapped rows/jobs,
no-Place rows/jobs, unmapped rows/jobs, aggregated pair count, reconciliation
result, source filename/date, release and transformation versions, and
`coverage_status` (`available_validated`, `provider_unavailable_2023`, or a
specific failure state). An absent fact row is never evidence of zero without
this table.

### `silver.lehd_lodes_od_place`

Publish the staging grain without collapsing parts or job types. Add governed
Place labels only as a convenience enrichment; GEOIDs and statuses remain the
identity and coverage authority. Validate nonnegative jobs, unique grain,
source-part handling, and equality of source jobs to matched + no-Place +
unmapped jobs for every available asset.

## Recommended next step

Approve this contract, then implement the Place staging/Silver pair and its
coverage table in a state-replace, sequential loader. Run a second profiling
state with a materially different Place pattern (for example California or
Texas) before locking the capacity reservation, but that validation should not
delay the contract review: the observed Place-to-tract compression is already
large enough to support the durable-Place / on-demand-tract decision.
