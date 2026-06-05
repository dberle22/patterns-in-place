library(DBI)
library(duckdb)
library(glue)
library(here)

source(here::here("foundations", "etl", "R", "generic_functions.R"))

user_renv <- path.expand("~/.Renviron")
if (file.exists(user_renv)) {
  readRenviron(user_renv)
}

if (file.exists(".Renviron")) {
  readRenviron(".Renviron")
}

src_path <- get_env_path("OLD_DB_PATH")
dst_path <- get_env_path("DB_PATH")

if (is.na(src_path) || !file.exists(src_path)) {
  stop("OLD_DB_PATH must point to an existing DuckDB file.", call. = FALSE)
}

if (is.na(dst_path) || !file.exists(dst_path)) {
  stop("DB_PATH must point to an existing local DuckDB file before seeding geo.", call. = FALSE)
}

geo_tables <- c(
  "states",
  "cbsas",
  "counties",
  "tracts_all_us"
)

dst <- dbConnect(duckdb::duckdb(), dbdir = dst_path, read_only = FALSE)

on.exit({
  try(dbExecute(dst, "DETACH old_db"), silent = TRUE)
  try(dbDisconnect(dst), silent = TRUE)
}, add = TRUE)

dbExecute(dst, "CREATE SCHEMA IF NOT EXISTS geo;")
dbExecute(dst, sprintf("ATTACH %s AS old_db (READ_ONLY)", dbQuoteString(dst, src_path)))

available_tables <- dbGetQuery(
  dst,
  "
  SELECT table_name
  FROM information_schema.tables
  WHERE table_catalog = 'old_db'
    AND table_schema = 'geo'
  ORDER BY table_name
  "
)$table_name

missing_tables <- setdiff(geo_tables, available_tables)
if (length(missing_tables) > 0) {
  stop(
    glue("OLD_DB_PATH is missing required geo tables: {paste(missing_tables, collapse = ', ')}"),
    call. = FALSE
  )
}

message(glue("Seeding {length(geo_tables)} geo tables from OLD_DB_PATH."))

for (tbl in geo_tables) {
  dbExecute(
    dst,
    glue("CREATE OR REPLACE TABLE geo.{tbl} AS SELECT * FROM old_db.geo.{tbl}")
  )
  row_count <- dbGetQuery(dst, glue("SELECT COUNT(*) AS n FROM geo.{tbl}"))$n[[1]]
  message(glue("  seeded geo.{tbl} ({row_count} rows)"))
}

message("Geo seed complete.")
