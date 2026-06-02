# Bar Chart Decisions

## Decision B-001: Default storytelling variant
- Question: Which bar variant should be the default implementation target?
- Answer: Start with ranked horizontal bars and add grouped or diverging behavior through config rather than separate code paths.
- Status: Decided
- Date: 2026-04-14

## Decision B-002: First canonical test cases
- Question: Which business questions should anchor the first meaningful implementation?
- Answer: `bar_top_growth_cbsas` and `bar_county_affordability`.
- Status: Decided
- Date: 2026-04-14

## Decision B-003: Default target geography
- Question: Which target metro should sample outputs use first?
- Answer: Wilmington, NC (`48900`).
- Status: Decided
- Date: 2026-04-14

## Decision B-004: Default affordability metric
- Question: Which affordability metric should the first ranked county bar use?
- Answer: `rent_to_income` from `gold.affordability_wide`.
- Status: Decided
- Date: 2026-04-14

## Decision B-005: Default growth metric
- Question: Which growth metric should the first ranked CBSA bar use?
- Answer: `income_pc_growth_5yr` from `gold.economics_income_wide`.
- Status: Decided
- Date: 2026-04-14

## Decision B-006: Deferred benchmark variant
- Question: Should diverging benchmark bars be implemented in this pass?
- Answer: Defer for now and finish a working ranked-bar template first.
- Status: Decided
- Date: 2026-04-14
