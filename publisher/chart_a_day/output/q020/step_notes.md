# Step Notes for q020

- [2026-07-12 21:35:00] Built the q020 composition extract from 2023 CBSA rows in `gold.housing_core_wide`, limiting the universe to metros with population above 250,000 and assigning each metro to one of four vacancy-rate tiers in SQL.
- [2026-07-12 21:35:00] The resulting universe has 196 large metros. Only 2 fell into the "very tight" bucket below 4% vacancy, while 62 were "tight" and both the "balanced" and "loose" buckets each held 66 metros.
- [2026-07-12 21:35:00] The shared Python waterfall renderer worked on the first pass and produced the cleaner social artifact. The R reference rendered successfully too, but the top-axis and label composition is noticeably rougher here, which makes this one of the clearer examples where the Python output is already the stronger presentation.
- [2026-07-12 21:35:00] The analytical message is stable in both stacks: the large-metro housing market is not concentrated in one vacancy regime, and truly ultra-tight vacancy is rare even inside a broadly constrained national environment.
- [2026-07-12 21:35:00] Side-by-side verdict for q020: `match_with_minor_drift`. This should count as the completed `waterfall` parity proof point for the composition family.
