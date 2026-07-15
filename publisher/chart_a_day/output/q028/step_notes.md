# Step Notes for q028

- [2026-07-12 22:20:00] Built the q028 density view from 2023 CBSA rows in `gold.population_demographics` and `gold.housing_core_wide`, pairing median age with rent-to-income ratio across the full metro universe.
- [2026-07-12 22:20:00] The first Python hexbin render succeeded, but it surfaced the Matplotlib/font-cache behavior that likely explains some of the earlier "Python quit" concern on these geo-backed or Matplotlib-backed questions. Adding an explicit writable `XDG_CACHE_HOME` alongside `MPLCONFIGDIR` made the wrapper more stable for future runs.
- [2026-07-12 22:20:00] Both renders show the same cluster shape: most metros sit in a middle band around median age in the high-30s to low-40s and rent-to-income ratios in roughly the mid-teens to low-20s, with only a thinner tail at older ages and extreme rent burden.
- [2026-07-12 22:20:00] The R reference is more polished and easier to read as a presentation artifact. Python remains analytically correct, but the title/caption hierarchy is denser and the plotting area feels less intentionally composed.
- [2026-07-12 22:20:00] Side-by-side verdict for q028: `match_with_minor_drift`. This closes the `hexbin` proof point and gives us a concrete Matplotlib cache requirement to carry into the remaining manual workflow notes.
