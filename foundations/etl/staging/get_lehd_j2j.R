# In this script we land annualized LEHD J2J state and metro rows for the
# approved first-pass scope. We intentionally keep the source-faithful J2J
# mobility measures we expect to use downstream, but only for:
# 1. state geography and metro geography
# 2. worker age x industry rows, filtered to all-sex rows
# 3. the latest rolling 5 completed years in each source file
# 4. the counts table (`j2j`) only, with published rates (`j2jr`) deferred to
#    validation rather than managed storage
#
# We collapse quarter rows to one annual row per geography / year / industry /
# age slice. That keeps staging materially smaller while preserving the labor
# mobility signals we expect to use downstream.
#
# Silver will own any later rate derivations from these annual counts rather
# than persisting a second J2JR table with the same dimensional lattice.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the first-pass scope ----
j2j_base_url <- "https://lehd.ces.census.gov/data/j2j/latest_release"
j2j_keep_years <- 5L
j2j_state_scopes_default <- c(tolower(state.abb), "dc")

# We keep the KPI annualization rules explicit because J2J mixes event-flow
# counts, stock/reference counts, and average earnings in the same wide row.
# Annual rows should:
# - sum event counts across quarters
# - average stock/reference counts across observed quarters
# - average earnings measures across observed quarters
j2j_sum_measures <- c(
  "MHire",
  "MSep",
  "MJobStart",
  "MJobEnd",
  "EEHire",
  "EESep",
  "AQHire",
  "AQSep",
  "J2JHire",
  "J2JSep",
  "NEHire",
  "ENSep",
  "EESepS",
  "EEHireS",
  "AQSepS",
  "AQHireS"
)

j2j_avg_count_measures <- c(
  "NEPersist",
  "ENPersist",
  "NEFullQ",
  "ENFullQ",
  "MainB",
  "MainE",
  "NEPersistS",
  "ENPersistS",
  "JobStayS",
  "MainBS",
  "MainES"
)

j2j_avg_earn_measures <- c(
  "NEHireSEarn_Dest",
  "ENSepSEarn_Orig",
  "JobStaySEarn_Orig",
  "JobStaySEarn_Dest",
  "EESepSEarn_Orig",
  "EEHireSEarn_Dest",
  "AQSepSEarn_Orig",
  "AQHireSEarn_Dest"
)

resolve_j2j_append_mode <- function(env_var = "LEHD_J2J_APPEND_MODE") {
  raw_value <- Sys.getenv(env_var, unset = "")

  if (!nzchar(raw_value)) {
    return(FALSE)
  }

  normalized_value <- tolower(trimws(raw_value))

  if (normalized_value %in% c("1", "true", "t", "yes", "y")) {
    return(TRUE)
  }

  if (normalized_value %in% c("0", "false", "f", "no", "n")) {
    return(FALSE)
  }

  stop(
    sprintf(
      "Invalid %s value: %s. Use TRUE/FALSE, YES/NO, or 1/0.",
      env_var,
      raw_value
    ),
    call. = FALSE
  )
}

resolve_j2j_state_scope <- function(env_var = "LEHD_J2J_STATE_SCOPE") {
  # This optional env var lets us run one or a few state scopes during
  # development without changing the default production list.
  raw_value <- Sys.getenv(env_var, unset = "")

  if (!nzchar(raw_value)) {
    return(j2j_state_scopes_default)
  }

  scopes <- raw_value %>%
    stringr::str_split(",") %>%
    purrr::pluck(1) %>%
    stringr::str_trim() %>%
    tolower() %>%
    unique()

  invalid_scopes <- setdiff(scopes, j2j_state_scopes_default)
  if (length(invalid_scopes) > 0) {
    stop(
      sprintf(
        "Invalid %s values: %s",
        env_var,
        paste(invalid_scopes, collapse = ", ")
      ),
      call. = FALSE
    )
  }

  scopes
}

download_j2j_asset <- function(url, dest_path) {
  resp <- httr::GET(
    url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)

  writeBin(httr::content(resp, "raw"), dest_path)
  dest_path
}

