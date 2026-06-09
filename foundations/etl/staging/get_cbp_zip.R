# This script lands the latest available CBP ZIP industry detail file as a
# separate staging surface. We intentionally keep it isolated from the county
# history path because ZIP detail is a much larger, latest-year-only expansion.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "economics", "raw", "census", "cbp")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 1. Define the current ZIP-detail release ----
cbp_zip_year <- 2023

build_cbp_zip_detail_url <- function(year_value) {
  year_suffix <- stringr::str_sub(as.character(year_value), 3, 4)
  glue("https://www2.census.gov/programs-surveys/cbp/datasets/{year_value}/zbp{year_suffix}detail.zip")
}

build_cbp_zip_detail_zip_name <- function(year_value) {
  year_suffix <- stringr::str_sub(as.character(year_value), 3, 4)
  glue("zbp{year_suffix}detail.zip")
}

build_cbp_zip_detail_member_name <- function(year_value) {
  year_suffix <- stringr::str_sub(as.character(year_value), 3, 4)
  glue("zbp{year_suffix}detail.txt")
}

download_cbp_zip_detail <- function(year_value) {
  zip_name <- build_cbp_zip_detail_zip_name(year_value)
  zip_path <- file.path(raw_dir, zip_name)

  if (file.exists(zip_path)) {
    return(zip_path)
  }

  zip_url <- build_cbp_zip_detail_url(year_value)
  resp <- httr::GET(
    zip_url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)

  writeBin(httr::content(resp, "raw"), zip_path)
  zip_path
}

read_cbp_zip_detail <- function(zip_path, year_value) {
  member_name <- build_cbp_zip_detail_member_name(year_value)

  raw_df <- readr::read_csv(
    unz(zip_path, member_name),
    col_types = readr::cols(
      .default = readr::col_guess(),
      zip = readr::col_character(),
      name = readr::col_character(),
      naics = readr::col_character(),
      est = readr::col_double(),
      `n<5` = readr::col_double(),
      n5_9 = readr::col_double(),
      n10_19 = readr::col_double(),
      n20_49 = readr::col_double(),
      n50_99 = readr::col_double(),
      n100_249 = readr::col_double(),
      n250_499 = readr::col_double(),
      n500_999 = readr::col_double(),
      n1000 = readr::col_double(),
      city = readr::col_character(),
      stabbr = readr::col_character(),
      cty_name = readr::col_character()
    ),
    show_col_types = FALSE,
    progress = FALSE
  )

  names(raw_df) <- tolower(names(raw_df))

  tibble::tibble(
    year = year_value,
    zip_code = stringr::str_pad(raw_df$zip, width = 5, side = "left", pad = "0"),
    zip_name = raw_df$name,
    naics_code = raw_df$naics,
    establishments = raw_df$est,
    est_n_lt_5 = raw_df[["n<5"]],
    est_n_5_9 = raw_df$n5_9,
    est_n_10_19 = raw_df$n10_19,
    est_n_20_49 = raw_df$n20_49,
    est_n_50_99 = raw_df$n50_99,
    est_n_100_249 = raw_df$n100_249,
    est_n_250_499 = raw_df$n250_499,
    est_n_500_999 = raw_df$n500_999,
    est_n_1000_plus = raw_df$n1000,
    city = raw_df$city,
    state_abbr = raw_df$stabbr,
    county_name = raw_df$cty_name,
    source_file = basename(zip_path)
  )
}

# 2. Download and parse the current ZIP detail file ----
zip_path <- download_cbp_zip_detail(cbp_zip_year)
cbp_zip_detail <- read_cbp_zip_detail(zip_path, cbp_zip_year)

# 3. Contract checks ----
invalid_zip_rows <- cbp_zip_detail %>%
  filter(is.na(.data$zip_code) | !stringr::str_detect(.data$zip_code, "^\\d{5}$"))

if (nrow(invalid_zip_rows) > 0) {
  stop(
    glue("CBP ZIP detail staging contains {nrow(invalid_zip_rows)} rows with invalid 5-digit ZIP keys."),
    call. = FALSE
  )
}

invalid_naics_rows <- cbp_zip_detail %>%
  filter(is.na(.data$naics_code) | .data$naics_code == "")

if (nrow(invalid_naics_rows) > 0) {
  stop(
    glue("CBP ZIP detail staging contains {nrow(invalid_naics_rows)} rows with missing NAICS codes."),
    call. = FALSE
  )
}

duplicate_rows <- cbp_zip_detail %>%
  count(.data$zip_code, .data$year, .data$naics_code, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_rows) > 0) {
  stop(
    glue("CBP ZIP detail staging is not unique at zip_code + year + naics_code. Duplicate keys found: {nrow(duplicate_rows)}"),
    call. = FALSE
  )
}

# 4. Load the staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "cbp_zip_detail"),
  cbp_zip_detail,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
