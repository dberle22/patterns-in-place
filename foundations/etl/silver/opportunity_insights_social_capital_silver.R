# In this script we standardize the Opportunity Insights Social Capital Atlas
# into one static Silver table. County rows come from the county release, state
# and CBSA rows are derived from counties using population-weighted rollups, and
# ZCTA rows come directly from the ZIP release with the neighborhood-only fields
# preserved where the provider publishes them.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver;")

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

safe_weighted_mean <- function(x, w) {
  keep <- !is.na(x) & !is.na(w) & is.finite(x) & is.finite(w) & w > 0

  if (!any(keep)) {
    return(NA_real_)
  }

  stats::weighted.mean(x[keep], w[keep])
}

state_name_lookup <- tibble::tibble(
  state_abbr = c(state.abb, "DC"),
  state_name = c(state.name, "District of Columbia")
)

# 3. Read staging and geography helpers ----
county_stage <- DBI::dbGetQuery(
  con,
  "SELECT * FROM staging.opportunity_insights_social_capital_county"
) %>%
  mutate(
    county = as.character(.data$county),
    county_name = as.character(.data$county_name),
    pop2018 = as.double(.data$pop2018),
    num_below_p50 = as.double(.data$num_below_p50)
  )

zip_stage <- DBI::dbGetQuery(
  con,
  "SELECT * FROM staging.opportunity_insights_social_capital_zip"
) %>%
  mutate(
    zip = as.character(.data$zip),
    county = as.character(.data$county),
    pop2018 = as.double(.data$pop2018),
    num_below_p50 = as.double(.data$num_below_p50)
  )

county_lookup <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state") %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    county_name_long = as.character(.data$county_name_long),
    state_fips = as.character(.data$state_fip),
    state_abbr = as.character(.data$state_abbr)
  ) %>%
  distinct()

state_lookup <- county_lookup %>%
  distinct(.data$state_fips, .data$state_abbr) %>%
  left_join(state_name_lookup, by = "state_abbr")

population_weights <- DBI::dbGetQuery(
  con,
  "
  SELECT
    geo_id AS county_geoid,
    year,
    pop_total
  FROM silver.age_kpi
  WHERE geo_level = 'county'
    AND year = 2018
  "
) %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    total_population_weight = as.double(.data$pop_total)
  ) %>%
  distinct()

cbsa_lookup <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county") %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    cbsa_code = as.character(.data$cbsa_code),
    cbsa_name = as.character(.data$cbsa_name)
  ) %>%
  distinct()

# 4. Standardize county and ZCTA source-native rows ----
social_capital_county <- county_stage %>%
  left_join(county_lookup, by = c("county" = "county_geoid")) %>%
  left_join(population_weights, by = c("county" = "county_geoid")) %>%
  mutate(
    state_fips = dplyr::coalesce(.data$state_fips, stringr::str_sub(.data$county, 1, 2)),
    rollup_population = dplyr::coalesce(.data$pop2018, .data$total_population_weight)
  ) %>%
  transmute(
    geo_level = "county",
    geo_id = .data$county,
    geo_name = dplyr::coalesce(.data$county_name_long, .data$county_name),
    population_total = .data$pop2018,
    children_below_p50 = .data$num_below_p50,
    economic_connectedness = as.double(.data$ec_county),
    economic_connectedness_se = as.double(.data$ec_se_county),
    childhood_economic_connectedness = as.double(.data$child_ec_county),
    childhood_economic_connectedness_se = as.double(.data$child_ec_se_county),
    neighborhood_economic_connectedness = as.double(NA),
    economic_exposure = as.double(.data$exposure_grp_mem_county),
    childhood_economic_exposure = as.double(.data$child_exposure_county),
    neighborhood_economic_exposure = as.double(NA),
    friending_bias = as.double(.data$bias_grp_mem_county),
    childhood_friending_bias = as.double(.data$child_bias_county),
    neighborhood_friending_bias = as.double(NA),
    cohesion_clustering = as.double(.data$clustering_county),
    cohesion_support_ratio = as.double(.data$support_ratio_county),
    civic_engagement_volunteering_rate = as.double(.data$volunteering_rate_county),
    civic_organizations_per_1000 = as.double(.data$civic_organizations_county),
    state_fips = .data$state_fips,
    rollup_population = .data$rollup_population
  )

social_capital_zcta <- zip_stage %>%
  transmute(
    geo_level = "zcta",
    geo_id = .data$zip,
    geo_name = paste("ZCTA", .data$zip),
    population_total = .data$pop2018,
    children_below_p50 = .data$num_below_p50,
    economic_connectedness = as.double(.data$ec_zip),
    economic_connectedness_se = as.double(.data$ec_se_zip),
    childhood_economic_connectedness = as.double(NA),
    childhood_economic_connectedness_se = as.double(NA),
    neighborhood_economic_connectedness = as.double(.data$nbhd_ec_zip),
    economic_exposure = as.double(.data$exposure_grp_mem_zip),
    childhood_economic_exposure = as.double(NA),
    neighborhood_economic_exposure = as.double(.data$nbhd_exposure_zip),
    friending_bias = as.double(.data$bias_grp_mem_zip),
    childhood_friending_bias = as.double(NA),
    neighborhood_friending_bias = as.double(.data$nbhd_bias_zip),
    cohesion_clustering = as.double(.data$clustering_zip),
    cohesion_support_ratio = as.double(.data$support_ratio_zip),
    civic_engagement_volunteering_rate = as.double(.data$volunteering_rate_zip),
    civic_organizations_per_1000 = as.double(.data$civic_organizations_zip),
    state_fips = as.character(NA)
  )