fetch_j2j_metro_metadata <- function() {
  # The metro release publishes one metadata line per CBSA/micro area. We use
  # it both to discover the available metro codes and to preserve file-level
  # provenance for each annualized batch.
  metro_version_tmp <- tempfile(pattern = "lehd_j2j_metro_version_", fileext = ".txt")
  download_j2j_asset(
    url = glue("{j2j_base_url}/metro/j2j/version_j2j.txt"),
    dest_path = metro_version_tmp
  )
  on.exit(unlink(metro_version_tmp), add = TRUE)

  version_lines <- readLines(metro_version_tmp, warn = FALSE)
  non_empty_lines <- version_lines[nzchar(trimws(version_lines))]

  purrr::map_dfr(non_empty_lines, function(line) {
    parts <- stringr::str_split(trimws(line), "\\s+")[[1]]

    if (length(parts) < 7 || parts[1] != "J2J" || parts[2] != "METRO") {
      return(NULL)
    }

    tibble::tibble(
      source_scope_type = "metro",
      source_scope_id = parts[3],
      state_scope = "metro",
      metadata_type = parts[1],
      metadata_geo_scope = parts[2],
      metadata_geo_code = parts[3],
      metadata_period_range = parts[4],
      schema_version = parts[5],
      release_id = parts[6],
      metadata_source_id = parts[7]
    )
  })
}

resolve_j2j_metro_scope <- function(metro_metadata, env_var = "LEHD_J2J_METRO_SCOPE") {
  # This optional env var lets us run one or a few metro codes during
  # development. By default we ingest the full current metro menu.
  raw_value <- Sys.getenv(env_var, unset = "")
  available_codes <- metro_metadata$source_scope_id

  if (!nzchar(raw_value)) {
    return(available_codes)
  }

  scopes <- raw_value %>%
    stringr::str_split(",") %>%
    purrr::pluck(1) %>%
    stringr::str_trim() %>%
    unique()

  invalid_scopes <- setdiff(scopes, available_codes)
  if (length(invalid_scopes) > 0) {
    stop(
      sprintf(
        "Invalid %s values: %s",
        env_var,
        paste(invalid_scopes, collapse = ", ")
      ),
      call. = FALSE
    )
  }

  scopes
}

parse_j2j_state_metadata <- function(version_lines, state_scope) {
  non_empty_lines <- version_lines[nzchar(trimws(version_lines))]
  j2j_line <- non_empty_lines[stringr::str_detect(non_empty_lines, "^J2J\\s")][1]

  if (is.na(j2j_line) || !nzchar(j2j_line)) {
    stop(
      glue("J2J version metadata for scope {state_scope} is missing a J2J line."),
      call. = FALSE
    )
  }

  parts <- stringr::str_split(trimws(j2j_line), "\\s+")[[1]]

  if (length(parts) < 7) {
    stop(
      glue("J2J version metadata for scope {state_scope} is malformed: {j2j_line}"),
      call. = FALSE
    )
  }

  tibble::tibble(
    source_scope_type = "state",
    source_scope_id = state_scope,
    state_scope = state_scope,
    metadata_type = parts[1],
    metadata_geo_scope = parts[2],
    metadata_geo_code = parts[3],
    metadata_period_range = parts[4],
    schema_version = parts[5],
    release_id = parts[6],
    metadata_source_id = parts[7]
  )
}

build_j2j_csv_url <- function(source_scope_type, source_scope_id) {
  if (identical(source_scope_type, "state")) {
    return(
      glue(
        "{j2j_base_url}/{source_scope_id}/j2j/j2j_{source_scope_id}_sa_f_gs_ns_oslp_u.csv.gz"
      )
    )
  }

  if (identical(source_scope_type, "metro")) {
    return(
      glue(
        "{j2j_base_url}/metro/j2j/j2j_{source_scope_id}_sarhe_f_gb_ns_oslp_u.csv.gz"
      )
    )
  }

  stop(glue("Unsupported J2J scope type: {source_scope_type}"), call. = FALSE)
}

