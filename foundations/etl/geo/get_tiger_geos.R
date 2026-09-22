# Build Census cartographic-boundary display geometry for the geography engine.
#
# This is intentionally an on-demand build: it does not run as part of the
# default pipeline and it never creates full TIGER/Line analysis geometry.
# Set GEOGRAPHY_TIGER_STATE_SCOPE to a comma-separated list such as VA,FL, or
# ALL before running it. State-scoped runs create only state-specific tract
# display tables, so adding a consumer's footprint does not rebuild the nation.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")
con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

DBI::dbExecute(con, "INSTALL spatial")
DBI::dbExecute(con, "LOAD spatial")
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS geo")

# A required scope prevents an accidental national geometry refresh. ALL is
# deliberate and is the only scope that writes the nationwide tract product.
resolve_state_scope <- function(env_var = "GEOGRAPHY_TIGER_STATE_SCOPE") {
  raw_value <- Sys.getenv(env_var, unset = "")
  if (!nzchar(raw_value)) {
    stop(
      "Set GEOGRAPHY_TIGER_STATE_SCOPE to comma-separated state abbreviations or ALL.",
      call. = FALSE
    )
  }

  requested <- raw_value |>
    stringr::str_split(",") |>
    purrr::pluck(1) |>
    stringr::str_trim() |>
    toupper() |>
    unique()

  valid_states <- c(state.abb, "DC")
  if (identical(requested, "ALL")) return(valid_states)

  invalid_states <- setdiff(requested, valid_states)
  if (length(invalid_states) > 0) {
    stop(
      sprintf("Invalid %s values: %s", env_var, paste(invalid_states, collapse = ", ")),
      call. = FALSE
    )
  }

  requested
}

write_display_geometry <- function(sf_object, target_table, boundary_vintage) {
  # Keep WKB for portable extraction and a DuckDB GEOMETRY column for spatial
  # consumers. The metadata makes these map shapes unambiguously display-only.
  geometry_wkb <- blob::as_blob(unclass(sf::st_as_binary(sf::st_geometry(sf_object))))
  geometry_data <- sf::st_drop_geometry(sf_object) |>
    dplyr::mutate(
      boundary_vintage = as.character(boundary_vintage),
      geometry_role = "display",
      geometry_authority = "Census cartographic boundary",
      geom_wkb = geometry_wkb
    )

  temp_name <- paste0("display_geometry_", as.integer(stats::runif(1, 1e7, 9e7)))
  duckdb::duckdb_register(con, temp_name, geometry_data)
  on.exit(duckdb::duckdb_unregister(con, temp_name), add = TRUE)

  DBI::dbExecute(
    con,
    sprintf("CREATE OR REPLACE TABLE %s AS SELECT * FROM %s", target_table, temp_name)
  )
  DBI::dbExecute(con, sprintf("ALTER TABLE %s ADD COLUMN geom GEOMETRY", target_table))
  DBI::dbExecute(con, sprintf("UPDATE %s SET geom = ST_GeomFromWKB(geom_wkb)", target_table))
}

resolve_geo_id_column <- function(sf_object, candidates, geography_name) {
  # Census cartographic products vary between GEOID and GEOID20 across vintage.
  # Resolve once so consumers receive a stable canonical identifier column.
  matched <- intersect(candidates, names(sf_object))
  if (length(matched) == 0) {
    stop(
      sprintf("Could not find a GEOID field for %s; checked: %s", geography_name, paste(candidates, collapse = ", ")),
      call. = FALSE
    )
  }
  matched[[1]]
}

geometry_year <- as.integer(Sys.getenv("GEOGRAPHY_TIGER_YEAR", unset = "2024"))
selected_states <- resolve_state_scope()
all_states <- c(state.abb, "DC")
is_national_scope <- setequal(selected_states, all_states)
sqm_per_sqmi <- 2589988.110336

# Tracts are fetched per state because they are the large, consumer-oriented
# product. A submarket-only refresh can skip this existing product explicitly.
build_tracts <- !identical(tolower(Sys.getenv("GEOGRAPHY_TIGER_SKIP_TRACTS", unset = "false")), "true")
tracts_by_state <- if (build_tracts) lapply(selected_states, function(state_abbr) {
  message(glue::glue("Downloading {state_abbr} tract display geometry ({geometry_year})"))
  tracts <- tigris::tracts(state = state_abbr, cb = TRUE, year = geometry_year) |>
    dplyr::mutate(
      tract_geoid = GEOID,
      state_fips = STATEFP,
      state_abbr = state_abbr,
      county_fips = COUNTYFP,
      county_geoid = paste0(STATEFP, COUNTYFP),
      tract_name = NAME,
      aland_m2 = as.numeric(ALAND),
      awater_m2 = as.numeric(AWATER),
      land_area_sqmi = aland_m2 / sqm_per_sqmi,
      water_area_sqmi = awater_m2 / sqm_per_sqmi
    )

  write_display_geometry(
    tracts,
    sprintf("geo.tracts_%s_display", tolower(state_abbr)),
    geometry_year
  )
  tracts
}) else list()

