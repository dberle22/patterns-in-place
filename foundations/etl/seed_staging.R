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

if (is.na(dst_path)) {
  stop("DB_PATH must be set before seeding staging.", call. = FALSE)
}

if (file.exists(dst_path)) {
  stop("DB_PATH already exists. Remove the destination DB before re-running seed_staging.R.", call. = FALSE)
}

dst <- dbConnect(duckdb::duckdb(), dbdir = dst_path, read_only = FALSE)

on.exit({
  try(dbExecute(dst, "DETACH old_db"), silent = TRUE)
  try(dbDisconnect(dst), silent = TRUE)
}, add = TRUE)

dbExecute(dst, "CREATE SCHEMA IF NOT EXISTS staging;")
dbExecute(dst, "CREATE SCHEMA IF NOT EXISTS silver;")
dbExecute(dst, "CREATE SCHEMA IF NOT EXISTS gold;")
dbExecute(dst, sprintf("ATTACH %s AS old_db (READ_ONLY)", dbQuoteString(dst, src_path)))

tables <- dbGetQuery(
  dst,
  "
  SELECT table_name
  FROM information_schema.tables
  WHERE table_catalog = 'old_db'
    AND table_schema = 'staging'
  ORDER BY table_name
  "
)

message(glue("Found {nrow(tables)} staging tables to seed."))

for (tbl in tables$table_name) {
  dbExecute(
    dst,
    glue("CREATE OR REPLACE TABLE staging.{tbl} AS SELECT * FROM old_db.staging.{tbl}")
  )
  row_count <- dbGetQuery(dst, glue("SELECT COUNT(*) AS n FROM staging.{tbl}"))$n[[1]]
  message(glue("  seeded staging.{tbl} ({row_count} rows)"))
}

message("Staging seed complete.")