build_j2j_version_url <- function(state_scope) {
  glue("{j2j_base_url}/{state_scope}/j2j/version_j2j.txt")
}

build_j2j_source_filename <- function(source_scope_type, source_scope_id) {
  if (identical(source_scope_type, "state")) {
    return(glue("j2j_{source_scope_id}_sa_f_gs_ns_oslp_u.csv.gz"))
  }

  if (identical(source_scope_type, "metro")) {
    return(glue("j2j_{source_scope_id}_sarhe_f_gb_ns_oslp_u.csv.gz"))
  }

  stop(glue("Unsupported J2J scope type: {source_scope_type}"), call. = FALSE)
}

build_measure_sql <- function(measures, agg_fun, prefix) {
  glue::glue_collapse(
    glue("{agg_fun}(CAST({measures} AS DOUBLE)) AS {prefix}_{tolower(measures)}"),
    sep = ",\n        "
  )
}

create_j2j_batch_table <- function(con, csv_path, metadata_row, source_file) {
  # DuckDB can scan the compressed CSV directly, filter in SQL, determine the
  # latest completed source year, and annualize in SQL so we only materialize
  # the retained state/metro age-industry subset we plan to manage in staging.
  csv_path_sql <- DBI::dbQuoteString(con, csv_path)
  source_file_sql <- DBI::dbQuoteString(con, source_file)
  source_scope_type_sql <- DBI::dbQuoteString(con, metadata_row$source_scope_type[[1]])
  source_scope_id_sql <- DBI::dbQuoteString(con, metadata_row$source_scope_id[[1]])
  state_scope_sql <- DBI::dbQuoteString(con, metadata_row$state_scope[[1]])
  release_id_sql <- DBI::dbQuoteString(con, metadata_row$release_id[[1]])
  schema_version_sql <- DBI::dbQuoteString(con, metadata_row$schema_version[[1]])
  metadata_period_range_sql <- DBI::dbQuoteString(con, metadata_row$metadata_period_range[[1]])
  geo_level_sql <- if (identical(metadata_row$source_scope_type[[1]], "state")) "'S'" else "'B'"
  state_fips_sql <- if (identical(metadata_row$source_scope_type[[1]], "state")) "SUBSTR(geo_id, 1, 2)" else "CAST(NULL AS VARCHAR)"
  sum_sql <- build_measure_sql(j2j_sum_measures, "SUM", "annual")
  avg_count_sql <- build_measure_sql(j2j_avg_count_measures, "AVG", "annual_avg")
  avg_earn_sql <- build_measure_sql(j2j_avg_earn_measures, "AVG", "annual_avg")

  DBI::dbExecute(con, "DROP TABLE IF EXISTS j2j_batch")

  DBI::dbExecute(
    con,
    glue(
      "
      CREATE TEMP TABLE j2j_batch AS
      WITH src AS (
        SELECT *
        FROM read_csv_auto({csv_path_sql}, header = TRUE)
      ),
      yearly_coverage AS (
        SELECT
          CAST(year AS INTEGER) AS year,
          COUNT(DISTINCT CAST(quarter AS INTEGER)) AS distinct_quarters
        FROM src
        GROUP BY 1
      ),
      bounds AS (
        SELECT
          MAX(CASE WHEN distinct_quarters = 4 THEN year END) AS keep_end_year,
          MAX(year) AS latest_source_year
        FROM yearly_coverage
      ),
      filtered AS (
        SELECT
          CAST(periodicity AS VARCHAR) AS source_periodicity,
          CAST(seasonadj AS VARCHAR) AS seasonadj,
          CAST(geo_level AS VARCHAR) AS geo_level,
          LPAD(CAST(geography AS VARCHAR), CASE WHEN CAST(geo_level AS VARCHAR) = 'S' THEN 2 ELSE 5 END, '0') AS geo_id,
          CAST(geography AS VARCHAR) AS geography,
          CAST(ind_level AS VARCHAR) AS ind_level,
          CAST(industry AS VARCHAR) AS industry_code,
          CAST(ownercode AS VARCHAR) AS ownercode,
          CAST(sex AS VARCHAR) AS sex,
          CAST(agegrp AS VARCHAR) AS agegrp,
          CAST(race AS VARCHAR) AS race,
          CAST(ethnicity AS VARCHAR) AS ethnicity,
          CAST(education AS VARCHAR) AS education,
          CAST(firmage AS VARCHAR) AS firmage,
          CAST(firmsize AS VARCHAR) AS firmsize,
          CAST(year AS INTEGER) AS year,
          CAST(quarter AS INTEGER) AS quarter,
          bounds.keep_end_year - ({j2j_keep_years} - 1) AS keep_start_year,
          bounds.keep_end_year AS keep_end_year,
          bounds.latest_source_year AS latest_source_year,
          {glue::glue_collapse(glue('CAST({c(j2j_sum_measures, j2j_avg_count_measures, j2j_avg_earn_measures)} AS DOUBLE) AS {c(j2j_sum_measures, j2j_avg_count_measures, j2j_avg_earn_measures)}'), sep = ',\n          ')}
        FROM src
        CROSS JOIN bounds
        WHERE
          CAST(geo_level AS VARCHAR) = {geo_level_sql}
          AND CAST(sex AS VARCHAR) = '0'
          AND CAST(race AS VARCHAR) = 'A0'
          AND CAST(ethnicity AS VARCHAR) = 'A0'
          AND CAST(education AS VARCHAR) = 'E0'
          AND CAST(year AS INTEGER) BETWEEN bounds.keep_end_year - ({j2j_keep_years} - 1) AND bounds.keep_end_year
      )
      SELECT
        {source_scope_type_sql} AS source_scope_type,
        {source_scope_id_sql} AS source_scope_id,
        {state_scope_sql} AS state_scope,
        {state_fips_sql} AS state_fips,
        'age' AS demo_family,
        'A' AS periodicity,
        source_periodicity,
        seasonadj,
        geo_level,
        geo_id,
        geography,
        ind_level,
        industry_code,
        ownercode,
        sex,
        agegrp,
        race,
        ethnicity,
        education,
        firmage,
        firmsize,
        year,
        COUNT(DISTINCT quarter) AS quarters_observed,
        {sum_sql},
        {avg_count_sql},
        {avg_earn_sql},
        {source_file_sql} AS source_file,
        {release_id_sql} AS release_id,
        {schema_version_sql} AS schema_version,
        {metadata_period_range_sql} AS metadata_period_range,
        MAX(latest_source_year) AS latest_source_year,
        MAX(keep_start_year) AS keep_start_year,
        MAX(keep_end_year) AS keep_end_year
      FROM filtered
      GROUP BY
        source_periodicity,
        seasonadj,
        geo_level,
        geo_id,
        geography,
        ind_level,
        industry_code,
        ownercode,
        sex,
        agegrp,
        race,
        ethnicity,
        education,
        firmage,
        firmsize,
        year
      "
    )
  )
}

