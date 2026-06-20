# Shared utilities for Intelligence Framework analysis notebooks.
# Source this at the top of every phase notebook:
#   source(here::here("exploration/intelligence_framework/R/utils.R"))

library(DBI)
library(duckdb)
library(dplyr)
library(ggplot2)
library(scales)
library(here)

# Visual standards from the shared library
source(here("foundations/visual_library/shared/standards.R"))

# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------

db_connect <- function(read_only = TRUE) {
  dbConnect(duckdb(), Sys.getenv("DB_PATH"), read_only = read_only)
}

# ---------------------------------------------------------------------------
# Standard CBSA spine
# Filters to CBSAs with population >= 100k in the reference year.
# Returns geo_id, geo_name, pop_total — suitable for joining to any Gold table.
# ---------------------------------------------------------------------------

get_cbsa_spine <- function(con, min_pop = 100000, year = 2024) {
  dbGetQuery(con, glue::glue("
    SELECT
      geo_id,
      geo_name,
      pop_total,
      year
    FROM gold.population_demographics
    WHERE geo_level = 'cbsa'
      AND year = {year}
      AND pop_total >= {min_pop}
    ORDER BY pop_total DESC
  "))
}

# ---------------------------------------------------------------------------
# Coverage note helper
# Prints a one-line note on how many spine CBSAs have data in a given table.
# Call after joining spine to a data frame to document partial source coverage.
# ---------------------------------------------------------------------------

coverage_note <- function(joined_df, spine_df, label = "source") {
  n_spine  <- nrow(spine_df)
  n_joined <- sum(!is.na(joined_df[[names(joined_df)[3]]]))  # first non-key column
  pct      <- round(100 * n_joined / n_spine, 1)
  message(sprintf("[coverage] %s: %d / %d CBSAs (%.1f%%)", label, n_joined, n_spine, pct))
}
