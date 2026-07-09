# Function Reuse Matrix

Purpose: define how section modules reuse existing project functions sourced via `scripts/utils.R`.

## Shared runtime
- Base loader: `scripts/utils.R`
- Existing sourced function files:
  - `R/add_growth_cols.R`
  - `R/benchmark_summary.R`
  - `R/generic_functions.R`
  - `R/rebase_cbsa_from_counties.R`
  - `R/acs_ingest.R`
  - `R/standardize_acs_df.R`

## Section mapping (initial)

### 01_setup
- `generic_functions.R::get_env_path` (if needed for environment pathing)
- `sections/_shared/helpers.R::run_metadata`

### 02_market_overview
- `benchmark_summary.R::bench_summary`
- `add_growth_cols.R::add_growth_cols`
- `generic_functions.R::pct`

### 03_eligibility_scoring
- `add_growth_cols.R::add_growth_cols` (if growth windows are recomputed)
- `sections/_shared/helpers.R::zscore`
- `sections/_shared/helpers.R::pct_rank`

### 04_zones
- Prefer `sf`/graph workflow in section scripts
- Reuse `generic_functions` only when utility is relevant

### 05_parcels
- Prefer section-specific parcel logic
- Reuse common formatting/helpers from `generic_functions` where needed

### 06_conclusion_appendix
- Reuse run metadata + common formatters from shared helpers

## Rules
- If a needed function already exists in `R/`, use it instead of reimplementing.
- If no suitable function exists, add section-local helper first; promote to `R/` only when reused across sections.
- Keep `.qmd` integration chunks free of core transformations.
