# ETL Migration Plan

Moving the Places pipeline from `metro_deep_dive` into `foundations/etl/` and rebuilding against a fresh `patterns_in_place.duckdb`.

---

## Build strategy: seed from existing staging

Rather than re-running all API ingestion scripts, we seed the new database by copying staging tables directly out of `metro_deep_dive.duckdb`. This gives us a working `patterns_in_place.duckdb` immediately. Ingestion scripts can be reviewed and improved source-by-source at our own pace after the migration.

**Phase 1 — Seed:** Copy all staging tables from `metro_deep_dive.duckdb` → `patterns_in_place.duckdb` using a one-time migration script.

**Phase 2 — Build:** Run silver and gold scripts against the new DB.

**Phase 3 — Improve ingestion (ongoing):** Review each staging script, document data sources and download steps, then re-ingest source-by-source as needed.

---

## What changes

### 1. New database file
`patterns_in_place.duckdb` — stored on the Lexar SSD at `/Volumes/Lexar/data/patterns-in-place/duckdb/patterns_in_place.duckdb`. Fresh file, no data carried over directly — staging is seeded via the migration script. Schema structure (`staging` / `silver` / `gold`) stays identical.

### 2. DB stored on external SSD
Set `DB_PATH` in `~/.Renviron` to the full path on the SSD. Every script reads this variable — nothing else changes. The SSD path never appears in committed files.

```
# ~/.Renviron
DB_PATH=/Volumes/Lexar/data/patterns-in-place/duckdb/patterns_in_place.duckdb
```

If the SSD is not mounted when a script runs, `get_env_path("DB_PATH")` will return the path but the DuckDB connection will fail with a clear error. No special handling needed.

### 3. DB path reference in R scripts
Every script currently derives the path with two lines:
```r
data    <- get_env_path("DATA")
db_path <- paste0(data, "/duckdb/metro_deep_dive.duckdb")
```
Replace both with a single line:
```r
db_path <- get_env_path("DB_PATH")
```
One line per script, no new abstraction.

### 4. DB name in gold SQL
Gold scripts use fully-qualified references: `metro_deep_dive.gold.table_name`.
Find/replace across all `.sql` files:
```
metro_deep_dive.  →  patterns_in_place.
```

### 5. `utils.R` and R utility paths
`utils.R` sources six R utility functions via `here::here("R", ...)`. Copy those files into `foundations/etl/R/` so the ETL folder is self-contained. `utils.R` paths stay unchanged.

### 6. `create_DB.R` rewrite
Rewrite as a proper orchestrator: opens the connection once, creates schemas, then sources each layer script in order (see sequencing below).

---

## What does NOT change

- Script logic, variable names, ACS/BEA/BLS ingest patterns — untouched
- Schema names (`staging`, `silver`, `gold`)
- All env vars other than the DB path (`DATA_DEMO_RAW`, etc. stay as-is)
- `here::here()` usage — still works as long as scripts are run from `foundations/etl/`

---

## `.Renviron` setup

Set in `~/.Renviron` (user-level, never committed):
```
DB_PATH=/Volumes/Lexar/data/patterns-in-place/duckdb/patterns_in_place.duckdb
OLD_DB_PATH=/Users/danberle/Documents/projects/data/duckdb/metro_deep_dive.duckdb
DATA_DEMO_RAW=/path/to/your/data/raw/demographics
```
`OLD_DB_PATH` is only needed during the Phase 1 seed — remove it from `.Renviron` once seeding is complete.

A `.Renviron.example` in `foundations/etl/` documents all required variables.

---

## Phase 1: Staging seed script

Rather than re-running every API and CSV ingestion script, we copy all staging tables directly from `metro_deep_dive.duckdb` into the new `patterns_in_place.duckdb`. This gives us a fully populated staging schema in one pass, with no API calls, no credentials, and no download time. Silver and gold can then be built immediately.

**Prerequisites:**
1. `DB_PATH` and `OLD_DB_PATH` are set in `~/.Renviron`
2. Both DuckDB files are accessible (Lexar SSD mounted, `metro_deep_dive.duckdb` path correct)
3. `patterns_in_place.duckdb` does not yet exist — the script creates it fresh

