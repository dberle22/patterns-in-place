# Publish the governed Place OD fact and coverage surfaces without collapsing
# source parts: no_census_place pairs can legitimately recur across parts.
source(here::here("foundations", "etl", "utils.R"))
if (file.exists(".Renviron")) readRenviron(".Renviron")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = get_env_path("DB_PATH"), read_only = FALSE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver;")

duplicate_count <- DBI::dbGetQuery(con, "SELECT count(*) AS n FROM (SELECT home_place_geoid, home_place_status, work_place_geoid, work_place_status, year, source_state, source_part, job_type, segment, count(*) AS n FROM staging.lehd_lodes_od_place GROUP BY ALL HAVING n > 1)")$n[[1]]
if (duplicate_count > 0) stop("Place OD Silver grain is not unique.", call. = FALSE)
if (DBI::dbGetQuery(con, "SELECT count(*) AS n FROM staging.lehd_lodes_od_place WHERE jobs < 0 OR source_block_row_count < 0")$n[[1]] > 0) stop("Place OD Silver contains negative measures.", call. = FALSE)
if (DBI::dbGetQuery(con, "SELECT count(*) AS n FROM staging.lehd_lodes_od_place WHERE home_place_status NOT IN ('matched', 'no_census_place', 'unmapped_block') OR work_place_status NOT IN ('matched', 'no_census_place', 'unmapped_block')")$n[[1]] > 0) stop("Place OD contains an undeclared endpoint status.", call. = FALSE)
if (DBI::dbGetQuery(con, "SELECT count(*) AS n FROM staging.lehd_lodes_od_place_coverage WHERE coverage_status = 'available_validated' AND NOT reconciliation_passed")$n[[1]] > 0) stop("Place OD coverage has an unresolved source reconciliation.", call. = FALSE)

# Keep labels out of the primary key. The identity authority remains the 2020
# Census Place GEOID in the flow fact; status explains intentional non-Place rows.
DBI::dbExecute(con, "CREATE OR REPLACE TABLE silver.lehd_lodes_od_place AS SELECT * FROM staging.lehd_lodes_od_place")
DBI::dbExecute(con, "CREATE OR REPLACE TABLE silver.lehd_lodes_od_place_coverage AS SELECT * FROM staging.lehd_lodes_od_place_coverage")
DBI::dbExecute(con, "CHECKPOINT")
