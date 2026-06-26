library(arrow)
library(DBI)
library(duckdb)
library(dplyr)
library(here)
library(readr)
library(tidyr)

resolve_loader_db_path <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  arg_db_path <- if (length(args) >= 1) args[[1]] else ""
  env_db_path <- Sys.getenv("DB_PATH", unset = "")

  db_path <- if (nzchar(arg_db_path)) arg_db_path else env_db_path

  if (!nzchar(db_path)) {
    stop(
      "Set DB_PATH or pass the DuckDB path as the first script argument before running intelligence loaders.",
      call. = FALSE
    )
  }

  db_path
}

write_intelligence_datamart <- function(parquet_rel_path, table_name, transform_fn) {
  parquet_path <- here::here(parquet_rel_path)

  if (!file.exists(parquet_path)) {
    stop(sprintf("Parquet not found: %s", parquet_path), call. = FALSE)
  }

  datamart_df <- arrow::read_parquet(parquet_path) |>
    as.data.frame() |>
    transform_fn()

  if ("cbsa_code" %in% names(datamart_df)) {
    unique_cbsa_codes <- unique(datamart_df$cbsa_code)
    if (length(unique_cbsa_codes) != nrow(datamart_df)) {
      stop(
        sprintf("Expected one row per cbsa_code for mart_intelligence.%s.", table_name),
        call. = FALSE
      )
    }
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
    DBI::Id(schema = "mart_intelligence", table = table_name),
    datamart_df,
    overwrite = TRUE
  )

  written_rows <- DBI::dbGetQuery(
    con,
    sprintf("SELECT COUNT(*) AS n FROM mart_intelligence.%s", table_name)
  )$n[[1]]

  message(sprintf(
    "Wrote %s rows to mart_intelligence.%s from %s",
    written_rows,
    table_name,
    parquet_rel_path
  ))
}

read_optional_csv <- function(csv_rel_path) {
  csv_path <- here::here(csv_rel_path)

  if (!file.exists(csv_path)) {
    stop(sprintf("CSV not found: %s", csv_path), call. = FALSE)
  }

  readr::read_csv(csv_path, show_col_types = FALSE)
}

build_peer_wide <- function(csv_rel_path) {
  peer_long <- read_optional_csv(csv_rel_path) |>
    mutate(
      cbsa_code = as.character(cbsa_code),
      peer_cbsa_code = as.character(peer_cbsa_code),
      peer_rank = as.integer(peer_rank)
    )

  peer_codes <- peer_long |>
    select(cbsa_code, peer_rank, peer_cbsa_code) |>
    pivot_wider(
      names_from = peer_rank,
      values_from = peer_cbsa_code,
      names_glue = "top10_peer_{peer_rank}_cbsa_code"
    )

  peer_names <- peer_long |>
    select(cbsa_code, peer_rank, peer_cbsa_name) |>
    pivot_wider(
      names_from = peer_rank,
      values_from = peer_cbsa_name,
      names_glue = "top10_peer_{peer_rank}_cbsa_name"
    )

  peer_similarity <- peer_long |>
    select(cbsa_code, peer_rank, cosine_similarity) |>
    pivot_wider(
      names_from = peer_rank,
      values_from = cosine_similarity,
      names_glue = "top10_peer_{peer_rank}_similarity"
    )

  peer_codes |>
    left_join(peer_names, by = "cbsa_code") |>
    left_join(peer_similarity, by = "cbsa_code")
}