validate_j2j_batch <- function(con, metadata_row) {
  scope_label <- glue("{metadata_row$source_scope_type[[1]]}:{metadata_row$source_scope_id[[1]]}")
  expected_geo_level <- if (identical(metadata_row$source_scope_type[[1]], "state")) "S" else "B"
  expected_geo_regex <- if (identical(metadata_row$source_scope_type[[1]], "state")) "^[0-9]{2}$" else "^[0-9]{5}$"

  invalid_summary <- DBI::dbGetQuery(
    con,
    glue(
      "
      SELECT
        SUM(CASE WHEN geo_id IS NULL OR NOT regexp_matches(geo_id, '{expected_geo_regex}') THEN 1 ELSE 0 END) AS invalid_geo_rows,
        SUM(CASE WHEN year IS NULL OR year < keep_start_year OR year > keep_end_year THEN 1 ELSE 0 END) AS invalid_year_rows,
        SUM(CASE WHEN quarters_observed < 1 OR quarters_observed > 4 THEN 1 ELSE 0 END) AS invalid_quarter_counts,
        SUM(CASE WHEN keep_end_year IS NULL THEN 1 ELSE 0 END) AS invalid_completed_year_rows,
        SUM(CASE WHEN geo_level <> '{expected_geo_level}' THEN 1 ELSE 0 END) AS invalid_geo_level_rows
      FROM j2j_batch
      "
    )
  )

  if (invalid_summary$invalid_geo_rows[[1]] > 0) {
    stop(
      glue(
        "LEHD J2J staging for {scope_label} contains ",
        "{invalid_summary$invalid_geo_rows[[1]]} rows with invalid GEOIDs."
      ),
      call. = FALSE
    )
  }

  if (invalid_summary$invalid_year_rows[[1]] > 0) {
    stop(
      glue(
        "LEHD J2J staging for {scope_label} contains ",
        "{invalid_summary$invalid_year_rows[[1]]} rows outside the retained rolling {j2j_keep_years}-year window."
      ),
      call. = FALSE
    )
  }

  if (invalid_summary$invalid_quarter_counts[[1]] > 0) {
    stop(
      glue(
        "LEHD J2J staging for {scope_label} contains ",
        "{invalid_summary$invalid_quarter_counts[[1]]} rows with invalid annual quarter counts."
      ),
      call. = FALSE
    )
  }

  if (invalid_summary$invalid_completed_year_rows[[1]] > 0) {
    stop(
      glue(
        "LEHD J2J staging for {scope_label} could not detect a fully completed source year."
      ),
      call. = FALSE
    )
  }

  if (invalid_summary$invalid_geo_level_rows[[1]] > 0) {
    stop(
      glue(
        "LEHD J2J staging for {scope_label} contains rows outside the expected geography level {expected_geo_level}."
      ),
      call. = FALSE
    )
  }

  invalid_scope_rows <- DBI::dbGetQuery(
    con,
    "
    SELECT COUNT(*) AS invalid_scope_rows
    FROM j2j_batch
    WHERE
      demo_family <> 'age'
      OR sex <> '0'
      OR race <> 'A0'
      OR ethnicity <> 'A0'
      OR education <> 'E0'
    "
  )

  if (invalid_scope_rows$invalid_scope_rows[[1]] > 0) {
    stop(
      glue(
        "LEHD J2J staging for {scope_label} contains ",
        "{invalid_scope_rows$invalid_scope_rows[[1]]} rows outside the approved age-slice scope."
      ),
      call. = FALSE
    )
  }

  duplicate_rows <- DBI::dbGetQuery(
    con,
    "
    SELECT COUNT(*) AS duplicate_keys
    FROM (
      SELECT
        geo_level,
        geo_id,
        ind_level,
        industry_code,
        ownercode,
        sex,
        agegrp,
        race,
        ethnicity,
        education,
        firmage,
        firmsize,
        year,
        COUNT(*) AS n
      FROM j2j_batch
      GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13
      HAVING COUNT(*) > 1
    )
    "
  )

  if (duplicate_rows$duplicate_keys[[1]] > 0) {
    stop(
      glue(
        "LEHD J2J staging for {scope_label} is not unique at the published J2J identifier grain. ",
        "Duplicate keys found: {duplicate_rows$duplicate_keys[[1]]}"
      ),
      call. = FALSE
    )
  }
}

