# In this script we land tract-aggregated LEHD LODES staging tables for the
# approved first-pass scope. The public source artifacts are state-based block
# files, but our current managed contract does not need persistent block-level
# storage. We therefore:
# 1. download one state-year WAC or RAC file at a time
# 2. validate that every source block joins the published state crosswalk
# 3. roll the block rows up to 11-digit tract GEOIDs immediately
# 4. write tract-grain staging tables for WAC and RAC
#
# OD is intentionally not ingested here. We keep the source doc aligned to that
# deferred path, but the current script only manages the tract-ready WAC/RAC
# surface that the roadmap calls for now.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the first-pass scope ----
lodes_default_year <- 2023L
lodes_default_version <- "LODES8"
lodes_default_job_type <- "JT02"
lodes_default_segment <- "S000"
lodes_state_scopes_default <- c(tolower(state.abb), "dc")

is_known_missing_lodes_combo <- function(state_scope, lodes_type, year_value) {
  # Current LODES 8.4 coverage tables show that Alaska and Michigan do not have
  # WAC files in 2022-2023 even though RAC is still available. We skip those
  # known-missing WAC combinations so one absent provider file does not abort
  # the entire national run.
  identical(lodes_type, "wac") &&
    year_value %in% c(2022L, 2023L) &&
    state_scope %in% c("ak", "mi")
}

resolve_lodes_year <- function(env_var = "LEHD_LODES_YEAR") {
  raw_value <- Sys.getenv(env_var, unset = "")

  if (!nzchar(raw_value)) {
    return(lodes_default_year)
  }

  parsed_value <- suppressWarnings(as.integer(raw_value))

  if (is.na(parsed_value)) {
    stop(
      sprintf("Invalid %s value: %s", env_var, raw_value),
      call. = FALSE
    )
  }

  parsed_value
}

resolve_lodes_state_scope <- function(env_var = "LEHD_LODES_STATE_SCOPE") {
  # This optional env var lets us run one or a few state folders during
  # development without changing the default full-state loop.
  raw_value <- Sys.getenv(env_var, unset = "")

  if (!nzchar(raw_value)) {
    return(lodes_state_scopes_default)
  }

  scopes <- raw_value %>%
    stringr::str_split(",") %>%
    purrr::pluck(1) %>%
    stringr::str_trim() %>%
    tolower() %>%
    unique()

  invalid_scopes <- setdiff(scopes, lodes_state_scopes_default)
  if (length(invalid_scopes) > 0) {
    stop(
      sprintf(
        "Invalid %s values: %s",
        env_var,
        paste(invalid_scopes, collapse = ", ")
      ),
      call. = FALSE
    )
  }

  scopes
}

resolve_lodes_download_dir <- function(env_var = "LEHD_LODES_DOWNLOAD_DIR") {
  raw_value <- Sys.getenv(env_var, unset = "")

  if (!nzchar(raw_value)) {
    return(NULL)
  }

  normalized_path <- normalizePath(raw_value, winslash = "/", mustWork = FALSE)

  if (!dir.exists(normalized_path)) {
    stop(
      sprintf("Invalid %s directory: %s", env_var, raw_value),
      call. = FALSE
    )
  }

  normalized_path
}

lodes_year <- resolve_lodes_year()
lodes_state_scopes <- resolve_lodes_state_scope()
lodes_download_dir <- resolve_lodes_download_dir()

build_lodes_version_url <- function(state_scope, version = lodes_default_version) {
  glue("https://lehd.ces.census.gov/data/lodes/{version}/{state_scope}/version.txt")
}

download_lodes_asset <- function(urls, dest_path, local_filenames = character()) {
  # We use the system `curl` binary instead of R HTTP clients because bulk
  # Census downloads have been more reliable that way in this repo environment.
  if (!is.null(lodes_download_dir) && length(local_filenames) > 0) {
    for (filename in local_filenames) {
      local_path <- file.path(lodes_download_dir, filename)

      if (file.exists(local_path) && file.info(local_path)$size > 0) {
        file.copy(local_path, dest_path, overwrite = TRUE)
        return(dest_path)
      }
    }
  }

  for (url in urls) {
    for (attempt in seq_len(3)) {
      cmd_output <- suppressWarnings(system2(
        command = "/usr/bin/curl",
        args = c("-fsSL", url, "-o", dest_path),
        stdout = TRUE,
        stderr = TRUE
      ))
      exit_status <- attr(cmd_output, "status")

      if ((is.null(exit_status) || identical(exit_status, 0L)) &&
          file.exists(dest_path) &&
          file.info(dest_path)$size > 0) {
        return(dest_path)
      }

      Sys.sleep(attempt)
    }
  }

  stop(
    glue("Could not download LODES asset from any candidate URL: {paste(urls, collapse = ', ')}"),
    call. = FALSE
  )
}

