# Data Dictionary: staging CHR Health Rankings

## Overview
- Schema: `staging`
- Family: `County Health Rankings`
- Contract scope: source-family staging contract for the wide county analytic table produced by [`foundations/etl/staging/get_chr.R`](../../../etl/staging/get_chr.R)
- Documentation rule: CHR currently lands as one source-faithful annual county table, so this file is the canonical staging contract for the entire CHR analytic ingest

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| County analytic release | `chr_health_rankings` | Annual CHR analytic CSV with all published measure columns retained in wide form, including raw values, numerators, denominators, CI bounds, quality fields where shipped, and selected provider-specific helper fields |

## Contract Summary
- All staged CHR analytic columns live in one table.
- Grain: one row per `fips5 + release_year`
- Geography scope: source-faithful analytic release rows, including national and state summary rows plus the county and county-equivalent jurisdictions that feed downstream Silver
- Current initial scope: `2025` annual analytic release
- Shape expectation: approximately `3,200` county rows and approximately `2,388` columns in the 2025 file; future yearly refreshes may change the measure count

## Shared Columns
- Geography identifiers: `state_fips`, `county_fips`, `fips5`, `state_abbr`, `county_name`
- Release metadata: `release_year`, `county_clustered`
- Standard measure provenance pattern:
  - `v###_rawvalue`: published raw measure value
  - `v###_numerator`: source numerator underlying the measure
  - `v###_denominator`: source denominator underlying the measure
  - `v###_cilow`, `v###_cihigh`: lower and upper confidence interval bounds when provided
  - `v###_flag`: CHR quality or suppression flag where available in the provider file
- Provider-specific helper fields that also appear in the analytic file:
  - `v###_other_data_*`: supplemental components for selected measures such as provider ratios or severe housing subcomponents
  - `v###_race_*`: race and ethnicity specific estimates for measures that CHR publishes with subgroup breakout coverage

## Lineage
- [`foundations/etl/staging/get_chr.R`](../../../etl/staging/get_chr.R) resolves the current CHR analytic CSV URL from the official documentation page, caches the annual file under the raw data directory, preserves the source-wide measure inventory with snake-cased column names, pads the county identifiers, validates uniqueness at `fips5 + release_year`, and writes `staging.chr_health_rankings`.
- The provider-level measure inventory, Silver inclusion decisions, and downstream architecture notes live in [`../../sources/source__chr.md`](../../sources/source__chr.md).

## Data Quality Notes
- Verify uniqueness at `fips5 + release_year`; CHR analytic staging should be one row per source geography release, including the national and state summary rows that use zero-padded pseudo-FIPS keys.
- Confirm `fips5` is always a zero-padded five-digit county FIPS key after ingest.
- Retain `county_clustered` even though it is not part of the planned Silver contract. CHR uses this flag to mark counties grouped for ranking due to small population, and it is useful context for interpretation and QA.
- Keep all `rawvalue`, `numerator`, `denominator`, `cilow`, `cihigh`, `flag`, `other_data_*`, and `race_*` fields intact in staging so we do not need to re-ingest when Silver scope changes.
- Treat the CHR analytic release as source-faithful provenance. Any measure pruning, relabeling, or CBSA derivation belongs in downstream Silver modeling.

## Known Gaps / To-Dos
- The current staging contract is intentionally broader than the planned Silver output. Track 4.4 still needs to select the approved CHR metric subset and derive CBSA rollups from county staging.
- The provider changes the analytic CSV filename pattern across release years, including inconsistent version suffixes such as `_v3`. Refresh QA should confirm the resolved documentation-page link before each annual rerun.
