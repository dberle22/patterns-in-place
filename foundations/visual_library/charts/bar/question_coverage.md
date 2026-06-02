# Bar Question Coverage

## Canonical Test Cases
- `bar_top_growth_cbsas`: top-ranked CBSA growth comparison.
- `bar_county_affordability`: county rent-to-income ranking within a target metro.
- `bar_target_vs_peers`: highlighted target metro rank against peer set.
- `bar_state_benchmark_delta`: diverging benchmark comparison for states.

## Source Question Mapping
- Top 25 CBSAs by 5-year median income growth -> `bar_top_growth_cbsas`
- Counties with the highest rent-to-income ratio -> `bar_county_affordability`
- Selected metro rank on affordability vs peers -> `bar_target_vs_peers`
- ZCTAs with highest home value-to-income ratio -> `bar_county_affordability` with ZCTA filter
- States with the largest divergence from the national benchmark -> `bar_state_benchmark_delta`

## Current Implementation Status
- Implemented first: `bar_top_growth_cbsas`
- Implemented first: `bar_county_affordability`
- Deferred: `bar_target_vs_peers`
- Deferred: `bar_state_benchmark_delta`
