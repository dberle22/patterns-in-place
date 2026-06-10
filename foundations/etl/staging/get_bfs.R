# In this script we land the annual Census BFS county workbook as a normalized
# county-year staging table. The verified county workbook only carries Business
# Applications (`BA`), so we keep the first pass deliberately small and leave
# richer monthly BFS series for a later sibling ingest.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "economics", "raw", "census", "bfs")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 1. Define the current county workbook ----
bfs_url <- "https://www.census.gov/econ/bfs/xlsx/bfs_county_apps_annual.xlsx"
bfs_file <- file.path(raw_dir, "bfs_county_apps_annual.xlsx")

download_bfs_workbook <- function(url, dest_path) {
  if (file.exists(dest_path)) {
    return(dest_path)
  }

  resp <- httr::GET(
    url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)

  writeBin(httr::content(resp, "raw"), dest_path)
  dest_path
}

normalize_bfs_county <- function(path) {
  raw_df <- readxl::read_excel(
    path,
    sheet = "County Data",
    skip = 2
  ) %>%
    janitor::clean_names()

  ba_cols <- names(raw_df)[stringr::str_detect(names(raw_df), "^ba\\d{4}$")]

  if (length(ba_cols) == 0) {
    stop("No BA year columns were found in the BFS county workbook.", call. = FALSE)
  }

  raw_df %>%
    transmute(
      state_abbr = as.character(.data$state),
      county_name = as.character(.data$county),
      county_fips = stringr::str_pad(as.character(.data$county_code), width = 5, side = "left", pad = "0"),
      state_fips = stringr::str_pad(as.character(.data$state_fips), width = 2, side = "left", pad = "0"),
      county_fips_3 = stringr::str_sub(
        stringr::str_pad(as.character(.data$county_code), width = 5, side = "left", pad = "0"),
        3,
        5
      ),
      across(all_of(ba_cols), as.double)
    ) %>%
    pivot_longer(
      cols = all_of(ba_cols),
      names_to = "series_year",
      values_to = "business_applications"
    ) %>%
    mutate(
      year = as.integer(stringr::str_remove(.data$series_year, "^ba")),
      series_code = "BA",
      source_file = basename(path)
    ) %>%
    select(
      .data$year,
      .data$state_abbr,
      .data$county_name,
      .data$county_fips,
      .data$state_fips,
      .data$county_fips_3,
      .data$business_applications,
      .data$series_code,
      .data$source_file
    ) %>%
    filter(
      !is.na(.data$county_fips),
      stringr::str_detect(.data$county_fips, "^\\d{5}$"),
      !is.na(.data$year)
    )
}

# 2. Download and normalize the workbook ----
local_file <- download_bfs_workbook(bfs_url, bfs_file)
bfs_county <- normalize_bfs_county(local_file)

# 3. Contract checks ----
invalid_state_rows <- bfs_county %>%
  filter(is.na(.data$state_fips) | !stringr::str_detect(.data$state_fips, "^\\d{2}$"))

if (nrow(invalid_state_rows) > 0) {
  stop(
    glue("BFS county staging contains {nrow(invalid_state_rows)} rows with invalid 2-digit state FIPS keys."),
    call. = FALSE
  )
}

invalid_county_rows <- bfs_county %>%
  filter(is.na(.data$county_fips) | !stringr::str_detect(.data$county_fips, "^\\d{5}$"))

if (nrow(invalid_county_rows) > 0) {
  stop(
    glue("BFS county staging contains {nrow(invalid_county_rows)} rows with invalid 5-digit county FIPS keys."),
    call. = FALSE
  )
}

duplicate_rows <- bfs_county %>%
  count(.data$county_fips, .data$year, .data$series_code, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_rows) > 0) {
  stop(
    glue("BFS county staging is not unique at county_fips + year + series_code. Duplicate keys found: {nrow(duplicate_rows)}"),
    call. = FALSE
  )
}

# 4. Load the staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "bfs_county"),
  bfs_county,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
