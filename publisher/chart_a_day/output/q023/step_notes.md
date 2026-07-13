# Step Notes for q023

- [2026-07-12 22:20:00] Built the q023 demographic extract from `silver.age_base`, unpivoting the 2023 Miami CBSA and United States age-sex columns into the long age-pyramid contract with one row per age bin and sex.
- [2026-07-12 22:20:00] The first important workflow gap here was structural rather than visual: the Python prep was dropping `facet_label`, which would have forced Miami and the US into separate panels instead of overlaying the benchmark outline. Preserving `facet_label` in the shared Python prep fixed that comparison path cleanly.
- [2026-07-12 22:20:00] Both renders tell the same demographic story. Miami skews older than the US benchmark in the upper-middle and older age bands, while the US outline is relatively larger in the younger bins.
- [2026-07-12 22:20:00] Python is the clearer artifact for this question because the overlaid benchmark outline reads cleanly against the mirrored bars. The R reference still works, but the dashed benchmark treatment is denser and more visually busy.
- [2026-07-12 22:20:00] Side-by-side verdict for q023: `match_with_minor_drift`. This closes the `age_pyramid` proof point and adds a useful comparison-overlay fix to the shared Python prep path.
