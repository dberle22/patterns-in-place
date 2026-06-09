# In this script we land the archived EJScreen tract CSV as one source-faithful
# staging table. We intentionally keep the tract geography only for the first
# pass because the archive already provides tract rows directly and that avoids
# an unnecessary block-group aggregation step.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "epa", "ejscreen")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the archived tract file ----
ejscreen_year <- 2024L
ejscreen_file_id <- 10775979L
ejscreen_url <- glue("https://dataverse.harvard.edu/api/access/datafile/{ejscreen_file_id}")
ejscreen_local_file <- file.path(raw_dir, "EJScreen_2024_Tract_with_AS_CNMI_GU_VI.csv")

download_ejscreen_file <- function(url, dest_path) {
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

# 3. Download and clean the tract file ----
download_ejscreen_file(ejscreen_url, ejscreen_local_file)

ejscreen_raw <- readr::read_csv(
  ejscreen_local_file,
  col_types = readr::cols(
    ID = readr::col_character(),
    STATE_NAME = readr::col_character(),
    ST_ABBREV = readr::col_character(),
    CNTY_NAME = readr::col_character(),
    REGION = readr::col_character(),
    .default = readr::col_guess()
  ),
  guess_max = 5000,
  show_col_types = FALSE,
  progress = FALSE
) %>%
  janitor::clean_names()

ejscreen_staging <- ejscreen_raw %>%
  rename(
    object_id = oid,
    tract_geoid = id,
    state_name = state_name,
    state_abbrev = st_abbrev,
    county_name = cnty_name,
    epa_region = region
  ) %>%
  mutate(
    tract_geoid = stringr::str_pad(as.character(tract_geoid), width = 11, side = "left", pad = "0"),
    state_fips = stringr::str_sub(tract_geoid, 1, 2),
    county_fips = stringr::str_sub(tract_geoid, 1, 5),
    year = ejscreen_year,
    across(
      .cols = c(state_name, state_abbrev, county_name, epa_region),
      .fns = ~ iconv(.x, from = "", to = "UTF-8", sub = "")
    )
  )

# 4. Validate the tract key contract ----
invalid_tract_rows <- ejscreen_staging %>%
  filter(is.na(.data$tract_geoid) | !stringr::str_detect(.data$tract_geoid, "^\\d{11}$"))

if (nrow(invalid_tract_rows) > 0) {
  stop(
    glue("EJScreen staging contains {nrow(invalid_tract_rows)} rows with invalid tract GEOIDs."),
    call. = FALSE
  )
}

duplicate_rows <- ejscreen_staging %>%
  count(.data$tract_geoid, .data$year, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_rows) > 0) {
  stop(
    glue("EJScreen staging is not unique at tract_geoid + year. Duplicate keys found: {nrow(duplicate_rows)}"),
    call. = FALSE
  )
}

# 5. Materialize the tract staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "ejscreen"),
  ejscreen_staging,
  overwrite = TRUE
)