ingest_j2j_scope <- function(con, metadata_row, table_exists, append_mode) {
  scope_label <- glue("{metadata_row$source_scope_type[[1]]}:{metadata_row$source_scope_id[[1]]}")
  message("Processing LEHD J2J file for scope: ", scope_label)

  scope_tmp_dir <- file.path(
    tempdir(),
    glue("lehd_j2j_{metadata_row$source_scope_type[[1]]}_{metadata_row$source_scope_id[[1]]}_{as.integer(Sys.time())}")
  )
  dir.create(scope_tmp_dir, recursive = TRUE, showWarnings = FALSE)
  on.exit(unlink(scope_tmp_dir, recursive = TRUE, force = TRUE), add = TRUE)

  source_file <- build_j2j_source_filename(
    source_scope_type = metadata_row$source_scope_type[[1]],
    source_scope_id = metadata_row$source_scope_id[[1]]
  )
  csv_path <- file.path(scope_tmp_dir, source_file)

  download_j2j_asset(
    url = build_j2j_csv_url(
      source_scope_type = metadata_row$source_scope_type[[1]],
      source_scope_id = metadata_row$source_scope_id[[1]]
    ),
    dest_path = csv_path
  )

  if (append_mode && table_exists) {
    DBI::dbExecute(
      con,
      glue(
        "
        DELETE FROM staging.lehd_j2j
        WHERE
          source_scope_type = {DBI::dbQuoteString(con, metadata_row$source_scope_type[[1]])}
          AND source_scope_id = {DBI::dbQuoteString(con, metadata_row$source_scope_id[[1]])}
        "
      )
    )
  }

  create_j2j_batch_table(
    con = con,
    csv_path = csv_path,
    metadata_row = metadata_row,
    source_file = source_file
  )

  validate_j2j_batch(
    con = con,
    metadata_row = metadata_row
  )

  batch_rows <- DBI::dbGetQuery(con, "SELECT COUNT(*) AS n FROM j2j_batch")$n[[1]]

  if (!table_exists) {
    DBI::dbExecute(con, "CREATE TABLE staging.lehd_j2j AS SELECT * FROM j2j_batch")
    table_exists <- TRUE
  } else {
    DBI::dbExecute(con, "INSERT INTO staging.lehd_j2j SELECT * FROM j2j_batch")
  }

  DBI::dbExecute(con, "DROP TABLE IF EXISTS j2j_batch")

  message("Finished LEHD J2J file for scope: ", scope_label, " (", scales::comma(batch_rows), " rows)")

  unlink(scope_tmp_dir, recursive = TRUE, force = TRUE)
  table_exists
}

