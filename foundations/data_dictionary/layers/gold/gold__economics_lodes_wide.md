# Data Dictionary: gold.economics_lodes_wide

## Overview
- **Table**: `gold.economics_lodes_wide`
- **Purpose**: Gold tract-and-above labor geography mart that joins workplace jobs from LODES WAC with resident workers from LODES RAC on a shared `geo_level + geo_id + year` surface and adds jobs-versus-workers mismatch metrics for downstream Deep Dive and regional analysis.
- **Status**: materialized from the current 2023 tract-first LODES build.
- **Row count**: `88,158`

## Grain & Keys
- **Declared grain**: one row per `geo_level + geo_id + year`
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
- **Current geography coverage**: `tract`, `county`, `cbsa`, `state`, and `division`
- **Current time coverage**: `year` min=`2023`, max=`2023`

## Contract Summary
- Inputs:
  - `silver.lehd_lodes_wac`
  - `silver.lehd_lodes_rac`
- Join rule:
  - full outer join on `geo_level + geo_id + geo_name + year`
  - preserve RAC-only rows where WAC is unavailable in the current source release
- Surface design:
  - keep the full WAC analytical family
  - keep the full RAC analytical family
  - add a compact set of cross-surface mismatch metrics
- Deferred from Gold:
  - OD home-to-work flows
  - race / ethnicity
  - sex

## Recommended Canonical Columns
- Dimensions: `geo_level`, `geo_id`, `geo_name`, `year`
- WAC totals and composition:
  - `jobs_total`
  - `jobs_age_*`, `jobs_earnings_*`, `jobs_edu_*`, `jobs_ind_*`
  - `jobs_firm_age_*`, `jobs_firm_size_*`
  - `pct_jobs_*`
- RAC totals and composition:
  - `workers_total`
  - `workers_age_*`, `workers_earnings_*`, `workers_edu_*`, `workers_ind_*`
  - `pct_workers_*`
- Gold-only mismatch metrics:
  - `jobs_minus_workers`
  - `workers_minus_jobs`
  - `jobs_to_workers_ratio`
  - `workers_to_jobs_ratio`
  - `pct_point_gap_age_*`
  - `pct_point_gap_earnings_*`
  - `pct_point_gap_edu_*`
  - `pct_point_gap_ind_*`

## Gold Rules
- Keep the Silver geography grain unchanged; do not widen with repeated parent geography fields.
- Use the full outer join because the current 2023 LODES release has RAC coverage in some geographies where WAC is unavailable.
- Compute ratio metrics only when the denominator is positive.
- Compute percentage-point gaps as `pct_jobs_* - pct_workers_*` so positive values mean the workplace-side share is more concentrated than the resident-worker-side share.

## Coverage Notes
- Current landed geography coverage:
  - `tract`: `84,029` rows
  - `county`: `3,144` rows
  - `cbsa`: `925` rows
  - `state`: `51` rows
  - `division`: `9` rows
- Rows with non-null `jobs_total`:
  - `tract`: `80,782`
  - `county`: `3,031`
  - `cbsa`: `889`
  - `state`: `49`
  - `division`: `9`
- Rows with non-null `workers_total`:
  - all `88,158` rows
- CBSA totals remain lower than county/state/division totals because non-metro counties do not belong to a CBSA.

## Data Quality Notes
- The current Gold table keeps the RAC-led geography surface because a full outer join preserves geographies that are present only on the resident-worker side.
- WAC is intentionally narrower in 2023 because Alaska and Michigan have missing WAC coverage in the current provider release.
- The governed Silver build already excludes the small set of unmatched tract GEOIDs before Gold is assembled, so Gold inherits the validated geography surface rather than re-handling those exceptions.

## Lineage
1. [`foundations/etl/staging/get_lehd_lodes.R`](../../../etl/staging/get_lehd_lodes.R) downloads state-based LODES bulk files and aggregates WAC and RAC to tract.
2. [`foundations/etl/silver/lehd_lodes_silver.R`](../../../etl/silver/lehd_lodes_silver.R) validates geography, derives tract-to-higher-geography rollups, and writes the canonical WAC and RAC Silver tables.
3. [`foundations/etl/gold/gold_economics_lodes.sql`](../../../etl/gold/gold_economics_lodes.sql) joins WAC and RAC and computes the Gold mismatch metrics.

## Known Gaps / To-Dos
- Add the deferred OD flow layer when the Deep Dive commute and spatial-mismatch methodology is ready.
- Revisit whether any of the industry percentage-point gap family should be collapsed into broader platform industry groups for lighter product surfaces.
