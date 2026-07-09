source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

source("notebooks/retail_opportunity_finder/data_platform/layers/01_foundation_features/foundation_feature_workflow.R")

load_section_02_inputs <- function(con, profile = get_market_profile()) {
  use_foundation <- duckdb_table_exists(con, "foundation", "cbsa_features") &&
    duckdb_table_exists(con, "foundation", "tract_features") &&
    duckdb_table_exists(con, "foundation", "market_tract_geometry") &&
    duckdb_table_exists(con, "foundation", "market_county_geometry")

  if (!use_foundation) {
    cbsa_features <- query_df_sql_file(con, resolve_sql_path("cbsa_features"))
    tract_features <- query_tract_features_for_market(con, cbsa_code = profile$cbsa_code, target_year = TARGET_YEAR)

    tract_wkb <- query_tract_geometry_wkb(con, profile = profile, cbsa_code = profile$cbsa_code)
    market_tract_sf <- sf_from_wkb_df(tract_wkb, c("tract_geoid")) %>%
      left_join(
        tract_features %>% select(tract_geoid, cbsa_code, county_geoid, pop_growth_3yr, pop_growth_5yr, pop_density, median_gross_rent, median_home_value),
        by = "tract_geoid"
      )

    county_wkb <- query_county_geometry_wkb(con, profile = profile, cbsa_code = profile$cbsa_code)
    market_county_sf <- sf_from_wkb_df(county_wkb, c("county_geoid", "county_name"))

    return(list(
      cbsa_features = cbsa_features,
      tract_features = tract_features,
      market_tract_sf = market_tract_sf,
      market_county_sf = market_county_sf,
      source = "legacy_sql_and_geometry_helpers"
    ))
  }

  cbsa_features <- DBI::dbGetQuery(
    con,
    "SELECT * FROM foundation.cbsa_features"
  ) %>%
    select(-any_of(c("market_key", "state_scope", "build_source", "run_timestamp")))

  tract_features <- DBI::dbGetQuery(
    con,
    glue::glue("SELECT * FROM foundation.tract_features WHERE cbsa_code = '{profile$cbsa_code}'")
  ) %>%
    select(-any_of(c("market_key", "state_scope", "build_source", "run_timestamp")))

  market_tract_tbl <- DBI::dbGetQuery(
    con,
    glue::glue("SELECT * FROM foundation.market_tract_geometry WHERE cbsa_code = '{profile$cbsa_code}'")
  ) %>%
    select(-any_of(c("market_key", "state_scope", "build_source", "run_timestamp")))

  market_county_tbl <- DBI::dbGetQuery(
    con,
    glue::glue("SELECT * FROM foundation.market_county_geometry WHERE cbsa_code = '{profile$cbsa_code}'")
  ) %>%
    select(-any_of(c("market_key", "state_scope", "build_source", "run_timestamp")))

  market_tract_sf <- geometry_wkt_table_to_sf(market_tract_tbl) %>%
    left_join(
      tract_features %>% select(tract_geoid, cbsa_code, county_geoid, pop_growth_3yr, pop_growth_5yr, pop_density, median_gross_rent, median_home_value),
      by = "tract_geoid"
    )

  market_county_sf <- geometry_wkt_table_to_sf(market_county_tbl)

  list(
    cbsa_features = cbsa_features,
    tract_features = tract_features,
    market_tract_sf = market_tract_sf,
    market_county_sf = market_county_sf,
    source = "foundation_duckdb"
  )
}
