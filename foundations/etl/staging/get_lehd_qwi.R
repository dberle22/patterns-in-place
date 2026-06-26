# In this script we land annualized LEHD QWI county rows for the approved
# first-pass scope. We intentionally keep the core published QWI measure payload
# needed for downstream rollups, but only for:
# 1. county geography
# 2. age x industry rows (all-sex)
# 3. education x industry rows (all-sex)
# 4. the latest rolling 10 years in each source file
#
# We now collapse quarter rows to one annual row per county / year / industry /
# demographic slice. That keeps staging materially smaller while still
# preserving the labor-composition signals we expect to use downstream.
#
# Silver will own county -> CBSA/state/division/national rollups and will
# recompute rates from the staged annual counts rather than relying on direct
# aggregation of the published quarterly rate fields.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the first-pass scope ----
qwi_base_url <- "https://lehd.ces.census.gov/data/qwi/latest_release"
qwi_keep_years <- 10L
qwi_demo_families <- c(age = "sa", education = "se")
qwi_state_scopes_default <- c(tolower(state.abb), "dc", "pr")

resolve_qwi_append_mode <- function(env_var = "LEHD_QWI_APPEND_MODE") {
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

resolve_qwi_state_scope <- function(env_var = "LEHD_QWI_STATE_SCOPE") {
  # This optional env var lets us run one or a few scopes during development
  # without changing the default production list of all states plus DC and PR.
  raw_value <- Sys.getenv(env_var, unset = "")

  if (!nzchar(raw_value)) {
    return(qwi_state_scopes_default)
  }

  scopes <- raw_value %>%
    stringr::str_split(",") %>%
    purrr::pluck(1) %>%
    stringr::str_trim() %>%
    tolower() %>%
    unique()

  invalid_scopes <- setdiff(scopes, qwi_state_scopes_default)
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

qwi_append_mode <- resolve_qwi_append_mode()
qwi_state_scopes <- resolve_qwi_state_scope()

build_qwi_csv_url <- function(state_scope, demo_code) {
  # We pin the first-pass file contract here instead of trying to infer it at
  # runtime: county (`gc`), no firm age/size detail (`f`), NAICS sectors (`ns`),
  # all private (`op`), and unadjusted (`u`).
  glue(
    "{qwi_base_url}/{state_scope}/qwi_{state_scope}_{demo_code}_f_gc_ns_op_u.csv.gz"
  )
}

build_qwi_version_url <- function(state_scope) {
  glue("{qwi_base_url}/{state_scope}/version_qwi.txt")
}

download_qwi_asset <- function(url, dest_path) {
  # Assets are downloaded to a temporary state-specific scratch directory and
  # removed after filtering so we do not keep the full raw historical panels.
  resp <- httr::GET(
    url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)

  writeBin(httr::content(resp, "raw"), dest_path)
  dest_path
}

parse_qwi_release_metadata <- function(version_lines, state_scope) {
  # `version_qwi.txt` is the provider's compact metadata manifest. We keep the
  # release id and schema version alongside the staged rows for provenance.
  non_empty_lines <- version_lines[nzchar(trimws(version_lines))]
  qwi_f_line <- non_empty_lines[stringr::str_detect(non_empty_lines, "^QWI_F\\s")][1]

  if (is.na(qwi_f_line) || !nzchar(qwi_f_line)) {
    stop(
      glue("QWI version metadata for scope {state_scope} is missing a QWI_F line."),
      call. = FALSE
    )
  }

  parts <- stringr::str_split(trimws(qwi_f_line), "\\s+")[[1]]

  if (length(parts) < 7) {
    stop(
      glue("QWI version metadata for scope {state_scope} is malformed: {qwi_f_line}"),
      call. = FALSE
    )
  }

  tibble::tibble(
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

get_demo_filter_sql <- function(demo_family) {
  if (identical(demo_family, "age")) {
    return("CAST(sex AS VARCHAR) = '0' AND CAST(education AS VARCHAR) = 'E0'")
  }

  if (identical(demo_family, "education")) {
    return("CAST(sex AS VARCHAR) = '0' AND CAST(agegrp AS VARCHAR) = 'A00' AND CAST(education AS VARCHAR) <> 'E0'")
  }

  stop(glue("Unsupported QWI demo family: {demo_family}"), call. = FALSE)
}

create_qwi_batch_table <- function(con, csv_path, demo_family, source_file, metadata_row) {
  # Large states can exceed R's vector memory limit if we parse the whole file
  # into an in-memory tibble first. DuckDB can scan the compressed CSV directly,
  # filter in SQL, annualize in SQL, and materialize only the retained county
  # subset we plan to manage in staging.
  demo_filter_sql <- get_demo_filter_sql(demo_family)
  csv_path_sql <- DBI::dbQuoteString(con, csv_path)
  source_file_sql <- DBI::dbQuoteString(con, source_file)
  state_scope_sql <- DBI::dbQuoteString(con, metadata_row$state_scope[[1]])
  release_id_sql <- DBI::dbQuoteString(con, metadata_row$release_id[[1]])
  schema_version_sql <- DBI::dbQuoteString(con, metadata_row$schema_version[[1]])
  metadata_period_range_sql <- DBI::dbQuoteString(con, metadata_row$metadata_period_range[[1]])
  demo_family_sql <- DBI::dbQuoteString(con, demo_family)

  DBI::dbExecute(con, "DROP TABLE IF EXISTS qwi_batch")

  DBI::dbExecute(
    con,
    glue(
      "
      CREATE TEMP TABLE qwi_batch AS
      WITH src AS (
        SELECT *
        FROM read_csv_auto({csv_path_sql}, header = TRUE)
      ),
      bounds AS (
        SELECT MAX(CAST(year AS INTEGER)) AS keep_end_year
        FROM src
      ),
      filtered AS (
        SELECT
          CAST(periodicity AS VARCHAR) AS source_periodicity,
          CAST(seasonadj AS VARCHAR) AS seasonadj,
          CAST(geo_level AS VARCHAR) AS geo_level,
          LPAD(CAST(geography AS VARCHAR), 5, '0') AS geo_id,
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
          CAST(Emp AS DOUBLE) AS Emp,
          CAST(EmpEnd AS DOUBLE) AS EmpEnd,
          CAST(EmpS AS DOUBLE) AS EmpS,
          CAST(EmpTotal AS DOUBLE) AS EmpTotal,
          CAST(EmpSpv AS DOUBLE) AS EmpSpv,
          CAST(HirA AS DOUBLE) AS HirA,
          CAST(HirN AS DOUBLE) AS HirN,
          CAST(HirR AS DOUBLE) AS HirR,
          CAST(Sep AS DOUBLE) AS Sep,
          CAST(HirAEnd AS DOUBLE) AS HirAEnd,
          CAST(SepBeg AS DOUBLE) AS SepBeg,
          CAST(HirAEndRepl AS DOUBLE) AS HirAEndRepl,
          CAST(EarnS AS DOUBLE) AS EarnS,
          CAST(EarnBeg AS DOUBLE) AS EarnBeg,
          CAST(EarnHirAS AS DOUBLE) AS EarnHirAS,
          CAST(EarnHirNS AS DOUBLE) AS EarnHirNS,
          CAST(EarnSepS AS DOUBLE) AS EarnSepS,
          CAST(Payroll AS DOUBLE) AS Payroll,
          bounds.keep_end_year - ({qwi_keep_years} - 1) AS keep_start_year,
          bounds.keep_end_year AS keep_end_year
        FROM src
        CROSS JOIN bounds
        WHERE
          CAST(geo_level AS VARCHAR) = 'C'
          AND CAST(year AS INTEGER) >= bounds.keep_end_year - ({qwi_keep_years} - 1)
          AND {demo_filter_sql}
      )
      SELECT
        {state_scope_sql} AS state_scope,
        SUBSTR(geo_id, 1, 2) AS state_fips,
        {demo_family_sql} AS demo_family,
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
        COUNT(*) AS quarters_observed,
        AVG(Emp) AS annual_avg_emp,
        AVG(EmpEnd) AS annual_avg_empend,
        AVG(EmpS) AS annual_avg_emps,
        AVG(EmpTotal) AS annual_avg_emptotal,
        AVG(EmpSpv) AS annual_avg_empspv,
        SUM(HirA) AS annual_hira,
        SUM(HirN) AS annual_hirn,
        SUM(HirR) AS annual_hirr,
        SUM(Sep) AS annual_sep,
        SUM(HirAEnd) AS annual_hiraend,
        SUM(SepBeg) AS annual_sepbeg,
        SUM(HirAEndRepl) AS annual_hiraendrepl,
        AVG(EarnS) AS annual_avg_earns,
        AVG(EarnBeg) AS annual_avg_earnbeg,
        AVG(EarnHirAS) AS annual_avg_earnhiras,
        AVG(EarnHirNS) AS annual_avg_earnhirns,
        AVG(EarnSepS) AS annual_avg_earnseps,
        SUM(Payroll) AS annual_payroll,
        {source_file_sql} AS source_file,
        {release_id_sql} AS release_id,
        {schema_version_sql} AS schema_version,
        {metadata_period_range_sql} AS metadata_period_range,
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

validate_qwi_batch <- function(con, state_scope, demo_family) {
  # Batch-level checks fail fast before rows are appended into DuckDB. That
  # keeps one bad scope from contaminating an otherwise valid staged table.
  invalid_summary <- DBI::dbGetQuery(
    con,
    "
    SELECT
      SUM(CASE WHEN geo_id IS NULL OR NOT regexp_matches(geo_id, '^[0-9]{5}$') THEN 1 ELSE 0 END) AS invalid_geo_rows,
      SUM(CASE WHEN year IS NULL OR year < keep_start_year THEN 1 ELSE 0 END) AS invalid_year_rows,
      SUM(CASE WHEN quarters_observed < 1 OR quarters_observed > 4 THEN 1 ELSE 0 END) AS invalid_quarter_counts
    FROM qwi_batch
    "
  )

  if (invalid_summary$invalid_geo_rows[[1]] > 0) {
    stop(
      glue(
        "LEHD QWI {demo_family} county staging for {state_scope} contains ",
        "{invalid_summary$invalid_geo_rows[[1]]} rows with invalid 5-digit county GEOIDs."
      ),
      call. = FALSE
    )
  }

  if (invalid_summary$invalid_year_rows[[1]] > 0) {
    stop(
      glue(
        "LEHD QWI {demo_family} county staging for {state_scope} contains ",
        "{invalid_summary$invalid_year_rows[[1]]} rows outside the retained rolling {qwi_keep_years}-year window."
      ),
      call. = FALSE
    )
  }

  if (invalid_summary$invalid_quarter_counts[[1]] > 0) {
    stop(
      glue(
        "LEHD QWI {demo_family} county staging for {state_scope} contains ",
        "{invalid_summary$invalid_quarter_counts[[1]]} rows with invalid annual quarter counts."
      ),
      call. = FALSE
    )
  }

  invalid_demo_rows <- DBI::dbGetQuery(
    con,
    if (identical(demo_family, "age")) {
      "
      SELECT COUNT(*) AS invalid_demo_rows
      FROM qwi_batch
      WHERE sex <> '0' OR education <> 'E0'
      "
    } else {
      "
      SELECT COUNT(*) AS invalid_demo_rows
      FROM qwi_batch
      WHERE sex <> '0' OR agegrp <> 'A00' OR education = 'E0'
      "
    }
  )

  if (invalid_demo_rows$invalid_demo_rows[[1]] > 0) {
    stop(
      glue(
        "LEHD QWI {demo_family} county staging for {state_scope} contains ",
        "{invalid_demo_rows$invalid_demo_rows[[1]]} rows outside the approved demographic scope."
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
        demo_family,
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
      FROM qwi_batch
      GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13
      HAVING COUNT(*) > 1
    )
    "
  )

  if (duplicate_rows$duplicate_keys[[1]] > 0) {
    stop(
      glue(
        "LEHD QWI {demo_family} county staging for {state_scope} is not unique at the published QWI identifier grain. ",
        "Duplicate keys found: {duplicate_rows$duplicate_keys[[1]]}"
      ),
      call. = FALSE
    )
  }
}

# 3. Download, filter, and materialize county files one state at a time ----
if (!qwi_append_mode) {
  DBI::dbExecute(con, "DROP TABLE IF EXISTS staging.lehd_qwi")
}

table_exists <- DBI::dbExistsTable(con, DBI::Id(schema = "staging", table = "lehd_qwi"))

for (state_scope in qwi_state_scopes) {
  message("Processing LEHD QWI county files for scope: ", state_scope)

  # Each state uses its own scratch directory so raw files never need to live
  # outside this run, and a failed state can be retried cleanly.
  state_tmp_dir <- file.path(tempdir(), glue("lehd_qwi_{state_scope}_{as.integer(Sys.time())}"))
  dir.create(state_tmp_dir, recursive = TRUE, showWarnings = FALSE)

  on.exit(unlink(state_tmp_dir, recursive = TRUE, force = TRUE), add = TRUE)

  version_path <- file.path(state_tmp_dir, "version_qwi.txt")
  download_qwi_asset(
    url = build_qwi_version_url(state_scope),
    dest_path = version_path
  )

  version_lines <- readLines(version_path, warn = FALSE)
  metadata_row <- parse_qwi_release_metadata(version_lines, state_scope = state_scope)
  state_batch_rows <- 0L

  # In append mode, make each scope idempotent by replacing that state's rows
  # before loading the refreshed batches. This lets us run safe chunks without
  # manually cleaning the table or worrying about duplicate appends.
  if (qwi_append_mode && table_exists) {
    DBI::dbExecute(
      con,
      glue(
        "DELETE FROM staging.lehd_qwi WHERE state_scope = {DBI::dbQuoteString(con, state_scope)}"
      )
    )
  }

  for (demo_family in names(qwi_demo_families)) {
    demo_code <- qwi_demo_families[[demo_family]]
    csv_name <- glue("qwi_{state_scope}_{demo_code}_f_gc_ns_op_u.csv.gz")
    csv_path <- file.path(state_tmp_dir, csv_name)

    download_qwi_asset(
      url = build_qwi_csv_url(state_scope, demo_code),
      dest_path = csv_path
    )

    create_qwi_batch_table(
      con = con,
      csv_path = csv_path,
      demo_family = demo_family,
      source_file = csv_name,
      metadata_row = metadata_row
    )

    validate_qwi_batch(
      con = con,
      state_scope = state_scope,
      demo_family = demo_family
    )

    # We write each state/demo batch as soon as it is validated so we do not
    # need to hold the multi-state panel in memory.
    batch_rows <- DBI::dbGetQuery(con, "SELECT COUNT(*) AS n FROM qwi_batch")$n[[1]]
    state_batch_rows <- state_batch_rows + batch_rows

    if (!table_exists) {
      DBI::dbExecute(con, "CREATE TABLE staging.lehd_qwi AS SELECT * FROM qwi_batch")
      table_exists <- TRUE
    } else {
      DBI::dbExecute(con, "INSERT INTO staging.lehd_qwi SELECT * FROM qwi_batch")
    }

    DBI::dbExecute(con, "DROP TABLE IF EXISTS qwi_batch")
  }

  message("Finished LEHD QWI county files for scope: ", state_scope, " (", scales::comma(state_batch_rows), " rows)")

  unlink(state_tmp_dir, recursive = TRUE, force = TRUE)
}

# 4. Final contract checks on the staged table ----
# These table-level checks confirm that the combined staged output still matches
# the intended contract after all state/demo batches have been appended.
invalid_scope_summary <- DBI::dbGetQuery(
  con,
  "
  SELECT
    SUM(CASE WHEN geo_level <> 'C' THEN 1 ELSE 0 END) AS non_county_rows,
    SUM(CASE WHEN seasonadj <> 'U' THEN 1 ELSE 0 END) AS adjusted_rows,
    SUM(CASE WHEN ownercode <> 'A05' THEN 1 ELSE 0 END) AS non_private_rows,
    SUM(CASE WHEN geo_id IS NULL OR NOT regexp_matches(geo_id, '^[0-9]{5}$') THEN 1 ELSE 0 END) AS invalid_geo_rows,
    SUM(CASE WHEN periodicity <> 'A' THEN 1 ELSE 0 END) AS non_annual_rows,
    SUM(CASE WHEN source_periodicity <> 'Q' THEN 1 ELSE 0 END) AS non_quarter_sources
  FROM staging.lehd_qwi
  "
)

if (invalid_scope_summary$non_county_rows[[1]] > 0) {
  stop("LEHD QWI staging contains non-county rows after county-only filtering.", call. = FALSE)
}

if (invalid_scope_summary$adjusted_rows[[1]] > 0) {
  stop("LEHD QWI staging contains seasonally adjusted rows outside the approved first-pass scope.", call. = FALSE)
}

if (invalid_scope_summary$non_private_rows[[1]] > 0) {
  stop("LEHD QWI staging contains ownership rows outside the approved all-private first-pass scope.", call. = FALSE)
}

if (invalid_scope_summary$invalid_geo_rows[[1]] > 0) {
  stop("LEHD QWI staging contains invalid county GEOIDs.", call. = FALSE)
}

if (invalid_scope_summary$non_annual_rows[[1]] > 0) {
  stop("LEHD QWI staging contains non-annual rows after annualization.", call. = FALSE)
}

if (invalid_scope_summary$non_quarter_sources[[1]] > 0) {
  stop("LEHD QWI staging contains unexpected source periodicity values.", call. = FALSE)
}

duplicate_summary <- DBI::dbGetQuery(
  con,
  "
  SELECT COUNT(*) AS duplicate_keys
  FROM (
    SELECT
      demo_family,
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
    FROM staging.lehd_qwi
    GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13
    HAVING COUNT(*) > 1
  )
  "
)

if (duplicate_summary$duplicate_keys[[1]] > 0) {
  stop(
    glue(
      "LEHD QWI staging is not unique at the published QWI identifier grain. ",
      "Duplicate keys found: {duplicate_summary$duplicate_keys[[1]]}"
    ),
    call. = FALSE
  )
}

DBI::dbExecute(con, "CHECKPOINT")
