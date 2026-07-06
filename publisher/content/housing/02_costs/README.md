# Costs Section

Production workspace for the housing Costs section.

This section follows the same standalone build pattern as `01_vacancy/` so each
publishable chart is easy to rerun, review, and reuse in later publishing work.

## Folder Structure

`sql/`
- Chart-shaped SQL inputs for Costs visuals.
- Keep metric definitions in shared marts and use section SQL for framing,
  filtering, weighting, and simple growth calculations.

`visuals/`
- One production `.R` file per visual.
- `_shared_costs_visuals.R` holds the repeated path, DuckDB, visual-library, and
  export helpers for the section.

`outputs/`
- Deliberate exported PNG artifacts for review and publishing.

`VISUAL_BACKLOG.md`
- Source-of-truth checklist for the first-pass Costs build order and scope.

## Canonical Workflow

For a new Costs visual:

1. Add or update the chart-shaped SQL in `sql/`.
2. Create one chart-specific script in `visuals/`.
3. Use the shared helper file to:
   - resolve repo-relative paths
   - connect to `foundations/etl/data/duckdb/patterns_in_place.duckdb`
   - load the needed shared visual-library helpers
   - run the local SQL file
   - export one PNG to `outputs/`
4. Tick the item off in `VISUAL_BACKLOG.md`.

## First-Pass Editorial Rules

- Treat `2024` as the canonical snapshot year.
- Treat `2019` to `2024` as the canonical growth window for first-pass change
  visuals in this section.
- Use `major_cbsa_100k_flag = TRUE` for metro visuals.
- Exclude `AK`, `HI`, and `PR` from contiguous-US state maps.
- Build publishable outputs, not exploratory checks.

## How To Run

Run one visual:

```bash
Rscript publisher/content/housing/02_costs/visuals/state_rent_to_income_map.R
```

Run the full section:

```bash
Rscript publisher/content/housing/02_costs/render_all.R
```

## Current Status

This section now uses the same production-first pattern as Vacancy:

- one script per chart
- stable SQL inputs
- stable PNG outputs
- one batch rerun path for the full first pass
