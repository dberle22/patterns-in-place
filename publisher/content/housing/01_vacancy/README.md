# Vacancy Section

Production workspace for the housing Vacancy section.

This folder now treats standalone visual scripts as the canonical build path.
The main goal is to make each chart easy to:

- run on its own
- review as a single artifact
- reuse in later publishing workflows
- scale into the other housing sections without relying on Quarto notebooks

## Folder Structure

`sql/`
- Chart-shaped SQL inputs for Vacancy visuals.
- Keep business logic in shared marts where possible.
- Keep section SQL focused on filtering, grouping, ranking, weighting, and geometry joins needed for the chart.

`visuals/`
- One production `.R` file per visual.
- `_shared_vacancy_visuals.R` holds section-local helpers for paths, DuckDB connection, SQL execution, shared visual-library loading, and PNG export.

`outputs/`
- Deliberate exported PNG artifacts.
- These are the reviewable outputs for the section.

`VISUAL_BACKLOG.md`
- Source-of-truth checklist for the Vacancy visual build order and scope.

`archive/`
- Exploratory Quarto notebook artifacts from the earlier notebook-first pass.
- Keep this only for historical reference or one-off review needs.

## Canonical Workflow

For a new Vacancy visual:

1. Add or update the chart-shaped SQL in `sql/`.
2. Create one chart-specific script in `visuals/`.
3. Use the shared helper file to:
   - resolve paths
   - connect to `foundations/etl/data/duckdb/patterns_in_place.duckdb`
   - load the needed `foundations/visual_library` prep/render functions
   - run the local SQL file
   - export one PNG to `outputs/`
4. Tick the item off in `VISUAL_BACKLOG.md`.

## How To Run

Run one visual:

```bash
Rscript publisher/content/housing/01_vacancy/visuals/state_vacancy_map.R
```

Run the full section:

```bash
Rscript publisher/content/housing/01_vacancy/render_all.R
```

## Reusable Pattern For Other Housing Sections

This Vacancy structure is the template I would reuse for:

- `02_costs/`
- `03_supply_character/`
- `04_overheating/`
- `05_synthesis/`

Recommended section pattern:

`sql/`
- section-local chart SQL

`visuals/`
- one `.R` build script per chart
- one `_shared_<section>_visuals.R` helper file at first

`outputs/`
- exported PNGs

`VISUAL_BACKLOG.md`
- exact build checklist

`README.md`
- short operating guide

`archive/`
- optional notebook / exploratory artifacts only

## What Patterns We Follow

### 1. One visual, one script, one output

Each visual script should do one job and export one stable file.

Why this scales:

- reruns are simple
- debugging is localized
- publishing workflows can target single visuals
- git diffs stay readable

### 2. Shared marts own definitions

Use `mart_housing.core_metrics` and other shared marts as the semantic source of truth.

Section SQL should mainly own:

- scope filters
- time windows
- ranking / grouping
- weight logic
- geometry joins

### 3. Section helper first, broader abstraction later

For now, a section-local shared helper is the safest level of reuse.
Once Costs and Supply Character exist, we can promote the truly repeated parts into a higher-level housing shared helper.

### 4. Backlog before build

Lock the visual list first in `VISUAL_BACKLOG.md` so we are building against an explicit scope, not adding charts ad hoc.

### 5. Portable paths only

All scripts should resolve repo-relative paths and avoid machine-specific hardcoding in committed files.

## What Inputs I Need From You For New Sections

Before building another section efficiently, the useful inputs are:

- the exact first-pass visual list
- the intended order of build priority
- any editorial scope cuts
  Examples:
  - which year is canonical
  - which geographies matter first
  - whether we exclude small markets
  - whether county visuals are in or out
- any benchmark or weighting rules
  Examples:
  - housing-unit weighted
  - population weighted
  - major-CBSA filters
- whether a chart is exploratory or intended as a publishable artifact

## What Context Matters Most

For a section to scale cleanly, the most important context is:

- which marts are canonical
- which fields are editorially safe to use
- which geography levels are in scope
- which filters are temporary versus canonical
- which outputs are final deliverables versus exploratory checks

If those are clear, the rest of the build becomes much more mechanical.

## How To Make Outputs Scalable

To keep this scalable across all housing sections, I would do the following next:

1. Keep one output per script, with stable names.
2. Add a `render_all.R` file per section.
3. Keep SQL chart-local unless it is reused across multiple visuals.
4. Promote only the truly repeated helper logic into a shared housing utility later.
5. Add a lightweight manifest if we start publishing many outputs.
   That could eventually track:
   - visual id
   - script path
   - sql path
   - output path
   - chart type
   - status

## Current Status

Vacancy is the first section to adopt this structure fully.
It should be treated as the reference implementation for the next housing sections, with cleanup and standardization informed by what repeats there.
