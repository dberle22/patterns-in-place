# In this script we land the current BLS OEWS state and metro/nonmetro workbooks
# into source-faithful staging tables. We keep the published workbook columns
# intact, then add only a small amount of provenance so Silver can decide later
# how to model states, metros, nonmetros, and territorial rows.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "bls", "oews")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

release_year <- 2025L

download_oews_zip <- function(zip_stub) {
  zip_name <- glue("{zip_stub}.zip")
  zip_url <- glue("https://www.bls.gov/oes/special-requests/{zip_name}")
  zip_path <- file.path(raw_dir, zip_name)

  if (!file.exists(zip_path)) {
    response <- httr::GET(
      zip_url,
      httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
    )
    httr::stop_for_status(response)
    writeBin(httr::content(response, "raw"), zip_path)
  }

  zip_path
}

extract_member <- function(zip_path, member_name) {
  extract_dir <- file.path(
    raw_dir,
    tools::file_path_sans_ext(basename(zip_path))
  )

  dir.create(extract_dir, recursive = TRUE, showWarnings = FALSE)

  member_path <- file.path(extract_dir, member_name)
  if (!file.exists(member_path)) {
    utils::unzip(
      zip_path,
      files = member_name,
      exdir = extract_dir
    )
  }

  member_path
}

read_oews_workbook <- function(workbook_path, geo_family, workbook_name) {
  readxl::read_xlsx(
    workbook_path,
    sheet = 1,
    col_types = "text"
  ) %>%
    janitor::clean_names() %>%
    mutate(
      release_year = release_year,
      source_geo_family = geo_family,
      source_workbook = workbook_name
    )
}

# 1. Download and cache the current release workbooks ----
state_zip_path <- download_oews_zip("oesm25st")
metro_zip_path <- download_oews_zip("oesm25ma")

state_workbook_path <- extract_member(
  state_zip_path,
  file.path("oesm25st", "state_M2025_dl.xlsx")
)

msa_workbook_path <- extract_member(
  metro_zip_path,
  file.path("oesm25ma", "MSA_M2025_dl.xlsx")
)

bos_workbook_path <- extract_member(
  metro_zip_path,
  file.path("oesm25ma", "BOS_M2025_dl.xlsx")
)

# 2. Read the published workbook rows source-faithfully ----
state_rows <- read_oews_workbook(
  state_workbook_path,
  geo_family = "state",
  workbook_name = "state_M2025_dl.xlsx"
) %>%
  mutate(
    source_area_scope = case_when(
      area_type == "2" ~ "state",
      area_type == "3" ~ "territory",
      TRUE ~ "other"
    )
  )

msa_rows <- read_oews_workbook(
  msa_workbook_path,
  geo_family = "metro_nonmetro",
  workbook_name = "MSA_M2025_dl.xlsx"
) %>%
  mutate(source_area_scope = "metro")

bos_rows <- read_oews_workbook(
  bos_workbook_path,
  geo_family = "metro_nonmetro",
  workbook_name = "BOS_M2025_dl.xlsx"
) %>%
  mutate(source_area_scope = "nonmetro")

metro_nonmetro_rows <- bind_rows(msa_rows, bos_rows)

# 3. Validate the current released row contracts before loading ----
required_columns <- c(
  "area", "area_title", "area_type", "prim_state", "naics", "naics_title",
  "i_group", "own_code", "occ_code", "occ_title", "o_group", "tot_emp",
  "emp_prse", "jobs_1000", "loc_quotient", "h_mean", "a_mean", "mean_prse",
  "h_pct10", "h_pct25", "h_median", "h_pct75", "h_pct90",
  "a_pct10", "a_pct25", "a_median", "a_pct75", "a_pct90",
  "annual", "hourly", "release_year", "source_geo_family",
  "source_workbook", "source_area_scope"
)

missing_state_columns <- setdiff(required_columns, names(state_rows))
missing_metro_columns <- setdiff(required_columns, names(metro_nonmetro_rows))

if (length(missing_state_columns) > 0) {
  stop(
    glue(
      "State OEWS workbook is missing required columns: {paste(missing_state_columns, collapse = ', ')}"
    ),
    call. = FALSE
  )
}

if (length(missing_metro_columns) > 0) {
  stop(
    glue(
      "Metro/nonmetro OEWS workbook is missing required columns: {paste(missing_metro_columns, collapse = ', ')}"
    ),
    call. = FALSE
  )
}

state_key_issues <- state_rows %>%
  count(release_year, area, occ_code, name = "row_count") %>%
  filter(row_count > 1)

metro_key_issues <- metro_nonmetro_rows %>%
  count(release_year, source_area_scope, area, occ_code, name = "row_count") %>%
  filter(row_count > 1)

if (nrow(state_key_issues) > 0) {
  stop("State OEWS rows are not unique at release_year + area + occ_code.", call. = FALSE)
}

if (nrow(metro_key_issues) > 0) {
  stop(
    "Metro/nonmetro OEWS rows are not unique at release_year + source_area_scope + area + occ_code.",
    call. = FALSE
  )
}

# 4. Materialize staging tables ----
if (DBI::dbExistsTable(con, DBI::Id(schema = "staging", table = "bls_oews_state"))) {
  DBI::dbRemoveTable(con, DBI::Id(schema = "staging", table = "bls_oews_state"))
}

if (DBI::dbExistsTable(con, DBI::Id(schema = "staging", table = "bls_oews_metro_nonmetro"))) {
  DBI::dbRemoveTable(con, DBI::Id(schema = "staging", table = "bls_oews_metro_nonmetro"))
}

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "bls_oews_state"),
  state_rows,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "bls_oews_metro_nonmetro"),
  metro_nonmetro_rows,
  overwrite = TRUE
)

# 5. Print a compact run summary for quick QA ----
state_summary <- state_rows %>%
  summarise(
    rows = n(),
    distinct_areas = n_distinct(area),
    distinct_occ_codes = n_distinct(occ_code)
  )

metro_summary <- metro_nonmetro_rows %>%
  summarise(
    rows = n(),
    distinct_areas = n_distinct(area),
    distinct_occ_codes = n_distinct(occ_code)
  )

scope_summary <- metro_nonmetro_rows %>%
  count(source_area_scope, name = "rows") %>%
  arrange(source_area_scope)

message("Loaded staging.bls_oews_state")
print(state_summary)

message("Loaded staging.bls_oews_metro_nonmetro")
print(metro_summary)
print(scope_summary)

DBI::dbDisconnect(con, shutdown = TRUE)