**What the script does, step by step:**
1. Opens `metro_deep_dive.duckdb` read-only as the source
2. Creates `patterns_in_place.duckdb` at the Lexar path as the destination
3. Creates the `staging`, `silver`, and `gold` schemas in the destination
4. Queries `information_schema.tables` on the source to get every table in the `staging` schema
5. For each table: reads it into R as a data frame, writes it to `staging.<table_name>` in the destination with `overwrite = TRUE`
6. Prints a progress message for each table so you can see it working
7. Disconnects and shuts down both connections cleanly

```r
# seed_staging.R — run once to populate patterns_in_place staging from metro_deep_dive
library(DBI)
library(duckdb)
library(glue)

source(here::here("R", "generic_functions.R"))  # for get_env_path

if (file.exists("~/.Renviron")) readRenviron("~/.Renviron")

src_path <- get_env_path("OLD_DB_PATH")
dst_path <- get_env_path("DB_PATH")

stopifnot(!is.na(src_path), file.exists(src_path))
stopifnot(!is.na(dst_path))

src <- dbConnect(duckdb::duckdb(), dbdir = src_path, read_only = TRUE)
dst <- dbConnect(duckdb::duckdb(), dbdir = dst_path, read_only = FALSE)

dbExecute(dst, "CREATE SCHEMA IF NOT EXISTS staging;")
dbExecute(dst, "CREATE SCHEMA IF NOT EXISTS silver;")
dbExecute(dst, "CREATE SCHEMA IF NOT EXISTS gold;")

tables <- dbGetQuery(src, "
  SELECT table_name
  FROM information_schema.tables
  WHERE table_schema = 'staging'
  ORDER BY table_name
")

message(glue("Found {nrow(tables)} staging tables to seed."))

for (tbl in tables$table_name) {
  df <- dbGetQuery(src, glue("SELECT * FROM staging.{tbl}"))
  dbWriteTable(dst, DBI::Id(schema = "staging", table = tbl), df, overwrite = TRUE)
  message(glue("  ✓ staging.{tbl} ({nrow(df)} rows)"))
}

message("Seed complete. Disconnecting.")
dbDisconnect(src, shutdown = TRUE)
dbDisconnect(dst, shutdown = TRUE)
```

**After running:** verify with a quick spot-check in R:
```r
con <- dbConnect(duckdb::duckdb(), dbdir = get_env_path("DB_PATH"), read_only = TRUE)
dbGetQuery(con, "SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = 'staging' ORDER BY table_name")
dbDisconnect(con, shutdown = TRUE)
```
You should see all 20 staging tables listed. Then remove `OLD_DB_PATH` from `~/.Renviron`.

---

## Phase 3: Ingestion source audit (ongoing)

For each staging script, document:
- **Data source** — API, CSV download, or manual export
- **Download steps** — URL, query parameters, authentication needed
- **Refresh cadence** — annual (ACS), quarterly (BLS), ad hoc

This documentation goes in `foundations/etl/staging/SOURCES.md`. Build it out script-by-script after the DB is running.

| Script | Source type | Notes |
|---|---|---|
| `get_acs_*.R` | API (tidycensus) | Census API key required |
| `get_bea.R` | API (bea.R) | BEA API key required |
| `get_bls_laus.R` | API | BLS API key required |
| `get_bls_qcew.R` | API | BLS API key required |
| `get_bps.R` | CSV download | Census Building Permits Survey |
| `get_hud_chas.R` | CSV download | HUD website |
| `get_hud_fmr.R` | CSV download | HUD website |
| `get_irs_migration.R` | CSV download | IRS SOI website |
| `get_tea.R` | CSV download | Texas Education Agency |
| `get_tiger_geos.R` | API (tigris) | No key required |
| `get_zillow.R` | CSV download | Zillow Research Data |
| `get_bls_qcew.R` | API | BLS API key required |
| `tx_school_acs_ingest.R` | API (tidycensus) | Census API key required |

---

## Build sequence (`create_DB.R` orchestration order)

