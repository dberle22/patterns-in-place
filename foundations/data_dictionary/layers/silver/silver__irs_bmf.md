# Data Dictionary: silver.irs_bmf

## Overview
- **Table**: `silver.irs_bmf`
- **Purpose**: Canonical latest-snapshot nonprofit-density table for county and CBSA social-fabric analysis.
- **KPI applicability**: supports `nonprofits_per_100k` and the companion all-org density metric for Character / Social Fabric work.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id`.
- **Primary key candidate**: (`geo_level`, `geo_id`)
- **Current scope**:
  - `geo_level = county`, `cbsa`
  - snapshot date `2026-05-12`
  - ACS denominator year `2024`

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`
- **Snapshot metadata**: `snapshot_date`, `population_year`
- **Denominator**: `population_total`
- **Estimated organization counts**: `nonprofit_org_count_est`, `nonprofit_org_count_nonreligious_est`
- **Per-capita metrics**: `nonprofits_per_100k`, `nonprofits_total_per_100k`
- **Allocation QA helpers**: `source_zip5_count`, `weight_method`

## Data Quality Notes
- The first-pass Silver contract aggregates the staging rows to `zip5` before any county allocation, then applies the HUD ZIP-county relationship file. That keeps the modeled geography step aligned with the actual source grain we can trust.
- `weight_method` reflects the ZIP allocation hierarchy:
  - prefer `BUS_RATIO`
  - fall back to `TOT_RATIO` / housing when the business ratio is unavailable
- Distinct staged ZIP5 coverage in the landed snapshot is `36,760`.
  - `662` of those ZIPs do not resolve in `silver.xwalk_zcta_county` and are excluded from the modeled geography rollup.
  - `2,251` ZIPs rely on the housing-ratio fallback rather than direct business-ratio coverage.
- The current landed table has `4,068` rows:
  - `3,143` county rows
  - `925` CBSA rows
- The non-religious count is a conservative approximation:
  - exclude `NTEE_CD` values beginning with `X`
  - exclude filing-requirement codes `06` and `13`

## Lineage
1. `foundations/etl/staging/get_irs_bmf.R` downloads the latest IRS regional EO BMF files, filters to active U.S. rows, derives `zip5`, and writes `staging.irs_bmf`.
2. `foundations/etl/silver/irs_bmf_silver.R` summarizes staged organizations to ZIP5, allocates ZIP counts to county with the HUD ZIP-county crosswalk, rolls county counts to CBSA, joins ACS population denominators, and writes `silver.irs_bmf`.

## Known Gaps / To-Dos
- This is a headquarters / mailing-address density proxy, not a direct measure of where nonprofit services are delivered.
- The current Silver contract is static-snapshot only and does not yet support time-trend analysis across monthly EO BMF releases.
- State rows are intentionally not modeled in the first pass because the metric-map need is county and CBSA social-fabric coverage.
