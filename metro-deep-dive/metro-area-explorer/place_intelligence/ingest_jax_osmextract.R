#!/usr/bin/env Rscript

# Jacksonville-first OSM infrastructure ingestion via osmextract.
#
# This mirrors the Richmond prototype but points it at Jacksonville so D3 can
# reuse the same provider-backed path that already proved viable in this repo.

suppressPackageStartupMessages({
  library(DBI)
  library(dplyr)
  library(duckdb)
  library(jsonlite)
  library(osmextract)
  library(sf)
  library(arrow)
})

section_root <- normalizePath("metro-deep-dive/metro-area-explorer/place_intelligence", mustWork = TRUE)
output_dir <- file.path(section_root, "outputs", "jacksonville_fl")
download_dir <- file.path(output_dir, "raw")
dir.create(download_dir, recursive = TRUE, showWarnings = FALSE)

market_slug <- "jacksonville_fl"
place_name <- "Jacksonville, Florida"
provider_name <- "openstreetmap_fr"
extract_date <- format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")

extra_tags <- c(
  "name", "highway", "railway", "aeroway", "harbour", "landuse",
  "industrial", "amenity", "building", "office", "ref", "maxspeed",
  "lanes", "oneway", "iata", "icao", "waterway", "natural", "water",
  "bridge", "tunnel", "man_made"
)

line_query <- paste(
  "SELECT * FROM lines",
  "WHERE highway IN ('motorway','motorway_link','trunk','trunk_link',",
  "'primary','primary_link','secondary','secondary_link','tertiary','tertiary_link')",
  "OR railway IN ('rail','light_rail','subway')",
  "OR waterway IN ('river','canal')"
)

point_query <- paste(
  "SELECT * FROM points",
  "WHERE aeroway IN ('aerodrome','terminal','helipad')",
  "OR harbour IS NOT NULL",
  "OR amenity = 'ferry_terminal'",
  "OR building = 'warehouse'",
  "OR office = 'logistics'",
  "OR industrial IN ('logistics','depot','port')"
)

polygon_query <- paste(
  "SELECT * FROM multipolygons",
  "WHERE aeroway IN ('aerodrome','terminal','runway','helipad')",
  "OR harbour IS NOT NULL",
  "OR landuse = 'port'",
  "OR natural = 'water'",
  "OR water IN ('river','canal','reservoir','lake')",
  "OR waterway = 'riverbank'",
  "OR industrial IN ('port','logistics','depot')",
  "OR amenity = 'ferry_terminal'",
  "OR building = 'warehouse'",
  "OR office = 'logistics'"
)

layer_from_tags <- function(frame) {
  frame %>%
    mutate(
      layer_group = case_when(
        !is.na(highway) & highway %in% c("motorway", "motorway_link", "trunk", "trunk_link") ~ "highways",
        !is.na(highway) & highway %in% c(
          "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link"
        ) ~ "major_roads",
        !is.na(railway) & railway %in% c("rail", "light_rail", "subway") ~ "rail",
        !is.na(waterway) & waterway %in% c("river", "canal") ~ "water",
        !is.na(natural) & natural == "water" ~ "water",
        !is.na(water) & water %in% c("river", "canal", "reservoir", "lake") ~ "water",
        !is.na(aeroway) ~ "airports",
        !is.na(harbour) | (!is.na(landuse) & landuse == "port") |
          (!is.na(industrial) & industrial == "port") |
          (!is.na(amenity) & amenity == "ferry_terminal") ~ "ports",
        (!is.na(building) & building == "warehouse") |
          (!is.na(office) & office == "logistics") |
          (!is.na(industrial) & industrial %in% c("logistics", "depot")) ~ "warehouses_logistics",
        TRUE ~ "other_infrastructure"
      ),
      subcategory = case_when(
        layer_group == "highways" ~ "highway",
        layer_group == "major_roads" ~ "major_road",
        layer_group == "rail" ~ "rail",
        layer_group == "water" ~ "water",
        layer_group == "airports" ~ "airport",
        layer_group == "ports" ~ "port",
        layer_group == "warehouses_logistics" ~ "warehouse_logistics",
        TRUE ~ "infrastructure"
      )
    )
}

