# In this script we keep the USDA Food Access Research Atlas tract-native in
# Silver and then derive county and CBSA rollups from the tract keys. County
# rollups come directly from the first 5 digits of the tract GEOID, which lets
# us avoid unnecessary tract-vintage joins for the main food-desert measures.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Helpers ----
check_unique_annual_grain <- function(df, table_name) {
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

safe_ratio <- function(num, den) {
  if (is.na(den) || den <= 0) {
    return(NA_real_)
  }

  num / den
}

safe_weighted_mean <- function(x, w) {
  keep <- !is.na(x) & !is.na(w) & is.finite(x) & is.finite(w) & w > 0

  if (!any(keep)) {
    return(NA_real_)
  }

  stats::weighted.mean(x[keep], w[keep])
}

unsupported_county_geoids <- c(
  "02261"
)

# 3. Read staging and crosswalk helpers ----
food_stage <- DBI::dbGetQuery(con, "SELECT * FROM staging.usda_food_atlas") %>%
  mutate(
    year = as.integer(.data$year),
    tract_geoid = as.character(.data$tract_geoid),
    county_geoid = stringr::str_sub(.data$tract_geoid, 1, 5)
  )

county_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state") %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    county_name_long = as.character(.data$county_name_long)
  ) %>%
  distinct()

county_manual_lookup <- tibble::tribble(
  ~county_geoid, ~county_name_long,
  "09001", "Fairfield County, Connecticut",
  "09003", "Hartford County, Connecticut",
  "09005", "Litchfield County, Connecticut",
  "09007", "Middlesex County, Connecticut",
  "09009", "New Haven County, Connecticut",
  "09011", "New London County, Connecticut",
  "09013", "Tolland County, Connecticut",
  "09015", "Windham County, Connecticut"
)

county_lookup <- county_xwalk %>%
  select("county_geoid", "county_name_long") %>%
  bind_rows(county_manual_lookup) %>%
  distinct(.data$county_geoid, .keep_all = TRUE)

cbsa_xwalk <- get_cbsa_rollup_xwalk(con) %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    cbsa_code = as.character(.data$cbsa_code),
    cbsa_name = as.character(.data$cbsa_name)
  ) %>%
  distinct()

tract_cbsa_xwalk <- food_stage %>%
  distinct(.data$tract_geoid) %>%
  transmute(
    tract_geoid = as.character(.data$tract_geoid),
    county_geoid = stringr::str_sub(.data$tract_geoid, 1, 5)
  ) %>%
  inner_join(cbsa_xwalk, by = "county_geoid") %>%
  distinct(.data$tract_geoid, .keep_all = TRUE)

# 4. Audit county coverage before rollups ----
county_match_audit <- food_stage %>%
  distinct(.data$county_geoid) %>%
  left_join(
    county_lookup %>% transmute(county_geoid, in_xwalk = TRUE),
    by = "county_geoid"
  ) %>%
  mutate(in_xwalk = dplyr::coalesce(.data$in_xwalk, FALSE))

unmatched_counties <- county_match_audit %>%
  filter(!.data$in_xwalk, !.data$county_geoid %in% unsupported_county_geoids)

if (nrow(unmatched_counties) > 0) {
  stop(
    sprintf(
      paste(
        "USDA Food Atlas county coverage audit failed.",
        "%s county GEOIDs derived from tract keys did not resolve to silver.xwalk_county_state."
      ),
      nrow(unmatched_counties)
    ),
    call. = FALSE
  )
}

