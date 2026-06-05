# In this script we land FHFA annual House Price Index rows across the published
# annual geographies we currently want to stage: U.S., state, CBSA, county,
# five-digit ZIP, and census tract.
#
# FHFA publishes annual developmental-index files by geography. We keep the staged
# tables close to those source files so Silver can standardize the annual metrics later
# without rebuilding them from other vintages or frequency ladders.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "fhfa")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the annual source files and staging targets ----
fhfa_sources <- list(
  list(
    geo_level = "us",
    staging_table = "fhfa_hpi_us",
    local_file = file.path(raw_dir, "hpi_at_national.xlsx"),
    urls = c(
      "https://www.fhfa.gov/hpi/download/annual/hpi_at_national.xlsx"
    ),
    hpi_flavor = "all-transactions",
    frequency = "annual",
    level = "US"
  ),
  list(
    geo_level = "state",
    staging_table = "fhfa_hpi_state",
    local_file = file.path(raw_dir, "hpi_at_state.xlsx"),
    urls = c(
      "https://www.fhfa.gov/hpi/download/annual/hpi_at_state.xlsx"
    ),
    hpi_flavor = "all-transactions",
    frequency = "annual",
    level = "State"
  ),
  list(
    geo_level = "cbsa",
    staging_table = "fhfa_hpi_cbsa",
    local_file = file.path(raw_dir, "hpi_at_cbsa.xlsx"),
    urls = c(
      "https://www.fhfa.gov/hpi/download/annual/hpi_at_cbsa.xlsx"
    ),
    hpi_flavor = "all-transactions",
    frequency = "annual",
    level = "CBSA"
  ),
  list(
    geo_level = "county",
    staging_table = "fhfa_hpi_county",
    local_file = file.path(raw_dir, "hpi_at_county.xlsx"),
    urls = c(
      "https://www.fhfa.gov/hpi/download/annual/hpi_at_county.xlsx"
    ),
    hpi_flavor = "all-transactions",
    frequency = "annual",
    level = "County"
  ),
  list(
    geo_level = "zip5",
    staging_table = "fhfa_hpi_zip5",
    local_file = file.path(raw_dir, "hpi_at_zip5.xlsx"),
    urls = c(
      "https://www.fhfa.gov/hpi/download/annual/hpi_at_zip5.xlsx"
    ),
    hpi_flavor = "all-transactions",
    frequency = "annual",
    level = "ZIP5"
  ),
  list(
    geo_level = "tract",
    staging_table = "fhfa_hpi_tract",
    local_file = file.path(raw_dir, "hpi_at_tract.csv"),
    urls = c(
      "https://www.fhfa.gov/hpi/download/annual/hpi_at_tract.csv"
    ),
    hpi_flavor = "all-transactions",
    frequency = "annual",
    level = "Tract"
  )
)

# 3. Shared helpers ----
download_fhfa_file <- function(urls, dest_path) {
  if (file.exists(dest_path)) {
    return(dest_path)
  }

  last_error <- NULL

  for (url in urls) {
    resp <- tryCatch(
      httr::GET(
        url,
        httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
      ),
      error = function(e) e
    )

    if (inherits(resp, "error")) {
      last_error <- resp
      next
    }

    if (httr::status_code(resp) == 200) {
      writeBin(httr::content(resp, "raw"), dest_path)
      return(dest_path)
    }

    last_error <- simpleError(
      glue("HTTP {httr::status_code(resp)} for {url}")
    )
  }

  stop(
    glue(
      "FHFA download failed for {basename(dest_path)}. Tried: {paste(urls, collapse = ', ')}. Last error: {conditionMessage(last_error)}"
    ),
    call. = FALSE
  )
}

read_fhfa_annual_workbook <- function(path) {
  readxl::read_excel(
    path,
    sheet = 1,
    skip = 5
  ) %>%
    janitor::clean_names()
}

read_fhfa_annual_csv <- function(path) {
  readr::read_csv(
    path,
    col_types = readr::cols(.default = readr::col_character()),
    show_col_types = FALSE,
    progress = FALSE
  ) %>%
    janitor::clean_names()
}

