# Shared helper functions for Retail Opportunity Finder section modules

suppressPackageStartupMessages({
  library(dplyr)
  library(glue)
})

resolve_project_root <- function() {
  project <- get_env_path("METRO")
  if (is.na(project) || !nzchar(project)) {
    project <- normalizePath(".", winslash = "/", mustWork = TRUE)
  }
  project
}

resolve_sql_path <- function(name, group = c("features", "qa", "staging")) {
  group <- match.arg(group)
  sql_group <- SQL_PATHS[[group]]

  if (is.null(sql_group) || is.null(sql_group[[name]])) {
    stop(glue("Unknown SQL registry entry: {group}/{name}"), call. = FALSE)
  }

  sql_path <- file.path(resolve_project_root(), sql_group[[name]])
  if (!file.exists(sql_path)) {
    stop(glue("SQL file not found: {sql_path}"), call. = FALSE)
  }

  sql_path
}

get_market_profile <- function(key = ACTIVE_MARKET_KEY) {
  profile <- MARKET_PROFILES[[key]]
  if (is.null(profile)) {
    stop(glue("Unknown market profile key: {key}"), call. = FALSE)
  }
  profile
}

get_market_context <- function(key = ACTIVE_MARKET_KEY) {
  profile <- get_market_profile(key)

  list(
    market_key = profile$market_key,
    cbsa_code = profile$cbsa_code,
    state_scope = profile$state_scope,
    labels = profile$labels
  )
}

get_market_state_scope <- function(profile = get_market_profile()) {
  state_scope <- profile$state_scope
  if (is.null(state_scope)) {
    state_scope <- character()
  }

  states <- unique(as.character(state_scope))
  states <- states[nzchar(states)]

  if (length(states) == 0) {
    stop(
      glue("Market profile '{profile$market_key}' is missing a usable state_scope."),
      call. = FALSE
    )
  }

  states
}

unsupported_geometry_source_message <- function(profile = get_market_profile(), geometry_type = "tract") {
  states <- paste(get_market_state_scope(profile), collapse = ", ")
  supported_states <- names(GEOMETRY_SOURCE_REGISTRY$tract_tables)

  glue(
    "Unsupported {geometry_type} geometry source for market '{profile$market_key}' ",
    "(cbsa_code={profile$cbsa_code}, state_scope={states}). ",
    "The legacy tract geometry adapter only supports single-state scope values: ",
    "{paste(supported_states, collapse = ', ')}. ",
    "Managed ROF consumers should prefer foundation geometry tables or the ",
    "upstream national tract source once metro_deep_dive.geo.tracts_all_us is materialized."
  )
}

resolve_tract_geometry_table <- function(profile = get_market_profile()) {
  states <- get_market_state_scope(profile)

  if (length(states) != 1) {
    stop(unsupported_geometry_source_message(profile, "tract"), call. = FALSE)
  }

  table_name <- GEOMETRY_SOURCE_REGISTRY$tract_tables[[states[[1]]]]
  if (is.null(table_name) || !nzchar(table_name)) {
    stop(unsupported_geometry_source_message(profile, "tract"), call. = FALSE)
  }

  table_name
}

