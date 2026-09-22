# Land the Virginia LODES OD pilot at county-pair grain. The provider files are
# block-to-block; block rows are validated and aggregated within each source run.

source(here::here("foundations", "etl", "utils.R"))
if (file.exists(".Renviron")) readRenviron(".Renviron")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = get_env_path("DB_PATH"), read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

state_scopes <- Sys.getenv("LEHD_LODES_OD_STATE_SCOPE", unset = paste(c(tolower(state.abb), "dc"), collapse = ",")) %>%
  stringr::str_split(",") %>% purrr::pluck(1) %>% stringr::str_trim() %>% tolower() %>% unique()
append_mode <- identical(tolower(Sys.getenv("LEHD_LODES_OD_APPEND_MODE", unset = "false")), "true")
year_value <- 2023L
job_types <- c("JT00", "JT02")
parts <- c("main", "aux")

download_asset <- function(url, destination) {
  # Use curl, as in the WAC/RAC ingest, for reliable Census bulk downloads.
  output <- suppressWarnings(system2("/usr/bin/curl", c("-fsSL", url, "-o", destination), stdout = TRUE, stderr = TRUE))
  if (!is.null(attr(output, "status")) || !file.exists(destination) || file.info(destination)$size <= 0) {
    stop(glue::glue("Could not download {url}"), call. = FALSE)
  }
}

read_provider_csv <- function(url, columns) {
  local_file <- tempfile(fileext = ".csv.gz")
  on.exit(unlink(local_file), add = TRUE)
  download_asset(url, local_file)
  readr::read_csv(local_file, col_types = columns, show_col_types = FALSE, progress = FALSE)
}

valid_counties <- DBI::dbGetQuery(con, "SELECT DISTINCT state_fip, county_fip FROM silver.xwalk_tract_county") %>%
  dplyr::transmute(county_geoid = stringr::str_c(as.character(.data$state_fip), as.character(.data$county_fip)))
DBI::dbWriteTable(con, "temp_lodes_od_counties", valid_counties, overwrite = TRUE, temporary = TRUE)

prepare_state_xwalk <- function(state_scope) {
  xwalk <- read_provider_csv(glue::glue("https://lehd.ces.census.gov/data/lodes/LODES8/{state_scope}/{state_scope}_xwalk.csv.gz"), readr::cols(tabblk2020 = readr::col_character(), cty = readr::col_character())) %>%
    dplyr::transmute(block_geoid = .data$tabblk2020, county_geoid = stringr::str_pad(.data$cty, 5, side = "left", pad = "0")) %>%
    dplyr::distinct(.data$block_geoid, .keep_all = TRUE)
  DBI::dbWriteTable(con, "temp_lodes_od_xwalk", xwalk, overwrite = TRUE, temporary = TRUE)
}

aggregate_part <- function(job_type, source_part) {
  source_file <- glue::glue("{state_scope}_od_{source_part}_{job_type}_{year_value}.csv.gz")
  local_file <- tempfile(fileext = ".csv.gz")
  on.exit(unlink(local_file), add = TRUE)
  download_asset(glue::glue("https://lehd.ces.census.gov/data/lodes/LODES8/{state_scope}/od/{source_file}"), local_file)
  source_path <- DBI::dbQuoteString(con, local_file)
  source_sql <- glue::glue("read_csv_auto({source_path}, types = {{'w_geocode':'VARCHAR', 'h_geocode':'VARCHAR', 'createdate':'VARCHAR'}})")
  totals <- DBI::dbGetQuery(con, glue::glue("SELECT count(*) AS source_row_count, sum(S000) AS source_jobs_total, min(createdate) AS source_createdate FROM {source_sql}"))
  # Aux contains home geographies outside Virginia, including provider areas
  # absent from the current managed county backbone. Retain their FIPS prefix
  # and flag it in Silver rather than dropping a valid workplace-side flow.
  home_join <- if (identical(source_part, "main")) "JOIN temp_lodes_od_xwalk h ON source.h_geocode = h.block_geoid" else ""
  home_county <- if (identical(source_part, "main")) "h.county_geoid" else "substr(source.h_geocode, 1, 5)"
  county_df <- DBI::dbGetQuery(con, glue::glue("SELECT {home_county} AS home_county_geoid, w.county_geoid AS work_county_geoid, sum(source.S000) AS jobs, count(*) AS source_block_row_count FROM {source_sql} source JOIN temp_lodes_od_xwalk w ON source.w_geocode = w.block_geoid {home_join} GROUP BY 1, 2")) %>%
    dplyr::mutate(year = year_value, segment = "S000", source_state = toupper(state_scope), source_part = source_part, job_type = job_type, source_file = source_file, source_createdate = totals$source_createdate[[1]], source_row_count = totals$source_row_count[[1]], source_jobs_total = totals$source_jobs_total[[1]], geography_match_rate = 1)
  if (sum(county_df$source_block_row_count) != totals$source_row_count[[1]] || sum(county_df$jobs) != totals$source_jobs_total[[1]]) stop("OD geography join did not reconcile to the source file.", call. = FALSE)
  list(
    county = county_df,
    coverage = county_df %>% dplyr::summarise(
      source_state = dplyr::first(.data$source_state), year = dplyr::first(.data$year), job_type = dplyr::first(.data$job_type), source_part = dplyr::first(.data$source_part),
      source_file = dplyr::first(.data$source_file), source_createdate = dplyr::first(.data$source_createdate), source_row_count = dplyr::first(.data$source_row_count),
      source_jobs_total = dplyr::first(.data$source_jobs_total), county_pair_row_count = dplyr::n(), county_jobs_total = sum(.data$jobs),
      geography_match_rate = 1, reconciliation_passed = sum(.data$jobs) == dplyr::first(.data$source_jobs_total), coverage_status = "available_validated"
    )
  )
}

