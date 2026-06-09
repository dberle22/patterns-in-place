# In this script we aggregate block-group EPA Smart Location Database staging
# rows into a county-only analytical Silver table. We recompute densities from
# summed numerators and denominators where we can do so exactly, and use
# documented weighted means for the remaining index-like and accessibility
# measures.

getwd()

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
    count(geo_level, geo_id, year, name = "row_count") %>%
    filter(row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf("%s has duplicate geo_level + geo_id + year rows", table_name),
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

safe_ratio <- function(num, den) {
  if (is.na(den) || den <= 0) {
    return(NA_real_)
  }

  num / den
}

unsupported_county_geoids <- c(
  "02261"
)

# 3. Read staging and canonical county references ----
epa_sld_stage <- DBI::dbGetQuery(con, "SELECT * FROM staging.epa_sld") %>%
  mutate(
    year = as.integer(year),
    state_fips = as.character(state_fips),
    county_fips = as.character(county_fips),
    county_geoid = paste0(as.character(state_fips), as.character(county_fips))
  )

county_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state") %>%
  transmute(
    county_geoid = as.character(county_geoid),
    county_name = as.character(county_name),
    county_name_long = as.character(county_name_long),
    state_abbr = as.character(state_abbr),
    state_fips = as.character(state_fip)
  ) %>%
  distinct()

county_manual_lookup <- tibble::tribble(
  ~county_geoid, ~county_name_long, ~state_abbr,
  "09001", "Fairfield County, Connecticut", "CT",
  "09003", "Hartford County, Connecticut", "CT",
  "09005", "Litchfield County, Connecticut", "CT",
  "09007", "Middlesex County, Connecticut", "CT",
  "09009", "New Haven County, Connecticut", "CT",
  "09011", "New London County, Connecticut", "CT",
  "09013", "Tolland County, Connecticut", "CT",
  "09015", "Windham County, Connecticut", "CT"
)

county_lookup <- county_xwalk %>%
  select(county_geoid, county_name_long, state_abbr) %>%
  bind_rows(county_manual_lookup) %>%
  distinct(county_geoid, .keep_all = TRUE)

# 4. Audit county-key coverage before modeling ----
county_match_audit <- epa_sld_stage %>%
  distinct(county_geoid) %>%
  left_join(
    county_lookup %>% transmute(county_geoid, in_xwalk = TRUE),
    by = "county_geoid"
  ) %>%
  mutate(in_xwalk = dplyr::coalesce(in_xwalk, FALSE))

unmatched_counties <- county_match_audit %>%
  filter(!in_xwalk, !county_geoid %in% unsupported_county_geoids)

if (nrow(unmatched_counties) > 0) {
  stop(
    sprintf(
      paste(
        "EPA SLD county coverage audit failed.",
        "%s staged county GEOIDs did not resolve to silver.xwalk_county_state."
      ),
      nrow(unmatched_counties)
    ),
    call. = FALSE
  )
}

# 5. Aggregate block groups to county ----
epa_sld_county <- epa_sld_stage %>%
  filter(!county_geoid %in% unsupported_county_geoids) %>%
  left_join(
    county_xwalk,
    by = c("county_geoid", "state_fips")
  ) %>%
  left_join(
    county_manual_lookup %>% rename(manual_county_name_long = county_name_long, manual_state_abbr = state_abbr),
    by = "county_geoid"
  ) %>%
  group_by(county_geoid, year) %>%
  summarise(
    geo_level = "county",
    geo_id = dplyr::first(county_geoid),
    geo_name = dplyr::first(dplyr::coalesce(county_name_long, manual_county_name_long, county_geoid)),
    state_abbr = dplyr::first(dplyr::coalesce(state_abbr, manual_state_abbr)),
    walkability_index = safe_weighted_mean(walkability_index, total_population),
    employment_housing_mix = safe_weighted_mean(employment_housing_mix, households),
    employment_mix = safe_weighted_mean(employment_mix, total_employment),
    street_intersection_density = safe_weighted_mean(street_intersection_density, land_acres_unprotected),
    auto_oriented_intersection_share = safe_weighted_mean(auto_oriented_intersection_share, land_acres_unprotected),
    transit_service_density = safe_weighted_mean(transit_service_density, total_population),
    transit_frequency_peak = safe_weighted_mean(transit_frequency_peak, total_population),
    distance_to_transit = safe_weighted_mean(distance_to_transit, total_population),
    jobs_access_45min_transit = safe_weighted_mean(jobs_access_45min_transit, total_population),
    workers_access_45min_transit = safe_weighted_mean(workers_access_45min_transit, total_population),
    jobs_access_45min_auto = safe_weighted_mean(jobs_access_45min_auto, total_population),
    workers_access_45min_auto = safe_weighted_mean(workers_access_45min_auto, total_population),
    total_population_sum = sum(total_population, na.rm = TRUE),
    total_employment_sum = sum(total_employment, na.rm = TRUE),
    housing_units_sum = sum(housing_units, na.rm = TRUE),
    households_sum = sum(households, na.rm = TRUE),
    land_acres_unprotected_sum = sum(land_acres_unprotected, na.rm = TRUE),
    block_group_count = dplyr::n(),
    block_group_count_transit_non_null = sum(!is.na(transit_service_density)),
    block_group_count_walkability_non_null = sum(!is.na(walkability_index)),
    transit_metric_population_covered_sum = sum(
      ifelse(!is.na(transit_service_density), dplyr::coalesce(total_population, 0), 0),
      na.rm = TRUE
    ),
    walkability_metric_population_covered_sum = sum(
      ifelse(!is.na(walkability_index), dplyr::coalesce(total_population, 0), 0),
      na.rm = TRUE
    ),
    .groups = "drop"
  ) %>%
  mutate(
    total_population = total_population_sum,
    total_employment = total_employment_sum,
    housing_units = housing_units_sum,
    households = households_sum,
    land_acres_unprotected = land_acres_unprotected_sum,
    employment_density_gross = purrr::map2_dbl(total_employment_sum, land_acres_unprotected_sum, safe_ratio),
    population_density_gross = purrr::map2_dbl(total_population_sum, land_acres_unprotected_sum, safe_ratio),
    housing_density_gross = purrr::map2_dbl(housing_units_sum, land_acres_unprotected_sum, safe_ratio),
    transit_population_coverage_share = purrr::map2_dbl(
      transit_metric_population_covered_sum,
      total_population_sum,
      safe_ratio
    ),
    walkability_population_coverage_share = purrr::map2_dbl(
      walkability_metric_population_covered_sum,
      total_population_sum,
      safe_ratio
    )
  ) %>%
  select(
    geo_level,
    geo_id,
    geo_name,
    year,
    state_abbr,
    total_population,
    total_employment,
    housing_units,
    households,
    land_acres_unprotected,
    block_group_count,
    block_group_count_transit_non_null,
    block_group_count_walkability_non_null,
    transit_population_coverage_share,
    walkability_population_coverage_share,
    walkability_index,
    employment_housing_mix,
    employment_mix,
    street_intersection_density,
    auto_oriented_intersection_share,
    transit_service_density,
    transit_frequency_peak,
    distance_to_transit,
    jobs_access_45min_transit,
    workers_access_45min_transit,
    jobs_access_45min_auto,
    workers_access_45min_auto,
    employment_density_gross,
    population_density_gross,
    housing_density_gross
  ) %>%
  arrange(geo_id, year)

check_unique_annual_grain(epa_sld_county, "silver.epa_sld")

# 6. Materialize to Silver ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "epa_sld"),
  epa_sld_county,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
