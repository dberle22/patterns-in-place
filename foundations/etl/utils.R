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
