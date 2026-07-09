# mart_deep_dive — Table Catalog

Tables are accumulated here as markets are built. Each table has a `cbsa_geoid` column so
rows for Richmond, Jacksonville, and future markets coexist. Do not design tables in advance
of building the market `.qmd` that writes them — let the table shape emerge from what the
section actually needs, then document it here.

## Tables

| Table | Written by | Grain | Status |
|---|---|---|---|
| (none yet) | | | |

## Conventions

- Every table includes `cbsa_geoid TEXT` and `mart_run_ts TIMESTAMP` columns.
- Tables are CREATE OR REPLACE on each run (idempotent per market).
- Schema is `mart_deep_dive`. Create it once with `ddl/001_mart_deep_dive.sql`.