# Nationwide display output is useful for broad maps, but only an explicit ALL
# request refreshes it. Existing geo.tracts_all_us remains untouched here.
if (is_national_scope && build_tracts) {
  write_display_geometry(
    dplyr::bind_rows(tracts_by_state),
    "geo.tracts_all_us_display",
    geometry_year
  )
}

# State, county, and CBSA display products are national reference layers. They
# are optional so a tract-only consumer need not fetch or replace them.
if (identical(tolower(Sys.getenv("GEOGRAPHY_TIGER_REFERENCE", unset = "false")), "true")) {
  states <- tigris::states(cb = TRUE, year = geometry_year) |>
    dplyr::rename(state_fips = STATEFP, state_abbr = STUSPS, state_name = NAME)
  counties <- tigris::counties(cb = TRUE, year = geometry_year) |>
    dplyr::mutate(
      county_geoid = paste0(STATEFP, COUNTYFP), state_fips = STATEFP,
      county_fips = COUNTYFP, county_name = NAME, aland_m2 = as.numeric(ALAND),
      awater_m2 = as.numeric(AWATER), land_area_sqmi = aland_m2 / sqm_per_sqmi,
      water_area_sqmi = awater_m2 / sqm_per_sqmi
    )
  cbsas <- tigris::core_based_statistical_areas(cb = TRUE, year = geometry_year) |>
    dplyr::rename(cbsa_code = CBSAFP, cbsa_name = NAME, cbsa_name_long = NAMELSAD)

  write_display_geometry(states, "geo.states_display", geometry_year)
  write_display_geometry(counties, "geo.counties_display", geometry_year)
  write_display_geometry(cbsas, "geo.cbsas_display", geometry_year)
}

# ZCTA and Place display geometries support product-facing submarket maps. They
# remain opt-in because a national ZCTA pull is materially larger than the core
# tract build. A nationwide scope writes canonical tables for the reusable Q1
# market selector; a scoped run writes state-specific Place tables only.
if (identical(tolower(Sys.getenv("GEOGRAPHY_TIGER_SUBMARKET_REFERENCE", unset = "false")), "true")) {
  # Census publishes cartographic-boundary ZCTAs only for the decennial 2020
  # vintage at present; the table records that distinct display vintage.
  zcta_geometry_year <- 2020L
  message(glue::glue("Downloading ZCTA display geometry ({zcta_geometry_year})"))
  zctas <- tigris::zctas(cb = TRUE, year = zcta_geometry_year)
  zcta_id_column <- resolve_geo_id_column(zctas, c("GEOID20", "GEOID"), "ZCTA")
  zctas <- zctas |>
    dplyr::mutate(zcta_geoid = .data[[zcta_id_column]])

  if (is_national_scope) {
    write_display_geometry(zctas, "geo.zctas_display", zcta_geometry_year)
  } else {
    warning(
      "ZCTA geometry is nationwide; run with GEOGRAPHY_TIGER_STATE_SCOPE=ALL to materialize geo.zctas_display.",
      call. = FALSE
    )
  }

  places_by_state <- lapply(selected_states, function(state_abbr) {
    message(glue::glue("Downloading {state_abbr} Place display geometry ({geometry_year})"))
    places <- tigris::places(state = state_abbr, cb = TRUE, year = geometry_year)
    place_id_column <- resolve_geo_id_column(places, c("GEOID", "GEOID20"), "Place")
    places |>
      dplyr::mutate(place_geoid = .data[[place_id_column]], state_abbr = state_abbr)
  })

  if (is_national_scope) {
    write_display_geometry(dplyr::bind_rows(places_by_state), "geo.places_display", geometry_year)
  } else {
    write_display_geometry(
      dplyr::bind_rows(places_by_state),
      sprintf("geo.places_%s_display", tolower(paste(selected_states, collapse = "_"))),
      geometry_year
    )
  }
}

message("Built display geometry for: ", paste(selected_states, collapse = ", "))