normalize_sf <- function(frame, geometry_family) {
  if (nrow(frame) == 0) {
    return(tibble::tibble(
      market_id = character(),
      source_system = character(),
      source_id = character(),
      feature_name = character(),
      layer_group = character(),
      category = character(),
      subcategory = character(),
      geometry_type = character(),
      geometry_wkt = character(),
      centroid_lat = numeric(),
      centroid_lon = numeric(),
      attributes_json = character(),
      extract_date = character()
    ))
  }

  frame <- st_transform(frame, 4326)
  frame <- layer_from_tags(frame)
  centroids <- suppressWarnings(st_centroid(frame$geometry))
  centroid_coords <- st_coordinates(centroids)
  geometry_types <- as.character(st_geometry_type(frame))
  geometry_wkt <- st_as_text(frame$geometry)

  attribute_names <- setdiff(names(st_drop_geometry(frame)), c("osm_id", "name", "layer_group", "subcategory"))
  attributes_json <- apply(
    st_drop_geometry(frame)[, attribute_names, drop = FALSE],
    1,
    function(row) {
      row_list <- as.list(row)
      row_list <- row_list[!vapply(row_list, function(value) {
        length(value) == 1 && (is.na(value) || identical(value, ""))
      }, logical(1))]
      toJSON(row_list, auto_unbox = TRUE, null = "null")
    }
  )

  tibble::tibble(
    market_id = market_slug,
    source_system = "osm",
    source_id = if ("osm_id" %in% names(frame)) as.character(frame$osm_id) else as.character(seq_len(nrow(frame))),
    feature_name = if ("name" %in% names(frame)) dplyr::coalesce(frame$name, "") else "",
    layer_group = frame$layer_group,
    category = "infrastructure",
    subcategory = frame$subcategory,
    geometry_type = geometry_types,
    geometry_family = geometry_family,
    geometry_wkt = geometry_wkt,
    centroid_lat = centroid_coords[, "Y"],
    centroid_lon = centroid_coords[, "X"],
    attributes_json = attributes_json,
    extract_date = extract_date
  )
}

safe_read_query <- function(gpkg_path, query_text) {
  tryCatch(
    st_read(gpkg_path, query = query_text, quiet = TRUE),
    error = function(exc) {
      structure(list(message = conditionMessage(exc)), class = "ingest_error")
    }
  )
}

matched_extract <- oe_match(place_name, provider = provider_name)
gpkg_path <- oe_get(
  place = place_name,
  provider = provider_name,
  layer = "lines",
  extra_tags = extra_tags,
  download_directory = download_dir,
  download_only = TRUE,
  quiet = TRUE
)

lines_raw <- safe_read_query(gpkg_path, line_query)
points_raw <- safe_read_query(gpkg_path, point_query)
polygons_raw <- safe_read_query(gpkg_path, polygon_query)

notes <- c(
  sprintf("Matched provider %s extract: %s", provider_name, matched_extract$url),
  sprintf("Reported source file size: %s bytes", matched_extract$file_size),
  sprintf("Cached GeoPackage path: %s", gpkg_path)
)

lines <- if (inherits(lines_raw, "ingest_error")) tibble::tibble() else normalize_sf(lines_raw, "line")
points <- if (inherits(points_raw, "ingest_error")) tibble::tibble() else normalize_sf(points_raw, "point")
polygons <- if (inherits(polygons_raw, "ingest_error")) tibble::tibble() else normalize_sf(polygons_raw, "polygon")

if (inherits(lines_raw, "ingest_error")) {
  notes <- c(notes, sprintf("Lines extract failed: %s", lines_raw$message))
}
if (inherits(points_raw, "ingest_error")) {
  notes <- c(notes, sprintf("Points extract failed: %s", points_raw$message))
}
if (inherits(polygons_raw, "ingest_error")) {
  notes <- c(notes, sprintf("Multipolygons extract failed: %s", polygons_raw$message))
}

write_parquet(lines, file.path(output_dir, "osmextract_infrastructure_lines.parquet"))
write_parquet(points, file.path(output_dir, "osmextract_infrastructure_points.parquet"))
write_parquet(polygons, file.path(output_dir, "osmextract_infrastructure_polygons.parquet"))

build_layer_summary <- function(frame, geometry_family) {
  if (nrow(frame) == 0) {
    return(list())
  }
  counts <- frame %>%
    count(layer_group, name = "row_count") %>%
    arrange(desc(row_count))
  lapply(seq_len(nrow(counts)), function(idx) {
    list(
      source = "osm",
      layer_name = counts$layer_group[[idx]],
      geometry_type = geometry_family,
      row_count = unname(counts$row_count[[idx]])
    )
  })
}

manifest <- list(
  market_id = market_slug,
  source = "osmextract",
  provider = provider_name,
  place = place_name,
  extract_date = extract_date,
  layers = c(
    build_layer_summary(lines, "line"),
    build_layer_summary(points, "point"),
    build_layer_summary(polygons, "polygon")
  ),
  notes = notes
)

summary <- list(
  market_slug = market_slug,
  provider = provider_name,
  place = place_name,
  extract_date = extract_date,
  source_url = matched_extract$url,
  source_file_size = matched_extract$file_size,
  line_rows = nrow(lines),
  point_rows = nrow(points),
  polygon_rows = nrow(polygons),
  line_layer_counts = as.list(table(lines$layer_group)),
  point_layer_counts = as.list(table(points$layer_group)),
  polygon_layer_counts = as.list(table(polygons$layer_group))
)

writeLines(toJSON(manifest, pretty = TRUE, auto_unbox = TRUE), file.path(output_dir, "osmextract_manifest.json"))
writeLines(toJSON(summary, pretty = TRUE, auto_unbox = TRUE), file.path(output_dir, "osmextract_summary.json"))

cat(toJSON(summary, pretty = TRUE, auto_unbox = TRUE))
