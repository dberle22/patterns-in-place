# In this script we aggregate block-group EPA Smart Location Database staging
# rows into county, CBSA, and state analytical Silver tables. County remains
# the first rollup off staging, and the broader geographies are derived from
# that county base so we do not reopen the deferred tract-recovery problem.

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

single_value_or_na <- function(x) {
  values <- unique(stats::na.omit(x))

  if (length(values) == 1) {
    return(values[[1]])
  }

  NA_character_
}

aggregate_epa_sld_metrics <- function(df) {
  df %>%
    summarise(
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
      total_population = sum(total_population, na.rm = TRUE),
      total_employment = sum(total_employment, na.rm = TRUE),
      housing_units = sum(housing_units, na.rm = TRUE),
      households = sum(households, na.rm = TRUE),
      land_acres_unprotected = sum(land_acres_unprotected, na.rm = TRUE),
      block_group_count = sum(block_group_count, na.rm = TRUE),
      block_group_count_transit_non_null = sum(block_group_count_transit_non_null, na.rm = TRUE),
      block_group_count_walkability_non_null = sum(block_group_count_walkability_non_null, na.rm = TRUE),
      transit_metric_population_covered = sum(transit_metric_population_covered, na.rm = TRUE),
      walkability_metric_population_covered = sum(walkability_metric_population_covered, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    mutate(
      employment_density_gross = purrr::map2_dbl(total_employment, land_acres_unprotected, safe_ratio),
      population_density_gross = purrr::map2_dbl(total_population, land_acres_unprotected, safe_ratio),
      housing_density_gross = purrr::map2_dbl(housing_units, land_acres_unprotected, safe_ratio),
      transit_population_coverage_share = purrr::map2_dbl(
        transit_metric_population_covered,
        total_population,
        safe_ratio
      ),
      walkability_population_coverage_share = purrr::map2_dbl(
        walkability_metric_population_covered,
        total_population,
        safe_ratio
      )
    )
}

unsupported_county_geoids <- c(
  "02261"
)

# 3. Read staging and canonical geography references ----
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

state_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_state_region") %>%
  transmute(
    state_fips = as.character(state_fips),
    state_abbr = as.character(state_abbr),
    state_name = as.character(state_name)
  ) %>%
  distinct()

cbsa_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county") %>%
  transmute(
    county_geoid = as.character(county_geoid),
    cbsa_code = as.character(cbsa_code),
    cbsa_name = as.character(cbsa_name)
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

# 4. Audit coverage before modeling ----
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

duplicate_cbsa_counties <- cbsa_xwalk %>%
  count(county_geoid, name = "cbsa_count") %>%
  filter(cbsa_count > 1)

if (nrow(duplicate_cbsa_counties) > 0) {
  stop(
    sprintf(
      paste(
        "EPA SLD CBSA rollup requires a one-county-to-one-CBSA crosswalk.",
        "%s county GEOIDs resolve to multiple CBSAs."
      ),
      nrow(duplicate_cbsa_counties)
    ),
    call. = FALSE
  )
}

# 5. Standardize the block-group rollup base ----
epa_sld_rollup_base <- epa_sld_stage %>%
  filter(!county_geoid %in% unsupported_county_geoids) %>%
  left_join(
    county_xwalk,
    by = c("county_geoid", "state_fips")
  ) %>%
  left_join(
    county_manual_lookup %>%
      rename(
        manual_county_name_long = county_name_long,
        manual_state_abbr = state_abbr
      ),
    by = "county_geoid"
  ) %>%
  mutate(
    county_name_long = dplyr::coalesce(county_name_long, manual_county_name_long, county_geoid),
    state_abbr = dplyr::coalesce(state_abbr, manual_state_abbr),
    block_group_count = 1L,
    block_group_count_transit_non_null = as.integer(!is.na(transit_service_density)),
    block_group_count_walkability_non_null = as.integer(!is.na(walkability_index)),
    transit_metric_population_covered = ifelse(
      !is.na(transit_service_density),
      dplyr::coalesce(total_population, 0),
      0
    ),
    walkability_metric_population_covered = ifelse(
      !is.na(walkability_index),
      dplyr::coalesce(total_population, 0),
      0
    )
  )

# 6. Aggregate block groups to county ----
epa_sld_county <- epa_sld_rollup_base %>%
  group_by(county_geoid, county_name_long, state_fips, state_abbr, year) %>%
  aggregate_epa_sld_metrics() %>%
  transmute(
    geo_level = "county",
    geo_id = county_geoid,
    geo_name = county_name_long,
    year = year,
    state_abbr = state_abbr,
    state_fips = state_fips,
    total_population,
    total_employment,
    housing_units,
    households,
    land_acres_unprotected,
    block_group_count,
    block_group_count_transit_non_null,
    block_group_count_walkability_non_null,
    transit_metric_population_covered,
    walkability_metric_population_covered,
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
  )

# 7. Aggregate counties to CBSAs ----
epa_sld_cbsa <- epa_sld_county %>%
  inner_join(cbsa_xwalk, by = c("geo_id" = "county_geoid")) %>%
  group_by(cbsa_code, cbsa_name, year) %>%
  aggregate_epa_sld_metrics() %>%
  left_join(
    epa_sld_county %>%
      inner_join(cbsa_xwalk, by = c("geo_id" = "county_geoid")) %>%
      group_by(cbsa_code, cbsa_name, year) %>%
      summarise(state_abbr = single_value_or_na(state_abbr), .groups = "drop"),
    by = c("cbsa_code", "cbsa_name", "year")
  ) %>%
  transmute(
    geo_level = "cbsa",
    geo_id = cbsa_code,
    geo_name = cbsa_name,
    year = year,
    state_abbr = state_abbr,
    state_fips = NA_character_,
    total_population,
    total_employment,
    housing_units,
    households,
    land_acres_unprotected,
    block_group_count,
    block_group_count_transit_non_null,
    block_group_count_walkability_non_null,
    transit_metric_population_covered,
    walkability_metric_population_covered,
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
  )

# 8. Aggregate counties to states ----
epa_sld_state <- epa_sld_county %>%
  left_join(state_xwalk, by = "state_fips", suffix = c("", "_state")) %>%
  mutate(
    state_abbr = dplyr::coalesce(state_abbr_state, state_abbr)
  ) %>%
  group_by(state_fips, state_abbr, state_name, year) %>%
  aggregate_epa_sld_metrics() %>%
  transmute(
    geo_level = "state",
    geo_id = state_fips,
    geo_name = state_name,
    year = year,
    state_abbr = state_abbr,
    state_fips = state_fips,
    total_population,
    total_employment,
    housing_units,
    households,
    land_acres_unprotected,
    block_group_count,
    block_group_count_transit_non_null,
    block_group_count_walkability_non_null,
    transit_metric_population_covered,
    walkability_metric_population_covered,
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
  )

# 9. Materialize unified Silver table ----
epa_sld_silver <- bind_rows(
  epa_sld_county,
  epa_sld_cbsa,
  epa_sld_state
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
  arrange(geo_level, geo_id, year)

check_unique_annual_grain(epa_sld_silver, "silver.epa_sld")

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "epa_sld"),
  epa_sld_silver,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
