# In this script we normalize BEA MARPP data into our Silver layer

# 1. Set up our Environment
# 2. Read in our Staging Data to R Data Frames
# 3. Standardize our value names
# 4. Union our Data Frames together
# 5. Check for duplicates
# 6. Compute new KPIs and select main columns
# 7. Create Wide and Long versions
# 8. Materialize to Silver

# Find our current directory 
getwd()

# 1. Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
bea_key <- get_env_path("BEA_KEY")
db_path <- get_env_path("DB_PATH")

## Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# 2. Read in our Staging Data to R Data Frames ----

## Metric Tables ----
cbsa_marpp_stage <- dbGetQuery(con, "SELECT * FROM staging.bea_regional_cbsa_marpp")
state_marpp_stage <- dbGetQuery(con, "SELECT * FROM staging.bea_regional_state_marpp")

## CBSA <> County Xwalk ----
cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")

## Reference Tables ----
line_codes_ref <- dbGetQuery(con, "SELECT * FROM silver.bea_regional_metrics_ref")

# 3. Standardize Value Names ----
# Column names are already standard and value columns are multiplied

## Create Long Data Set ----
# Union together tables, add Line Code Names from 
# Clean up the value names using the Line Code Names from our Ref table

# Union data frames together
marpp_stage_all <- bind_rows(
  cbsa_marpp_stage,
  state_marpp_stage
) %>%
  mutate(line_code = as.character(line_code))

# Keep only MARPP from Line Codes
line_codes_marpp <- line_codes_ref %>%
  filter(table %in% c("MARPP", "SARPP")) %>%
  select(table, line_code, metric_key, line_desc_clean)

# Join on line_code (and table, if present)
marpp_long <- marpp_stage_all %>%
  left_join(line_codes_marpp,
            by = c("table" = "table", "line_code" = "line_code"))

marpp_test <- marpp_long %>%
  filter(geo_level == "state")

# Dupe Check
dupes <- marpp_long %>%
  group_by(geo_level, geo_id, geo_name, period, table, metric_key) %>%
  summarize(count = n()) %>%
  ungroup() %>%
  filter(count > 1)

## Create the Wide data set ----
marpp_wide <- marpp_long %>%
  select(geo_level, geo_id, geo_name, period, table, metric_key, value) %>%
  pivot_wider(
    names_from  = metric_key,   
    values_from = value
  )

## Write data frames to our database ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_marpp_long"),
                  marpp_long, overwrite = TRUE)

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_marpp_wide"),
                  marpp_wide, overwrite = TRUE)

# Disconnect our DB ----
dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)