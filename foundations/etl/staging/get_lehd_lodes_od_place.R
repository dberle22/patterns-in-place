# Build the compact Place OD staging surface. LODES publishes block-to-block
# files, so each source asset is mapped and aggregated before any managed write.
source(here::here("foundations", "etl", "utils.R"))
if (file.exists(".Renviron")) readRenviron(".Renviron")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = get_env_path("DB_PATH"), read_only = FALSE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

year_value <- 2023L
job_types <- c("JT00", "JT02")
parts <- c("main", "aux")
state_scopes <- Sys.getenv("LEHD_LODES_OD_PLACE_STATE_SCOPE", unset = paste(c(tolower(state.abb), "dc"), collapse = ",")) %>%
  stringr::str_split(",") %>% purrr::pluck(1) %>% stringr::str_trim() %>% tolower() %>% unique()
append_mode <- identical(tolower(Sys.getenv("LEHD_LODES_OD_PLACE_APPEND_MODE", unset = "false")), "true")

if (length(setdiff(state_scopes, c(tolower(state.abb), "dc"))) > 0) stop("Invalid LEHD_LODES_OD_PLACE_STATE_SCOPE.", call. = FALSE)

download_asset <- function(url, destination) {
  # Keep raw Census assets local only for the current source-file transaction.
  output <- suppressWarnings(system2("/usr/bin/curl", c("-fsSL", url, "-o", destination), stdout = TRUE, stderr = TRUE))
  if (!is.null(attr(output, "status")) || !file.exists(destination) || file.info(destination)$size <= 0) stop(glue::glue("Could not download {url}"), call. = FALSE)
}

DBI::dbExecute(con, "DROP TABLE IF EXISTS temp_lodes_od_place_rows")
DBI::dbExecute(con, "CREATE TEMP TABLE temp_lodes_od_place_rows AS SELECT * FROM (SELECT CAST(NULL AS VARCHAR) AS home_place_geoid, CAST(NULL AS VARCHAR) AS home_place_status, CAST(NULL AS VARCHAR) AS work_place_geoid, CAST(NULL AS VARCHAR) AS work_place_status, CAST(NULL AS INTEGER) AS year, CAST(NULL AS VARCHAR) AS source_state, CAST(NULL AS VARCHAR) AS source_part, CAST(NULL AS VARCHAR) AS job_type, CAST(NULL AS VARCHAR) AS segment, CAST(NULL AS DOUBLE) AS jobs, CAST(NULL AS BIGINT) AS source_block_row_count, CAST(NULL AS VARCHAR) AS source_file, CAST(NULL AS VARCHAR) AS source_createdate, CAST(NULL AS VARCHAR) AS release_format_version, CAST(NULL AS VARCHAR) AS transformation_version) WHERE FALSE")
DBI::dbExecute(con, "DROP TABLE IF EXISTS temp_lodes_od_place_coverage")
DBI::dbExecute(con, "CREATE TEMP TABLE temp_lodes_od_place_coverage AS SELECT * FROM (SELECT CAST(NULL AS VARCHAR) AS source_state, CAST(NULL AS INTEGER) AS year, CAST(NULL AS VARCHAR) AS source_part, CAST(NULL AS VARCHAR) AS job_type, CAST(NULL AS VARCHAR) AS segment, CAST(NULL AS VARCHAR) AS source_file, CAST(NULL AS VARCHAR) AS source_createdate, CAST(NULL AS BIGINT) AS source_row_count, CAST(NULL AS DOUBLE) AS source_jobs_total, CAST(NULL AS BIGINT) AS endpoint_matched_row_count, CAST(NULL AS DOUBLE) AS endpoint_matched_jobs_total, CAST(NULL AS BIGINT) AS no_place_row_count, CAST(NULL AS DOUBLE) AS no_place_jobs_total, CAST(NULL AS BIGINT) AS unmapped_block_row_count, CAST(NULL AS DOUBLE) AS unmapped_block_jobs_total, CAST(NULL AS BIGINT) AS place_pair_row_count, CAST(NULL AS DOUBLE) AS place_jobs_total, CAST(NULL AS DOUBLE) AS geography_match_rate, CAST(NULL AS BOOLEAN) AS reconciliation_passed, CAST(NULL AS VARCHAR) AS coverage_status, CAST(NULL AS VARCHAR) AS release_format_version, CAST(NULL AS VARCHAR) AS transformation_version) WHERE FALSE")

