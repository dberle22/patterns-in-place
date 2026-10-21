#!/usr/bin/env Rscript

# Adapt the approved, dated Geofabrik NY PBF to the same GDAL GeoPackage
# shape used by Richmond and Jacksonville. Run from the monorepo root after
# downloading the source declared in osm_infrastructure.yml. This only builds
# the ignored source cache; Geography clipping and classification happen later.
suppressPackageStartupMessages(library(osmextract))
# Surface GDAL/provider warnings as they happen during a long conversion.
options(warn = 1)

source_path <- file.path(
  "metro-deep-dive-program/engines/infrastructure/outputs/new_york_state/raw",
  "geofabrik_new-york-261017.osm.pbf"
)
stopifnot(file.exists(source_path))

# Promote the fields read directly by acquisition. Leave ref, operator and
# usage in GDAL's other_tags string so the existing source-tag interface stays
# consistent across markets. Point features are cached for named-landmark QA,
# but never enter the Infrastructure line/polygon serving product.
extra_tags <- c(
  "highway", "railway", "waterway", "water", "natural", "bridge", "tunnel",
  "layer", "oneway", "maxspeed", "lanes"
)
for (layer_name in c("lines", "multipolygons", "points")) {
  message(format(Sys.time(), tz = "UTC"), " START adapter layer: ", layer_name)
  adapter_path <- oe_vectortranslate(
    source_path, layer = layer_name, extra_tags = extra_tags, quiet = FALSE
  )
  message(format(Sys.time(), tz = "UTC"), " COMPLETE adapter layer: ", layer_name)
}
message("COMPLETE cached adapter: ", adapter_path)