normalize_fhfa_file <- function(path, source_meta) {
  raw <- if (identical(source_meta$geo_level, "tract")) {
    read_fhfa_annual_csv(path)
  } else {
    read_fhfa_annual_workbook(path)
  }

  if (identical(source_meta$geo_level, "us")) {
    normalized <- raw %>%
      transmute(
        hpi_flavor = source_meta$hpi_flavor,
        frequency = source_meta$frequency,
        level = source_meta$level,
        place_name = "United States",
        place_id = "US",
        yr = suppressWarnings(as.integer(.data$year)),
        annual_change_pct = suppressWarnings(as.numeric(.data$annual_change_percent)),
        hpi = suppressWarnings(as.numeric(.data$hpi)),
        hpi_1990_base = suppressWarnings(as.numeric(.data$hpi_with_1990_base)),
        hpi_2000_base = suppressWarnings(as.numeric(.data$hpi_with_2000_base))
      )
  } else if (identical(source_meta$geo_level, "state")) {
    normalized <- raw %>%
      transmute(
        hpi_flavor = source_meta$hpi_flavor,
        frequency = source_meta$frequency,
        level = source_meta$level,
        state_name = .data$state,
        state_abbr = .data$abbreviation,
        state_fips = stringr::str_pad(.data$fips, width = 2, side = "left", pad = "0"),
        place_name = .data$state,
        place_id = stringr::str_pad(.data$fips, width = 2, side = "left", pad = "0"),
        yr = suppressWarnings(as.integer(.data$year)),
        annual_change_pct = suppressWarnings(as.numeric(.data$annual_change_percent)),
        hpi = suppressWarnings(as.numeric(.data$hpi)),
        hpi_1990_base = suppressWarnings(as.numeric(.data$hpi_with_1990_base)),
        hpi_2000_base = suppressWarnings(as.numeric(.data$hpi_with_2000_base))
      )
  } else if (identical(source_meta$geo_level, "cbsa")) {
    normalized <- raw %>%
      transmute(
        hpi_flavor = source_meta$hpi_flavor,
        frequency = source_meta$frequency,
        level = source_meta$level,
        place_name = .data$name,
        place_id = .data$cbsa,
        yr = suppressWarnings(as.integer(.data$year)),
        annual_change_pct = suppressWarnings(as.numeric(.data$annual_change_percent)),
        hpi = suppressWarnings(as.numeric(.data$hpi)),
        hpi_1990_base = suppressWarnings(as.numeric(.data$hpi_with_1990_base)),
        hpi_2000_base = suppressWarnings(as.numeric(.data$hpi_with_2000_base))
      )
  } else if (identical(source_meta$geo_level, "county")) {
    normalized <- raw %>%
      transmute(
        hpi_flavor = source_meta$hpi_flavor,
        frequency = source_meta$frequency,
        level = source_meta$level,
        state_abbr = .data$state,
        place_name = .data$county,
        place_id = .data$fips_code,
        yr = suppressWarnings(as.integer(.data$year)),
        annual_change_pct = suppressWarnings(as.numeric(.data$annual_change_percent)),
        hpi = suppressWarnings(as.numeric(.data$hpi)),
        hpi_1990_base = suppressWarnings(as.numeric(.data$hpi_with_1990_base)),
        hpi_2000_base = suppressWarnings(as.numeric(.data$hpi_with_2000_base))
      ) %>%
      mutate(
        place_id = stringr::str_pad(place_id, width = 5, side = "left", pad = "0")
      )
  } else if (identical(source_meta$geo_level, "zip5")) {
    normalized <- raw %>%
      transmute(
        hpi_flavor = source_meta$hpi_flavor,
        frequency = source_meta$frequency,
        level = source_meta$level,
        place_name = stringr::str_pad(.data$five_digit_zip_code, width = 5, side = "left", pad = "0"),
        place_id = stringr::str_pad(.data$five_digit_zip_code, width = 5, side = "left", pad = "0"),
        yr = suppressWarnings(as.integer(.data$year)),
        annual_change_pct = suppressWarnings(as.numeric(.data$annual_change_percent)),
        hpi = suppressWarnings(as.numeric(.data$hpi)),
        hpi_1990_base = suppressWarnings(as.numeric(.data$hpi_with_1990_base)),
        hpi_2000_base = suppressWarnings(as.numeric(.data$hpi_with_2000_base))
      )
  } else if (identical(source_meta$geo_level, "tract")) {
    normalized <- raw %>%
      transmute(
        hpi_flavor = source_meta$hpi_flavor,
        frequency = source_meta$frequency,
        level = source_meta$level,
        state_abbr = .data$state_abbr,
        place_name = .data$tract,
        place_id = .data$tract,
        yr = suppressWarnings(as.integer(.data$year)),
        annual_change_pct = suppressWarnings(as.numeric(.data$annual_change)),
        hpi = suppressWarnings(as.numeric(.data$hpi)),
        hpi_1990_base = suppressWarnings(as.numeric(.data$hpi1990)),
        hpi_2000_base = suppressWarnings(as.numeric(.data$hpi2000))
      )
  } else {
    stop(glue("Unsupported FHFA geography: {source_meta$geo_level}"), call. = FALSE)
  }

  normalized %>%
    mutate(
      place_id = as.character(place_id),
      place_name = stringr::str_squish(place_name)
    ) %>%
    filter(
      !is.na(place_id),
      !is.na(place_name),
      !is.na(yr),
      !is.na(hpi)
    )
}

