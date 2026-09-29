# Shared Act 1 Assets

This folder holds shared issue-facing assembly for `Act 1`.

Use it for:

- reusable Act 1 notebooks
- shared Act 1 helper code
- common visual assembly patterns that multiple market issues will reuse

Current assets:

- `ACT_1_POSITION_NOTEBOOK.py`
  Shared Marimo notebook for Act 1 Position surfaces built from the current
  `profile` and `peers` analyses.
- `duckdb_helpers.py`
  Small helper module for connecting to DuckDB and loading parameterized SQL
  query files inside shared issue notebooks.

## Run

```bash
.venv-marimo/bin/marimo edit metro-deep-dive-program/issues/_shared/act_1/ACT_1_POSITION_NOTEBOOK.py
```

## Notebook Pattern

Use this pattern for future shared Act 1 notebooks:

- query DuckDB through reusable SQL surfaces in `analyses/position/`
- keep helper code next to the notebook when it is only supporting shared
  issue assembly
- prefer readable UI labels like `Richmond, VA (40060)` while still mapping to
  raw `cbsa_code` values under the hood
- keep notebook outputs focused on inspection and act assembly, not on creating
  a parallel exported data layer

## Marimo Findings

These are now part of the local notebook context for future work:

- use `.venv-marimo/bin/python` as the VS Code notebook interpreter
- install plotting and notebook-only dependencies into `.venv-marimo`, not the
  system Python, so the extension and CLI use the same environment
- avoid reusing variable names across cells for things like DuckDB connections;
  use cell-specific names such as `cbsa_options_con` or `profile_query_con`
- when configuring `mo.ui.dropdown`, the default `value` must be the visible
  option label, not only the mapped code
- if the notebook is being authored in VS Code, use the extension for editing
  and the browser view for final interactive review
