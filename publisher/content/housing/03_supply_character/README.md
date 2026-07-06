# Supply Character Section

Production workspace for the housing Supply Character section.

This section follows the same standalone build pattern as `01_vacancy/` and
`02_costs/` so each publishable chart is easy to rerun, review, and reuse.

## Folder Structure

`sql/`
- Chart-shaped SQL inputs for Supply Character visuals.
- Keep metric definitions in shared marts and use section SQL for framing,
  filtering, ranking, and light chart shaping.

`visuals/`
- One production `.R` file per visual.
- `_shared_supply_character_visuals.R` holds the repeated path, DuckDB,
  visual-library, and export helpers for the section.

`outputs/`
- Deliberate exported PNG artifacts for review and publishing.

`VISUAL_BACKLOG.md`
- Source-of-truth checklist for the first-pass Supply Character build order and
  scope.

## Canonical Workflow

For a new Supply Character visual:

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
- Treat `2019` to `2024` population growth as the main growth comparison window.
- Use `major_cbsa_100k_flag = TRUE` for metro visuals.
- Exclude Puerto Rico rows from metro visuals.
- Build publishable outputs, not exploratory checks.

## How To Run

Run one visual:

```bash
Rscript publisher/content/housing/03_supply_character/visuals/cbsa_permit_intensity_map.R
```

Run the full section:

```bash
Rscript publisher/content/housing/03_supply_character/render_all.R
```

## Current Status

This section now uses the same production-first pattern as Vacancy and Costs:

- one script per chart
- stable SQL inputs
- stable PNG outputs
- one batch rerun path for the full first pass