build_cbsa_geometry_query <- function(profile = get_market_profile(), cbsa_code = profile$cbsa_code) {
  glue("
    SELECT
      cbsa_code,
      cbsa_name,
      ST_AsWKB(geom) AS geom_wkb
    FROM {GEOMETRY_SOURCE_REGISTRY$cbsa_table}
    WHERE cbsa_code = '{cbsa_code}'
  ")
}

build_county_geometry_query <- function(profile = get_market_profile(), cbsa_code = profile$cbsa_code) {
  glue("
    WITH cbsa_counties AS (
      SELECT DISTINCT county_geoid, cbsa_code
      FROM metro_deep_dive.silver.xwalk_cbsa_county
      WHERE cbsa_code = '{cbsa_code}'
    )
    SELECT
      c.county_geoid,
      c.county_name,
      c.state_fips,
      cbsa_counties.cbsa_code,
      ST_AsWKB(c.geom) AS geom_wkb
    FROM {GEOMETRY_SOURCE_REGISTRY$county_table} c
    INNER JOIN cbsa_counties ON c.county_geoid = cbsa_counties.county_geoid
  ")
}

build_tract_geometry_query <- function(profile = get_market_profile(), cbsa_code = profile$cbsa_code) {
  tract_table <- resolve_tract_geometry_table(profile)

  glue("
    WITH cbsa_counties AS (
      SELECT DISTINCT county_geoid, cbsa_code
      FROM metro_deep_dive.silver.xwalk_cbsa_county
      WHERE cbsa_code = '{cbsa_code}'
    ),
    tracts AS (
      SELECT
        tract_geoid,
        printf('%02d%03d', CAST(state_fip AS INTEGER), CAST(county_fip AS INTEGER)) AS county_geoid
      FROM metro_deep_dive.silver.xwalk_tract_county
    ),
    tracts_final AS (
      SELECT t.tract_geoid, t.county_geoid, c.cbsa_code
      FROM tracts t
      JOIN cbsa_counties c ON t.county_geoid = c.county_geoid
    )
    SELECT
      geo.tract_geoid,
      geo.county_geoid,
      geo.state_fips,
      tr.cbsa_code,
      ST_AsWKB(geo.geom) AS geom_wkb
    FROM {tract_table} geo
    INNER JOIN tracts_final tr ON geo.tract_geoid = tr.tract_geoid
  ")
}

query_cbsa_geometry_wkb <- function(con, profile = get_market_profile(), cbsa_code = profile$cbsa_code) {
  DBI::dbGetQuery(con, build_cbsa_geometry_query(profile = profile, cbsa_code = cbsa_code))
}

query_county_geometry_wkb <- function(con, profile = get_market_profile(), cbsa_code = profile$cbsa_code) {
  DBI::dbGetQuery(con, build_county_geometry_query(profile = profile, cbsa_code = cbsa_code))
}

query_tract_geometry_wkb <- function(con, profile = get_market_profile(), cbsa_code = profile$cbsa_code) {
  DBI::dbGetQuery(con, build_tract_geometry_query(profile = profile, cbsa_code = cbsa_code))
}

sf_from_wkb_df <- function(df, data_cols, geometry_col = "geom_wkb", crs = GEOMETRY_ASSUMPTIONS$expected_crs_epsg) {
  if (!geometry_col %in% names(df)) {
    stop(glue("WKB column not found: {geometry_col}"), call. = FALSE)
  }

  missing_data_cols <- setdiff(data_cols, names(df))
  if (length(missing_data_cols) > 0) {
    stop(
      glue("Cannot build sf object; missing columns: {paste(missing_data_cols, collapse = ', ')}"),
      call. = FALSE
    )
  }

  if (nrow(df) == 0) {
    empty_geom <- sf::st_sfc(crs = crs)
    return(sf::st_sf(df[, data_cols, drop = FALSE], geometry = empty_geom))
  }

  wkb_list <- df[[geometry_col]]
  if (inherits(wkb_list, "blob")) {
    wkb_list <- lapply(wkb_list, function(x) x)
  }

  geom <- sf::st_as_sfc(structure(wkb_list, class = "WKB"), crs = crs)
  sf::st_sf(df[, data_cols, drop = FALSE], geometry = geom)
}

validate_market_profile <- function(profile) {
  required_top_level <- c(
    "market_key", "cbsa_code", "state_scope",
    "benchmark_region_type", "benchmark_region_value", "benchmark_region_label",
    "peers", "labels"
  )
  required_labels <- c("cbsa_name", "cbsa_name_full", "market_name", "peer_group", "target_flag", "us_label")

  missing_top_level <- setdiff(required_top_level, names(profile))
  label_names <- if (is.list(profile$labels)) names(profile$labels) else character()
  missing_labels <- setdiff(required_labels, label_names)

  list(
    market_key = if (!is.null(profile$market_key)) profile$market_key else NA_character_,
    missing_top_level = missing_top_level,
    missing_labels = missing_labels,
    has_cbsa_code = !is.null(profile$cbsa_code) && nzchar(profile$cbsa_code),
    has_state_scope = !is.null(profile$state_scope) && length(profile$state_scope) > 0,
    has_peers = !is.null(profile$peers) && length(profile$peers) > 0,
    pass = length(missing_top_level) == 0 &&
      length(missing_labels) == 0 &&
      !is.null(profile$cbsa_code) && nzchar(profile$cbsa_code) &&
      !is.null(profile$state_scope) && length(profile$state_scope) > 0 &&
      !is.null(profile$peers) && length(profile$peers) > 0
  )
}

market_label <- function(name, profile = get_market_profile()) {
  labels <- profile$labels
  if (is.null(labels[[name]])) {
    stop(glue("Unknown market label: {name}"), call. = FALSE)
  }
  labels[[name]]
}

resolve_market_output_dir <- function(section_id, key = ACTIVE_MARKET_KEY, subdir = NULL) {
  market_context <- get_market_context(key)

  base_output_root <- if (identical(Sys.getenv("ROF_OUTPUT_MODE", unset = ""), "notebook_build")) {
    "notebooks/retail_opportunity_finder/notebook_build/sections"
  } else {
    SECTION_OUTPUT_ROOT
  }

  output_dir <- file.path(base_output_root, section_id, "outputs", market_context$market_key)

  if (!is.null(subdir) && nzchar(subdir)) {
    output_dir <- file.path(output_dir, subdir)
  }

  output_dir
}

resolve_output_path <- function(section_id, artifact_name, ext = "rds", key = ACTIVE_MARKET_KEY, subdir = NULL) {
  artifact_file <- if (!is.null(ext) && nzchar(ext)) {
    paste0(artifact_name, ".", ext)
  } else {
    artifact_name
  }

  file.path(resolve_market_output_dir(section_id, key = key, subdir = subdir), artifact_file)
}

resolve_legacy_output_path <- function(section_id, artifact_name, ext = "rds", subdir = NULL) {
  artifact_file <- if (!is.null(ext) && nzchar(ext)) {
    paste0(artifact_name, ".", ext)
  } else {
    artifact_name
  }

  output_dir <- file.path(SECTION_OUTPUT_ROOT, section_id, "outputs")
  if (!is.null(subdir) && nzchar(subdir)) {
    output_dir <- file.path(output_dir, subdir)
  }

  file.path(output_dir, artifact_file)
}

read_artifact_path <- function(section_id, artifact_name, ext = "rds", key = ACTIVE_MARKET_KEY, subdir = NULL) {
  market_path <- resolve_output_path(section_id, artifact_name, ext = ext, key = key, subdir = subdir)
  if (file.exists(market_path)) {
    return(market_path)
  }

  stop(
    glue(
      "Artifact not found for section '{section_id}': looked for '{market_path}'."
    ),
    call. = FALSE
  )
}

resolve_duckdb_path <- function() {
  data_root <- get_env_path("DATA")
  if (is.na(data_root) || !nzchar(data_root)) {
    stop("Environment variable DATA is required to resolve DuckDB path.", call. = FALSE)
  }
  file.path(data_root, "duckdb", "metro_deep_dive.duckdb")
}

connect_project_duckdb <- function(read_only = TRUE) {
  db_path <- resolve_duckdb_path()
  if (!file.exists(db_path)) {
    stop(glue("DuckDB file not found: {db_path}"), call. = FALSE)
  }
  con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = read_only)
  DBI::dbExecute(con, "LOAD spatial;")
  con
}

resolve_parcel_standardized_root <- function(root = PARCEL_STANDARDIZATION_ROOT) {
  if (is.na(root) || !nzchar(root)) {
    stop("Parcel standardized root is not configured.", call. = FALSE)
  }

  if (!dir.exists(root)) {
    stop(glue("Parcel standardized root not found: {root}"), call. = FALSE)
  }

  root
}

read_parcel_ingest_manifest <- function(root = PARCEL_STANDARDIZATION_ROOT) {
  manifest_path <- file.path(resolve_parcel_standardized_root(root), "parcel_ingest_manifest.rds")
  if (!file.exists(manifest_path)) {
    stop(glue("Parcel ingest manifest not found: {manifest_path}"), call. = FALSE)
  }
  readRDS(manifest_path)
}

resolve_parcel_analysis_paths <- function(root = PARCEL_STANDARDIZATION_ROOT, prefer_manifest = TRUE) {
  parcel_root <- resolve_parcel_standardized_root(root)

  if (isTRUE(prefer_manifest)) {
    manifest_path <- file.path(parcel_root, "parcel_ingest_manifest.rds")
    if (file.exists(manifest_path)) {
      manifest <- readRDS(manifest_path)
      paths <- manifest$analysis_path[!is.na(manifest$analysis_path) & file.exists(manifest$analysis_path)]
      if (length(paths) > 0) {
        return(unique(paths))
      }
    }
  }

  Sys.glob(file.path(parcel_root, "county_outputs", "*", "parcel_geometries_analysis.rds"))
}

read_sql_file <- function(path) {
  paste(readLines(path, warn = FALSE), collapse = "\n")
}

query_df_sql_file <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}

assert_required_columns <- function(df, required, df_name = "data.frame") {
  missing <- setdiff(required, names(df))
  if (length(missing) > 0) {
    stop(glue("{df_name} missing required columns: {paste(missing, collapse = ', ')}"), call. = FALSE)
  }
  invisible(TRUE)
}

validate_columns <- function(df, required, df_name = "data.frame") {
  missing <- setdiff(required, names(df))
  list(
    dataset = df_name,
    n_rows = nrow(df),
    n_cols = ncol(df),
    missing_columns = missing,
    missing_count = length(missing),
    pass = length(missing) == 0
  )
}

validate_unique_key <- function(df, key_col, df_name = "data.frame") {
  if (!key_col %in% names(df)) {
    return(list(dataset = df_name, key = key_col, pass = FALSE, issue = "missing_key_column"))
  }
  n <- nrow(df)
  n_distinct <- dplyr::n_distinct(df[[key_col]])
  list(
    dataset = df_name,
    key = key_col,
    n_rows = n,
    n_distinct = n_distinct,
    duplicates = n - n_distinct,
    pass = n == n_distinct
  )
}

null_rate_summary <- function(df, cols, df_name = "data.frame") {
  cols <- intersect(cols, names(df))
  if (length(cols) == 0) {
    return(data.frame(dataset = character(), column = character(), null_rate = numeric()))
  }
  out <- lapply(cols, function(col) {
    data.frame(
      dataset = df_name,
      column = col,
      null_rate = mean(is.na(df[[col]])),
      stringsAsFactors = FALSE
    )
  })
  dplyr::bind_rows(out)
}

validate_sf <- function(sf_obj, name = "sf_object", expected_epsg = 4326) {
  is_sf <- inherits(sf_obj, "sf")
  n <- if (is_sf) nrow(sf_obj) else NA_integer_
  crs <- if (is_sf) sf::st_crs(sf_obj)$epsg else NA_integer_
  n_empty <- if (is_sf) sum(sf::st_is_empty(sf_obj)) else NA_integer_
  validity <- if (is_sf) sf::st_is_valid(sf_obj) else NA
  invalid <- if (is_sf) sum(!validity, na.rm = TRUE) else NA_integer_

  list(
    dataset = name,
    is_sf = is_sf,
    n_rows = n,
    crs_epsg = crs,
    empty_geometries = n_empty,
    invalid_geometries = invalid,
    pass = is_sf &&
      !is.na(n) && n > 0 &&
      !is.na(crs) && crs == expected_epsg &&
      !is.na(n_empty) && n_empty == 0 &&
      !is.na(invalid) && invalid == 0
  )
}

zscore <- function(x) {
  s <- stats::sd(x, na.rm = TRUE)
  if (is.na(s) || s == 0) return(rep(0, length(x)))
  (x - mean(x, na.rm = TRUE)) / s
}

pct_rank <- function(x) {
  dplyr::percent_rank(x)
}

run_metadata <- function() {
  git_hash <- tryCatch(
    system("git rev-parse --short HEAD", intern = TRUE),
    error = function(e) NA_character_
  )
  if (length(git_hash) == 0) git_hash <- NA_character_

  market_profile <- if (exists("ACTIVE_MARKET_KEY") && exists("MARKET_PROFILES")) {
    tryCatch(get_market_profile(), error = function(e) NULL)
  } else {
    NULL
  }

  list(
    run_timestamp = as.character(Sys.time()),
    r_version = as.character(getRversion()),
    git_hash = git_hash,
    market_key = if (!is.null(market_profile)) market_profile$market_key else NA_character_,
    market_name = if (!is.null(market_profile)) market_profile$labels$market_name else NA_character_,
    target_cbsa = if (exists("TARGET_CBSA")) TARGET_CBSA else NA_character_,
    target_vintage = if (exists("TARGET_VINTAGE")) TARGET_VINTAGE else NA_character_,
    baseline_vintage = if (exists("BASELINE_VINTAGE")) BASELINE_VINTAGE else NA_character_,
    target_year = if (exists("TARGET_YEAR")) TARGET_YEAR else NA_integer_
  )
}

validate_model_params <- function(model_params) {
  required_weights <- c("growth", "units", "headroom", "price", "commute", "income")
  has_weights <- all(required_weights %in% names(model_params$weights))
  weight_sum <- sum(model_params$weights[required_weights])

  list(
    has_required_weights = has_weights,
    weights_sum_to_one = isTRUE(all.equal(weight_sum, 1, tolerance = 1e-9)),
    weight_sum = weight_sum,
    pass = has_weights && isTRUE(all.equal(weight_sum, 1, tolerance = 1e-9))
  )
}

save_artifact <- function(obj, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  saveRDS(obj, path)
}
