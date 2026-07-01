library(arrow)
library(DBI)
library(duckdb)
library(dplyr)
library(here)

source(here::here("foundations", "loaders", "_shared_intelligence_loader.R"))

# The Phase 7 tract model is the canonical zone surface for downstream products.
# This loader keeps the tract-grain output intact and writes it directly into the
# intelligence mart rather than forcing it through the CBSA-grain helper path.
if (Sys.getenv("DB_PATH") == "" && file.exists(here::here(".Renviron"))) {
  readRenviron(here::here(".Renviron"))
}

zone_scores_path <- here::here(
  "exploration",
  "intelligence_framework",
  "phase_7_zone_methodology",
  "outputs",
  "zone_scores.parquet"
)

if (!file.exists(zone_scores_path)) {
  stop(sprintf("Parquet not found: %s", zone_scores_path), call. = FALSE)
}

zone_assignments <- arrow::read_parquet(zone_scores_path) |>
  as.data.frame() |>
  mutate(
    tract_geoid = as.character(tract_geoid),
    cbsa_code = as.character(cbsa_code),
    county_geoid = as.character(county_geoid),
    zone_composite_percentile_rank = as.integer(round(national_composite_percentile)),
    cbsa_zone_composite_percentile_rank = as.integer(round(cbsa_composite_percentile)),
    zone_type_peer_percentile_rank = as.integer(round(zone_peer_composite_percentile))
  )

duplicated_tracts <- zone_assignments |>
  count(tract_geoid, name = "row_count") |>
  filter(row_count > 1L)

if (nrow(duplicated_tracts) > 0L) {
  stop(
    sprintf(
      "Expected one row per tract_geoid for mart_intelligence.intelligence_zones; found %s duplicate tracts.",
      nrow(duplicated_tracts)
    ),
    call. = FALSE
  )
}

con <- DBI::dbConnect(
  duckdb::duckdb(),
  dbdir = resolve_loader_db_path(),
  read_only = FALSE
)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS mart_intelligence;")
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "mart_intelligence", table = "intelligence_zones"),
  zone_assignments,
  overwrite = TRUE
)

written_counts <- DBI::dbGetQuery(
  con,
  "
  SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT tract_geoid) AS tract_count
  FROM mart_intelligence.intelligence_zones
  "
)

message(sprintf(
  paste(
    "Wrote %s tract rows (%s distinct tracts) to",
    "mart_intelligence.intelligence_zones from %s"
  ),
  written_counts$row_count[[1]],
  written_counts$tract_count[[1]],
  zone_scores_path
))
