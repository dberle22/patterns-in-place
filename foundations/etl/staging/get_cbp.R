# In this script we land source-faithful County Business Patterns county rows
# for the approved first-pass year range. We intentionally keep the full county
# metric payload from the annual files because the county slice is our canonical
# business-structure base for later county -> CBSA/state rollups, and Silver can
# prune industries later without forcing us to re-download the source archive.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "economics", "raw", "census", "cbp")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the first-pass year range and county source pattern ----
cbp_years <- 2010:2023

build_cbp_county_url <- function(year_value) {
  year_suffix <- stringr::str_sub(as.character(year_value), 3, 4)
  glue("https://www2.census.gov/programs-surveys/cbp/datasets/{year_value}/cbp{year_suffix}co.zip")
}

build_cbp_county_zip_name <- function(year_value) {
  year_suffix <- stringr::str_sub(as.character(year_value), 3, 4)
  glue("cbp{year_suffix}co.zip")
}

build_cbp_county_member_name <- function(year_value) {
  year_suffix <- stringr::str_sub(as.character(year_value), 3, 4)
  glue("cbp{year_suffix}co.txt")
}

download_cbp_county_zip <- function(year_value) {
  zip_name <- build_cbp_county_zip_name(year_value)
  zip_path <- file.path(raw_dir, zip_name)

  if (file.exists(zip_path)) {
    return(zip_path)
  }

  zip_url <- build_cbp_county_url(year_value)
  resp <- httr::GET(
    zip_url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)

  writeBin(httr::content(resp, "raw"), zip_path)
  zip_path
}

read_cbp_county_year <- function(zip_path, year_value) {
  member_name <- build_cbp_county_member_name(year_value)

  raw_df <- readr::read_csv(
    unz(zip_path, member_name),
    col_types = readr::cols(
      .default = readr::col_guess(),
      fipstate = readr::col_character(),
      fipscty = readr::col_character(),
      naics = readr::col_character(),
      empflag = readr::col_character(),
      emp_nf = readr::col_character(),
      emp = readr::col_double(),
      qp1_nf = readr::col_character(),
      qp1 = readr::col_double(),
      ap_nf = readr::col_character(),
      ap = readr::col_double(),
      est = readr::col_double(),
      n1_4 = readr::col_double(),
      `n<5` = readr::col_double(),
      n5_9 = readr::col_double(),
      n10_19 = readr::col_double(),
      n20_49 = readr::col_double(),
      n50_99 = readr::col_double(),
      n100_249 = readr::col_double(),
      n250_499 = readr::col_double(),
      n500_999 = readr::col_double(),
      n1000 = readr::col_double(),
      n1000_1 = readr::col_double(),
      n1000_2 = readr::col_double(),
      n1000_3 = readr::col_double(),
      n1000_4 = readr::col_double(),
      censtate = readr::col_character(),
      cencty = readr::col_character()
    ),
    show_col_types = FALSE,
    progress = FALSE
  )

  names(raw_df) <- tolower(names(raw_df))

  est_n_lt_5 <- if ("n<5" %in% names(raw_df)) {
    raw_df[["n<5"]]
  } else if ("n1_4" %in% names(raw_df)) {
    raw_df[["n1_4"]]
  } else {
    rep(NA_real_, nrow(raw_df))
  }

  emp_noise_flag <- if ("emp_nf" %in% names(raw_df)) {
    raw_df[["emp_nf"]]
  } else if ("empflag" %in% names(raw_df)) {
    raw_df[["empflag"]]
  } else {
    rep(NA_character_, nrow(raw_df))
  }

  tibble::tibble(
    year = year_value,
    state_fips = stringr::str_pad(raw_df$fipstate, width = 2, side = "left", pad = "0"),
    county_fips = stringr::str_c(
      stringr::str_pad(raw_df$fipstate, width = 2, side = "left", pad = "0"),
      stringr::str_pad(raw_df$fipscty, width = 3, side = "left", pad = "0")
    ),
    county_fips_3 = stringr::str_pad(raw_df$fipscty, width = 3, side = "left", pad = "0"),
    naics_code = raw_df$naics,
    emp_noise_flag = emp_noise_flag,
    employment_march12 = raw_df$emp,
    qp1_noise_flag = raw_df$qp1_nf,
    first_quarter_payroll_k = raw_df$qp1,
    ap_noise_flag = raw_df$ap_nf,
    annual_payroll_k = raw_df$ap,
    establishments = raw_df$est,
    est_n_lt_5 = est_n_lt_5,
    est_n_5_9 = raw_df$n5_9,
    est_n_10_19 = raw_df$n10_19,
    est_n_20_49 = raw_df$n20_49,
    est_n_50_99 = raw_df$n50_99,
    est_n_100_249 = raw_df$n100_249,
    est_n_250_499 = raw_df$n250_499,
    est_n_500_999 = raw_df$n500_999,
    est_n_1000_plus = raw_df$n1000,
    est_n_1000_1499 = raw_df$n1000_1,
    est_n_1500_2499 = raw_df$n1000_2,
    est_n_2500_4999 = raw_df$n1000_3,
    est_n_5000_plus = raw_df$n1000_4,
    source_file = basename(zip_path)
  )
}

# 3. Download, read, and bind the approved county files ----
cbp_county_staging <- purrr::map_dfr(
  cbp_years,
  function(year_value) {
    message("Processing CBP county file for year: ", year_value)
    zip_path <- download_cbp_county_zip(year_value)
    read_cbp_county_year(zip_path, year_value)
  }
)

# 4. Contract checks ----
invalid_county_rows <- cbp_county_staging %>%
  filter(is.na(.data$county_fips) | !stringr::str_detect(.data$county_fips, "^\\d{5}$"))

if (nrow(invalid_county_rows) > 0) {
  stop(
    glue("CBP county staging contains {nrow(invalid_county_rows)} rows with invalid 5-digit county FIPS keys."),
    call. = FALSE
  )
}

invalid_state_rows <- cbp_county_staging %>%
  filter(is.na(.data$state_fips) | !stringr::str_detect(.data$state_fips, "^\\d{2}$"))

if (nrow(invalid_state_rows) > 0) {
  stop(
    glue("CBP county staging contains {nrow(invalid_state_rows)} rows with invalid 2-digit state FIPS keys."),
    call. = FALSE
  )
}

invalid_naics_rows <- cbp_county_staging %>%
  filter(is.na(.data$naics_code) | .data$naics_code == "")

if (nrow(invalid_naics_rows) > 0) {
  stop(
    glue("CBP county staging contains {nrow(invalid_naics_rows)} rows with missing NAICS codes."),
    call. = FALSE
  )
}

duplicate_rows <- cbp_county_staging %>%
  count(.data$county_fips, .data$year, .data$naics_code, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_rows) > 0) {
  stop(
    glue("CBP county staging is not unique at county_fips + year + naics_code. Duplicate keys found: {nrow(duplicate_rows)}"),
    call. = FALSE
  )
}

# 5. Load the normalized staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "cbp_county"),
  cbp_county_staging,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