### Staging (seeded from migration — re-run individual scripts only when refreshing a source)
```
1.  get_tiger_geos.R          # geography — other scripts depend on these
2.  get_acs_age.R
3.  get_acs_edu.R
4.  get_acs_housing.R
5.  get_acs_income.R
6.  get_acs_labor.R
7.  get_acs_migration.R
8.  get_acs_race.R
9.  get_acs_social_infra.R
10. get_acs_transport.R
11. get_bea.R
12. get_bls_laus.R
13. get_bls_qcew.R
14. get_bps.R
15. get_hud_chas.R
16. get_hud_fmr.R
17. get_irs_migration.R
18. get_tea.R
19. get_zillow.R
20. tx_school_acs_ingest.R
```

### Silver (transform staging → clean analytical tables)
```
21. geo_crosswalks_silver.R
22. acs_metadata_silver.R
23. acs_variable_dictionary_silver.R
24. acs_age_silver.R
25. acs_edu_silver.R
26. acs_housing_silver.R
27. acs_income_silver.R
28. acs_labor_silver.R
29. acs_migration_silver.R
30. acs_race_silver.R
31. acs_social_infra_silver.R
32. acs_transport_silver.R
33. bea_cagdp2_silver.R
34. bea_cagdp9_silver.R
35. bea_cainc1_silver.R
36. bea_cainc4_silver.R
37. bea_marpp_silver.R
38. bea_metric_dictionary.R
39. bls_laus_silver.R
40. bps_silver.R
41. build_social_infra_dictionary.R
42. hud_fmr_silver.R
43. irs_migration_silver.R
```

### Gold (SQL — materialize wide analytical tables)
```
44. gold_dim_geo.sql                    ← from metro_deep_dive_chatbot/etl/gold/
45. gold_population_wide.sql
46. gold_affordability_wide.sql
47. gold_economy_gdp.sql
48. gold_economy_income.sql
49. gold_economy_industry.sql
50. gold_economy_labor.sql
51. gold_economy_wide.sql
52. gold_housing_core.sql
53. gold_migration_wide.sql
54. gold_transport_built_form_wide.sql
55. gold_tx_school_district.sql
```

---

## Migration checklist

### Phase 1 — Seed staging
- [x] Add to `~/.Renviron`: `DB_PATH=/Volumes/Lexar/data/patterns-in-place/duckdb/patterns_in_place.duckdb`
- [x] Add to `~/.Renviron`: `OLD_DB_PATH=/Users/danberle/Documents/projects/data/duckdb/metro_deep_dive.duckdb`
- [x] Write `seed_staging.R` in `foundations/etl/`
- [x] Run `seed_staging.R` — watch for per-table progress messages
- [x] Spot-check: query `information_schema.tables` and confirm all 20 staging tables are present
- [x] Remove `OLD_DB_PATH` from `~/.Renviron`

### Phase 2 — Copy and update scripts
- [x] Copy `utils.R` → `foundations/etl/utils.R`
- [x] Copy R utility files → `foundations/etl/R/` (6 files: `add_growth_cols.R`, `benchmark_summary.R`, `generic_functions.R`, `rebase_cbsa_from_counties.R`, `acs_ingest.R`, `standardize_acs_df.R`)
- [x] Copy all staging scripts → `foundations/etl/staging/`
- [x] Copy all silver scripts → `foundations/etl/silver/`
- [x] Copy gold SQL → `foundations/etl/gold/` (including `gold_dim_geo.sql` from `metro_deep_dive_chatbot/etl/gold/`)
- [x] In every R script: replace the two-line DB path block with `db_path <- get_env_path("DB_PATH")`
- [x] In every gold `.sql`: find/replace `metro_deep_dive.` → `patterns_in_place.`
- [x] Rewrite `create_DB.R` as orchestrator
- [x] Add `.Renviron.example`

### Phase 2 — Build silver and gold
- [x] Run silver scripts in order (21–43)
- [x] Run gold scripts in order (44–55)
- [x] Spot-check: query `gold.population_demographics` — confirm rows return
- [x] Spot-check: query `gold.dim_geo` — confirm rows return

### Phase 3 — Ingestion audit (ongoing, post-migration)
- [ ] Create `foundations/etl/staging/SOURCES.md`
- [ ] For each staging script: document source type, download steps, and refresh cadence
- [ ] For CSV sources: confirm files are on the SSD and paths are in `.Renviron`
- [ ] Update Migration.md — mark `foundations/etl/` complete
