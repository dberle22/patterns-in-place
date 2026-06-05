# In this script we standardize FHFA underserved tract flags into a full tract
# backbone for the current release year. The first-pass Silver contract is
# tract-only, so this script keeps the tract booleans and stops there.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Helpers ----
check_unique_grain <- function(df, table_name) {
  dupes <- df %>%
    count(.data$geo_level, .data$geo_id, .data$year, name = "row_count") %>%
    filter(.data$row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf("%s has duplicate geo_level + geo_id + year rows", table_name),
      call. = FALSE
    )
  }
}

# 3. Read staging and crosswalks ----
fhfa_stage <- DBI::dbGetQuery(con, "SELECT * FROM staging.fhfa_underserved") %>%
  transmute(
    tract_geoid = as.character(.data$tract_geoid),
    year = as.integer(.data$year),
    is_underserved = as.logical(.data$is_underserved),
    is_low_income_area = as.logical(.data$is_low_income_area),
    is_minority_area = as.logical(.data$is_minority_area),
    is_disaster_area = as.logical(.data$is_disaster_area)
  )

tract_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_tract_county") %>%
  transmute(
    tract_geoid = as.character(.data$tract_geoid),
    tract_name = as.character(.data$tract_name_long)
  ) %>%
  distinct()

release_year <- fhfa_stage %>%
  distinct(.data$year) %>%
  pull(.data$year)

if (length(release_year) != 1) {
  stop("staging.fhfa_underserved should contain exactly one release year in the first-pass contract.", call. = FALSE)
}

# 4. Build the tract backbone ----
fhfa_backbone <- tract_xwalk %>%
  left_join(fhfa_stage, by = "tract_geoid") %>%
  mutate(
    year = dplyr::coalesce(.data$year, release_year),
    is_underserved = dplyr::coalesce(.data$is_underserved, FALSE),
    is_low_income_area = dplyr::coalesce(.data$is_low_income_area, FALSE),
    is_minority_area = dplyr::coalesce(.data$is_minority_area, FALSE),
    is_disaster_area = dplyr::coalesce(.data$is_disaster_area, FALSE)
  )

fhfa_silver <- fhfa_backbone %>%
  transmute(
    geo_level = "tract",
    geo_id = .data$tract_geoid,
    geo_name = .data$tract_name,
    year = .data$year,
    is_underserved = .data$is_underserved,
    is_low_income_area = .data$is_low_income_area,
    is_minority_area = .data$is_minority_area,
    is_disaster_area = .data$is_disaster_area,
    underserved_tract_count = as.integer(.data$is_underserved),
    total_tract_count = 1L,
    pct_underserved_tracts = if_else(.data$is_underserved, 1, 0)
  ) %>%
  arrange(.data$geo_level, .data$geo_id, .data$year)

check_unique_grain(fhfa_silver, "silver.fhfa_underserved")

# 5. Materialize to Silver ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "fhfa_underserved"),
  fhfa_silver,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