# 5. Standardize tract rows ----
food_tract <- food_stage %>%
  transmute(
    geo_level = "tract",
    geo_id = .data$tract_geoid,
    geo_name = paste("Census Tract", .data$census_tract_label),
    year = .data$year,
    population_total = .data$population_total,
    population_low_access_1 = .data$low_access_pop_1,
    population_low_access_1_10 = .data$low_access_pop_1_10,
    population_low_income_low_access_1 = .data$low_access_low_income_pop_1,
    population_low_income_low_access_1_10 = .data$low_access_low_income_pop_1_10,
    total_tract_count = 1L,
    lila_tract_count_1_10 = dplyr::coalesce(.data$lila_1_and_10_flag, 0L),
    low_income_tract_count = dplyr::coalesce(.data$low_income_flag, 0L),
    low_access_tract_count_1_10 = dplyr::coalesce(.data$low_access_1_and_10_flag, 0L),
    pct_lila_tracts_1_and_10 = as.double(dplyr::coalesce(.data$lila_1_and_10_flag, 0L)),
    pct_low_income_tracts = as.double(dplyr::coalesce(.data$low_income_flag, 0L)),
    pct_low_access_tracts_1_and_10 = as.double(dplyr::coalesce(.data$low_access_1_and_10_flag, 0L)),
    pct_population_low_access_1 = purrr::map2_dbl(.data$low_access_pop_1, .data$population_total, safe_ratio),
    pct_population_low_access_1_10 = purrr::map2_dbl(.data$low_access_pop_1_10, .data$population_total, safe_ratio),
    pct_population_low_income_low_access_1 = purrr::map2_dbl(.data$low_access_low_income_pop_1, .data$population_total, safe_ratio),
    pct_population_low_income_low_access_1_10 = purrr::map2_dbl(.data$low_access_low_income_pop_1_10, .data$population_total, safe_ratio),
    poverty_rate = .data$poverty_rate,
    median_family_income = .data$median_family_income
  )

# 6. Aggregate tract rows to counties ----
food_county <- food_stage %>%
  filter(!.data$county_geoid %in% unsupported_county_geoids) %>%
  left_join(
    county_xwalk %>% rename(xwalk_county_name_long = county_name_long),
    by = "county_geoid"
  ) %>%
  left_join(
    county_manual_lookup %>% rename(manual_county_name_long = county_name_long),
    by = "county_geoid"
  ) %>%
  group_by(.data$county_geoid, .data$year) %>%
  summarise(
    geo_level = "county",
    geo_id = dplyr::first(.data$county_geoid),
    geo_name = dplyr::first(dplyr::coalesce(.data$xwalk_county_name_long, .data$manual_county_name_long)),
    population_total = sum(.data$population_total, na.rm = TRUE),
    population_low_access_1 = sum(.data$low_access_pop_1, na.rm = TRUE),
    population_low_access_1_10 = sum(.data$low_access_pop_1_10, na.rm = TRUE),
    population_low_income_low_access_1 = sum(.data$low_access_low_income_pop_1, na.rm = TRUE),
    population_low_income_low_access_1_10 = sum(.data$low_access_low_income_pop_1_10, na.rm = TRUE),
    total_tract_count = dplyr::n(),
    lila_tract_count_1_10 = sum(dplyr::coalesce(.data$lila_1_and_10_flag, 0L), na.rm = TRUE),
    low_income_tract_count = sum(dplyr::coalesce(.data$low_income_flag, 0L), na.rm = TRUE),
    low_access_tract_count_1_10 = sum(dplyr::coalesce(.data$low_access_1_and_10_flag, 0L), na.rm = TRUE),
    poverty_rate = safe_weighted_mean(.data$poverty_rate, .data$population_total),
    median_family_income = safe_weighted_mean(.data$median_family_income, .data$population_total),
    .groups = "drop"
  ) %>%
  mutate(
    pct_lila_tracts_1_and_10 = purrr::map2_dbl(.data$lila_tract_count_1_10, .data$total_tract_count, safe_ratio),
    pct_low_income_tracts = purrr::map2_dbl(.data$low_income_tract_count, .data$total_tract_count, safe_ratio),
    pct_low_access_tracts_1_and_10 = purrr::map2_dbl(.data$low_access_tract_count_1_10, .data$total_tract_count, safe_ratio),
    pct_population_low_access_1 = purrr::map2_dbl(.data$population_low_access_1, .data$population_total, safe_ratio),
    pct_population_low_access_1_10 = purrr::map2_dbl(.data$population_low_access_1_10, .data$population_total, safe_ratio),
    pct_population_low_income_low_access_1 = purrr::map2_dbl(.data$population_low_income_low_access_1, .data$population_total, safe_ratio),
    pct_population_low_income_low_access_1_10 = purrr::map2_dbl(.data$population_low_income_low_access_1_10, .data$population_total, safe_ratio)
  )