fetch_lodes_version_lines <- function(state_scope, version = lodes_default_version) {
  # The state-level version file gives us a light provenance stamp that we can
  # attach to every staged tract row without caching the raw download bundle.
  version_tmp <- tempfile(pattern = glue("{state_scope}_lodes_version_"), fileext = ".txt")
  tryCatch(
    download_lodes_asset(
      build_lodes_version_url(state_scope, version = version),
      version_tmp,
      local_filenames = "version.txt"
    ),
    error = function(cnd) NULL
  )

  on.exit(unlink(version_tmp), add = TRUE)

  if (!file.exists(version_tmp) || file.info(version_tmp)$size <= 0) {
    return(character())
  }

  stringr::str_trim(readLines(version_tmp, warn = FALSE), side = "both")
}

parse_lodes_version_metadata <- function(version_lines, state_scope) {
  non_empty_lines <- version_lines[nzchar(version_lines)]

  vintage_line <- non_empty_lines[stringr::str_detect(non_empty_lines, "^Data Vintage:")][1]
  format_line <- non_empty_lines[stringr::str_detect(non_empty_lines, "^Release Format Version")][1]

  if (is.na(vintage_line) || is.na(format_line)) {
    return(tibble::tibble(
      state_scope = state_scope,
      release_vintage = NA_character_,
      release_format_version = NA_character_
    ))
  }

  tibble::tibble(
    state_scope = state_scope,
    release_vintage = stringr::str_remove(vintage_line, "^Data Vintage:\\s*"),
    release_format_version = stringr::str_remove(format_line, "^Release Format Version\\s*")
  )
}

collect_lodes_state_dataset <- function(
  state_scope,
  lodes_type,
  year_value = lodes_year,
  version = lodes_default_version,
  job_type = lodes_default_job_type,
  segment = lodes_default_segment
) {
  # We intentionally pull block-grain source rows here so we can verify the
  # source IDs and published crosswalk coverage before we collapse to tract.
  source_tmp <- tempfile(
    pattern = glue("{state_scope}_{lodes_type}_{segment}_{job_type}_{year_value}_"),
    fileext = ".csv.gz"
  )

  source_urls <- if (identical(lodes_type, "wac")) {
    c(
      glue("https://lehd.ces.census.gov/data/lodes/{version}/{state_scope}/wac/{state_scope}_wac_{segment}_{job_type}_{year_value}.csv.gz")
    )
  } else {
    c(
      glue("https://lehd.ces.census.gov/data/lodes/{version}/{state_scope}/rac/{state_scope}_rac_{segment}_{job_type}_{year_value}.csv.gz"),
      glue("https://lehd.ces.census.gov/data/lodes/{version}/{state_scope}/rac/{state_scope}_rac_{segment}_{job_type}_{year_value}_1.csv.gz")
    )
  }

  source_local_filenames <- if (identical(lodes_type, "wac")) {
    glue("{state_scope}_wac_{segment}_{job_type}_{year_value}.csv.gz")
  } else {
    c(
      glue("{state_scope}_rac_{segment}_{job_type}_{year_value}.csv.gz"),
      glue("{state_scope}_rac_{segment}_{job_type}_{year_value}_1.csv.gz")
    )
  }

  download_lodes_asset(source_urls, source_tmp, local_filenames = source_local_filenames)

  on.exit(unlink(source_tmp), add = TRUE)

  source_df <- readr::read_csv(
    source_tmp,
    col_types = if (identical(lodes_type, "wac")) {
      readr::cols(
        w_geocode = readr::col_character(),
        createdate = readr::col_character()
      )
    } else {
      readr::cols(
        h_geocode = readr::col_character(),
        createdate = readr::col_character()
      )
    },
    show_col_types = FALSE,
    progress = FALSE
  )

  geocode_col <- if (identical(lodes_type, "wac")) "w_geocode" else "h_geocode"

  source_df %>%
    dplyr::mutate(
      state = toupper(state_scope),
      year = as.integer(year_value),
      block_geoid = as.character(.data[[geocode_col]]),
      createdate = as.character(.data$createdate)
    )
}