j2j_append_mode <- resolve_j2j_append_mode()
j2j_state_scopes <- resolve_j2j_state_scope()
j2j_metro_metadata <- fetch_j2j_metro_metadata()
j2j_metro_scopes <- resolve_j2j_metro_scope(j2j_metro_metadata)

# 3. Download, filter, and materialize files scope by scope ----
if (!j2j_append_mode) {
  DBI::dbExecute(con, "DROP TABLE IF EXISTS staging.lehd_j2j")
}

table_exists <- DBI::dbExistsTable(con, DBI::Id(schema = "staging", table = "lehd_j2j"))

for (state_scope in j2j_state_scopes) {
  version_path <- tempfile(pattern = glue("lehd_j2j_{state_scope}_version_"), fileext = ".txt")
  download_j2j_asset(
    url = build_j2j_version_url(state_scope),
    dest_path = version_path
  )
  on.exit(unlink(version_path), add = TRUE)

  version_lines <- readLines(version_path, warn = FALSE)
  metadata_row <- parse_j2j_state_metadata(version_lines, state_scope = state_scope)

  table_exists <- ingest_j2j_scope(
    con = con,
    metadata_row = metadata_row,
    table_exists = table_exists,
    append_mode = j2j_append_mode
  )
}

metro_rows <- dplyr::filter(j2j_metro_metadata, .data$source_scope_id %in% j2j_metro_scopes)

for (row_idx in seq_len(nrow(metro_rows))) {
  table_exists <- ingest_j2j_scope(
    con = con,
    metadata_row = metro_rows[row_idx, ],
    table_exists = table_exists,
    append_mode = j2j_append_mode
  )
}