# 5. Derive state and CBSA rollups from county rows ----
social_capital_state <- social_capital_county %>%
  inner_join(state_lookup, by = "state_fips") %>%
  group_by(.data$state_fips, .data$state_name) %>%
  summarise(
    geo_level = "state",
    geo_id = dplyr::first(.data$state_fips),
    geo_name = dplyr::first(.data$state_name),
    population_total = sum(.data$population_total, na.rm = TRUE),
    children_below_p50 = sum(.data$children_below_p50, na.rm = TRUE),
    economic_connectedness = safe_weighted_mean(.data$economic_connectedness, .data$rollup_population),
    economic_connectedness_se = as.double(NA),
    childhood_economic_connectedness = safe_weighted_mean(.data$childhood_economic_connectedness, .data$rollup_population),
    childhood_economic_connectedness_se = as.double(NA),
    neighborhood_economic_connectedness = as.double(NA),
    economic_exposure = safe_weighted_mean(.data$economic_exposure, .data$rollup_population),
    childhood_economic_exposure = safe_weighted_mean(.data$childhood_economic_exposure, .data$rollup_population),
    neighborhood_economic_exposure = as.double(NA),
    friending_bias = safe_weighted_mean(.data$friending_bias, .data$rollup_population),
    childhood_friending_bias = safe_weighted_mean(.data$childhood_friending_bias, .data$rollup_population),
    neighborhood_friending_bias = as.double(NA),
    cohesion_clustering = safe_weighted_mean(.data$cohesion_clustering, .data$rollup_population),
    cohesion_support_ratio = safe_weighted_mean(.data$cohesion_support_ratio, .data$rollup_population),
    civic_engagement_volunteering_rate = safe_weighted_mean(.data$civic_engagement_volunteering_rate, .data$rollup_population),
    civic_organizations_per_1000 = safe_weighted_mean(.data$civic_organizations_per_1000, .data$rollup_population),
    state_fips = dplyr::first(.data$state_fips),
    .groups = "drop"
  )

social_capital_cbsa <- social_capital_county %>%
  left_join(cbsa_lookup, by = c("geo_id" = "county_geoid")) %>%
  filter(!is.na(.data$cbsa_code), .data$cbsa_code != "") %>%
  group_by(.data$cbsa_code, .data$cbsa_name) %>%
  summarise(
    geo_level = "cbsa",
    geo_id = dplyr::first(.data$cbsa_code),
    geo_name = dplyr::first(.data$cbsa_name),
    population_total = sum(.data$population_total, na.rm = TRUE),
    children_below_p50 = sum(.data$children_below_p50, na.rm = TRUE),
    economic_connectedness = safe_weighted_mean(.data$economic_connectedness, .data$rollup_population),
    economic_connectedness_se = as.double(NA),
    childhood_economic_connectedness = safe_weighted_mean(.data$childhood_economic_connectedness, .data$rollup_population),
    childhood_economic_connectedness_se = as.double(NA),
    neighborhood_economic_connectedness = as.double(NA),
    economic_exposure = safe_weighted_mean(.data$economic_exposure, .data$rollup_population),
    childhood_economic_exposure = safe_weighted_mean(.data$childhood_economic_exposure, .data$rollup_population),
    neighborhood_economic_exposure = as.double(NA),
    friending_bias = safe_weighted_mean(.data$friending_bias, .data$rollup_population),
    childhood_friending_bias = safe_weighted_mean(.data$childhood_friending_bias, .data$rollup_population),
    neighborhood_friending_bias = as.double(NA),
    cohesion_clustering = safe_weighted_mean(.data$cohesion_clustering, .data$rollup_population),
    cohesion_support_ratio = safe_weighted_mean(.data$cohesion_support_ratio, .data$rollup_population),
    civic_engagement_volunteering_rate = safe_weighted_mean(.data$civic_engagement_volunteering_rate, .data$rollup_population),
    civic_organizations_per_1000 = safe_weighted_mean(.data$civic_organizations_per_1000, .data$rollup_population),
    state_fips = as.character(NA),
    .groups = "drop"
  )

# 6. Materialize the unified static Silver table ----
social_capital_silver <- bind_rows(
  social_capital_county %>%
    select(-state_fips, -rollup_population),
  social_capital_state,
  social_capital_cbsa,
  social_capital_zcta
) %>%
  select(
    geo_level,
    geo_id,
    geo_name,
    population_total,
    children_below_p50,
    economic_connectedness,
    economic_connectedness_se,
    childhood_economic_connectedness,
    childhood_economic_connectedness_se,
    neighborhood_economic_connectedness,
    economic_exposure,
    childhood_economic_exposure,
    neighborhood_economic_exposure,
    friending_bias,
    childhood_friending_bias,
    neighborhood_friending_bias,
    cohesion_clustering,
    cohesion_support_ratio,
    civic_engagement_volunteering_rate,
    civic_organizations_per_1000
  ) %>%
  arrange(.data$geo_level, .data$geo_id)

check_unique_grain(social_capital_silver, "silver.opportunity_insights_social_capital")

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "opportunity_insights_social_capital"),
  social_capital_silver,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