collect_lodes_state_xwalk <- function(state_scope) {
  # The local `lehdr` build we validated does not expose a crosswalk helper, so
  # we download the provider's own state crosswalk directly and treat it as the
  # validation source of truth for tract aggregation.
  xwalk_url <- glue(
    "https://lehd.ces.census.gov/data/lodes/{lodes_default_version}/{state_scope}/{state_scope}_xwalk.csv.gz"
  )
  xwalk_tmp <- tempfile(
    pattern = glue("{state_scope}_lodes_xwalk_"),
    fileext = ".csv.gz"
  )

  download_lodes_asset(
    xwalk_url,
    xwalk_tmp,
    local_filenames = glue("{state_scope}_xwalk.csv.gz")
  )

  on.exit(unlink(xwalk_tmp), add = TRUE)

  xwalk_df <- readr::read_csv(
    xwalk_tmp,
    col_types = readr::cols(
      tabblk2020 = readr::col_character(),
      cty = readr::col_character(),
      trct = readr::col_character(),
      cbsa = readr::col_character(),
      createdate = readr::col_character()
    ),
    show_col_types = FALSE,
    progress = FALSE
  )

  xwalk_df %>%
    dplyr::transmute(
      block_geoid = as.character(.data$tabblk2020),
      tract_geoid = stringr::str_pad(as.character(.data$trct), width = 11, side = "left", pad = "0"),
      county_geoid = stringr::str_pad(as.character(.data$cty), width = 5, side = "left", pad = "0"),
      cbsa_code = dplyr::na_if(as.character(.data$cbsa), ""),
      xwalk_createdate = as.character(.data$createdate)
    ) %>%
    dplyr::distinct(.data$block_geoid, .keep_all = TRUE)
}

get_lodes_measure_columns <- function(df, lodes_type) {
  excluded_columns <- c(
    if (identical(lodes_type, "wac")) "w_geocode" else "h_geocode",
    "block_geoid",
    "createdate",
    "state",
    "year"
  )

  measure_columns <- setdiff(names(df), excluded_columns)
  numeric_measure_columns <- measure_columns[vapply(df[measure_columns], is.numeric, logical(1))]

  numeric_measure_columns
}

aggregate_lodes_to_tract <- function(
  source_df,
  xwalk_df,
  state_scope,
  lodes_type,
  metadata_row,
  job_type = lodes_default_job_type,
  segment = lodes_default_segment
) {
  joined_df <- source_df %>%
    dplyr::left_join(xwalk_df, by = "block_geoid")

  missing_tract_rows <- joined_df %>%
    dplyr::filter(is.na(.data$tract_geoid) | !stringr::str_detect(.data$tract_geoid, "^\\d{11}$"))

  if (nrow(missing_tract_rows) > 0) {
    stop(
      glue(
        "LODES {toupper(lodes_type)} scope {state_scope} has {nrow(missing_tract_rows)} block rows that do not map to a valid tract GEOID."
      ),
      call. = FALSE
    )
  }

  measure_columns <- get_lodes_measure_columns(joined_df, lodes_type)

  aggregated_df <- joined_df %>%
    dplyr::group_by(.data$tract_geoid, .data$county_geoid, .data$cbsa_code) %>%
    dplyr::summarise(
      dplyr::across(dplyr::all_of(measure_columns), ~ sum(.x, na.rm = TRUE)),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      state = toupper(state_scope),
      state_fips = stringr::str_sub(.data$tract_geoid, 1, 2),
      year = source_df$year[[1]],
      lodes_type = toupper(lodes_type),
      job_type = job_type,
      segment = segment,
      release_vintage = metadata_row$release_vintage[[1]],
      release_format_version = metadata_row$release_format_version[[1]],
      source_createdate = dplyr::first(source_df$createdate),
      xwalk_createdate = dplyr::first(xwalk_df$xwalk_createdate),
      source_file = dplyr::case_when(
        identical(lodes_type, "wac") ~ glue("{state_scope}_wac_{segment}_{job_type}_{source_df$year[[1]]}.csv.gz"),
        identical(lodes_type, "rac") ~ glue("{state_scope}_rac_{segment}_{job_type}_{source_df$year[[1]]}.csv.gz"),
        TRUE ~ NA_character_
      )
    ) %>%
    dplyr::relocate(
      .data$state,
      .data$state_fips,
      .data$county_geoid,
      .data$cbsa_code,
      .data$tract_geoid,
      .data$year,
      .data$lodes_type,
      .data$job_type,
      .data$segment,
      .data$release_vintage,
      .data$release_format_version,
      .data$source_createdate,
      .data$xwalk_createdate,
      .data$source_file
    )

  duplicate_keys <- aggregated_df %>%
    dplyr::count(.data$tract_geoid, .data$year, name = "n") %>%
    dplyr::filter(.data$n > 1)

  if (nrow(duplicate_keys) > 0) {
    stop(
      glue(
        "LODES {toupper(lodes_type)} scope {state_scope} is not unique at tract_geoid + year after aggregation."
      ),
      call. = FALSE
    )
  }

  aggregated_df
}

