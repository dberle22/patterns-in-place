# In this script we land a compact, analysis-ready subset of the EPA Smart
# Location Database directly from EPA's published CSV. The source file is wide,
# but our first-pass staging contract only keeps the geography backbone and the
# high-signal built-form and accessibility measures we approved for Track 9.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "transportation", "raw", "epa", "sld")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the current EPA release ----
sld_vintage_year <- 2021L
sld_csv_name <- "EPA_SmartLocationDatabase_V3_Jan_2021_Final.csv"
sld_csv_url <- glue("https://edg.epa.gov/data/Public/OA/{sld_csv_name}")
sld_csv_path <- file.path(raw_dir, sld_csv_name)

download_epa_sld_csv <- function(url, dest_path) {
  if (file.exists(dest_path)) {
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

read_epa_sld_csv <- function(csv_path) {
  readr::read_csv(
    csv_path,
    col_types = readr::cols(
      GEOID10 = readr::col_character(),
      GEOID20 = readr::col_character(),
      STATEFP = readr::col_character(),
      COUNTYFP = readr::col_character(),
      TRACTCE = readr::col_character(),
      BLKGRPCE = readr::col_character(),
      CBSA = readr::col_character(),
      CBSA_Name = readr::col_character(),
      TotPop = readr::col_double(),
      TotEmp = readr::col_double(),
      CountHU = readr::col_double(),
      HH = readr::col_double(),
      Ac_Unpr = readr::col_double(),
      NatWalkInd = readr::col_double(),
      D2A_EPHHM = readr::col_double(),
      D2B_E8MIXA = readr::col_double(),
      D3B = readr::col_double(),
      D3AAO = readr::col_double(),
      D4B025 = readr::col_double(),
      D4D = readr::col_double(),
      D4E = readr::col_double(),
      D5AR = readr::col_double(),
      D5AE = readr::col_double(),
      D5BR = readr::col_double(),
      D5BE = readr::col_double(),
      D1C = readr::col_double(),
      D1B = readr::col_double(),
      D1A = readr::col_double(),
      .default = readr::col_skip()
    ),
    show_col_types = FALSE,
    progress = FALSE
  ) %>%
    janitor::clean_names()
}

normalize_epa_sld <- function(df) {
  # EPA's CSV writes both GEOID10 and GEOID20 in scientific notation, which
  # makes them unusable as stable join keys. The component geography fields are
  # still intact, so we rebuild the canonical 12-digit block-group GEOID from
  # those parts and keep the raw GEOID strings only as provenance helpers.
  df %>%
    transmute(
      year = sld_vintage_year,
      state_fips = stringr::str_pad(.data$statefp, width = 2, side = "left", pad = "0"),
      county_fips = stringr::str_pad(.data$countyfp, width = 3, side = "left", pad = "0"),
      tract_code = stringr::str_pad(.data$tractce, width = 6, side = "left", pad = "0"),
      block_group_code = stringr::str_pad(.data$blkgrpce, width = 1, side = "left", pad = "0"),
      bg_geoid = paste0(.data$state_fips, .data$county_fips, .data$tract_code, .data$block_group_code),
      bg_geoid_2020 = paste0(.data$state_fips, .data$county_fips, .data$tract_code, .data$block_group_code),
      source_geoid10_raw = .data$geoid10,
      source_geoid20_raw = .data$geoid20,
      cbsa_code = dplyr::if_else(
        is.na(.data$cbsa) | .data$cbsa == "",
        NA_character_,
        stringr::str_pad(.data$cbsa, width = 5, side = "left", pad = "0")
      ),
      cbsa_name = dplyr::if_else(
        is.na(.data$cbsa_name) | .data$cbsa_name == "",
        NA_character_,
        stringr::str_squish(iconv(.data$cbsa_name, from = "", to = "UTF-8", sub = ""))
      ),
      total_population = .data$tot_pop,
      total_employment = .data$tot_emp,
      housing_units = .data$count_hu,
      households = .data$hh,
      land_acres_unprotected = .data$ac_unpr,
      walkability_index = .data$nat_walk_ind,
      employment_housing_mix = .data$d2a_ephhm,
      employment_mix = .data$d2b_e8mixa,
      street_intersection_density = .data$d3b,
      auto_oriented_intersection_share = .data$d3aao,
      transit_service_density = .data$d4b025,
      transit_frequency_peak = .data$d4d,
      distance_to_transit = .data$d4e,
      jobs_access_45min_transit = .data$d5ar,
      workers_access_45min_transit = .data$d5ae,
      jobs_access_45min_auto = .data$d5br,
      workers_access_45min_auto = .data$d5be,
      employment_density_gross = .data$d1c,
      population_density_gross = .data$d1b,
      housing_density_gross = .data$d1a
    )
}

# 3. Download and normalize the current EPA release ----
download_epa_sld_csv(sld_csv_url, sld_csv_path)

epa_sld_staging <- read_epa_sld_csv(sld_csv_path) %>%
  normalize_epa_sld()

# 4. Contract checks ----
invalid_bg_rows <- epa_sld_staging %>%
  filter(is.na(.data$bg_geoid) | !stringr::str_detect(.data$bg_geoid, "^\\d{12}$"))

if (nrow(invalid_bg_rows) > 0) {
  stop(
    glue("EPA SLD staging contains {nrow(invalid_bg_rows)} rows with invalid 12-digit block-group GEOIDs."),
    call. = FALSE
  )
}

invalid_state_rows <- epa_sld_staging %>%
  filter(is.na(.data$state_fips) | !stringr::str_detect(.data$state_fips, "^\\d{2}$"))

if (nrow(invalid_state_rows) > 0) {
  stop(
    glue("EPA SLD staging contains {nrow(invalid_state_rows)} rows with invalid state FIPS values."),
    call. = FALSE
  )
}

invalid_county_rows <- epa_sld_staging %>%
  filter(is.na(.data$county_fips) | !stringr::str_detect(.data$county_fips, "^\\d{3}$"))

if (nrow(invalid_county_rows) > 0) {
  stop(
    glue("EPA SLD staging contains {nrow(invalid_county_rows)} rows with invalid county FIPS values."),
    call. = FALSE
  )
}

invalid_tract_rows <- epa_sld_staging %>%
  filter(is.na(.data$tract_code) | !stringr::str_detect(.data$tract_code, "^\\d{6}$"))

if (nrow(invalid_tract_rows) > 0) {
  stop(
    glue("EPA SLD staging contains {nrow(invalid_tract_rows)} rows with invalid tract codes."),
    call. = FALSE
  )
}

duplicate_rows <- epa_sld_staging %>%
  count(.data$bg_geoid, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_rows) > 0) {
  stop(
    glue("EPA SLD staging is not unique at bg_geoid. Duplicate keys found: {nrow(duplicate_rows)}"),
    call. = FALSE
  )
}

# 5. Load the normalized SLD staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "epa_sld"),
  epa_sld_staging,
  overwrite = TRUE
)