# 7. Aggregate counties to CBSAs ----
food_cbsa <- food_tract %>%
  inner_join(tract_cbsa_xwalk, by = c("geo_id" = "tract_geoid")) %>%
  group_by(.data$cbsa_code, .data$cbsa_name, .data$year) %>%
  summarise(
    geo_level = "cbsa",
    geo_id = dplyr::first(.data$cbsa_code),
    geo_name = dplyr::first(.data$cbsa_name),
    population_total = sum(.data$population_total, na.rm = TRUE),
    population_low_access_1 = sum(.data$population_low_access_1, na.rm = TRUE),
    population_low_access_1_10 = sum(.data$population_low_access_1_10, na.rm = TRUE),
    population_low_income_low_access_1 = sum(.data$population_low_income_low_access_1, na.rm = TRUE),
    population_low_income_low_access_1_10 = sum(.data$population_low_income_low_access_1_10, na.rm = TRUE),
    total_tract_count = sum(.data$total_tract_count, na.rm = TRUE),
    lila_tract_count_1_10 = sum(.data$lila_tract_count_1_10, na.rm = TRUE),
    low_income_tract_count = sum(.data$low_income_tract_count, na.rm = TRUE),
    low_access_tract_count_1_10 = sum(.data$low_access_tract_count_1_10, na.rm = TRUE),
    poverty_rate = safe_weighted_mean(.data$poverty_rate, .data$population_total),
    median_family_income = safe_weighted_mean(.data$median_family_income, .data$population_total),
    .groups = "drop"
  ) %>%
  mutate(
    pct_lila_tracts_1_and_10 = purrr::map2_dbl(.data$lila_tract_count_1_10, .data$total_tract_count, safe_ratio),
    pct_low_income_tracts = purrr::map2_dbl(.data$low_income_tract_count, .data$total_tract_count, safe_ratio),
    pct_low_access_tracts_1_and_10 = purrr::map2_dbl(.data$low_access_tract_count_1_10, .data$total_tract_count, safe_ratio),
    pct_population_low_access_1 = purrr::map2_dbl(.data$population_low_access_1, .data$population_total, safe_ratio),
    pct_population_low_access_1_10 = purrr::map2_dbl(.data$population_low_access_1_10, .data$population_total, safe_ratio),
    pct_population_low_income_low_access_1 = purrr::map2_dbl(.data$population_low_income_low_access_1, .data$population_total, safe_ratio),
    pct_population_low_income_low_access_1_10 = purrr::map2_dbl(.data$population_low_income_low_access_1_10, .data$population_total, safe_ratio)
  )

# 8. Materialize unified Silver table ----
food_silver <- bind_rows(
  food_tract,
  food_county,
  food_cbsa
) %>%
  select(
    geo_level,
    geo_id,
    geo_name,
    year,
    population_total,
    population_low_access_1,
    population_low_access_1_10,
    population_low_income_low_access_1,
    population_low_income_low_access_1_10,
    total_tract_count,
    lila_tract_count_1_10,
    low_income_tract_count,
    low_access_tract_count_1_10,
    pct_lila_tracts_1_and_10,
    pct_low_income_tracts,
    pct_low_access_tracts_1_and_10,
    pct_population_low_access_1,
    pct_population_low_access_1_10,
    pct_population_low_income_low_access_1,
    pct_population_low_income_low_access_1_10,
    poverty_rate,
    median_family_income
  ) %>%
  arrange(.data$geo_level, .data$geo_id, .data$year)

check_unique_annual_grain(food_silver, "silver.usda_food_atlas")

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "usda_food_atlas"),
  food_silver,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
