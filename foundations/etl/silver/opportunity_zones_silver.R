# In this script we standardize the static Opportunity Zones allowlist into a
# full tract backbone, then derive county and CBSA overlays from the tract
# designations plus the latest tract population snapshot.

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

safe_ratio <- function(num, den) {
  if (is.na(den) || den <= 0) {
    return(NA_real_)
  }

  num / den
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
    tract_name = as.character(.data$tract_name_long),
    county_geoid = stringr::str_sub(as.character(.data$tract_geoid), 1, 5)
  ) %>%
  distinct()

county_lookup <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state") %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    county_name = as.character(.data$county_name_long)
  ) %>%
  distinct()

cbsa_lookup <- get_cbsa_rollup_xwalk(con) %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    cbsa_code = as.character(.data$cbsa_code),
    cbsa_name = as.character(.data$cbsa_name)
  ) %>%
  distinct()

latest_population_year <- DBI::dbGetQuery(
  con,
  "
  SELECT MAX(year) AS year
  FROM silver.age_kpi
  WHERE geo_level = 'tract'
  "
) %>%
  pull(.data$year)

tract_population <- DBI::dbGetQuery(
  con,
  sprintf(
    "
    SELECT
      geo_id AS tract_geoid,
      pop_total
    FROM silver.age_kpi
    WHERE geo_level = 'tract'
      AND year = %s
    ",
    latest_population_year
  )
) %>%
  transmute(
    tract_geoid = as.character(.data$tract_geoid),
    total_population = as.double(.data$pop_total)
  ) %>%
  distinct()

# 4. Build the tract backbone ----
oz_backbone <- tract_xwalk %>%
  left_join(oz_stage, by = "tract_geoid") %>%
  left_join(tract_population, by = "tract_geoid") %>%
  mutate(
    is_opportunity_zone = dplyr::coalesce(.data$is_opportunity_zone, FALSE)
  ) %>%
  mutate(
    oz_flag = dplyr::if_else(.data$is_opportunity_zone, 1L, 0L),
    oz_population_component = dplyr::if_else(.data$is_opportunity_zone, dplyr::coalesce(.data$total_population, 0), 0)
  )

oz_tract <- oz_backbone %>%
  transmute(
    geo_level = "tract",
    geo_id = .data$tract_geoid,
    geo_name = .data$tract_name,
    is_opportunity_zone = .data$is_opportunity_zone,
    oz_tract_count = .data$oz_flag,
    total_tract_count = 1L,
    pct_oz_tracts = if_else(.data$is_opportunity_zone, 1, 0),
    oz_population = if_else(.data$is_opportunity_zone, .data$total_population, 0),
    total_population = .data$total_population,
    pct_population_in_oz = purrr::map2_dbl(.data$oz_population, .data$total_population, safe_ratio)
  )

oz_county <- oz_backbone %>%
  left_join(county_lookup, by = "county_geoid") %>%
  group_by(.data$county_geoid, .data$county_name) %>%
  summarise(
    geo_level = "county",
    geo_id = dplyr::first(.data$county_geoid),
    geo_name = dplyr::first(.data$county_name),
    is_opportunity_zone = as.logical(NA),
    oz_tract_count = sum(.data$oz_flag, na.rm = TRUE),
    total_tract_count = dplyr::n(),
    oz_population = sum(.data$oz_population_component, na.rm = TRUE),
    total_population = sum(.data$total_population, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(
    pct_oz_tracts = purrr::map2_dbl(.data$oz_tract_count, .data$total_tract_count, safe_ratio),
    pct_population_in_oz = purrr::map2_dbl(.data$oz_population, .data$total_population, safe_ratio)
  )

oz_cbsa <- oz_backbone %>%
  inner_join(cbsa_lookup, by = "county_geoid") %>%
  group_by(.data$cbsa_code, .data$cbsa_name) %>%
  summarise(
    geo_level = "cbsa",
    geo_id = dplyr::first(.data$cbsa_code),
    geo_name = dplyr::first(.data$cbsa_name),
    is_opportunity_zone = as.logical(NA),
    oz_tract_count = sum(.data$oz_flag, na.rm = TRUE),
    total_tract_count = dplyr::n(),
    oz_population = sum(.data$oz_population_component, na.rm = TRUE),
    total_population = sum(.data$total_population, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(
    pct_oz_tracts = purrr::map2_dbl(.data$oz_tract_count, .data$total_tract_count, safe_ratio),
    pct_population_in_oz = purrr::map2_dbl(.data$oz_population, .data$total_population, safe_ratio)
  )

oz_silver <- bind_rows(
  oz_tract,
  oz_county,
  oz_cbsa
) %>%
  select(
    geo_level,
    geo_id,
    geo_name,
    is_opportunity_zone,
    oz_tract_count,
    total_tract_count,
    pct_oz_tracts,
    oz_population,
    total_population,
    pct_population_in_oz
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
