# Build the narrow full-TIGER geography surfaces required by Regional Role.
#
# This is separate from the cartographic display builder. These full-resolution
# products are governed inputs for adjacency and centroid calculations; users
# consume the resulting mart tables, not notebook-local spatial logic.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")
boundary_vintage <- 2023L
source_label <- "Census TIGER/Line 2023 via tigris"
method_version <- "regional_lens_v1"

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

DBI::dbExecute(con, "INSTALL spatial")
DBI::dbExecute(con, "LOAD spatial")
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS geo")
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS mart_geography")

write_analysis_geometry <- function(sf_object, target_table) {
  # WKB keeps source geometry portable while GEOMETRY supports governed
  # warehouse use. It cannot be replaced by cartographic display geometry.
  geometry_data <- sf::st_drop_geometry(sf_object) |>
    dplyr::mutate(
      boundary_vintage = as.character(boundary_vintage),
      geometry_role = "analysis",
      geometry_authority = source_label,
      geom_wkb = blob::as_blob(unclass(sf::st_as_binary(sf::st_geometry(sf_object))))
    )
  temp_name <- paste0("regional_lens_geometry_", as.integer(stats::runif(1, 1e7, 9e7)))
  duckdb::duckdb_register(con, temp_name, geometry_data)
  on.exit(duckdb::duckdb_unregister(con, temp_name), add = TRUE)
  DBI::dbExecute(con, sprintf("CREATE OR REPLACE TABLE %s AS SELECT * FROM %s", target_table, temp_name))
  DBI::dbExecute(con, sprintf("ALTER TABLE %s ADD COLUMN geom GEOMETRY", target_table))
  DBI::dbExecute(con, sprintf("UPDATE %s SET geom = ST_GeomFromWKB(geom_wkb)", target_table))
}

# Full TIGER/Line boundaries, not Census cartographic boundaries, establish
# the relationships below. The CBSA vintage aligns with OMB 2023.
states <- tigris::states(cb = FALSE, year = boundary_vintage, class = "sf") |>
  dplyr::filter(STUSPS %in% c(state.abb, "DC")) |>
  dplyr::transmute(
    state_fips = STATEFP, state_abbr = STUSPS, state_name = NAME,
    aland_m2 = as.numeric(ALAND), awater_m2 = as.numeric(AWATER), geometry
  )
cbsas <- tigris::core_based_statistical_areas(cb = FALSE, year = boundary_vintage, class = "sf") |>
  dplyr::transmute(
    cbsa_code = CBSAFP, cbsa_name = NAME, cbsa_name_long = NAMELSAD,
    cbsa_type = LSAD, aland_m2 = as.numeric(ALAND), awater_m2 = as.numeric(AWATER), geometry
  )

write_analysis_geometry(states, "geo.states_analysis")
write_analysis_geometry(cbsas, "geo.cbsas_analysis")

# Measure boundaries in a projected CRS. A relationship exists only where the
# shared boundary is a line with nonzero length: point contacts are excluded.
states_projected <- sf::st_transform(states, 5070)
candidate_pairs <- sf::st_intersects(states_projected, states_projected)
adjacency_rows <- purrr::imap_dfr(candidate_pairs, function(neighbors, i) {
  neighbors <- neighbors[neighbors > i]
  purrr::map_dfr(neighbors, function(j) {
    shared_boundary <- suppressWarnings(sf::st_intersection(
      sf::st_boundary(states_projected[i, ]), sf::st_boundary(states_projected[j, ])
    ))
    shared_length_m <- sum(as.numeric(sf::st_length(shared_boundary)), na.rm = TRUE)
    if (shared_length_m <= 0) return(NULL)
    tibble::tibble(
      state_fips = states_projected$state_fips[[i]],
      adjacent_state_fips = states_projected$state_fips[[j]],
      shared_boundary_meters = shared_length_m
    )
  })
}) |>
  dplyr::mutate(
    boundary_vintage = as.character(boundary_vintage), source = source_label,
    method_version = method_version
  )

# Publish both directions so the table is directly reusable and symmetric.
adjacency_rows <- dplyr::bind_rows(
  adjacency_rows,
  adjacency_rows |>
    dplyr::select(
      state_fips = adjacent_state_fips, adjacent_state_fips = state_fips,
      dplyr::everything()
    )
)
duckdb::duckdb_register(con, "regional_lens_adjacency", adjacency_rows)
on.exit(duckdb::duckdb_unregister(con, "regional_lens_adjacency"), add = TRUE)
DBI::dbExecute(con, "CREATE OR REPLACE TABLE mart_geography.state_adjacency AS SELECT * FROM regional_lens_adjacency")

# Geometric centroids are declared reference points, not travel-time proxies.
# Compute them in an equal-area projection before returning WGS84 coordinates.
centroid_geometry <- cbsas |>
  sf::st_transform(5070) |>
  sf::st_centroid() |>
  sf::st_transform(4326)
