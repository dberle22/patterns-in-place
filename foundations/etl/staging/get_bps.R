# In this script we get HUD CHAS Data scraped directly from their website

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
raw_dir <- file.path(data, "demographics", "raw", "bps")
db_path <- get_env_path("DB_PATH")

## Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Ingest files from Bronze ----
## Set file paths 
bps_file <- file.path(raw_dir, "BPS Compiled_2025_08.csv")

## Read data 
bps_master <- read_csv(bps_file)

# Create smaller Staging files ----
## Filter to Annual, select Geo columns, select metrics

## Find Location Types
bps_master %>%
  select(LOCATION_TYPE) %>%
  unique()

## Region 
bps_region <- bps_master %>%
  filter(PERIOD == "Annual",
         LOCATION_TYPE == "Region"
         ) %>%
  select(FILE_NAME, LOCATION_TYPE, LOCATION_NAME, PERIOD, REGION_CODE, REGION_NAME,
         SURVEY_DATE, YEAR, TOTAL_BLDGS, TOTAL_UNITS, TOTAL_VALUE,
         BLDGS_1_UNIT, BLDGS_2_UNITS, BLDGS_3_4_UNITS, BLDGS_5_UNITS, 
         UNITS_1_UNIT, UNITS_2_UNITS, UNITS_3_4_UNITS, UNITS_5_UNITS,
         VALUE_1_UNIT, VALUE_2_UNITS, VALUE_3_4_UNITS, VALUE_5_UNITS)

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bps_region"),
                  bps_region, overwrite = TRUE)

## Division ----
bps_division <- bps_master %>%
  filter(PERIOD == "Annual",
         LOCATION_TYPE == "Division"
         ) %>%
  select(FILE_NAME, LOCATION_TYPE, LOCATION_NAME, PERIOD, DIVISION_CODE, DIVISION_NAME,
         SURVEY_DATE, YEAR, TOTAL_BLDGS, TOTAL_UNITS, TOTAL_VALUE,
         BLDGS_1_UNIT, BLDGS_2_UNITS, BLDGS_3_4_UNITS, BLDGS_5_UNITS, 
         UNITS_1_UNIT, UNITS_2_UNITS, UNITS_3_4_UNITS, UNITS_5_UNITS,
         VALUE_1_UNIT, VALUE_2_UNITS, VALUE_3_4_UNITS, VALUE_5_UNITS)

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bps_division"),
                  bps_division, overwrite = TRUE)

## State ----
bps_state <- bps_master %>%
  filter(PERIOD == "Annual",
         LOCATION_TYPE == "State"
         ) %>%
  select(FILE_NAME, LOCATION_TYPE, LOCATION_NAME, PERIOD, STATE_CODE, STATE_NAME,
         SURVEY_DATE, YEAR, TOTAL_BLDGS, TOTAL_UNITS, TOTAL_VALUE,
         BLDGS_1_UNIT, BLDGS_2_UNITS, BLDGS_3_4_UNITS, BLDGS_5_UNITS, 
         UNITS_1_UNIT, UNITS_2_UNITS, UNITS_3_4_UNITS, UNITS_5_UNITS,
         VALUE_1_UNIT, VALUE_2_UNITS, VALUE_3_4_UNITS, VALUE_5_UNITS)

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bps_state"),
                  bps_state, overwrite = TRUE)

## Metro ----
bps_cbsa <- bps_master %>%
  filter(PERIOD == "Annual",
         LOCATION_TYPE %in% c("Metro", "Micro")
         ) %>%
  select(FILE_NAME, LOCATION_TYPE, LOCATION_NAME, PERIOD, CBSA_CODE, 
         CBSA_NAME, CSA_CODE, STATE_NAME,
         SURVEY_DATE, YEAR, TOTAL_BLDGS, TOTAL_UNITS, TOTAL_VALUE,
         BLDGS_1_UNIT, BLDGS_2_UNITS, BLDGS_3_4_UNITS, BLDGS_5_UNITS, 
         UNITS_1_UNIT, UNITS_2_UNITS, UNITS_3_4_UNITS, UNITS_5_UNITS,
         VALUE_1_UNIT, VALUE_2_UNITS, VALUE_3_4_UNITS, VALUE_5_UNITS)

## County ----
bps_county <- bps_master %>%
  filter(PERIOD == "Annual",
         LOCATION_TYPE == "County"
         ) %>%
  select(FILE_NAME, LOCATION_TYPE, LOCATION_NAME, PERIOD, COUNTY_CODE, 
         COUNTY_NAME, FIPS_COUNTY_5_DIGITS, STATE_CODE, STATE_NAME,
         SURVEY_DATE, YEAR, TOTAL_BLDGS, TOTAL_UNITS, TOTAL_VALUE,
         BLDGS_1_UNIT, BLDGS_2_UNITS, BLDGS_3_4_UNITS, BLDGS_5_UNITS, 
         UNITS_1_UNIT, UNITS_2_UNITS, UNITS_3_4_UNITS, UNITS_5_UNITS,
         VALUE_1_UNIT, VALUE_2_UNITS, VALUE_3_4_UNITS, VALUE_5_UNITS) %>%
  mutate(
    across(
      where(is.character),
      ~ iconv(.x, from = "", to = "UTF-8", sub = "")
    )
  )

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bps_county"),
                  bps_county, overwrite = TRUE)

## Place 
bps_place <- bps_master %>%
  filter(PERIOD == "Annual",
         LOCATION_TYPE == "Place"
         ) %>%
  select(FILE_NAME, LOCATION_TYPE, LOCATION_NAME, PERIOD, COUNTY_CODE, 
         COUNTY_NAME, FIPS_COUNTY_5_DIGITS, STATE_CODE, STATE_NAME,
         FIPS_PLACE_CODE, ID_6_DIGIT, PLACE_NAME, ZIP_CODE,
         SURVEY_DATE, YEAR, TOTAL_BLDGS, TOTAL_UNITS, TOTAL_VALUE,
         BLDGS_1_UNIT, BLDGS_2_UNITS, BLDGS_3_4_UNITS, BLDGS_5_UNITS, 
         UNITS_1_UNIT, UNITS_2_UNITS, UNITS_3_4_UNITS, UNITS_5_UNITS,
         VALUE_1_UNIT, VALUE_2_UNITS, VALUE_3_4_UNITS, VALUE_5_UNITS) %>%
  mutate(
    across(
      where(is.character),
      ~ iconv(.x, from = "", to = "UTF-8", sub = "")
    )
  )

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bps_place"),
                  bps_place, overwrite = TRUE)

# Shutdown ----
dbDisconnect(con, shutdown = TRUE)
