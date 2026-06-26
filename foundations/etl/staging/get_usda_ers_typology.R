# In this script we land the two small USDA ERS county-classification files as
# source-faithful staging tables. The source already arrives in compact long
# `Attribute` / `Value` form, so staging should stay intentionally light:
# 1. download the current RUCC and County Typology CSVs
# 2. normalize the county-equivalent FIPS keys to 5-character text
# 3. preserve the published attribute/value rows plus a numeric parse helper
# 4. write one staging table per ERS file
#
# We intentionally do not reconcile Connecticut planning regions versus legacy
# counties here. That is a Silver modeling concern, not a raw landing concern.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "economics", "raw", "usda_ers_typology")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the current ERS assets ----
rucc_vintage_year <- 2023L
rucc_url <- "https://www.ers.usda.gov/media/5768/2023-rural-urban-continuum-codes.csv?v=25487"
rucc_file <- file.path(raw_dir, "usda_ers_rucc_2023.csv")

typology_vintage_year <- 2025L
typology_url <- "https://www.ers.usda.gov/media/6174/ers-county-typology-codes-2025-edition.csv?v=55079"
typology_file <- file.path(raw_dir, "usda_ers_county_typology_2025.csv")

download_ers_csv <- function(url, dest_path) {
  if (file.exists(dest_path) && file.info(dest_path)$size > 0) {
    return(dest_path)
  }

  resp <- httr::GET(
    url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)

  writeBin(httr::content(resp, "raw"), dest_path)
  dest_path
}

sanitize_utf8 <- function(x) {
  iconv(x, from = "", to = "UTF-8", sub = "")
}

normalize_ers_rucc <- function(path) {
  readr::read_csv(
    path,
    col_types = readr::cols(
      FIPS = readr::col_character(),
      State = readr::col_character(),
      County_Name = readr::col_character(),
      Attribute = readr::col_character(),
      Value = readr::col_character()
    ),
    show_col_types = FALSE,
    progress = FALSE
  ) %>%
    janitor::clean_names() %>%
    transmute(
      vintage_year = rucc_vintage_year,
      fips = stringr::str_pad(.data$fips, width = 5, side = "left", pad = "0"),
      state_abbr = as.character(.data$state),
      county_name = as.character(.data$county_name),
      attribute = as.character(.data$attribute),
      value_raw = as.character(.data$value),
      value_numeric = suppressWarnings(as.double(.data$value)),
      source_file = basename(path),
      source_url = rucc_url
    ) %>%
    mutate(across(where(is.character), sanitize_utf8))
}

normalize_ers_typology <- function(path) {
  readr::read_csv(
    path,
    col_types = readr::cols(
      FIPStxt = readr::col_character(),
      State = readr::col_character(),
      County_Name = readr::col_character(),
      Metro2023 = readr::col_character(),
      Attribute = readr::col_character(),
      Value = readr::col_character(),
      PublicationDate = readr::col_character(),
      Source = readr::col_character()
    ),
    show_col_types = FALSE,
      progress = FALSE
  ) %>%
    janitor::clean_names() %>%
    transmute(
      vintage_year = typology_vintage_year,
      fips = stringr::str_pad(.data$fip_stxt, width = 5, side = "left", pad = "0"),
      state_abbr = as.character(.data$state),
      county_name = as.character(.data$county_name),
      metro2023 = suppressWarnings(as.integer(.data$metro2023)),
      attribute = as.character(.data$attribute),
      value_raw = as.character(.data$value),
      value_numeric = suppressWarnings(as.double(.data$value)),
      publication_date = as.character(.data$publication_date),
      source_note = as.character(.data$source),
      source_file = basename(path),
      source_url = typology_url
    ) %>%
    mutate(across(where(is.character), sanitize_utf8))
}

assert_valid_fips <- function(df, table_name) {
  invalid_rows <- df %>%
    dplyr::filter(is.na(.data$fips) | !stringr::str_detect(.data$fips, "^\\d{5}$"))

  if (nrow(invalid_rows) > 0) {
    stop(
      glue("{table_name} contains {nrow(invalid_rows)} rows with invalid 5-digit county FIPS keys."),
      call. = FALSE
    )
  }
}

