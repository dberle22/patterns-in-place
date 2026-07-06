# Overheating Section

Production workspace for the housing Overheating section.

This section follows the same standalone build pattern as the earlier housing
sections so each publishable chart is easy to rerun, review, and reuse.

## Folder Structure

`sql/`
- Chart-shaped SQL inputs for Overheating visuals.
- Keep metric definitions in the shared overheating mart and use section SQL for
  framing, ranking, shortlist rules, and geometry joins.

`visuals/`
- One production `.R` file per visual.
- `_shared_overheating_visuals.R` holds the repeated path, DuckDB,
  visual-library, and export helpers for the section.

`outputs/`
- Deliberate exported PNG artifacts for review and publishing.

`VISUAL_BACKLOG.md`
- Source-of-truth checklist for the first-pass Overheating build order and
  scope.

## Canonical Workflow

For a new Overheating visual:

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
- Use `cbsa` first while the methodology is still being pressure-tested.
- Use `major_cbsa_100k_flag = TRUE` for metro visuals.
- Use the provisional overheating composite for rankings, but always pair it
  with component context.
- Treat the “still affordable” list as a cautious shortlist, not a definitive
  “best markets” claim.
- Build publishable outputs, not exploratory checks.

## How To Run

Run one visual:

```bash
Rscript publisher/content/housing/04_overheating/visuals/cbsa_overheating_hottest.R
```

Run the full section:

```bash
Rscript publisher/content/housing/04_overheating/render_all.R
```

## Current Status

This section now uses the same production-first pattern as Vacancy, Costs, and
Supply Character:

- one script per chart
- stable SQL inputs
- stable PNG outputs
- one batch rerun path for the full first pass