results <- list()
unavailable_coverage <- list()
for (state_scope in state_scopes) {
  if (state_scope %in% c("ak", "mi")) {
    # Census states that the 2023 release has no Alaska or Michigan worker
    # data. Record the gap explicitly so consumers never infer zero flows.
    unavailable_coverage[[state_scope]] <- tidyr::crossing(job_type = job_types, source_part = parts) %>%
      dplyr::mutate(
        source_state = toupper(state_scope), year = year_value,
        source_file = NA_character_, source_createdate = NA_character_,
        source_row_count = NA_real_, source_jobs_total = NA_real_,
        county_pair_row_count = NA_real_, county_jobs_total = NA_real_,
        geography_match_rate = NA_real_, reconciliation_passed = NA,
        coverage_status = "provider_unavailable_2023"
      )
    next
  }
  prepare_state_xwalk(state_scope)
  for (job_type in job_types) for (source_part in parts) {
    message("Processing LODES OD ", toupper(state_scope), " ", job_type, " ", source_part, ".")
    results[[paste(state_scope, job_type, source_part, sep = "_")]] <- aggregate_part(job_type, source_part)
  }
}

# Main homes are in the Virginia workplace state and aux homes are outside it.
# A county-pair overlap would therefore signal a provider-part handling error.
for (state_scope in setdiff(state_scopes, c("ak", "mi"))) for (job_type in job_types) {
  main_keys <- results[[paste(state_scope, job_type, "main", sep = "_")]]$county %>% dplyr::select(.data$home_county_geoid, .data$work_county_geoid)
  aux_keys <- results[[paste(state_scope, job_type, "aux", sep = "_")]]$county %>% dplyr::select(.data$home_county_geoid, .data$work_county_geoid)
  if (nrow(dplyr::inner_join(main_keys, aux_keys, by = c("home_county_geoid", "work_county_geoid"))) > 0) stop("LODES OD main and aux county pairs overlap.", call. = FALSE)
}

combine_part <- function(state_scope, source_part) {
  all_jobs <- results[[paste(state_scope, "JT00", source_part, sep = "_")]]$county %>%
    dplyr::select(.data$home_county_geoid, .data$work_county_geoid, .data$year, .data$segment, .data$source_state, .data$source_part,
                  jobs_all = .data$jobs, source_block_row_count_all = .data$source_block_row_count, source_file_all = .data$source_file, source_createdate_all = .data$source_createdate)
  private_jobs <- results[[paste(state_scope, "JT02", source_part, sep = "_")]]$county %>%
    dplyr::select(.data$home_county_geoid, .data$work_county_geoid, .data$year, .data$segment, .data$source_state, .data$source_part,
                  jobs_private = .data$jobs, source_block_row_count_private = .data$source_block_row_count, source_file_private = .data$source_file, source_createdate_private = .data$source_createdate)
  dplyr::full_join(all_jobs, private_jobs, by = c("home_county_geoid", "work_county_geoid", "year", "segment", "source_state", "source_part"))
}

od_staging <- if (length(results) > 0) {
  dplyr::bind_rows(unlist(lapply(setdiff(state_scopes, c("ak", "mi")), function(state_scope) lapply(parts, function(source_part) combine_part(state_scope, source_part))), recursive = FALSE))
} else {
  # A coverage-only Alaska/Michigan run has no flow rows to append.
  DBI::dbGetQuery(con, "SELECT * FROM staging.lehd_lodes_od_county LIMIT 0")
}
od_staging <- od_staging %>% dplyr::mutate(release_format_version = "8.4", transformation_version = "lodes_od_county_v1")
coverage_frames <- purrr::map(results, "coverage")
if (length(unavailable_coverage) > 0) coverage_frames <- c(coverage_frames, unavailable_coverage)
od_coverage <- dplyr::bind_rows(coverage_frames) %>%
  dplyr::mutate(release_format_version = "8.4", transformation_version = "lodes_od_county_v1")
if (anyDuplicated(od_staging[c("home_county_geoid", "work_county_geoid", "year", "source_state", "source_part")]) > 0) stop("OD staging has duplicate county-flow keys.", call. = FALSE)
if (any(od_coverage$coverage_status == "available_validated" & !od_coverage$reconciliation_passed)) stop("OD county totals did not reconcile to source totals.", call. = FALSE)

# Append mode is state-replace, not blind append: a failed or repeated state
# command can be rerun safely without duplicating its county-pair flows.
if (append_mode) {
  quoted_states <- paste(DBI::dbQuoteString(con, toupper(state_scopes)), collapse = ", ")
  DBI::dbExecute(con, glue::glue("DELETE FROM staging.lehd_lodes_od_county WHERE source_state IN ({quoted_states})"))
  DBI::dbExecute(con, glue::glue("DELETE FROM staging.lehd_lodes_od_coverage WHERE source_state IN ({quoted_states})"))
}

DBI::dbWriteTable(con, DBI::Id(schema = "staging", table = "lehd_lodes_od_county"), od_staging, overwrite = !append_mode, append = append_mode)
DBI::dbWriteTable(con, DBI::Id(schema = "staging", table = "lehd_lodes_od_coverage"), od_coverage, overwrite = !append_mode, append = append_mode)
DBI::dbExecute(con, "CHECKPOINT")