coordinates <- sf::st_coordinates(centroid_geometry)
centroid_rows <- sf::st_drop_geometry(centroid_geometry) |>
  dplyr::transmute(
    cbsa_code, boundary_vintage = as.character(boundary_vintage),
    centroid_method = "equal_area_geometric_centroid_epsg5070",
    longitude = coordinates[, "X"], latitude = coordinates[, "Y"],
    source = source_label, method_version = method_version
  )
duckdb::duckdb_register(con, "regional_lens_centroids", centroid_rows)
on.exit(duckdb::duckdb_unregister(con, "regional_lens_centroids"), add = TRUE)
DBI::dbExecute(con, "CREATE OR REPLACE TABLE mart_geography.cbsa_centroids AS SELECT * FROM regional_lens_centroids")

# Create every declared lens centrally. Static lenses retain a literal
# parameter so their keys remain as auditable as the 200/250/300-mile rows.
membership_sql <- glue::glue("
CREATE OR REPLACE TABLE mart_geography.region_lens_membership AS
WITH target_cbsa AS (
  SELECT geo_id AS target_cbsa_code, parent_division_id, state_fips AS primary_state_fips
  FROM gold.dim_geo WHERE geo_level = 'cbsa' AND is_metro = TRUE
),
member_cbsa AS (
  SELECT geo_id AS member_cbsa_code, parent_division_id, state_fips AS primary_state_fips
  FROM gold.dim_geo WHERE geo_level = 'cbsa' AND is_metro = TRUE
),
static_lenses AS (
  SELECT t.target_cbsa_code, 'census_division' AS lens_id, 'none' AS parameter_name,
         'none' AS parameter_value, m.member_cbsa_code, CAST(NULL AS DOUBLE) AS distance_miles
  FROM target_cbsa t JOIN member_cbsa m ON t.parent_division_id = m.parent_division_id
  WHERE t.parent_division_id IS NOT NULL
  UNION ALL
  SELECT t.target_cbsa_code, 'primary_state', 'none', 'none', m.member_cbsa_code, CAST(NULL AS DOUBLE)
  FROM target_cbsa t JOIN member_cbsa m ON t.primary_state_fips = m.primary_state_fips
  WHERE t.primary_state_fips IS NOT NULL
  UNION ALL
  SELECT t.target_cbsa_code, 'primary_state_adjacent', 'none', 'none', m.member_cbsa_code, CAST(NULL AS DOUBLE)
  FROM target_cbsa t
  JOIN member_cbsa m ON m.primary_state_fips = t.primary_state_fips
     OR EXISTS (
       SELECT 1 FROM mart_geography.state_adjacency a
       WHERE a.state_fips = t.primary_state_fips AND a.adjacent_state_fips = m.primary_state_fips
     )
  WHERE t.primary_state_fips IS NOT NULL
),
radius_distances AS (
  SELECT t.target_cbsa_code, m.member_cbsa_code,
         3958.7613 * 2 * asin(sqrt(
           pow(sin(radians(m_cent.latitude - t_cent.latitude) / 2), 2)
           + cos(radians(t_cent.latitude)) * cos(radians(m_cent.latitude))
             * pow(sin(radians(m_cent.longitude - t_cent.longitude) / 2), 2)
         )) AS distance_miles
  FROM target_cbsa t
  JOIN mart_geography.cbsa_centroids t_cent ON t.target_cbsa_code = t_cent.cbsa_code
  JOIN member_cbsa m ON TRUE
  JOIN mart_geography.cbsa_centroids m_cent ON m.member_cbsa_code = m_cent.cbsa_code
),
radius_lenses AS (
  SELECT target_cbsa_code, 'cbsa_centroid_250mi' AS lens_id, 'radius_miles' AS parameter_name,
         CAST(radius_miles AS VARCHAR) AS parameter_value, member_cbsa_code, distance_miles
  FROM radius_distances CROSS JOIN (VALUES (200), (250), (300)) AS radius(radius_miles)
  WHERE distance_miles <= radius_miles
)
SELECT target_cbsa_code, lens_id, '{method_version}' AS lens_version, parameter_name, parameter_value,
       member_cbsa_code, CASE WHEN target_cbsa_code = member_cbsa_code THEN 'target' ELSE 'comparison' END AS member_role,
       distance_miles, 'mart_geography regional_lens build' AS membership_source,
       '{boundary_vintage}' AS boundary_vintage, '{method_version}' AS method_version
FROM static_lenses
UNION ALL
SELECT target_cbsa_code, lens_id, '{method_version}', parameter_name, parameter_value,
       member_cbsa_code, CASE WHEN target_cbsa_code = member_cbsa_code THEN 'target' ELSE 'comparison' END,
       distance_miles, 'mart_geography regional_lens build', '{boundary_vintage}', '{method_version}'
FROM radius_lenses;")
DBI::dbExecute(con, membership_sql)

message("Built full-TIGER analytical state/CBSA geometry and Regional Role lens surfaces.")
