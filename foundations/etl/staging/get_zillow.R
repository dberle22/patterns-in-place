# In this script we get Zillow Data scraped directly from their website

# Set up our environment
# Create a single ingestion test
# Build our staging file
# Loop over all years

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
raw_dir <- file.path(data, "demographics", "raw", "zillow")
db_path <- get_env_path("DB_PATH")

## Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)



# Download Files ----
library(httr)
## ZHVI ----

### Set URLs ----
zhvi_state_url  <- "https://files.zillowstatic.com/research/public_csvs/zhvi/State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1764896489"
zhvi_state_file <- file.path(raw_dir, "zhvi_state.csv")

zhvi_county_url  <- "https://files.zillowstatic.com/research/public_csvs/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1764896489"
zhvi_county_file <- file.path(raw_dir, "zhvi_county.csv")

zhvi_city_url  <- "https://files.zillowstatic.com/research/public_csvs/zhvi/City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1764896489"
zhvi_city_file <- file.path(raw_dir, "zhvi_city.csv")

zhvi_zip_code_url  <- "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1764896489"
zhvi_zip_code_file <- file.path(raw_dir, "zhvi_zip_code.csv")


### Ingest files ----
if (!file.exists(zhvi_state_file)) {
  resp <- httr::GET(
    zhvi_state_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), zhvi_state_file)
}

if (!file.exists(zhvi_county_file)) {
  resp <- httr::GET(
    zhvi_county_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), zhvi_county_file)
}

if (!file.exists(zhvi_city_file)) {
  resp <- httr::GET(
    zhvi_city_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), zhvi_city_file)
}

if (!file.exists(zhvi_zip_code_file)) {
  resp <- httr::GET(
    zhvi_zip_code_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), zhvi_zip_code_file)
}


### Load Files to R ----
zhvi_state_raw <- read_csv(zhvi_state_file) %>%
  clean_names()

zhvi_county_raw <- read_csv(zhvi_county_file) %>%
  clean_names()

zhvi_city_raw <- read_csv(zhvi_city_file) %>%
  clean_names()

zhvi_zip_code_raw <- read_csv(zhvi_zip_code_file) %>%
  clean_names()

## ZORI ----

### Set URLs ----

zori_county_url  <- "https://files.zillowstatic.com/research/public_csvs/zori/County_zori_uc_sfrcondomfr_sm_month.csv?t=1764896489"
zori_county_file <- file.path(raw_dir, "zori_county.csv")

zori_city_url  <- "https://files.zillowstatic.com/research/public_csvs/zori/City_zori_uc_sfrcondomfr_sm_month.csv?t=1764896489"
zori_city_file <- file.path(raw_dir, "zori_city.csv")

zori_zip_code_url  <- "https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_uc_sfrcondomfr_sm_month.csv?t=1764896489"
zori_zip_code_file <- file.path(raw_dir, "zori_zip_code.csv")


### Ingest files ----

if (!file.exists(zori_county_file)) {
  resp <- httr::GET(
    zori_county_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), zori_county_file)
}

if (!file.exists(zori_city_file)) {
  resp <- httr::GET(
    zori_city_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), zori_city_file)
}

if (!file.exists(zori_zip_code_file)) {
  resp <- httr::GET(
    zori_zip_code_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), zori_zip_code_file)
}


### Load Files to R ----
zori_county_raw <- read_csv(zori_county_file) %>%
  clean_names()

zori_city_raw <- read_csv(zori_city_file) %>%
  clean_names()

zori_zip_code_raw <- read_csv(zori_zip_code_file) %>%
  clean_names()

# Create Staging Data ----
## Pivot data frame to long

## ZHVI ----
### State
zhvi_state <- zhvi_state_raw %>%
  filter(region_type == "state") %>%
  pivot_longer(
    cols = matches("^x\\d{4}_\\d{2}_\\d{2}$"),   # monthly date columns
    names_to  = "date_raw",
    values_to = "zhvi"
  ) %>%
  mutate(
    # strip leading "x", turn underscores into "-", then parse as Date
    date = str_remove(date_raw, "^x") |> 
      str_replace_all("_", "-") |> 
      as.Date(),
    year  = lubridate::year(date),
    month = lubridate::month(date)
  ) %>%
  select(state = region_name, region_type, date, year, month, zhvi) %>%
  filter(year > 2010)

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="zillow_zhvi_state"),
                  zhvi_state, overwrite = TRUE)
  
