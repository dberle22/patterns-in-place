# In this script we get HUD FMR Data scraped directly from their website

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
raw_dir <- file.path(data, "demographics", "raw", "hud")
db_path <- get_env_path("DB_PATH")

## Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Year range for HUD (can adjust later)
hud_years <- 2020:2026

# Scrape from HUD ----
library(httr)

## Store download links ----
fmr_county_url <- "https://www.huduser.gov/portal/datasets/fmr/fmr2023/FY23_FMRs_revised.xlsx"
safmr_zip_url <- "https://www.huduser.gov/portal/datasets/fmr/fmr2023/fy2023_safmrs_revised.xlsx"
rent50_county_url <- "https://www.huduser.gov/portal/datasets/50thper/FY2023_FMR_50_county_rev.xlsx"
rent50_area_url <- "https://www.huduser.gov/portal/datasets/50thper/FY2023_FMR_50_area_rev.xlsx"

fmr_county_file <- file.path(raw_dir, "fmr_county_2023.xlsx")
safmr_zip_file <- file.path(raw_dir, "safmr_zip_2023.xlsx")
rent50_county_file <- file.path(raw_dir, "rent50_county_2023.xlsx")
rent50_area_file <- file.path(raw_dir, "rent50_area_2023.xlsx")

## Scrape data into Bronze ----
### FMR County ----
if (!file.exists(fmr_county_file)) {
  resp <- httr::GET(
    fmr_county_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), fmr_county_file)
}

### FMR Zip ----
if (!file.exists(safmr_zip_file)) {
  resp <- httr::GET(
    safmr_zip_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), safmr_zip_file)
}

### 50th Percentile County Rent ----
if (!file.exists(rent50_county_file)) {
  resp <- httr::GET(
    rent50_county_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), rent50_county_file)
}

### 50th Percentile Area Rent ----
if (!file.exists(rent50_area_file)) {
  resp <- httr::GET(
    rent50_area_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), rent50_area_file)
}

# Build Staging Data ----

## Load scraped data ----
fmr_county_2023_raw <- readxl::read_xlsx(fmr_county_file) %>%
  clean_names()

fmr_zip_2023_raw <- readxl::read_xlsx(safmr_zip_file) %>%
  clean_names()

rent50_county_2023_raw <- readxl::read_xlsx(rent50_county_file) %>%
  clean_names()

rent50_area_2023_raw <- readxl::read_xlsx(rent50_area_file) %>%
  clean_names()

## Clean and standardize names ----

### FMR County ----
fmr_county_staging <- fmr_county_2023_raw %>%
  transmute(
    # ID / Geography
    county_geoid = str_sub(as.character(fips), 1, 5),
    state_fips = str_sub(county_geoid, 1, 2),
    county_name = countyname,
    state_abbr = state_alpha,
    hud_area_name = hud_area_name,
    hud_area_code = hud_area_code,
    metro_flag = ifelse(metro == 1, 1L, 0L),
    
    # Year
    period = 2023L,
    
    # FMRs by bedroom
    fmr_0br = fmr_0,
    fmr_1br = fmr_1,
    fmr_2br = fmr_2,
    fmr_3br = fmr_3,
    fmr_4br = fmr_4,
    
    # Population Weight
    pop_weight = pop2020
  )

#### Write to DB ----
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="hud_fmr_county"),
                  fmr_county_staging, overwrite = TRUE)

### FMR Zip ----
fmr_zip_staging <- fmr_zip_2023_raw %>%
  transmute(
    # IDs
    zip_geoid    = str_sub(as.character(zip_code), 1, 5),
    hud_area_code = hud_area_code,
    hud_area_name = hud_metro_fair_market_rent_area_name,
    
    # Area type based on prefix
    area_type = case_when(
      str_starts(hud_area_code, "METRO") ~ "metro",
      str_starts(hud_area_code, "NCNTY") ~ "nonmetro_county",
      TRUE                               ~ "other"
    ),
    
    # Last 5 characters of HUD Area Code are usually the CBSA or county FIPS
    area_geoid  = str_sub(hud_area_code, -5),
    
    period  = 2023,
    
    safmr_0br = safmr_0br,
    safmr_1br = safmr_1br,
    safmr_2br = safmr_2br,
    safmr_3br = safmr_3br,
    safmr_4br = safmr_4br
  ) %>%
  filter(!is.na(zip_geoid))

#### Write to DB ----
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="hud_fmr_zip"),
                  fmr_zip_staging, overwrite = TRUE)

### 50th Percentile Rent County ----
rent50_county_staging <- rent50_county_2023_raw %>%
  transmute(
    # ID / Geography
    county_geoid = str_sub(as.character(fips2010), 1, 5),
    state_fips = as.character(state_code),
    county_fips = as.character(county_code),
    county_name = cntyname,
    state_abbr = state_alpha,
    hud_area_name = hud_areaname,
    hud_area_code = hud_area_code,
    metro_flag = case_when(
      str_starts(hud_area_code, "METRO") ~ "metro",
      str_starts(hud_area_code, "NCNTY") ~ "nonmetro_county",
      TRUE                               ~ "other"
    ),
    
    # Year
    period = 2023L,
    
    # FMRs by bedroom
    rent50_0br = rent_50_0,
    rent50_1br = rent_50_1,
    rent50_2br = rent_50_2,
    rent50_3br = rent_50_3,
    rent50_4br = rent_50_4,
    
    # Population Weight
    pop_weight = pop2020
  )

#### Write to DB ----
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="hud_rent50_county"),
                  rent50_county_staging, overwrite = TRUE)


# Shutdown ----
dbDisconnect(con, shutdown = TRUE)