validate_fhfa_stage <- function(df, source_meta) {
  if (nrow(df) == 0) {
    stop(glue("FHFA {source_meta$geo_level} staging frame is empty."), call. = FALSE)
  }

  required_cols <- c(
    "hpi_flavor", "frequency", "level", "place_name", "place_id",
    "yr", "annual_change_pct", "hpi", "hpi_1990_base", "hpi_2000_base"
  )

  if (identical(source_meta$geo_level, "state")) {
    required_cols <- c(required_cols, "state_name", "state_abbr", "state_fips")
  }

  if (identical(source_meta$geo_level, "county") || identical(source_meta$geo_level, "tract")) {
    required_cols <- c(required_cols, "state_abbr")
  }

  missing_cols <- setdiff(required_cols, names(df))
  if (length(missing_cols) > 0) {
    stop(
      glue(
        "FHFA {source_meta$geo_level} staging frame is missing columns: {paste(missing_cols, collapse = ', ')}"
      ),
      call. = FALSE
    )
  }

  if (!all(df$frequency == source_meta$frequency)) {
    stop(
      glue(
        "FHFA {source_meta$geo_level} staging contains unexpected frequency values."
      ),
      call. = FALSE
    )
  }

  duplicate_keys <- df %>%
    count(place_id, yr) %>%
    filter(n > 1)

  if (nrow(duplicate_keys) > 0) {
    stop(
      glue(
        "FHFA {source_meta$geo_level} staging contains duplicate place_id + yr rows."
      ),
      call. = FALSE
    )
  }

  if (identical(source_meta$geo_level, "county")) {
    bad_fips <- df %>%
      filter(!stringr::str_detect(place_id, "^\\d{5}$"))

    if (nrow(bad_fips) > 0) {
      stop("FHFA county staging contains non-5-digit county FIPS values.", call. = FALSE)
    }
  }

  if (identical(source_meta$geo_level, "state")) {
    bad_fips <- df %>%
      filter(!stringr::str_detect(place_id, "^\\d{2}$"))

    if (nrow(bad_fips) > 0) {
      stop("FHFA state staging contains non-2-digit state FIPS values.", call. = FALSE)
    }
  }

  if (identical(source_meta$geo_level, "zip5")) {
    bad_zip <- df %>%
      filter(!stringr::str_detect(place_id, "^\\d{5}$"))

    if (nrow(bad_zip) > 0) {
      stop("FHFA ZIP5 staging contains non-5-digit ZIP values.", call. = FALSE)
    }
  }

  if (identical(source_meta$geo_level, "tract")) {
    bad_tract <- df %>%
      filter(!stringr::str_detect(place_id, "^\\d{11}$"))

    if (nrow(bad_tract) > 0) {
      stop("FHFA tract staging contains non-11-digit tract GEOIDs.", call. = FALSE)
    }
  }

  if (identical(source_meta$geo_level, "us")) {
    bad_us <- df %>%
      filter(place_id != "US")

    if (nrow(bad_us) > 0) {
      stop("FHFA U.S. staging contains unexpected national keys.", call. = FALSE)
    }
  }
}

# 4. Download, parse, validate, and materialize the staging tables ----
for (source_meta in fhfa_sources) {
  message("Processing FHFA ", source_meta$geo_level, " annual file.")

  local_path <- download_fhfa_file(source_meta$urls, source_meta$local_file)

  staged_df <- normalize_fhfa_file(local_path, source_meta)

  validate_fhfa_stage(staged_df, source_meta)

  DBI::dbWriteTable(
    con,
    DBI::Id(schema = "staging", table = source_meta$staging_table),
    staged_df,
    overwrite = TRUE
  )

  row_count <- DBI::dbGetQuery(
    con,
    glue("SELECT COUNT(*) AS n FROM staging.{source_meta$staging_table}")
  )$n[[1]]

  message("  wrote staging.", source_meta$staging_table, " (", scales::comma(row_count), " rows)")
}
