# Step Notes for q014

- [2026-07-12 19:56:53] Built the q014 SQL artifact as a five-year per-capita-income growth ranking: compare 2018 versus 2023 `per_capita_income` from `gold.housing_core_wide`, limit to CBSAs with population at or above 250,000 in 2023, then keep the top 15 growth metros.
- [2026-07-12 19:56:53] The result shape is exactly what the bar workflow wants: 15 rows, one row per CBSA, sorted descending by growth. The top five are Bend (`48.1%`), San Jose (`46.4%`), Boise (`44.1%`), Provo (`43.1%`), and Santa Cruz (`42.9%`).
- [2026-07-12 19:56:53] Both R and Python rendered cleanly on first pass from the same `result.csv`, which is a good sign that the ranked-bar path is now stable after the earlier bar-family fixes.
- [2026-07-12 19:56:53] Python still truncates a few longer metro labels more aggressively than the R reference and keeps title/note text slightly denser, but the rank order, highlight treatment, and quantitative read all match.
- [2026-07-12 19:56:53] Side-by-side verdict for q014: `match_with_minor_drift`. This is a usable Python parity candidate and it extends the growth-template coverage without exposing a new contract or renderer bug class.
