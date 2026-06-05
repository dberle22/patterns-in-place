# In this script we get BLS Data scraped directly from their website

# Find our current directory 
getwd()

# Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "bls")
db_path <- get_env_path("DB_PATH")

## Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Year range for LAUS (can adjust later)
laus_years <- 2010:2024

# Download a single LAUS Year to test ----
library(httr)

test_year <- 2024
two <- substr(test_year, 3, 4)

laus_url  <- glue("https://www.bls.gov/lau/laucnty{two}.xlsx")
laus_file <- file.path(raw_dir, glue("laucnty{two}.xlsx"))

if (!file.exists(laus_file)) {
  resp <- httr::GET(
    laus_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), laus_file)
}

laus_raw <- readxl::read_xlsx(laus_file, skip = 1) %>%
  clean_names()

names(laus_raw)
head(laus_raw)

# County ---- 
## Clean & Standardize Data ----
# Drop Footers, Create GEOID

laus_data <- laus_raw %>%
  transmute(
    geo_level = "county",
    # state_fips + county_fips → 5-digit GEOID
    geo_id    = sprintf("%02d%03d",
                        as.integer(state_fips_code),
                        as.integer(county_fips_code)),
    state_fips_code  = str_pad(as.character(state_fips_code),  width = 2, side = "left", pad = "0"),
    county_fips_code = str_pad(as.character(county_fips_code), width = 3, side = "left", pad = "0"),
    county_name = county_name_state_abbreviation,
    period = as.integer(year),
    labor_force = as.numeric(labor_force),
    employed = as.numeric(employed),
    unemployed = as.numeric(unemployed),
    unemployment_rate_percent = as.numeric(unemployment_rate_percent),
    src     = "BLS LAUS",
    version = "v1_raw"
  ) %>%
  filter(!is.na(state_fips_code), !is.na(county_fips_code))

## Loop over all years ----
laus_years <- 2010:2024

laus_county_all <- map_dfr(
  laus_years,
  \(yy) {
    message("Processing LAUS county file for year: ", yy)
    
    two <- substr(yy, 3, 4)
    laus_url  <- glue("https://www.bls.gov/lau/laucnty{two}.xlsx")
    laus_file <- file.path(raw_dir, glue("laucnty{two}.xlsx"))
    
    # Download via httr if file not already cached
    if (!file.exists(laus_file)) {
      resp <- httr::GET(
        laus_url,
        user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
      )
      httr::stop_for_status(resp)
      writeBin(content(resp, "raw"), laus_file)
    }
    
    # Read file: skip header rows, clean names
    laus_raw <- readxl::read_xlsx(laus_file, skip = 1) %>%
      janitor::clean_names()
    
    # Your transformation, with year-specific mapping
    laus_data <- laus_raw %>%
      transmute(
        geo_level = "county",
        # state_fips + county_fips → 5-digit GEOID
        geo_id    = sprintf("%02d%03d",
                            as.integer(state_fips_code),
                            as.integer(county_fips_code)),
        state_fips_code  = str_pad(as.character(state_fips_code),  width = 2, side = "left", pad = "0"),
        county_fips_code = str_pad(as.character(county_fips_code), width = 3, side = "left", pad = "0"),
        county_name      = county_name_state_abbreviation,
        period           = as.integer(year),
        labor_force      = as.numeric(labor_force),
        employed         = as.numeric(employed),
        unemployed       = as.numeric(unemployed),
        # use whatever the LAUS column is actually called (you saw unemployment_rate_percent)
        unemployment_rate_percent = as.numeric(unemployment_rate_percent),
        src     = "BLS LAUS",
        version = "v1_raw"
      ) %>%
      # Drop footer / bad rows
      filter(
        !is.na(state_fips_code),
        !is.na(county_fips_code)
      )
    
    laus_data
  }
)

glimpse(laus_county_all)

## Write to Stage ----
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bls_laus_county"),
                  laus_county_all, overwrite = TRUE)

# Shutdown ----
dbDisconnect(con, shutdown = TRUE)
