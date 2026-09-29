# Q6 Foundation Handoff — LODES Place-to-Place OD Profiling and Publication

You are extending the shared LODES OD foundation. This work serves Q6 and later
relationship analyses; it is not a Q6 anchor-classification implementation.

## Read first

1. `AGENTS.md`
2. `metro-deep-dive-program/analyses/explanation/q6_one_metro/LODES_OD_INGEST_AGENT_SCOPE.md`
3. `foundations/etl/staging/get_lehd_lodes_od.R`
4. `foundations/etl/silver/lehd_lodes_od_silver.R`
5. `foundations/data_dictionary/layers/silver/silver__lehd_lodes_od_county.md`
6. `metro-deep-dive-program/engines/geography/CONTRACT.md`
7. `metro-deep-dive-program/analyses/explanation/q6_one_metro/EXPLANATION_Q6_ONE_METRO_SPEC.md`

## Mission

Decide, from measured source profiling, whether Place-to-Place LODES OD should
be a durable national Silver surface. If it is safe, build it from block-native
OD without persisting block-to-block flows. Profile tract-to-tract alongside it
only to inform the storage decision; do not build a durable tract surface unless
the evidence shows a concrete shared consumer need.

## Source and current state

- LODES 2023 OD source files are block-to-block and are partitioned by
  workplace state, `main` versus `aux`, and job type.
- `w_geocode` is the workplace block and `h_geocode` is the home block.
- The existing `silver.lehd_lodes_od_county` is already a validated county
  aggregate. It cannot be disaggregated to Places.
- `silver.block_registry` has national block identity, including `place_geoid`,
  tract, county, and 2020 boundary metadata. It can map both OD endpoints.

## Required work

1. Profile one 2023 state’s `JT00` and `JT02`, `main` and `aux` source files:
   source row count, job totals, compressed/uncompressed size, endpoint match
   rates, rows/jobs with no Census Place endpoint, duplicates, and overlap
   between parts.
2. For that same source, calculate aggregate row counts and storage estimates
   for both home-Place × work-Place and home-tract × work-tract outputs. Keep
   home/work direction explicit.
3. Estimate national durable-table scale from the state profile(s). Record a
   recommendation: durable Place surface, parameterized Place helper, and
   whether tract flow is not justified or needs a separate consumer proposal.
4. Write the contract before implementation. The preferred Place grain is:
   home Place/status × work Place/status × year × source workplace state ×
   source part × job type × segment. Preserve release and transformation
   version, source filename/date, row accounting, and coverage status.
5. Map both endpoints through `silver.block_registry`, but retain a declared
   `no_census_place` status for unincorporated/missing Place endpoints. Never
   drop these rows; they are needed for a Place’s external and unincorporated
   denominator.
6. If implementation is approved by the measured profile, process source files
   sequentially, aggregate before persistence, validate `main`/`aux` handling,
   reconcile mapped plus no-Place totals to each source asset, and add Silver
   documentation plus coverage metadata.
7. Publish a consumer example that starts with a matrix or ranked connection
   table, not a flow map. State that OD describes work relationships and cannot
   determine anchor status by itself.

## Guardrails

- Do not persist national block-to-block OD by default.
- Do not infer Place flows from the county OD table.
- Do not confuse home Place and workplace Place direction.
- Do not treat unavailable provider coverage as zero; Alaska and Michigan are
  known 2023 provider gaps in the current contract.
- Do not run parallel DuckDB materializations.

## Done when

The team has a measured publication decision and, if the durable Place surface
is approved, a validated home-Place × work-Place table with coverage and
unincorporated-endpoint treatment that Q6 can consume read-only.
