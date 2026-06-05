# In this script we land the current FHFA low-income and designated-disaster-area
# tract file as a normalized staging table. FHFA publishes a fixed-width text
# file each year, so we parse the source layout into booleans that downstream
# Silver can aggregate without re-reading the raw text asset.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "fhfa_underserved")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the yearly FHFA ZIP asset ----
release_year <- 2026L
zip_url <- sprintf("https://www.fhfa.gov/document/d/ua/lya%d.zip", release_year)

download_fhfa_underserved_zip <- function(zip_url, dest_path) {
  if (file.exists(dest_path)) {
    return(dest_path)
  }

  resp <- httr::GET(
    zip_url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)

  writeBin(httr::content(resp, "raw"), dest_path)
  dest_path
}

# 3. Download and parse the fixed-width tract file ----
zip_path <- file.path(raw_dir, sprintf("fhfa_underserved_%s.zip", release_year))

download_fhfa_underserved_zip(
  zip_url = zip_url,
  dest_path = zip_path
)

zip_listing <- unzip(zip_path, list = TRUE)
txt_member <- zip_listing$Name[stringr::str_detect(zip_listing$Name, regex("^lya20\\d{2}\\.txt$", ignore_case = TRUE))][1]

if (is.na(txt_member)) {
  stop("Could not find the yearly FHFA low-income text file inside the ZIP archive.", call. = FALSE)
}

txt_path <- unzip(zip_path, files = txt_member, exdir = raw_dir, overwrite = TRUE)

fhfa_raw <- readr::read_table(
  txt_path,
  skip = 1,
  col_names = c("state_fips", "county_fips", "tract_code", "msa2023", "lya", "pctmin", "min_trct", "ceninc", "medinc", "dda"),
  col_types = readr::cols(
    state_fips = readr::col_character(),
    county_fips = readr::col_character(),
    tract_code = readr::col_character(),
    msa2023 = readr::col_character(),
    lya = readr::col_integer(),
    pctmin = readr::col_double(),
    min_trct = readr::col_integer(),
    ceninc = readr::col_double(),
    medinc = readr::col_double(),
    dda = readr::col_integer()
  ),
  progress = FALSE
)

code_to_flag <- function(x) {
  dplyr::case_when(
    x == 1L ~ TRUE,
    x == 0L ~ FALSE,
    TRUE ~ NA
  )
}

fhfa_staging <- fhfa_raw %>%
  transmute(
    tract_geoid = stringr::str_c(
      stringr::str_pad(.data$state_fips, width = 2, side = "left", pad = "0"),
      stringr::str_pad(.data$county_fips, width = 3, side = "left", pad = "0"),
      stringr::str_pad(.data$tract_code, width = 6, side = "left", pad = "0")
    ),
    year = release_year,
    is_low_income_area = code_to_flag(.data$lya),
    is_minority_area = code_to_flag(.data$min_trct),
    is_disaster_area = code_to_flag(.data$dda)
  ) %>%
  mutate(
    is_underserved = dplyr::case_when(
      .data$is_low_income_area %in% TRUE | .data$is_minority_area %in% TRUE | .data$is_disaster_area %in% TRUE ~ TRUE,
      .data$is_low_income_area %in% FALSE & .data$is_minority_area %in% FALSE & .data$is_disaster_area %in% FALSE ~ FALSE,
      TRUE ~ NA
    )
  ) %>%
  group_by(.data$tract_geoid, .data$year) %>%
  summarize(
    is_underserved = any(.data$is_underserved %in% TRUE),
    is_low_income_area = any(.data$is_low_income_area %in% TRUE),
    is_minority_area = any(.data$is_minority_area %in% TRUE),
    is_disaster_area = any(.data$is_disaster_area %in% TRUE),
    .groups = "drop"
  )

# 4. Materialize the staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "fhfa_underserved"),
  fhfa_staging,
  overwrite = TRUE
)
