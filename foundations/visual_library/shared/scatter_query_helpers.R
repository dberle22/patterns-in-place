# Query helpers for scatter chart sample pipelines.

get_env_path <- function(key) {
  val <- Sys.getenv(key, unset = "")
  if (!nzchar(val)) return(NA_character_)
  path.expand(val)
}

read_sql_file <- function(path) {
  if (!file.exists(path)) {
    stop(paste("SQL file not found:", path))
  }
  paste(readLines(path, warn = FALSE), collapse = "\n")
}

connect_metro_duckdb <- function(read_only = TRUE) {
  if (!requireNamespace("DBI", quietly = TRUE) || !requireNamespace("duckdb", quietly = TRUE)) {
    stop("Packages DBI and duckdb are required.")
  }

  data_root <- get_env_path("DATA")
  if (is.na(data_root)) stop("DATA environment variable is not set.")

  db_path <- file.path(data_root, "duckdb", "metro_deep_dive.duckdb")
  if (!file.exists(db_path)) stop(paste("DuckDB not found:", db_path))

  DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = read_only)
}

run_scatter_query <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}
