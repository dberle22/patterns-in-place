# Section 02 context layer ingestion
# Pulls all context layers from TIGER (no DuckDB dependency).

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running Section 02 context ingestion")

suppressPackageStartupMessages({
  library(dplyr)
  library(sf)
  library(tigris)
  library(glue)
  library(janitor)
})

cache_dir <- "notebooks/retail_opportunity_finder/sections/02_market_overview/context_layers/cache"
if (!dir.exists(cache_dir)) dir.create(cache_dir, recursive = TRUE)
Sys.setenv(TIGRIS_CACHE_DIR = normalizePath(cache_dir, winslash = "/", mustWork = FALSE))
options(
  tigris_use_cache = TRUE,
  tigris_cache_dir = normalizePath(cache_dir, winslash = "/", mustWork = FALSE)
)

out_dir <- resolve_market_output_dir("02_market_overview", subdir = "context_layers")
if (!dir.exists(out_dir)) dir.create(out_dir, recursive = TRUE)

target_cbsa <- TARGET_CBSA
target_year <- TARGET_YEAR

# CBSA boundary from TIGER
cbsa_boundary_sf <- tigris::core_based_statistical_areas(cb = TRUE, year = target_year, class = "sf") %>%
  janitor::clean_names() %>%
  transmute(
    cbsa_code = as.character(cbsafp),
    cbsa_name = as.character(name),
    geometry
  ) %>%
  filter(cbsa_code == as.character(target_cbsa)) %>%
  st_make_valid() %>%
  st_transform(GEOMETRY_ASSUMPTIONS$expected_crs_epsg)

if (nrow(cbsa_boundary_sf) == 0) {
  stop(glue("No CBSA boundary found in TIGER for cbsa_code={target_cbsa}, year={target_year}"), call. = FALSE)
}

# County polygons from TIGER clipped to CBSA
county_sf <- tigris::counties(state = "FL", cb = TRUE, year = target_year, class = "sf") %>%
  janitor::clean_names() %>%
  mutate(
    county_geoid = paste0(statefp, countyfp),
    county_name = as.character(name)
  ) %>%
  st_make_valid() %>%
  st_transform(GEOMETRY_ASSUMPTIONS$expected_crs_epsg) %>%
  st_filter(st_union(cbsa_boundary_sf), .predicate = st_intersects) %>%
  select(county_geoid, county_name, geometry)

cbsa_counties <- county_sf %>%
  st_drop_geometry() %>%
  mutate(
    state_fips = substr(county_geoid, 1, 2),
    county_fips = substr(county_geoid, 3, 5)
  )

read_county_tiger <- function(county_fips, fn) {
  tryCatch(
    fn(state = "FL", county = county_fips, year = target_year, class = "sf"),
    error = function(e) {
      warning(glue("Failed TIGER pull for county {county_fips}: {e$message}"), call. = FALSE)
      NULL
    }
  )
}

# Roads (county pulls + major road filter)
roads_list <- lapply(cbsa_counties$county_fips, function(cf) read_county_tiger(cf, tigris::roads))
roads_sf <- dplyr::bind_rows(roads_list)
if (nrow(roads_sf) > 0) {
  roads_sf <- roads_sf %>%
    st_make_valid() %>%
    filter(MTFCC %in% c("S1100", "S1200")) %>% # primary/secondary roads
    st_transform(GEOMETRY_ASSUMPTIONS$expected_crs_epsg) %>%
    st_filter(st_union(cbsa_boundary_sf), .predicate = st_intersects) %>%
    st_as_sf()
}

# Water polygons (county pulls)
water_list <- lapply(cbsa_counties$county_fips, function(cf) read_county_tiger(cf, tigris::area_water))
water_sf <- dplyr::bind_rows(water_list)
if (nrow(water_sf) > 0) {
  water_sf <- water_sf %>%
    st_make_valid() %>%
    st_transform(GEOMETRY_ASSUMPTIONS$expected_crs_epsg) %>%
    st_filter(st_union(cbsa_boundary_sf), .predicate = st_intersects) %>%
    st_as_sf()
}

# Municipal boundaries (state pull, clipped to CBSA)
places_sf <- tryCatch(
  tigris::places(state = "FL", cb = TRUE, year = target_year, class = "sf"),
  error = function(e) {
    warning(glue("Failed TIGER places pull: {e$message}"), call. = FALSE)
    sf::st_sf(geometry = sf::st_sfc(crs = GEOMETRY_ASSUMPTIONS$expected_crs_epsg))
  }
)
if (nrow(places_sf) > 0) {
  places_sf <- places_sf %>%
    janitor::clean_names() %>%
    st_make_valid() %>%
    st_transform(GEOMETRY_ASSUMPTIONS$expected_crs_epsg) %>%
    st_filter(st_union(cbsa_boundary_sf), .predicate = st_intersects) %>%
    st_as_sf() %>%
    mutate(
      place_geoid = if ("geoid" %in% names(.)) as.character(geoid) else NA_character_,
      place_name = if ("name" %in% names(.)) as.character(name) else NA_character_
    )
}

save_artifact(cbsa_boundary_sf, file.path(out_dir, "section_02_context_cbsa_boundary_sf.rds"))
save_artifact(county_sf, file.path(out_dir, "section_02_context_county_sf.rds"))
save_artifact(places_sf, file.path(out_dir, "section_02_context_places_sf.rds"))
save_artifact(roads_sf, file.path(out_dir, "section_02_context_major_roads_sf.rds"))
save_artifact(water_sf, file.path(out_dir, "section_02_context_water_sf.rds"))

ingest_report <- list(
  run_metadata = run_metadata(),
  market_context = get_market_context(),
  output_dir = out_dir,
  target_cbsa = target_cbsa,
  target_year = target_year,
  source = "tigris_only",
  counts = list(
    cbsa_rows = nrow(cbsa_boundary_sf),
    county_rows = nrow(county_sf),
    place_rows = nrow(places_sf),
    major_roads_rows = nrow(roads_sf),
    water_rows = nrow(water_sf)
  ),
  pass = nrow(cbsa_boundary_sf) > 0 && nrow(county_sf) > 0
)

save_artifact(ingest_report, file.path(out_dir, "section_02_context_ingest_report.rds"))

if (!isTRUE(ingest_report$pass)) {
  stop("Section 02 context ingestion failed minimum checks.", call. = FALSE)
}

message("Section 02 context ingestion complete.")
