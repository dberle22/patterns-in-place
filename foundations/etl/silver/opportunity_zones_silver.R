# In this script we standardize the static Opportunity Zones allowlist into a
# full tract backbone. The first-pass Silver contract is tract-only, so this
# script stops after applying the designation flag to every tract in the spine.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Helpers ----
check_unique_grain <- function(df, table_name) {
  dupes <- df %>%
    count(.data$geo_level, .data$geo_id, name = "row_count") %>%
    filter(.data$row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf("%s has duplicate geo_level + geo_id rows", table_name),
      call. = FALSE
    )
  }
}

# 3. Read staging and crosswalks ----
oz_stage <- DBI::dbGetQuery(con, "SELECT * FROM staging.opportunity_zones") %>%
  transmute(
    tract_geoid = as.character(.data$tract_geoid),
    is_opportunity_zone = as.logical(.data$is_opportunity_zone)
  ) %>%
  distinct()

tract_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_tract_county") %>%
  transmute(
    tract_geoid = as.character(.data$tract_geoid),
    tract_name = as.character(.data$tract_name_long)
  ) %>%
  distinct()

# 4. Build the tract backbone ----
oz_backbone <- tract_xwalk %>%
  left_join(oz_stage, by = "tract_geoid") %>%
  mutate(
    is_opportunity_zone = dplyr::coalesce(.data$is_opportunity_zone, FALSE)
  )

oz_silver <- oz_backbone %>%
  transmute(
    geo_level = "tract",
    geo_id = .data$tract_geoid,
    geo_name = .data$tract_name,
    is_opportunity_zone = .data$is_opportunity_zone,
    oz_tract_count = as.integer(.data$is_opportunity_zone),
    total_tract_count = 1L,
    pct_oz_tracts = if_else(.data$is_opportunity_zone, 1, 0)
  ) %>%
  arrange(.data$geo_level, .data$geo_id)

check_unique_grain(oz_silver, "silver.opportunity_zones")

# 5. Materialize to Silver ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "opportunity_zones"),
  oz_silver,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
