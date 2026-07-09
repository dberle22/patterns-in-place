# Section 01 checks script
# Purpose: sanity checks and QA assertions for section outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 01 checks: 01_setup")

market_profile <- get_market_profile()
market_context <- get_market_context()
market_profile_check <- validate_market_profile(market_profile)
section_output_dir <- resolve_market_output_dir("01_setup")
con <- connect_project_duckdb(read_only = TRUE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

tract_features_sql <- resolve_sql_path("tract_features")
cbsa_features_sql <- resolve_sql_path("cbsa_features")

tract_features <- query_df_sql_file(con, tract_features_sql)
cbsa_features <- query_df_sql_file(con, cbsa_features_sql)

cbsa_wkb <- query_cbsa_geometry_wkb(con, profile = market_profile, cbsa_code = TARGET_CBSA)
county_wkb <- query_county_geometry_wkb(con, profile = market_profile, cbsa_code = TARGET_CBSA)
tract_wkb <- query_tract_geometry_wkb(con, profile = market_profile, cbsa_code = TARGET_CBSA)

cbsa_sf <- sf_from_wkb_df(cbsa_wkb, c("cbsa_code", "cbsa_name"))
county_sf <- sf_from_wkb_df(county_wkb, c("county_geoid", "county_name", "state_fips", "cbsa_code"))
tract_sf <- sf_from_wkb_df(tract_wkb, c("tract_geoid", "county_geoid", "state_fips", "cbsa_code"))

column_checks <- list(
  tract_features = validate_columns(tract_features, REQUIRED_COLUMNS$tract_features, "tract_features"),
  cbsa_features = validate_columns(cbsa_features, REQUIRED_COLUMNS$cbsa_features, "cbsa_features"),
  tract_geom = validate_columns(tract_wkb, REQUIRED_COLUMNS$tract_geom, "tract_geom"),
  county_geom = validate_columns(county_wkb, REQUIRED_COLUMNS$county_geom, "county_geom"),
  cbsa_geom = validate_columns(cbsa_wkb, REQUIRED_COLUMNS$cbsa_geom, "cbsa_geom")
)

key_checks <- list(
  tract_features = validate_unique_key(tract_features, "tract_geoid", "tract_features"),
  cbsa_features = validate_unique_key(cbsa_features %>% filter(year == TARGET_YEAR), "cbsa_code", "cbsa_features_target_year")
)

null_checks <- bind_rows(
  null_rate_summary(
    tract_features,
    c("land_area_sqmi", "pop_density", "median_gross_rent", "median_home_value", "pct_commute_wfh", "total_units_3yr_avg"),
    "tract_features"
  ),
  null_rate_summary(
    cbsa_features,
    c("pop_total", "pop_growth_5yr", "median_gross_rent", "median_home_value", "bps_units_per_1k_3yr_avg"),
    "cbsa_features"
  )
)

geometry_checks <- list(
  cbsa = validate_sf(cbsa_sf, "cbsa_sf", GEOMETRY_ASSUMPTIONS$expected_crs_epsg),
  county = validate_sf(county_sf, "county_sf", GEOMETRY_ASSUMPTIONS$expected_crs_epsg),
  tract = validate_sf(tract_sf, "tract_sf", GEOMETRY_ASSUMPTIONS$expected_crs_epsg)
)

report <- list(
  run_metadata = run_metadata(),
  market_context = market_context,
  output_dir = section_output_dir,
  market_profile_check = market_profile_check,
  target_cbsa = TARGET_CBSA,
  target_year = TARGET_YEAR,
  column_checks = column_checks,
  key_checks = key_checks,
  null_checks = null_checks,
  geometry_checks = geometry_checks
)

save_artifact(
  report,
  resolve_output_path("01_setup", "section_01_validation_report")
)

all_pass <- all(vapply(column_checks, `[[`, logical(1), "pass")) &&
  isTRUE(market_profile_check$pass) &&
  all(vapply(key_checks, `[[`, logical(1), "pass")) &&
  all(vapply(geometry_checks, `[[`, logical(1), "pass"))

if (!all_pass) {
  stop("Section 01 checks failed. See section_01_validation_report.rds for details.", call. = FALSE)
}

message("Section 01 checks complete.")
