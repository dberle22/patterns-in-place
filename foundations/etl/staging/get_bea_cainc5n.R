# In this script we fetch BEA CAINC5N data into a dedicated staging path.
#
# Why this script exists separately from `get_bea.R`:
# - CAINC5N lives in the same BEA Regional API family as the existing GDP and
#   income tables, but we want to validate this new table end to end without
#   risking regressions in the long-lived shared BEA ingest.
# - The first pass keeps the source table as intact as possible, including the
#   county/state split, the raw line-code inventory, and suppression-friendly
#   text values before Silver decides how much to curate.

getwd()

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

bea_key <- get_env_path("BEA_KEY")
db_path <- get_env_path("DB_PATH")
db_path_override <- get_env_path("DB_PATH_OVERRIDE")

if (!is.na(db_path_override)) {
  db_path <- db_path_override
}

# Throttle controls ----
# CAINC5N has a large line-code surface, so we intentionally pace requests and
# add a periodic cooldown block to reduce the odds of running into BEA's rate
# limits during a full county/state refresh.
base_sleep_seconds <- 4.0
cooldown_every_n_lines <- 10L
cooldown_seconds <- 45.0
max_retries <- 8L
retry_backoff <- 1.8
retry_jitter <- 0.3

# Resume controls ----
# We cache each completed geography + line-code pull as an RDS checkpoint next
# to the configured DuckDB path so interrupted runs can resume without starting
# the entire API crawl over again.
checkpoint_root <- file.path(dirname(db_path), "api_checkpoints", "bea_cainc5n")
dir.create(checkpoint_root, recursive = TRUE, showWarnings = FALSE)

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

`%||%` <- function(x, y) if (is.null(x)) y else x

collapse_years <- function(years) {
  if (length(years) == 1 && years %in% c("ALL", "X", "LAST5", "LAST10")) return(years)
  paste(as.integer(years), collapse = ",")
}

build_bea_spec <- function(api_key, table_name, geo_fips, line_code, years) {
  list(
    UserID = api_key,
    Method = "GetData",
    datasetname = "Regional",
    TableName = table_name,
    GeoFips = geo_fips,
    LineCode = as.character(line_code),
    Year = collapse_years(years)
  )
}

bea_get_safe <- function(spec,
                         max_retries_local = max_retries,
                         base_sleep = base_sleep_seconds,
                         backoff_local = retry_backoff,
                         jitter_local = retry_jitter) {
  delay <- base_sleep

  for (i in 0:max_retries_local) {
    if (i == 0) Sys.sleep(base_sleep)

    raw <- try(bea.R::beaGet(spec, asList = TRUE, asTable = FALSE, asString = FALSE), silent = TRUE)

    if (!(inherits(raw, "try-error")) && is.null(raw$APIError)) {
      out <- try(bea.R::beaGet(spec, asTable = TRUE, asWide = FALSE), silent = TRUE)
      if (!inherits(out, "try-error")) {
        return(tibble::as_tibble(out) |> janitor::clean_names())
      }
    }

    if (i < max_retries_local) {
      sleep_now <- delay * (1 + runif(1, -jitter_local, jitter_local))
      message(sprintf("BEA retry %d/%d in %.2fs ...", i + 1, max_retries_local, sleep_now))
      Sys.sleep(sleep_now)
      delay <- delay * backoff_local
    } else {
      if (!inherits(raw, "try-error") && !is.null(raw$APIError)) stop(raw$APIError$ErrorDetail)
      stop("bea_get_safe: request failed and retries exhausted.")
    }
  }
}

checkpoint_path_for_line <- function(geo_level, line_code) {
  file.path(checkpoint_root, sprintf("%s_line_%s.rds", geo_level, line_code))
}

fetch_cainc5n_line_codes <- function(api_key) {
  raw_lines <- tibble::as_tibble(bea.R::beaParamVals(api_key, "Regional", "LineCode")[[1]]) |>
    janitor::clean_names() |>
    dplyr::filter(grepl("CAINC5N", .data$desc, fixed = TRUE))

  # BEA publishes duplicate labels for many CAINC5N lines: one plain label and
  # one label with the explicit NAICS code suffix. Prefer the latter because it
  # gives us the cleanest downstream industry metadata.
  raw_lines |>
    dplyr::mutate(
      line_code = as.integer(.data$key),
      line_desc = as.character(.data$desc),
      naics_raw = stringr::str_match(.data$line_desc, "\\(([^()]*)\\)\\s*$")[, 2],
      line_desc_clean = dplyr::if_else(
        is.na(.data$naics_raw),
        stringr::str_trim(stringr::str_remove(.data$line_desc, "^\\[CAINC5N\\]\\s*")),
        stringr::str_trim(
          stringr::str_remove(
            stringr::str_remove(.data$line_desc, "^\\[CAINC5N\\]\\s*"),
            "\\([^()]*\\)\\s*$"
          )
        )
      ),
      is_aggregate = dplyr::case_when(
        is.na(.data$naics_raw) ~ FALSE,
        stringr::str_detect(.data$naics_raw, ",") ~ TRUE,
        stringr::str_detect(.data$naics_raw, "-") ~ TRUE,
        TRUE ~ FALSE
      )
    ) |>
    dplyr::arrange(.data$line_code, is.na(.data$naics_raw)) |>
    dplyr::group_by(.data$line_code) |>
    dplyr::slice(1) |>
    dplyr::ungroup() |>
    dplyr::transmute(
      table = "CAINC5N",
      line_code = .data$line_code,
      line_desc = .data$line_desc,
      line_desc_clean = .data$line_desc_clean,
      naics_raw = .data$naics_raw,
      is_aggregate = .data$is_aggregate
    ) |>
    dplyr::arrange(.data$line_code)
}

