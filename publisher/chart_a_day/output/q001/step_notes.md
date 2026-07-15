# Step Notes for q001

- [2026-07-12 20:26:52] The legacy q001 folder turned out not to be parity-ready: the old `result.sql` was answering a per-capita-income question, not the current backlog question about rent-to-income ratios. I treated q001 as a full refresh rather than trusting the inherited artifact set.
- [2026-07-12 20:26:52] Rebuilt the q001 SQL artifact from `gold.housing_core_wide` joined to `gold.dim_geo`, filtered to 2023 CBSAs with population >= 250k, and converted `rent_to_income` to percentage points for display.
- [2026-07-12 20:26:52] The raw top rows included Puerto Rico metros, but that did not fit the intended “Sun Belt vs coastal” framing in the backlog note. I excluded Puerto Rico metros explicitly so the ranking stays focused on the contiguous-US affordability pattern.
- [2026-07-12 20:26:52] The refreshed result is analytically plausible before charting: 15 rows, led by Miami (`28.9%`), Cape Coral (`26.2%`), and Orlando (`25.9%`), with a heavy Florida and California presence.
- [2026-07-12 20:26:52] Both R and Python rendered cleanly from the same `result.csv`. The ranked-bar path now looks stable enough that the remaining drift is mostly the familiar one: Python truncates long labels and compresses metadata slightly more than the R reference.
- [2026-07-12 20:26:52] Side-by-side verdict for q001: `match_with_minor_drift`. The story, order, and values match across both stacks, and the biggest workflow lesson is procedural: old pre-CE artifacts need a quick question-to-metric sanity check before we reuse them.
