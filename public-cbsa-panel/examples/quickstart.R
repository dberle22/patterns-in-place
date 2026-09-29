# Print a small v2026.1 affordability query from a canonical release directory.
arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 1) {
  stop("Usage: Rscript quickstart.R <canonical-release-directory-url>")
}

# The httpfs extension lets DuckDB read published Source Cooperative Parquet directly.
panel_base_url <- sub("/$", "", arguments[[1]])
connection <- DBI::dbConnect(duckdb::duckdb())
on.exit(DBI::dbDisconnect(connection, shutdown = TRUE), add = TRUE)
DBI::dbExecute(connection, "INSTALL httpfs")
DBI::dbExecute(connection, "LOAD httpfs")

query <- sprintf(
  paste(
    "SELECT geo_name, annualized_median_rent, rent_to_income",
    "FROM read_parquet('%s/affordability_wide.parquet')",
    "WHERE year = 2024 ORDER BY rent_to_income DESC LIMIT 10"
  ),
  panel_base_url
)
print(DBI::dbGetQuery(connection, query))
