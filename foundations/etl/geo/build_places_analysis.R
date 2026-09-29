# Build a bounded Census Place analytical-geometry product for spatial joins.
#
# This deliberately uses full Census TIGER/Line geometry rather than the
# cartographic `geo.places_display` layer. Set GEOGRAPHY_PLACE_ANALYSIS_STATE_SCOPE
# to comma-separated state abbreviations for a bounded refresh or ALL for the
# sequential national materialization.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

resolve_state_scope <- function() {
  raw_value <- Sys.getenv("GEOGRAPHY_PLACE_ANALYSIS_STATE_SCOPE", unset = "")
  if (!nzchar(raw_value)) {
    stop(
      "Set GEOGRAPHY_PLACE_ANALYSIS_STATE_SCOPE to comma-separated state abbreviations or ALL.",
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
    stop("Use valid state abbreviations only, or ALL by itself.", call. = FALSE)
  }
  requested
}

db_path <- get_env_path("DB_PATH")
boundary_vintage <- as.integer(Sys.getenv("GEOGRAPHY_PLACE_ANALYSIS_YEAR", unset = "2024"))
analytical_crs <- 5070L
source_label <- sprintf("Census TIGER/Line %s via tigris", boundary_vintage)
selected_states <- resolve_state_scope()

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
DBI::dbExecute(con, "INSTALL spatial")
DBI::dbExecute(con, "LOAD spatial")
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS geo")

# Preserve source WGS84 geometry for interchange. Spatial measurements are
# intentionally deferred to EPSG:5070 at query time rather than measuring
# degrees in the stored interchange CRS.
places <- purrr::map_dfr(selected_states, function(state_abbr) {
  message(glue::glue("Downloading {state_abbr} Census Place TIGER/Line geometry ({boundary_vintage})"))
  tigris::places(state = state_abbr, cb = FALSE, year = boundary_vintage, class = "sf") |>
    dplyr::transmute(
      place_geoid = GEOID,
      state_fips = STATEFP,
      state_abbr = state_abbr,
      place_name = NAME,
      place_name_long = NAMELSAD,
      place_class = LSAD,
      aland_m2 = as.numeric(ALAND),
      awater_m2 = as.numeric(AWATER),
      geometry
    )
})

if (any(!sf::st_is_valid(places))) {
  stop("Census TIGER/Line Place source contains invalid geometry; do not repair silently.", call. = FALSE)
}

place_rows <- sf::st_drop_geometry(places) |>
  dplyr::mutate(
    boundary_vintage = as.character(boundary_vintage),
    geometry_role = "analysis",
    geometry_authority = source_label,
    interchange_crs = "EPSG:4326",
    analytical_crs = sprintf("EPSG:%s", analytical_crs),
    geom_wkb = blob::as_blob(unclass(sf::st_as_binary(sf::st_geometry(places))))
  )

duckdb::duckdb_register(con, "places_analysis_source", place_rows)
on.exit(duckdb::duckdb_unregister(con, "places_analysis_source"), add = TRUE)
DBI::dbExecute(con, "CREATE OR REPLACE TABLE geo.places_analysis AS SELECT * FROM places_analysis_source")
DBI::dbExecute(con, "ALTER TABLE geo.places_analysis ADD COLUMN geom GEOMETRY")
DBI::dbExecute(con, "UPDATE geo.places_analysis SET geom = ST_GeomFromWKB(geom_wkb)")

# Structural QA is materialized with the product so consumers can inspect the
# scope and validity checks that governed this particular state-scoped build.
qa_sql <- sprintf("
CREATE OR REPLACE TABLE geo.places_analysis_qa AS
SELECT 'unique_place_identity_vintage' AS check_name,
       CASE WHEN count(*) = count(DISTINCT place_geoid || '|' || boundary_vintage) THEN 'pass' ELSE 'fail' END AS check_status,
       count(*) AS observed_value, '%s' AS check_scope
FROM geo.places_analysis
UNION ALL
SELECT 'valid_geometry',
       CASE WHEN count(*) = count_if(ST_IsValid(geom)) THEN 'pass' ELSE 'fail' END,
       count_if(ST_IsValid(geom)), '%s'
FROM geo.places_analysis
UNION ALL
SELECT 'expected_selected_state_coverage',
       CASE WHEN count(DISTINCT state_abbr) = %s THEN 'pass' ELSE 'fail' END,
       count(DISTINCT state_abbr), '%s'
FROM geo.places_analysis",
  paste(selected_states, collapse = ","), paste(selected_states, collapse = ","), length(selected_states), paste(selected_states, collapse = ",")
)
DBI::dbExecute(con, qa_sql)

if (any(DBI::dbGetQuery(con, "SELECT check_status FROM geo.places_analysis_qa")$check_status != "pass")) {
  stop("Place analytical geometry structural QA failed.", call. = FALSE)
}

# Richmond smoke checks exercise both supported operations against analytical
# geometry. A representative point must have one strict interior match; a
# boundary line must intersect at least one Place. The checks run only when VA
# is in scope, because a bounded build must not claim Richmond coverage absent.
if ("VA" %in% selected_states) {
  richmond_checks <- DBI::dbGetQuery(con, "
    WITH richmond AS (
      SELECT geom FROM geo.places_analysis
      WHERE state_abbr = 'VA' AND place_name = 'Richmond'
      ORDER BY place_geoid LIMIT 1
    ), representative_point AS (
      SELECT ST_PointOnSurface(geom) AS geom FROM richmond
    ), test_line AS (
      SELECT ST_MakeLine(ST_Point(ST_XMin(geom), ST_YMin(geom)), ST_Point(ST_XMax(geom), ST_YMax(geom))) AS geom
      FROM richmond
    )
    SELECT
      (SELECT count(*) FROM geo.places_analysis p, representative_point q WHERE ST_Contains(p.geom, q.geom)) AS point_match_count,
      (SELECT count(*) FROM geo.places_analysis p, test_line l WHERE ST_Intersects(p.geom, l.geom)) AS line_match_count
  ")
  if (nrow(richmond_checks) != 1 || richmond_checks$point_match_count != 1 || richmond_checks$line_match_count < 1) {
    stop("Richmond analytical point/line smoke check failed.", call. = FALSE)
  }
  DBI::dbExecute(
    con,
    sprintf(
      "INSERT INTO geo.places_analysis_qa VALUES ('richmond_point_in_polygon', 'pass', %s, 'VA')",
      richmond_checks$point_match_count
    )
  )
  DBI::dbExecute(
    con,
    sprintf(
      "INSERT INTO geo.places_analysis_qa VALUES ('richmond_line_intersection', 'pass', %s, 'VA')",
      richmond_checks$line_match_count
    )
  )
}

message("Built geo.places_analysis for: ", paste(selected_states, collapse = ", "))
