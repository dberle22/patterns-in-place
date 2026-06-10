# Data Dictionary: staging Opportunity Insights Social Capital Atlas

## Overview
- Schema: `staging`
- Family: `Opportunity Insights Social Capital Atlas`
- Contract scope: source-family staging contract for the county and ZIP Social Capital Atlas releases produced by [`foundations/etl/staging/get_opportunity_insights_social_capital.R`](../../../etl/staging/get_opportunity_insights_social_capital.R)
- Documentation rule: the source publishes two related but non-identical tabular slices, so this file is the canonical staging contract for both source-faithful landings

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| County social capital release | `opportunity_insights_social_capital_county` | One row per county FIPS with the published current-place, childhood-place, cohesion, and civic-engagement fields |
| ZIP social capital release | `opportunity_insights_social_capital_zip` | One row per ZIP / ZCTA-style geography with the published neighborhood-place, cohesion, and civic-engagement fields |

## Contract Summary
- The county and ZIP files intentionally land as separate staging tables.
- Grain:
  - county table: one row per `county`
  - ZIP table: one row per `zip`
- Geography scope:
  - county table: county FIPS geographies in the public release
  - ZIP table: ZIP / ZCTA-style geographies in the public release
- Current scope: static public Social Capital Atlas release documented in the July 2022 public codebook
- Shape expectation:
  - county table: approximately `3,089` rows
  - ZIP table: approximately `23,028` rows in the current landed release

## Shared Columns

Shared across both staging tables:
- geography identifiers:
  - county table: `county`, `county_name`
  - ZIP table: `zip`, `county`
- context fields:
  - `num_below_p50`
  - `pop2018`
- connectedness fields:
  - `ec_*`
  - `ec_se_*`
  - `ec_grp_mem_*`
  - `exposure_grp_mem_*`
  - `bias_grp_mem_*`
- cohesion fields:
  - `clustering_*`
  - `support_ratio_*`
- civic-engagement fields:
  - `volunteering_rate_*`
  - `civic_organizations_*`

Published only in the county file:
- childhood-place fields:
  - `child_ec_county`
  - `child_ec_se_county`
  - `child_exposure_county`
  - `child_bias_county`
- high-SES helper variants:
  - `ec_high_*`
  - `child_high_*`
  - `exposure_grp_mem_high_*`
  - `bias_grp_mem_high_*`

Published only in the ZIP file:
- neighborhood-place fields:
  - `nbhd_ec_zip`
  - `nbhd_ec_high_zip`
  - `nbhd_exposure_zip`
  - `nbhd_bias_zip`
  - `nbhd_bias_high_zip`

## Lineage
- [`foundations/etl/staging/get_opportunity_insights_social_capital.R`](../../../etl/staging/get_opportunity_insights_social_capital.R) downloads the public county and ZIP CSVs, preserves the published field shapes in separate staging tables, zero-pads geography identifiers, validates uniqueness at the source-native keys, and writes both staging outputs.
- Provider-level context and downstream modeling decisions live in [`../../sources/source__social_capital_atlas.md`](../../sources/source__social_capital_atlas.md).

## Data Quality Notes
- Validate uniqueness at the source-native keys:
  - county table: `county`
  - ZIP table: `zip`
- Confirm county FIPS and ZIP identifiers are always stored as zero-padded character keys.
- Preserve the county and ZIP releases separately rather than forcing them into one shared staging schema.
  - The ZIP release contains neighborhood-only fields that do not exist in the county release.
  - The county release contains childhood-place and high-SES helper fields that do not exist in the ZIP release.
- Keep the provider-published standard errors and helper fields in staging even when downstream Silver does not use every field in the first modeled contract.
- The current ZIP release contains 3 rows with null `county` values in the public source. Those should remain null in staging and be handled downstream only if a modeled use case requires county assignment.

## Known Gaps / To-Dos
- This staging contract covers only the Social Capital Atlas half of Track 14.
- Opportunity Atlas is currently deferred and should keep its own staging contract when resumed rather than being folded into this file.
- If Opportunity Insights publishes a newer Social Capital Atlas release later, refresh QA should confirm whether the county and ZIP schemas have changed before rerunning Silver.