process_asset <- function(state_scope, job_type, source_part) {
  source_file <- glue::glue("{state_scope}_od_{source_part}_{job_type}_{year_value}.csv.gz")
  local_file <- tempfile(fileext = ".csv.gz")
  on.exit(unlink(local_file), add = TRUE)
  download_asset(glue::glue("https://lehd.ces.census.gov/data/lodes/LODES8/{state_scope}/od/{source_file}"), local_file)
  source_sql <- glue::glue("read_csv_auto({DBI::dbQuoteString(con, local_file)}, types = {{'w_geocode':'VARCHAR', 'h_geocode':'VARCHAR', 'createdate':'VARCHAR'}})")
  # block_registry stores the five-digit state-local Place code separately from
  # state FIPS. Q6 and Geography use the seven-digit Census Place GEOID, so
  # retain the state prefix before aggregating OD endpoints nationally.
  mapped_sql <- glue::glue("WITH source AS (SELECT * FROM {source_sql}), mapped AS (SELECT source.*, CASE WHEN h.place_geoid IS NOT NULL THEN concat(h.state_fips, h.place_geoid) END AS home_place, CASE WHEN w.place_geoid IS NOT NULL THEN concat(w.state_fips, w.place_geoid) END AS work_place, h.block_geoid AS home_block, w.block_geoid AS work_block FROM source LEFT JOIN silver.block_registry h ON source.h_geocode = h.block_geoid LEFT JOIN silver.block_registry w ON source.w_geocode = w.block_geoid)")
  coverage <- DBI::dbGetQuery(con, glue::glue("{mapped_sql} SELECT count(*) AS source_row_count, sum(S000) AS source_jobs_total, min(createdate) AS source_createdate, count(*) FILTER (WHERE home_block IS NOT NULL AND work_block IS NOT NULL) AS endpoint_matched_row_count, sum(S000) FILTER (WHERE home_block IS NOT NULL AND work_block IS NOT NULL) AS endpoint_matched_jobs_total, count(*) FILTER (WHERE home_block IS NOT NULL AND work_block IS NOT NULL AND (home_place IS NULL OR work_place IS NULL)) AS no_place_row_count, sum(S000) FILTER (WHERE home_block IS NOT NULL AND work_block IS NOT NULL AND (home_place IS NULL OR work_place IS NULL)) AS no_place_jobs_total, count(*) FILTER (WHERE home_block IS NULL OR work_block IS NULL) AS unmapped_block_row_count, sum(S000) FILTER (WHERE home_block IS NULL OR work_block IS NULL) AS unmapped_block_jobs_total FROM mapped"))
  aggregate_sql <- glue::glue("{mapped_sql} SELECT coalesce(home_place, CASE WHEN home_block IS NULL THEN 'unmapped_block' ELSE 'no_census_place' END) AS home_place_geoid, CASE WHEN home_block IS NULL THEN 'unmapped_block' WHEN home_place IS NULL THEN 'no_census_place' ELSE 'matched' END AS home_place_status, coalesce(work_place, CASE WHEN work_block IS NULL THEN 'unmapped_block' ELSE 'no_census_place' END) AS work_place_geoid, CASE WHEN work_block IS NULL THEN 'unmapped_block' WHEN work_place IS NULL THEN 'no_census_place' ELSE 'matched' END AS work_place_status, {year_value} AS year, '{toupper(state_scope)}' AS source_state, '{source_part}' AS source_part, '{job_type}' AS job_type, 'S000' AS segment, sum(S000) AS jobs, count(*) AS source_block_row_count, '{source_file}' AS source_file, '{coverage$source_createdate[[1]]}' AS source_createdate, '8.4' AS release_format_version, 'lodes_od_place_v2' AS transformation_version FROM mapped GROUP BY ALL")
  DBI::dbExecute(con, glue::glue("INSERT INTO temp_lodes_od_place_rows {aggregate_sql}"))
  aggregate_totals <- DBI::dbGetQuery(con, glue::glue("SELECT count(*) AS place_pair_row_count, sum(jobs) AS place_jobs_total FROM ({aggregate_sql})"))
  reconciliation_passed <- isTRUE(all.equal(as.numeric(coverage$source_jobs_total[[1]]), as.numeric(aggregate_totals$place_jobs_total[[1]])))
  if (!reconciliation_passed) stop(glue::glue("Place aggregation did not reconcile for {source_file}."), call. = FALSE)
  coverage_row <- tibble::tibble(source_state = toupper(state_scope), year = year_value, source_part = source_part, job_type = job_type, segment = "S000", source_file = source_file, source_createdate = coverage$source_createdate[[1]], source_row_count = coverage$source_row_count[[1]], source_jobs_total = coverage$source_jobs_total[[1]], endpoint_matched_row_count = coverage$endpoint_matched_row_count[[1]], endpoint_matched_jobs_total = coverage$endpoint_matched_jobs_total[[1]], no_place_row_count = coverage$no_place_row_count[[1]], no_place_jobs_total = coverage$no_place_jobs_total[[1]], unmapped_block_row_count = coverage$unmapped_block_row_count[[1]], unmapped_block_jobs_total = coverage$unmapped_block_jobs_total[[1]], place_pair_row_count = aggregate_totals$place_pair_row_count[[1]], place_jobs_total = aggregate_totals$place_jobs_total[[1]], geography_match_rate = coverage$endpoint_matched_row_count[[1]] / coverage$source_row_count[[1]], reconciliation_passed = reconciliation_passed, coverage_status = "available_validated", release_format_version = "8.4", transformation_version = "lodes_od_place_v2")
  DBI::dbWriteTable(con, "temp_lodes_od_place_coverage", coverage_row, append = TRUE)
}