normalize_cainc5n_stage <- function(raw_df, requested_geo_level) {
  if (!"code" %in% names(raw_df)) raw_df$code <- NA_character_
  if (!"note_ref" %in% names(raw_df)) raw_df$note_ref <- NA_character_

  raw_df |>
    dplyr::mutate(
      line_code = suppressWarnings(as.integer(.data$line_code_req)),
      table = "CAINC5N",
      geo_level = dplyr::case_when(
        .data$geo_fips == "00000" ~ "us",
        requested_geo_level == "state" ~ "state",
        TRUE ~ requested_geo_level
      ),
      data_value_text = as.character(.data$data_value),
      value_raw = suppressWarnings(as.numeric(gsub(",", "", .data$data_value_text))),
      period = suppressWarnings(as.integer(.data$time_period)),
      unit_mult = suppressWarnings(as.integer(.data$unit_mult)),
      value = dplyr::if_else(
        is.na(.data$value_raw) | is.na(.data$unit_mult),
        NA_real_,
        .data$value_raw * (10 ^ .data$unit_mult)
      ),
      is_value_suppressed = is.na(.data$value_raw) & !is.na(.data$data_value_text),
      note_ref = dplyr::na_if(as.character(.data$note_ref), "")
    ) |>
    dplyr::transmute(
      code = as.character(.data$code),
      table = .data$table,
      geo_level = .data$geo_level,
      geo_id = as.character(.data$geo_fips),
      geo_name = as.character(.data$geo_name),
      period = .data$period,
      line_code = .data$line_code,
      unit_raw = as.character(.data$cl_unit),
      unit_mult = .data$unit_mult,
      data_value_text = .data$data_value_text,
      value_raw = .data$value_raw,
      value = .data$value,
      note_ref = .data$note_ref,
      is_value_suppressed = .data$is_value_suppressed
    )
}

fetch_cainc5n_geo <- function(api_key, years, geo_fips_token, geo_level, line_codes) {
  out <- vector("list", length(line_codes))

  for (i in seq_along(line_codes)) {
    line_code <- line_codes[[i]]
    checkpoint_path <- checkpoint_path_for_line(geo_level, line_code)

    if (file.exists(checkpoint_path)) {
      message(sprintf("Using CAINC5N checkpoint | %s | line=%s", toupper(geo_level), line_code))
      out[[i]] <- readRDS(checkpoint_path)
    } else {
      message(sprintf("Fetching CAINC5N | %s | line=%s", toupper(geo_level), line_code))

      spec <- build_bea_spec(
        api_key = api_key,
        table_name = "CAINC5N",
        geo_fips = geo_fips_token,
        line_code = line_code,
        years = years
      )

      raw <- bea_get_safe(spec, base_sleep = base_sleep_seconds)
      raw$line_code_req <- line_code
      out[[i]] <- normalize_cainc5n_stage(raw, geo_level)
      saveRDS(out[[i]], checkpoint_path)
    }

    if (i %% cooldown_every_n_lines == 0L && i < length(line_codes)) {
      message(
        sprintf(
          "Cooling down after %s %s lines for %.0fs to avoid BEA throttling.",
          i,
          toupper(geo_level),
          cooldown_seconds
        )
      )
      Sys.sleep(cooldown_seconds)
    }
  }

  dplyr::bind_rows(out)
}

line_codes_ref <- fetch_cainc5n_line_codes(bea_key)
line_codes <- line_codes_ref$line_code
years <- 2001:2023

county_stage <- fetch_cainc5n_geo(
  api_key = bea_key,
  years = years,
  geo_fips_token = "COUNTY",
  geo_level = "county",
  line_codes = line_codes
)

state_stage <- fetch_cainc5n_geo(
  api_key = bea_key,
  years = years,
  geo_fips_token = "STATE",
  geo_level = "state",
  line_codes = line_codes
)

stage_cainc5n <- dplyr::bind_rows(county_stage, state_stage) |>
  dplyr::arrange(.data$geo_level, .data$geo_id, .data$period, .data$line_code)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "bea_cainc5n"),
  stage_cainc5n,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "bea_cainc5n_line_codes"),
  line_codes_ref,
  overwrite = TRUE
)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
