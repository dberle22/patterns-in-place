# In this script we get our ACS Raw data

# Find our current directory 
getwd()

# Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))

# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
bronze_acs <- get_env_path("DATA_DEMO_RAW")
db_path <- get_env_path("DB_PATH")

# Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

dbExecute(con, "INSTALL spatial;")
dbExecute(con, "LOAD spatial;")

# optional: make a schema for geometries
dbExecute(con, "CREATE SCHEMA IF NOT EXISTS patterns_in_place.geo;")

# Set Vars 
year <- 2024
SQM_PER_SQMI <- 2589988.110336

resolve_tract_state_scope <- function(env_var = "ROF_TRACT_STATE_SCOPE") {
  raw_value <- Sys.getenv(env_var, unset = "")
  if (!nzchar(raw_value)) {
    return(c(state.abb, "DC"))
  }

  states <- raw_value %>%
    stringr::str_split(",") %>%
    purrr::pluck(1) %>%
    stringr::str_trim() %>%
    toupper() %>%
    unique()

  valid_states <- c(state.abb, "DC")
  invalid_states <- setdiff(states, valid_states)
  if (length(invalid_states) > 0) {
    stop(
      sprintf(
        "Invalid %s values: %s",
        env_var,
        paste(invalid_states, collapse = ", ")
      ),
      call. = FALSE
    )
  }

  states
}

tract_states <- resolve_tract_state_scope()

# ---- Helper: write sf -> duckdb with WKB + (optional) DuckDB geom column ----
write_sf_duckdb <- function(con, sf_obj, fq_table, make_geom_col = TRUE) {
  stopifnot(inherits(sf_obj, "sf"))
  
  # Build DF with WKB as a DB-friendly blob vector
  wkb <- sf::st_as_binary(sf::st_geometry(sf_obj))
  geom_wkb <- blob::as_blob(unclass(wkb))
  
  df <- sf::st_drop_geometry(sf_obj)
  df$geom_wkb <- geom_wkb
  
  # Register DF in DuckDB
  tmp_name <- paste0("tmp_", as.integer(runif(1, 1e7, 9e7)))
  duckdb::duckdb_register(con, tmp_name, df)
  
  # Create/replace target table from registered DF
  DBI::dbExecute(con, sprintf("CREATE OR REPLACE TABLE %s AS SELECT * FROM %s;", fq_table, tmp_name))
  
  # Optional: create DuckDB GEOMETRY column
  if (make_geom_col) {
    DBI::dbExecute(con, sprintf("ALTER TABLE %s ADD COLUMN IF NOT EXISTS geom GEOMETRY;", fq_table))
    DBI::dbExecute(con, sprintf("UPDATE %s SET geom = ST_GeomFromWKB(geom_wkb);", fq_table))
  }
  
  # Unregister temp
  duckdb::duckdb_unregister(con, tmp_name)
  
  invisible(TRUE)
}

# Download TIGER Geometries ----
## States ----
states <- tigris::states(cb = TRUE, year = year) %>%
  rename(state_fips = STATEFP, state_abbr = STUSPS, state_name = NAME)

write_sf_duckdb(con, states, "patterns_in_place.geo.states")

### Tests
dbGetQuery(con, "SELECT COUNT(*) n FROM patterns_in_place.geo.states;")
dbGetQuery(con, "SELECT typeof(geom_wkb) AS wkb_type, typeof(geom) AS geom_type FROM patterns_in_place.geo.states LIMIT 1;")

## CBSAs ----
cbsa_all <- tigris::core_based_statistical_areas(cb = TRUE, year = year) %>%
  rename(cbsa_code = CBSAFP, cbsa_name = NAME, cbsa_name_long = NAMELSAD)

write_sf_duckdb(con, cbsa_all, "patterns_in_place.geo.cbsas")

## Counties ----
counties <- tigris::counties(cb = TRUE, year = year) %>%
  mutate(county_geoid = paste0(STATEFP, COUNTYFP),
         state_fips = STATEFP, 
         county_fips = COUNTYFP, 
         county_name = NAME,
         aland_m2 = as.numeric(ALAND),
         awater_m2 = as.numeric(AWATER),
         land_area_sqmi  = aland_m2 / SQM_PER_SQMI,
         water_area_sqmi = awater_m2 / SQM_PER_SQMI)

write_sf_duckdb(con, counties, "patterns_in_place.geo.counties")

## Tracts ----
# Target table is patterns_in_place.geo.tracts_all_us.
# patterns_in_place.geo.tracts_supported_states remains as a compatibility alias
# until all downstream consumers stop referencing the older name.
build_tract_geometries <- function(state_abbr, year, cb = TRUE) {
  tigris::tracts(state = state_abbr, cb = cb, year = year) %>%
    mutate(
      tract_geoid = GEOID,
      state_fips = STATEFP,
      state_abbr = state_abbr,
      county_fips = COUNTYFP,
      county_geoid = paste0(STATEFP, COUNTYFP),
      tract_name = NAME,
      aland_m2 = as.numeric(ALAND),
      awater_m2 = as.numeric(AWATER),
      land_area_sqmi = aland_m2 / SQM_PER_SQMI,
      water_area_sqmi = awater_m2 / SQM_PER_SQMI
    )
}

tract_tables <- setNames(
  paste0("patterns_in_place.geo.tracts_", tolower(tract_states)),
  tract_states
)

tracts_by_state <- lapply(tract_states, function(state_abbr) {
  message(glue("Downloading tract geometries for {state_abbr} ({year})"))
  build_tract_geometries(state_abbr = state_abbr, year = year)
})
names(tracts_by_state) <- tract_states

for (state_abbr in tract_states) {
  write_sf_duckdb(con, tracts_by_state[[state_abbr]], tract_tables[[state_abbr]])
}

tracts_all_us <- dplyr::bind_rows(tracts_by_state)
write_sf_duckdb(con, tracts_all_us, "patterns_in_place.geo.tracts_all_us")
write_sf_duckdb(con, tracts_all_us, "patterns_in_place.geo.tracts_supported_states")

# Validations ----
print(dbGetQuery(con, "SELECT COUNT(*) n FROM patterns_in_place.geo.states;"))
print(dbGetQuery(con, "SELECT COUNT(*) n FROM patterns_in_place.geo.cbsas;"))
print(dbGetQuery(con, "SELECT COUNT(*) n FROM patterns_in_place.geo.counties;"))

for (state_abbr in tract_states) {
  print(dbGetQuery(
    con,
    glue("SELECT '{state_abbr}' AS state_abbr, COUNT(*) AS n FROM {tract_tables[[state_abbr]]};")
  ))
}

print(dbGetQuery(con, "SELECT COUNT(*) n FROM patterns_in_place.geo.tracts_all_us;"))
print(dbGetQuery(con, "SELECT COUNT(*) n FROM patterns_in_place.geo.tracts_supported_states;"))

# Quick column checks
print(dbGetQuery(con, "DESCRIBE patterns_in_place.geo.tracts_all_us;"))

# Land area sanity (tracts)
print(dbGetQuery(con, "
  SELECT
    COUNT(DISTINCT state_abbr) AS states_loaded,
    MIN(land_area_sqmi) min_sqmi,
    MAX(land_area_sqmi) max_sqmi,
    AVG(land_area_sqmi) avg_sqmi
  FROM patterns_in_place.geo.tracts_all_us;
"))

dbDisconnect(con, shutdown = TRUE)
