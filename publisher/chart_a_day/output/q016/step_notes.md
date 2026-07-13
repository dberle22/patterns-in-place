# Step Notes for q016

- [2026-07-12 20:43:21] Built the q016 SQL artifact from `gold.population_demographics`, `gold.housing_core_wide`, and `gold.dim_geo`, filtered to 2023 CBSAs with population >= 500k and mapped into the `scatter` contract with 2018-2023 population growth on `x_value` and 2023 rent-to-income ratio on `y_value`.
- [2026-07-12 20:43:21] The result shape is a strong correlation test case: 107 major metros with clear outliers and five labeled metros that make the Sun Belt paradox legible without overwhelming the canvas.
- [2026-07-12 20:43:21] Both R and Python rendered successfully, and the optional Python fallback `hexbin` artifact now renders too. This run exposed that Matplotlib backend/cache guardrails are needed for `hexbin` just as much as for geo charts.
- [2026-07-12 20:43:21] Visual parity is mixed rather than blocked. The R scatter reads more editorially polished, while the Python scatter is analytically correct but still drifts in palette choices, legend treatment, and caption density.
- [2026-07-12 20:43:21] Side-by-side verdict for q016: `match_with_minor_drift`. The analytical story matches across stacks, and the main lessons are reusable environment guidance for Matplotlib-backed fallback charts plus continued Python scatter styling polish.