assert_unique_attribute_rows <- function(df, table_name) {
  duplicate_rows <- df %>%
    dplyr::count(.data$fips, .data$attribute, name = "n") %>%
    dplyr::filter(.data$n > 1)

  if (nrow(duplicate_rows) > 0) {
    stop(
      glue("{table_name} is not unique at fips + attribute. Duplicate keys found: {nrow(duplicate_rows)}"),
      call. = FALSE
    )
  }
}

assert_expected_attributes <- function(df, table_name, expected_attributes) {
  observed_attributes <- df %>%
    dplyr::distinct(.data$attribute) %>%
    dplyr::pull(.data$attribute) %>%
    sort()

  missing_attributes <- setdiff(expected_attributes, observed_attributes)
  extra_attributes <- setdiff(observed_attributes, expected_attributes)

  if (length(missing_attributes) > 0 || length(extra_attributes) > 0) {
    stop(
      glue(
        "{table_name} attribute set mismatch. Missing: {paste(missing_attributes, collapse = ', ')}. ",
        "Unexpected: {paste(extra_attributes, collapse = ', ')}."
      ),
      call. = FALSE
    )
  }
}

# 3. Download and normalize the current files ----
download_ers_csv(rucc_url, rucc_file)
download_ers_csv(typology_url, typology_file)

staging_rucc <- normalize_ers_rucc(rucc_file)
staging_typology <- normalize_ers_typology(typology_file)

# 4. Contract checks ----
assert_valid_fips(staging_rucc, "staging.usda_rucc")
assert_valid_fips(staging_typology, "staging.usda_county_typology")

assert_unique_attribute_rows(staging_rucc, "staging.usda_rucc")
assert_unique_attribute_rows(staging_typology, "staging.usda_county_typology")

assert_expected_attributes(
  staging_rucc,
  "staging.usda_rucc",
  expected_attributes = c("Description", "Population_2020", "RUCC_2023")
)

assert_expected_attributes(
  staging_typology,
  "staging.usda_county_typology",
  expected_attributes = c(
    "High_Farming_2025",
    "High_Government_2025",
    "High_Manufacturing_2025",
    "High_Mining_2025",
    "High_Recreation_2025",
    "Housing_Stress_2025",
    "Industry_Dependence_2025",
    "Low_Employment_2025",
    "Low_PostSecondary_Ed_2025",
    "Nonspecialized_2025",
    "Persistent_Poverty_1721",
    "Population_Loss_2025",
    "Retirement_Destination_2025"
  )
)

rucc_value_row_counts <- staging_rucc %>%
  dplyr::count(.data$attribute, name = "n")

expected_rucc_counts <- tibble::tribble(
  ~attribute, ~n_expected,
  "Description", 3235L,
  "Population_2020", 3235L,
  "RUCC_2023", 3233L
)

rucc_count_mismatches <- expected_rucc_counts %>%
  dplyr::left_join(rucc_value_row_counts, by = "attribute") %>%
  dplyr::mutate(n = dplyr::coalesce(.data$n, 0L)) %>%
  dplyr::filter(.data$n != .data$n_expected)

if (nrow(rucc_count_mismatches) > 0) {
  stop(
    glue("staging.usda_rucc row-count check failed for one or more attributes."),
    call. = FALSE
  )
}

if (dplyr::n_distinct(staging_rucc$fips) != 3235L) {
  stop("staging.usda_rucc does not contain the expected 3,235 distinct FIPS keys.", call. = FALSE)
}

if (dplyr::n_distinct(staging_typology$fips) != 3152L) {
  stop("staging.usda_county_typology does not contain the expected 3,152 distinct FIPS keys.", call. = FALSE)
}

rucc_missing_code_fips <- staging_rucc %>%
  dplyr::group_by(.data$fips) %>%
  dplyr::summarise(has_rucc_code = any(.data$attribute == "RUCC_2023"), .groups = "drop") %>%
  dplyr::filter(!.data$has_rucc_code) %>%
  dplyr::pull(.data$fips) %>%
  sort()

if (!identical(rucc_missing_code_fips, c("60030", "60040"))) {
  stop(
    glue(
      "staging.usda_rucc missing-code exception changed. Observed FIPS without RUCC_2023 rows: ",
      "{paste(rucc_missing_code_fips, collapse = ', ')}"
    ),
    call. = FALSE
  )
}

# 5. Load the staging tables ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "usda_rucc"),
  staging_rucc,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "usda_county_typology"),
  staging_typology,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
