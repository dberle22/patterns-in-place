library(arrow)
library(DBI)
library(duckdb)
library(dplyr)
library(here)

source(here::here("foundations", "loaders", "_shared_intelligence_loader.R"))

# The ZCTA rollup is a downstream presentation surface built from the canonical
# tract assignments. We retain the weighted composition columns so future label
# rules can change without rerunning the tract-to-ZCTA join.
if (Sys.getenv("DB_PATH") == "" && file.exists(here::here(".Renviron"))) {
  readRenviron(here::here(".Renviron"))
}

zone_scores_zcta_path <- here::here(
  "exploration",
  "intelligence_framework",
  "phase_7_zone_methodology",
  "outputs",
  "zone_scores_zcta.parquet"
)

if (!file.exists(zone_scores_zcta_path)) {
  stop(sprintf("Parquet not found: %s", zone_scores_zcta_path), call. = FALSE)
}

zone_scores_zcta <- arrow::read_parquet(zone_scores_zcta_path) |>
  as.data.frame() |>
  mutate(
    zip_geoid = as.character(zip_geoid),
    source_vintage = as.integer(source_vintage),
    tract_count = as.integer(tract_count)
  )

duplicated_zctas <- zone_scores_zcta |>
  count(zip_geoid, name = "row_count") |>
  filter(row_count > 1L)

if (nrow(duplicated_zctas) > 0L) {
  stop(
    sprintf(
      "Expected one row per zip_geoid for mart_intelligence.intelligence_zones_zcta; found %s duplicate ZCTAs.",
      nrow(duplicated_zctas)
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
  DBI::Id(schema = "mart_intelligence", table = "intelligence_zones_zcta"),
  zone_scores_zcta,
  overwrite = TRUE
)

written_counts <- DBI::dbGetQuery(
  con,
  "
  SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT zip_geoid) AS zcta_count
  FROM mart_intelligence.intelligence_zones_zcta
  "
)

message(sprintf(
  paste(
    "Wrote %s ZCTA rows (%s distinct ZCTAs) to",
    "mart_intelligence.intelligence_zones_zcta from %s"
  ),
  written_counts$row_count[[1]],
  written_counts$zcta_count[[1]],
  zone_scores_zcta_path
))