# 4. Final contract checks on the staged table ----
invalid_scope_summary <- DBI::dbGetQuery(
  con,
  "
  SELECT
    SUM(CASE WHEN geo_level NOT IN ('S', 'B') THEN 1 ELSE 0 END) AS invalid_geo_level_rows,
    SUM(CASE WHEN source_scope_type = 'state' AND geo_level <> 'S' THEN 1 ELSE 0 END) AS invalid_state_level_rows,
    SUM(CASE WHEN source_scope_type = 'metro' AND geo_level <> 'B' THEN 1 ELSE 0 END) AS invalid_metro_level_rows,
    SUM(CASE WHEN sex <> '0' THEN 1 ELSE 0 END) AS non_all_sex_rows,
    SUM(CASE WHEN race <> 'A0' OR ethnicity <> 'A0' OR education <> 'E0' THEN 1 ELSE 0 END) AS non_age_scope_rows,
    SUM(CASE WHEN seasonadj <> 'U' THEN 1 ELSE 0 END) AS adjusted_rows,
    SUM(CASE WHEN source_scope_type = 'state' AND (geo_id IS NULL OR NOT regexp_matches(geo_id, '^[0-9]{2}$')) THEN 1 ELSE 0 END) AS invalid_state_geo_rows,
    SUM(CASE WHEN source_scope_type = 'metro' AND (geo_id IS NULL OR NOT regexp_matches(geo_id, '^[0-9]{5}$')) THEN 1 ELSE 0 END) AS invalid_metro_geo_rows,
    SUM(CASE WHEN periodicity <> 'A' THEN 1 ELSE 0 END) AS non_annual_rows,
    SUM(CASE WHEN source_periodicity <> 'Q' THEN 1 ELSE 0 END) AS non_quarter_sources
  FROM staging.lehd_j2j
  "
)

if (invalid_scope_summary$invalid_geo_level_rows[[1]] > 0) {
  stop("LEHD J2J staging contains rows outside the approved state/metro geography levels.", call. = FALSE)
}

if (invalid_scope_summary$invalid_state_level_rows[[1]] > 0) {
  stop("LEHD J2J staging contains state-scope rows with a non-state geography level.", call. = FALSE)
}

if (invalid_scope_summary$invalid_metro_level_rows[[1]] > 0) {
  stop("LEHD J2J staging contains metro-scope rows with a non-metro geography level.", call. = FALSE)
}

if (invalid_scope_summary$non_all_sex_rows[[1]] > 0) {
  stop("LEHD J2J staging contains sex-specific rows outside the approved first-pass scope.", call. = FALSE)
}

if (invalid_scope_summary$non_age_scope_rows[[1]] > 0) {
  stop("LEHD J2J staging contains rows outside the approved age-family scope.", call. = FALSE)
}

if (invalid_scope_summary$adjusted_rows[[1]] > 0) {
  stop("LEHD J2J staging contains seasonally adjusted rows outside the approved first-pass scope.", call. = FALSE)
}

if (invalid_scope_summary$invalid_state_geo_rows[[1]] > 0) {
  stop("LEHD J2J staging contains invalid state GEOIDs.", call. = FALSE)
}

if (invalid_scope_summary$invalid_metro_geo_rows[[1]] > 0) {
  stop("LEHD J2J staging contains invalid metro GEOIDs.", call. = FALSE)
}

if (invalid_scope_summary$non_annual_rows[[1]] > 0) {
  stop("LEHD J2J staging contains non-annual rows after annualization.", call. = FALSE)
}

if (invalid_scope_summary$non_quarter_sources[[1]] > 0) {
  stop("LEHD J2J staging contains unexpected source periodicity values.", call. = FALSE)
}

duplicate_summary <- DBI::dbGetQuery(
  con,
  "
  SELECT COUNT(*) AS duplicate_keys
  FROM (
    SELECT
      source_scope_type,
      source_scope_id,
      geo_level,
      geo_id,
      ind_level,
      industry_code,
      ownercode,
      sex,
      agegrp,
      race,
      ethnicity,
      education,
      firmage,
      firmsize,
      year,
      COUNT(*) AS n
    FROM staging.lehd_j2j
    GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    HAVING COUNT(*) > 1
  )
  "
)

if (duplicate_summary$duplicate_keys[[1]] > 0) {
  stop(
    glue(
      "LEHD J2J staging is not unique at the published J2J identifier grain. ",
      "Duplicate keys found: {duplicate_summary$duplicate_keys[[1]]}"
    ),
    call. = FALSE
  )
}

DBI::dbExecute(con, "CHECKPOINT")