collect_lodes_type_staging <- function(
  lodes_type,
  state_scopes = lodes_state_scopes,
  year_value = lodes_year,
  version = lodes_default_version,
  job_type = lodes_default_job_type,
  segment = lodes_default_segment
) {
  purrr::map_dfr(
    state_scopes,
    function(state_scope) {
      if (is_known_missing_lodes_combo(state_scope, lodes_type, year_value)) {
        message(
          "Skipping known unavailable LEHD LODES ",
          toupper(lodes_type),
          " scope ",
          state_scope,
          " for year ",
          year_value,
          "."
        )
        return(tibble::tibble())
      }

      message(
        "Processing LEHD LODES ",
        toupper(lodes_type),
        " for scope ",
        state_scope,
        " and year ",
        year_value
      )

      metadata_row <- fetch_lodes_version_lines(state_scope, version = version) %>%
        parse_lodes_version_metadata(state_scope = state_scope)

      source_df <- collect_lodes_state_dataset(
        state_scope = state_scope,
        lodes_type = lodes_type,
        year_value = year_value,
        version = version,
        job_type = job_type,
        segment = segment
      )

      xwalk_df <- collect_lodes_state_xwalk(state_scope)

      aggregate_lodes_to_tract(
        source_df = source_df,
        xwalk_df = xwalk_df,
        state_scope = state_scope,
        lodes_type = lodes_type,
        metadata_row = metadata_row,
        job_type = job_type,
        segment = segment
      )
    }
  )
}

# 3. Download, validate, aggregate, and bind the approved state files ----
lodes_wac_staging <- collect_lodes_type_staging("wac")
lodes_rac_staging <- collect_lodes_type_staging("rac")

# 4. Contract checks ----
validate_lodes_stage <- function(df, table_name) {
  invalid_tract_rows <- df %>%
    dplyr::filter(is.na(.data$tract_geoid) | !stringr::str_detect(.data$tract_geoid, "^\\d{11}$"))

  if (nrow(invalid_tract_rows) > 0) {
    stop(
      glue("{table_name} contains {nrow(invalid_tract_rows)} rows with invalid tract GEOIDs."),
      call. = FALSE
    )
  }

  invalid_state_rows <- df %>%
    dplyr::filter(is.na(.data$state_fips) | !stringr::str_detect(.data$state_fips, "^\\d{2}$"))

  if (nrow(invalid_state_rows) > 0) {
    stop(
      glue("{table_name} contains {nrow(invalid_state_rows)} rows with invalid state FIPS values."),
      call. = FALSE
    )
  }

  duplicate_rows <- df %>%
    dplyr::count(.data$tract_geoid, .data$year, name = "n") %>%
    dplyr::filter(.data$n > 1)

  if (nrow(duplicate_rows) > 0) {
    stop(
      glue("{table_name} is not unique at tract_geoid + year."),
      call. = FALSE
    )
  }

  total_jobs_rows <- df %>%
    dplyr::filter(is.na(.data$C000) | .data$C000 < 0)

  if (nrow(total_jobs_rows) > 0) {
    stop(
      glue("{table_name} contains {nrow(total_jobs_rows)} rows with missing or negative C000 totals."),
      call. = FALSE
    )
  }
}

validate_lodes_stage(lodes_wac_staging, "staging.lehd_lodes_wac")
validate_lodes_stage(lodes_rac_staging, "staging.lehd_lodes_rac")

# 5. Load the normalized staging tables ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "lehd_lodes_wac"),
  lodes_wac_staging,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "lehd_lodes_rac"),
  lodes_rac_staging,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