### County
zhvi_county <- zhvi_county_raw %>%
  filter(region_type == "county") %>%
  pivot_longer(
    cols = matches("^x\\d{4}_\\d{2}_\\d{2}$"),   # monthly date columns
    names_to  = "date_raw",
    values_to = "zhvi"
  ) %>%
  mutate(
    # strip leading "x", turn underscores into "-", then parse as Date
    date = str_remove(date_raw, "^x") |> 
      str_replace_all("_", "-") |> 
      as.Date(),
    year  = lubridate::year(date),
    month = lubridate::month(date),
    county_geoid = paste0(state_code_fips, municipal_code_fips)
  ) %>%
  select(county_name = region_name, region_type, state, metro, 
         state_code_fips, municipal_code_fips, county_geoid, date, year, month, zhvi) %>%
  filter(year > 2010)

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="zillow_zhvi_county"),
                  zhvi_county, overwrite = TRUE)

### City
zhvi_city <- zhvi_city_raw %>%
  filter(region_type == "city") %>%
  pivot_longer(
    cols = matches("^x\\d{4}_\\d{2}_\\d{2}$"),   # monthly date columns
    names_to  = "date_raw",
    values_to = "zhvi"
  ) %>%
  mutate(
    # strip leading "x", turn underscores into "-", then parse as Date
    date = str_remove(date_raw, "^x") |> 
      str_replace_all("_", "-") |> 
      as.Date(),
    year  = lubridate::year(date),
    month = lubridate::month(date)
  ) %>%
  select(city_name = region_name, region_type, state, metro, county_name, 
         date, year, month, zhvi) %>%
  filter(year > 2010)

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="zillow_zhvi_city"),
                  zhvi_city, overwrite = TRUE)

### Zip Code
zhvi_zip_code <- zhvi_zip_code_raw %>%
  filter(region_type == "zip") %>%
  pivot_longer(
    cols = matches("^x\\d{4}_\\d{2}_\\d{2}$"),   # monthly date columns
    names_to  = "date_raw",
    values_to = "zhvi"
  ) %>%
  mutate(
    # strip leading "x", turn underscores into "-", then parse as Date
    date = str_remove(date_raw, "^x") |> 
      str_replace_all("_", "-") |> 
      as.Date(),
    year  = lubridate::year(date),
    month = lubridate::month(date)
  ) %>%
  select(zip_code = region_name, region_type, state, city, metro, county_name, 
         date, year, month, zhvi) %>%
  filter(year > 2010)

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="zillow_zhvi_zip_code"),
                  zhvi_zip_code, overwrite = TRUE)

## ZORI ----
### County
zori_county <- zori_county_raw %>%
  filter(region_type == "county") %>%
  pivot_longer(
    cols = matches("^x\\d{4}_\\d{2}_\\d{2}$"),   # monthly date columns
    names_to  = "date_raw",
    values_to = "zori"
  ) %>%
  mutate(
    # strip leading "x", turn underscores into "-", then parse as Date
    date = str_remove(date_raw, "^x") |> 
      str_replace_all("_", "-") |> 
      as.Date(),
    year  = lubridate::year(date),
    month = lubridate::month(date),
    county_geoid = paste0(state_code_fips, municipal_code_fips)
  ) %>%
  select(county_name = region_name, region_type, state, metro, 
         state_code_fips, municipal_code_fips, county_geoid, date, year, month, zori) %>%
  filter(year > 2010)

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="zillow_zori_county"),
                  zori_county, overwrite = TRUE)

### City
zori_city <- zori_city_raw %>%
  filter(region_type == "city") %>%
  pivot_longer(
    cols = matches("^x\\d{4}_\\d{2}_\\d{2}$"),   # monthly date columns
    names_to  = "date_raw",
    values_to = "zori"
  ) %>%
  mutate(
    # strip leading "x", turn underscores into "-", then parse as Date
    date = str_remove(date_raw, "^x") |> 
      str_replace_all("_", "-") |> 
      as.Date(),
    year  = lubridate::year(date),
    month = lubridate::month(date)
  ) %>%
  select(city_name = region_name, region_type, state, metro, county_name, 
         date, year, month, zori) %>%
  filter(year > 2010)

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="zillow_zori_city"),
                  zori_city, overwrite = TRUE)

### Zip Code
zori_zip_code <- zori_zip_code_raw %>%
  filter(region_type == "zip") %>%
  pivot_longer(
    cols = matches("^x\\d{4}_\\d{2}_\\d{2}$"),   # monthly date columns
    names_to  = "date_raw",
    values_to = "zori"
  ) %>%
  mutate(
    # strip leading "x", turn underscores into "-", then parse as Date
    date = str_remove(date_raw, "^x") |> 
      str_replace_all("_", "-") |> 
      as.Date(),
    year  = lubridate::year(date),
    month = lubridate::month(date)
  ) %>%
  select(zip_code = region_name, region_type, state, city, metro, county_name, 
         date, year, month, zori) %>%
  filter(year > 2010)

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="zillow_zori_zip_code"),
                  zori_zip_code, overwrite = TRUE)

# Shutdown ----
dbDisconnect(con, shutdown = TRUE)
