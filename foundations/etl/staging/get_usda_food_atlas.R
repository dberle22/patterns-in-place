# In this script we land a compact, source-faithful subset of the USDA Food
# Access Research Atlas workbook. The Atlas is already tract-native, so staging
# simply preserves the tract key, core food-desert flags, and the population
# burden counts we need for county and CBSA rollups downstream.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "access", "raw", "usda_food_atlas")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the current Atlas asset ----
atlas_vintage_year <- 2019L
atlas_xlsx_url <- "https://www.ers.usda.gov/media/5626/food-access-research-atlas-data-download-2019.xlsx?v=46096"
atlas_xlsx_path <- file.path(raw_dir, sprintf("usda_food_access_research_atlas_%s.xlsx", atlas_vintage_year))
atlas_sheet_name <- "Food Access Research Atlas"

download_food_atlas_xlsx <- function(url, dest_path) {
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

read_food_atlas_xlsx <- function(xlsx_path, sheet_name) {
  readxl::read_excel(
    xlsx_path,
    sheet = sheet_name,
    col_types = "guess"
  ) %>%
    janitor::clean_names()
}

normalize_food_atlas <- function(df) {
  df %>%
    transmute(
      year = atlas_vintage_year,
      tract_geoid = stringr::str_pad(as.character(.data$census_tract), width = 11, side = "left", pad = "0"),
      state_name = as.character(.data$state),
      county_name = as.character(.data$county),
      census_tract_label = as.character(.data$census_tract),
      urban_flag = as.integer(.data$urban),
      population_total = as.double(.data$pop2010),
      housing_units_total = as.double(.data$ohu2010),
      group_quarters_flag = as.integer(.data$group_quarters_flag),
      group_quarters_population = as.double(.data$numgqtrs),
      group_quarters_share = as.double(.data$pctgqtrs),
      lila_1_and_10_flag = as.integer(.data$lila_tracts_1and10),
      lila_half_and_10_flag = as.integer(.data$lila_tracts_half_and10),
      lila_1_and_20_flag = as.integer(.data$lila_tracts_1and20),
      lila_vehicle_flag = as.integer(.data$lila_tracts_vehicle),
      low_income_flag = as.integer(.data$low_income_tracts),
      low_access_1_and_10_flag = as.integer(.data$la1and10),
      low_access_half_and_10_flag = as.integer(.data$l_ahalfand10),
      low_access_1_and_20_flag = as.integer(.data$la1and20),
      low_access_pop_1 = as.double(.data$lapop1),
      low_access_pop_1_share = as.double(.data$lapop1share),
      low_access_pop_1_10 = as.double(.data$lapop1_10),
      low_access_pop_half_10 = as.double(.data$lapop05_10),
      low_access_pop_1_20 = as.double(.data$lapop1_20),
      low_access_low_income_pop_1 = as.double(.data$lalowi1),
      low_access_low_income_pop_1_share = as.double(.data$lalowi1share),
      low_access_low_income_pop_1_10 = as.double(.data$lalowi1_10),
      poverty_rate = as.double(.data$poverty_rate),
      median_family_income = as.double(.data$median_family_income),
      low_access_children_1 = as.double(.data$lakids1),
      low_access_children_1_share = as.double(.data$lakids1share),
      low_access_seniors_1 = as.double(.data$laseniors1),
      low_access_seniors_1_share = as.double(.data$laseniors1share),
      low_access_no_vehicle_housing_1 = as.double(.data$lahunv1),
      low_access_no_vehicle_housing_1_share = as.double(.data$lahunv1share),
      low_access_snap_housing_1 = as.double(.data$lasnap1),
      low_access_snap_housing_1_share = as.double(.data$lasnap1share)
    )
}

# 3. Download and normalize the current Atlas release ----
download_food_atlas_xlsx(atlas_xlsx_url, atlas_xlsx_path)

food_atlas_staging <- read_food_atlas_xlsx(
  xlsx_path = atlas_xlsx_path,
  sheet_name = atlas_sheet_name
) %>%
  normalize_food_atlas()

# 4. Contract checks ----
invalid_tract_rows <- food_atlas_staging %>%
  filter(is.na(.data$tract_geoid) | !stringr::str_detect(.data$tract_geoid, "^\\d{11}$"))

if (nrow(invalid_tract_rows) > 0) {
  stop(
    glue("USDA Food Atlas staging contains {nrow(invalid_tract_rows)} rows with invalid 11-digit tract GEOIDs."),
    call. = FALSE
  )
}

duplicate_rows <- food_atlas_staging %>%
  count(.data$tract_geoid, .data$year, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_rows) > 0) {
  stop(
    glue("USDA Food Atlas staging is not unique at tract_geoid + year. Duplicate keys found: {nrow(duplicate_rows)}"),
    call. = FALSE
  )
}

# 5. Load the normalized staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "usda_food_atlas"),
  food_atlas_staging,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
