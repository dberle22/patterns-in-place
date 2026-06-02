# Line Question Coverage

## Canonical Test Cases
- `line_test_single`: target CBSA population trend over 2013-2023.
- `line_test_multi`: target CBSA versus peer CBSAs over the same period.
- `line_test_indexed`: indexed per-capita income comparison with 2013 = 100.
- Planned extension: county small-multiples variant for within-metro divergence.

## Source Question Mapping
- "How has median income changed over the past decade in this CBSA vs its peers?" -> `line_test_multi`, `line_test_indexed`
- "Did population growth accelerate after 2018, or was it steady?" -> `line_test_single`
- "Are housing costs rising faster than incomes over time (indexed comparison)?" -> `line_test_indexed`
- "Which counties in this CBSA are diverging in growth trajectories?" -> planned county small-multiples extension
- "How did the Sweet Spot metros behave through 2020-2023 relative to the broader set?" -> `line_test_multi` with an alternate peer filter
