# Housing Content Workflow

Operating guide for building the housing section under `publisher/content/housing/`.

This README is meant to give a new agent enough context to start a section such as `02_costs/` without having to rediscover the structure from the Vacancy work.

## Purpose

The housing folder is organized as a section-based editorial workspace:

- `01_vacancy/`
- `02_costs/`
- `03_supply_character/`
- `04_overheating/`
- `05_synthesis/`

Each section should produce a small set of reusable chart artifacts, not just an exploratory notebook.

## Source Of Truth

Read these first:

1. [overview.md](/Users/danberle/Documents/projects/patterns_in_place/publisher/content/housing/overview.md)
2. [data_model.md](/Users/danberle/Documents/projects/patterns_in_place/publisher/content/housing/data_model.md)
3. Section-local `README.md` and `VISUAL_BACKLOG.md` when they exist

Use the shared section marts as the semantic source of truth:

- `mart_housing.core_metrics`
- `mart_housing.overheating_matrix`
- supporting `gold.*`, `geo.*`, and `silver.xwalk_*` tables as needed

Current production DuckDB:

- `foundations/etl/data/duckdb/patterns_in_place.duckdb`

## Recommended Section Structure

Each section should follow the same production-first pattern:

`README.md`
- short instructions for that section

`VISUAL_BACKLOG.md`
- exact first-pass visual checklist

`sql/`
- chart-shaped SQL inputs

`visuals/`
- one `.R` build script per visual
- one local shared helper file if needed

`outputs/`
- deliberate exported PNG outputs

`render_all.R`
- optional but recommended batch runner for the section

`archive/`
- optional home for exploratory notebooks and older render artifacts

## Patterns To Follow

### 1. One visual, one script, one output

Each production chart should have:

- one chart-specific `.R` script
- one stable output file

Why:

- reruns are simple
- debugging is localized
- git diffs are cleaner
- publishing workflows can target single visuals

### 2. Shared marts own metric definitions

Do not re-derive core housing KPIs in every section script.

Keep section SQL focused on:

- scope filters
- ranking
- grouping
- weighting
- time windows
- geometry joins

### 3. Backlog before build

Before creating visuals, write `VISUAL_BACKLOG.md` with:

- exact visual list
- priority order
- chart types
- questions
- metric and geography scope
- file targets

This prevents sections from growing ad hoc.

### 4. Section-local helpers first

It is fine to start with one helper file per section, for example:

- `visuals/_shared_vacancy_visuals.R`

Only promote helpers upward after at least two sections show the same repeated pattern.

### 5. Portable paths only

All scripts should use repo-relative path resolution.
Do not hardcode machine-specific paths in committed files.

## Inputs A New Agent Needs From You

Before a section can be built efficiently, the agent should know:

- the exact first-pass visual list
- the canonical year or time window
- geography scope
- benchmark rules
- weighting rules
- any exclusions or editorial filters
- whether outputs are exploratory or publishable

Examples of useful decisions:

- use `2024` snapshot or a multi-year series
- use `state`, `cbsa`, `county`, or mixed geography
- use housing-unit-weighted or population-weighted rollups
- exclude Puerto Rico, Alaska, or Hawaii for certain national visuals
- use `major_cbsa_100k_flag` or another market filter

## Context That Matters Most

When starting a section, the key context is:

- which marts are canonical
- which fields are editorially safe to use
- which geography levels are in scope
- which temporary flags are acceptable
- which outputs are final assets versus exploratory checks

If those are clear, the rest of the build should be fairly mechanical.

## Scalable Output Strategy

To keep the housing package scalable across sections:

1. Keep file naming aligned across SQL, script, and PNG output.
2. Export stable PNGs into `outputs/`.
3. Add `render_all.R` so the full section can be rerun quickly.
4. Keep notebooks optional and archive them when the production path is stable.
5. Add a higher-level shared helper only after repeated needs appear across sections.

Good naming pattern:

- `sql/cost_burden_state_map.sql`
- `visuals/cost_burden_state_map.R`
- `outputs/cost_burden_state_map.png`

## What A New Agent Should Do For `02_costs/`

Recommended startup sequence:

1. Read `overview.md` and `data_model.md`.
2. Create `02_costs/README.md`.
3. Create `02_costs/VISUAL_BACKLOG.md`.
4. Decide the first-pass visual set before writing chart code.
5. Create `sql/`, `visuals/`, and `outputs/`.
6. Build one standalone visual at a time.
7. Add `render_all.R` once there are multiple visuals.

## Reference Implementation

Use `01_vacancy/` as the current reference implementation for:

- backlog structure
- production folder layout
- standalone visual script pattern
- batch render pattern

Vacancy is the first section to move from notebook-first exploration to a cleaner production workflow. Costs should follow the same structure unless there is a strong reason to diverge.
