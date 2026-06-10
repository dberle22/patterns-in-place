# In this script we land the public Opportunity Insights Social Capital Atlas
# county and ZIP releases as separate staging tables. The two files have related
# but not identical schemas, so staging keeps each source slice source-faithful
# and leaves cross-geography normalization for Silver.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "opportunity_insights", "social_capital_atlas")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the public release assets ----
county_csv_url <- "https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/ec896b64-c922-4737-b759-e4bd7f73b8cc/download/social_capital_county.csv"
zip_csv_url <- "https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/ab878625-279b-4bef-a2b3-c132168d536e/download/social_capital_zip.csv"

county_csv_path <- file.path(raw_dir, "social_capital_county.csv")
zip_csv_path <- file.path(raw_dir, "social_capital_zip.csv")

download_social_capital_csv <- function(url, dest_path) {
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

read_social_capital_csv <- function(csv_path, id_cols) {
  readr::read_csv(
    csv_path,
    col_types = readr::cols(.default = readr::col_double(), !!!id_cols),
    show_col_types = FALSE,
    progress = FALSE
  ) %>%
    janitor::clean_names()
}

# 3. Download and normalize the county and ZIP releases ----
download_social_capital_csv(county_csv_url, county_csv_path)
download_social_capital_csv(zip_csv_url, zip_csv_path)

social_capital_county <- read_social_capital_csv(
  csv_path = county_csv_path,
  id_cols = list(
    county = readr::col_character(),
    county_name = readr::col_character()
  )
) %>%
  mutate(
    county = stringr::str_pad(.data$county, width = 5, side = "left", pad = "0"),
    county_name = as.character(.data$county_name)
  )

social_capital_zip <- read_social_capital_csv(
  csv_path = zip_csv_path,
  id_cols = list(
    zip = readr::col_character(),
    county = readr::col_character()
  )
) %>%
  mutate(
    zip = stringr::str_pad(.data$zip, width = 5, side = "left", pad = "0"),
    county = stringr::str_pad(.data$county, width = 5, side = "left", pad = "0")
  )

# 4. Validate the public release keys before materializing staging ----
invalid_county_rows <- social_capital_county %>%
  filter(is.na(.data$county) | !stringr::str_detect(.data$county, "^\\d{5}$"))

if (nrow(invalid_county_rows) > 0) {
  stop(
    glue("Social Capital county staging contains {nrow(invalid_county_rows)} rows with invalid five-digit county FIPS."),
    call. = FALSE
  )
}

duplicate_county_rows <- social_capital_county %>%
  count(.data$county, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_county_rows) > 0) {
  stop(
    glue("Social Capital county staging is not unique at county. Duplicate keys found: {nrow(duplicate_county_rows)}"),
    call. = FALSE
  )
}

invalid_zip_rows <- social_capital_zip %>%
  filter(
    is.na(.data$zip) | !stringr::str_detect(.data$zip, "^\\d{5}$") |
      (!is.na(.data$county) & !stringr::str_detect(.data$county, "^\\d{5}$"))
  )

if (nrow(invalid_zip_rows) > 0) {
  stop(
    glue("Social Capital ZIP staging contains {nrow(invalid_zip_rows)} rows with invalid ZIP or county identifiers."),
    call. = FALSE
  )
}

duplicate_zip_rows <- social_capital_zip %>%
  count(.data$zip, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_zip_rows) > 0) {
  stop(
    glue("Social Capital ZIP staging is not unique at zip. Duplicate keys found: {nrow(duplicate_zip_rows)}"),
    call. = FALSE
  )
}

# 5. Materialize the separate staging tables ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "opportunity_insights_social_capital_county"),
  social_capital_county,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "opportunity_insights_social_capital_zip"),
  social_capital_zip,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
