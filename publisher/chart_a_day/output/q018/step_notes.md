# Step Notes for q018

- [2026-07-12 20:43:21] Built the q018 SQL artifact from `gold.population_demographics` and `gold.housing_core_wide`, fixing the comparison universe to the top 20 CBSAs by 2023 population and deriving annual vacancy-rate ranks from 2015 through 2023.
- [2026-07-12 20:43:21] The fixed-universe choice matters here. Keeping the same top-20 metro set across all years makes the rank motion interpretable and avoids artificial jumps caused by metros entering or leaving the universe.
- [2026-07-12 20:43:21] Both R and Python rendered successfully on the first pass. The shared `bump_chart` contract held cleanly without extra prep fixes, which is a good signal for the rest of the rank-change family.
- [2026-07-12 20:43:21] The strongest movers are easy to read in both stacks: San Francisco fell from rank 3 to rank 11, while Philadelphia and Seattle moved upward. Python is the cleaner presentation artifact here because the end labeling and stroke contrast are more legible than the denser R reference.
- [2026-07-12 20:43:21] Side-by-side verdict for q018: `match_with_minor_drift`. The ranking story matches well, and the remaining work is mostly visual refinement rather than contract or environment stability.
