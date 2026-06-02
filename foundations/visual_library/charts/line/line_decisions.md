# Line Chart Decisions

## Decision L-001: Contract requirement by variant
- Question: Should `time_window` always be optional, or required for non-single variants?
- Answer: Keep optional in the base contract, but enforce conditionally by variant in prep/validation rules.
- Status: Open
- Date: 2026-03-02

## Decision L-002: Default zero baseline for line charts
- Question: Should line charts default to a zero baseline, even for indexed and narrow-range series?
- Answer: Default to a zero baseline across the line chart library to reduce the risk of exaggerated slope comparisons. Treat indexed and narrow-range series as a possible future override area if the zero baseline meaningfully reduces readability in review.
- Status: Accepted
- Date: 2026-04-15
