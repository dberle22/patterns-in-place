# Shared helpers for Supply Character production visuals.
#
# This file keeps the section's standalone chart scripts small by centralizing
# the repeated production work:
# - resolve repo-relative paths
# - connect to the materialized DuckDB
# - load shared visual-library helpers
# - run local section SQL files
# - export stable PNG outputs

suppressPackageStartupMessages({
  library(DBI)
  library(duckdb)
  library(sf)
  library(ggplot2)
})

supply_get_script_path <- function(default_path) {
  file_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
  if (length(file_arg) == 0) {
    return(normalizePath(default_path, mustWork = FALSE))
  }
  normalizePath(sub("^--file=", "", file_arg[[1]]), mustWork = FALSE)
}

supply_build_context <- function(script_path) {
  visual_dir <- dirname(script_path)
  section_dir <- dirname(visual_dir)
  repo_root <- normalizePath(file.path(section_dir, "..", "..", "..", ".."))

  list(
    script_path = script_path,
    visual_dir = visual_dir,
    section_dir = section_dir,
    repo_root = repo_root,
    foundations_dir = file.path(repo_root, "foundations"),
    sql_dir = file.path(section_dir, "sql"),
    output_dir = file.path(section_dir, "outputs"),
    db_path = file.path(
      repo_root,
      "foundations",
      "etl",
      "data",
      "duckdb",
      "patterns_in_place.duckdb"
    )
  )
}

supply_read_sql <- function(path) {
  paste(readLines(path, warn = FALSE), collapse = "\n")
}

supply_with_foundations_wd <- function(foundations_dir, expr) {
  old_wd <- getwd()
  on.exit(setwd(old_wd), add = TRUE)
  setwd(foundations_dir)
  force(expr)
}

supply_load_visual_library <- function(foundations_dir, chart_types = character()) {
  supply_with_foundations_wd(foundations_dir, {
    source("visual_library/shared/standards.R")
    source("visual_library/shared/chart_utils.R")
    source("visual_library/shared/data_contracts.R")

    for (chart_type in chart_types) {
      source(file.path("visual_library", "shared", "prep", paste0("prep_", chart_type, ".R")))
      source(file.path("visual_library", "shared", "render", paste0("render_", chart_type, ".R")))
    }
  })
}

supply_connect_duckdb <- function(db_path) {
  duckdb_drv <- duckdb::duckdb(dbdir = db_path, read_only = TRUE)
  con <- DBI::dbConnect(duckdb_drv)
  try(DBI::dbExecute(con, "LOAD spatial"), silent = TRUE)
  con
}

supply_run_sql_file <- function(con, sql_dir, filename) {
  DBI::dbGetQuery(con, supply_read_sql(file.path(sql_dir, filename)))
}

supply_save_plot <- function(plot, output_path, width, height) {
  dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
  ggplot2::ggsave(
    output_path,
    plot = plot,
    width = width,
    height = height,
    dpi = 300,
    bg = "white"
  )
  output_path
}

supply_load_contiguous_states_context <- function(con) {
  states_sql <- paste(
    "SELECT state_abbr, state_name, ST_AsText(geom) AS geom_wkt",
    "FROM geo.states",
    "WHERE state_abbr NOT IN ('AK', 'HI', 'PR')"
  )
  states_raw <- DBI::dbGetQuery(con, states_sql)
  sf::st_as_sf(states_raw, wkt = "geom_wkt", crs = 4326)
}

supply_load_contiguous_us_outline <- function(states_sf) {
  outline_geom <- sf::st_union(states_sf)
  sf::st_sf(
    data.frame(layer = "contiguous_us"),
    geometry = sf::st_sfc(outline_geom, crs = sf::st_crs(states_sf))
  )
}