for (state_scope in state_scopes) {
  if (state_scope %in% c("ak", "mi")) {
    unavailable <- tidyr::crossing(source_part = parts, job_type = job_types) %>% dplyr::mutate(source_state = toupper(state_scope), year = year_value, segment = "S000", source_file = NA_character_, source_createdate = NA_character_, source_row_count = NA_real_, source_jobs_total = NA_real_, endpoint_matched_row_count = NA_real_, endpoint_matched_jobs_total = NA_real_, no_place_row_count = NA_real_, no_place_jobs_total = NA_real_, unmapped_block_row_count = NA_real_, unmapped_block_jobs_total = NA_real_, place_pair_row_count = NA_real_, place_jobs_total = NA_real_, geography_match_rate = NA_real_, reconciliation_passed = NA, coverage_status = "provider_unavailable_2023", release_format_version = "8.4", transformation_version = "lodes_od_place_v1")
    DBI::dbWriteTable(con, "temp_lodes_od_place_coverage", unavailable, append = TRUE)
  } else for (job_type in job_types) for (source_part in parts) {
    message("Processing LODES Place OD ", toupper(state_scope), " ", job_type, " ", source_part, ".")
    process_asset(state_scope, job_type, source_part)
  }
}

if (DBI::dbGetQuery(con, "SELECT count(*) AS n FROM temp_lodes_od_place_rows")$n[[1]] > 0 && DBI::dbGetQuery(con, "SELECT count(*) AS n FROM (SELECT home_place_geoid, home_place_status, work_place_geoid, work_place_status, year, source_state, source_part, job_type, segment, count(*) AS n FROM temp_lodes_od_place_rows GROUP BY ALL HAVING n > 1)")$n[[1]] > 0) stop("Place OD staging grain is not unique.", call. = FALSE)

if (append_mode && DBI::dbExistsTable(con, DBI::Id(schema = "staging", table = "lehd_lodes_od_place"))) {
  quoted_states <- paste(DBI::dbQuoteString(con, toupper(state_scopes)), collapse = ", ")
  DBI::dbExecute(con, glue::glue("DELETE FROM staging.lehd_lodes_od_place WHERE source_state IN ({quoted_states})"))
  DBI::dbExecute(con, glue::glue("DELETE FROM staging.lehd_lodes_od_place_coverage WHERE source_state IN ({quoted_states})"))
  # Insert directly from DuckDB's temporary aggregate tables so a national run
  # never materializes millions of Place pairs in the R process.
  DBI::dbExecute(con, "INSERT INTO staging.lehd_lodes_od_place SELECT * FROM temp_lodes_od_place_rows")
  DBI::dbExecute(con, "INSERT INTO staging.lehd_lodes_od_place_coverage SELECT * FROM temp_lodes_od_place_coverage")
} else {
  DBI::dbExecute(con, "CREATE OR REPLACE TABLE staging.lehd_lodes_od_place AS SELECT * FROM temp_lodes_od_place_rows")
  DBI::dbExecute(con, "CREATE OR REPLACE TABLE staging.lehd_lodes_od_place_coverage AS SELECT * FROM temp_lodes_od_place_coverage")
}
DBI::dbExecute(con, "CHECKPOINT")
