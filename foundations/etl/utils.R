# Load Packages and Functions for the section

# Packages ----
library(tidyverse)
library(janitor)
library(readr)
library(lubridate)
library(glue)
library(scales)
library(sf)
library(tigris)
library(stringr)
library(fmsb)
library(patchwork)
library(viridis)
library(ggrepel)
library(tidycensus)
library(readxl)
library(bea.R)
library(here)
library(DBI)
library(blob)
library(spatial)
library(gt)

# Reproducibility ----
set.seed(42)

# Set the Working Directory

# Load Functions from R Scripts
source(here::here("foundations", "etl", "R", "add_growth_cols.R"))
source(here::here("foundations", "etl", "R", "benchmark_summary.R"))
source(here::here("foundations", "etl", "R", "generic_functions.R"))
source(here::here("foundations", "etl", "R", "rebase_cbsa_from_counties.R"))
source(here::here("foundations", "etl", "R", "acs_ingest.R"))
source(here::here("foundations", "etl", "R", "standardize_acs_df.R"))

# Load user-level Renviron first (e.g. API keys)
user_renv <- file.path(path.expand("~"), ".Renviron")
if (file.exists(user_renv)) {
  readRenviron(user_renv)
}

# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")


# Reusable tract state scope helper
resolve_tract_state_scope <- function(env_var = "ROF_TRACT_STATE_SCOPE") {
  raw_value <- Sys.getenv(env_var, unset = "")
  if (!nzchar(raw_value)) {
    return(c(state.abb, "DC"))
  }

  states <- raw_value %>%
    stringr::str_split(",") %>%
    purrr::pluck(1) %>%
    stringr::str_trim() %>%
    toupper() %>%
    unique()

  valid_states <- c(state.abb, "DC")
  invalid_states <- setdiff(states, valid_states)
  if (length(invalid_states) > 0) {
    stop(
      sprintf(
        "Invalid %s values: %s",
        env_var,
        paste(invalid_states, collapse = ", ")
      ),
      call. = FALSE
    )
  }

  states
}

get_ct_legacy_county_lookup <- function() {
  tibble::tribble(
    ~county_geoid, ~county_name, ~county_name_long,
    "09001", "Fairfield", "Fairfield County, Connecticut",
    "09003", "Hartford", "Hartford County, Connecticut",
    "09005", "Litchfield", "Litchfield County, Connecticut",
    "09007", "Middlesex", "Middlesex County, Connecticut",
    "09009", "New Haven", "New Haven County, Connecticut",
    "09011", "New London", "New London County, Connecticut",
    "09013", "Tolland", "Tolland County, Connecticut",
    "09015", "Windham", "Windham County, Connecticut"
  )
}

get_ct_current_cbsa_lookup <- function() {
  tibble::tribble(
    ~cbsa_code, ~cbsa_name,
    "14860", "Bridgeport-Stamford-Danbury, CT",
    "25540", "Hartford-West Hartford-East Hartford, CT",
    "35300", "New Haven, CT",
    "35980", "Norwich-New London-Willimantic, CT",
    "39480", "Putnam, CT",
    "45860", "Torrington, CT",
    "47930", "Waterbury-Shelton, CT"
  )
}

get_ct_legacy_county_cbsa_bridge <- function() {
  # This bridge is only for county-native legacy CT sources that still publish
  # the retired eight-county GEOIDs. Split counties use the dominant current
  # CT county-equivalent so we can materialize current-key CBSA rows without
  # duplicating one legacy county into multiple metros.
  tibble::tribble(
    ~county_geoid, ~cbsa_code,
    "09001", "14860",
    "09003", "25540",
    "09005", "45860",
    "09007", "25540",
    "09009", "35300",
    "09011", "35980",
    "09013", "25540",
    "09015", "39480"
  ) %>%
    dplyr::left_join(get_ct_legacy_county_lookup(), by = "county_geoid") %>%
    dplyr::left_join(get_ct_current_cbsa_lookup(), by = "cbsa_code") %>%
    dplyr::transmute(
      county_geoid = .data$county_geoid,
      county_name = .data$county_name,
      county_flag = "Legacy CT dominant bridge",
      cbsa_code = .data$cbsa_code,
      cbsa_name = .data$cbsa_name,
      cbsa_type = dplyr::if_else(.data$cbsa_code %in% c("39480", "45860"), "Micropolitan Statistical Area", "Metropolitan Statistical Area"),
      csa_code = NA_character_,
      csa_name = NA_character_,
      state_name = "Connecticut",
      state_fips = "09",
      county_fips = stringr::str_sub(.data$county_geoid, 3, 5),
      vintage = 2023L,
      source = "CT_LEGACY_COUNTY_DOMINANT_CBSA_BRIDGE"
    )
}

get_cbsa_rollup_xwalk <- function(con) {
  current_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county") %>%
    dplyr::mutate(
      dplyr::across(
        c("cbsa_code", "cbsa_name", "county_geoid", "county_name", "county_flag", "cbsa_type", "csa_code", "csa_name", "state_name", "state_fips", "county_fips", "source"),
        as.character
      ),
      vintage = as.integer(.data$vintage)
    )

  dplyr::bind_rows(
    current_xwalk,
    get_ct_legacy_county_cbsa_bridge()
  ) %>%
    dplyr::distinct(.data$county_geoid, .data$cbsa_code, .keep_all = TRUE)
}

harmonize_ct_cbsa_names <- function(df, code_col = "cbsa_code", name_col = "cbsa_name") {
  code_sym <- rlang::sym(code_col)
  name_sym <- rlang::sym(name_col)

  df %>%
    dplyr::mutate(
      !!name_sym := dplyr::case_when(
        .data[[code_col]] == "14860" ~ "Bridgeport-Stamford-Danbury, CT",
        .data[[code_col]] == "25540" ~ "Hartford-West Hartford-East Hartford, CT",
        .data[[code_col]] == "35300" ~ "New Haven, CT",
        .data[[code_col]] == "35980" ~ "Norwich-New London-Willimantic, CT",
        .data[[code_col]] == "39480" ~ "Putnam, CT",
        .data[[code_col]] == "45860" ~ "Torrington, CT",
        .data[[code_col]] == "47930" ~ "Waterbury-Shelton, CT",
        TRUE ~ as.character(!!name_sym)
      )
    )
}
