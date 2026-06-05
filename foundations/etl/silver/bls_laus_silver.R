# In this script we normalize BEA CAINC1 data into our Silver layer

# 1. Set up our Environment
# 2. Read in our Staging Data to R Data Frames
# 3. Build Final Tables
# 3.1. Add XWalks
# 3.2. Recompute Unemployment Rate
# 3.3 Create Wide and Long versions
# 4. Materialize to Silver

# Find our current directory 
getwd()

# 1. Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
db_path <- get_env_path("DB_PATH")

## Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

### List the tables available in the DB
tables <- dbListTables(con)
print(tables)

# 2. Read in our Staging Data to R Data Frames ----

## Metric Tables ----
county_laus_stage <- dbGetQuery(con, "SELECT * FROM staging.bls_laus_county")

## CBSA <> County Xwalk ----
cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")
county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state")


# 3. Build Final Tables ----
## 3.1. Add XWalks ----

### Add CBSA via Xwalk
laus_cbsa_base <- county_laus_stage %>%
  left_join(cbsa_county_xwalk %>% 
              select(cbsa_code, cbsa_name, state_name, county_geoid),
            by = c("geo_id" = "county_geoid"))

## State ---- 
### Rename Vars
laus_county <- laus_cbsa_base %>%
  select(geo_level, geo_id, geo_name = county_name, period,
         labor_force, employed, unemployed, unemployment_rate_percent)

## CBSA ----
### Select Vars and Aggregate
#### Dims: Geo Level, Geo ID, Geo Name, Period
#### Metrics: Employed, Unemployed, Labor Force
#### Calculated: Unemployment Rate
laus_cbsa <- laus_cbsa_base %>%
  group_by(cbsa_code, cbsa_name, period) %>%
  summarize(labor_force = sum(labor_force, na.rm = TRUE),
            employed = sum(employed, na.rm = TRUE),
            unemployed = sum(unemployed, na.rm = TRUE)) %>%
  ungroup() %>%
  mutate(unemployment_rate_percent = (unemployed / labor_force) * 100,
         geo_level = "CBSA"
         ) %>%
  select(geo_level, geo_id = cbsa_code, geo_name = cbsa_name, period,
         labor_force, employed, unemployed, unemployment_rate_percent)
  
# Check for Dupes - No Dupes
cbsa_dupe <- laus_cbsa %>%
  select(geo_id, period) %>%
  group_by(geo_id, period) %>%
  summarize(records = n()) %>%
  filter(records > 1)

## State ----
### Build State Code <> Name Map
state_code <- county_state_xwalk %>%
  select(state_fip, state_abbr) %>%
  unique()

laus_state <- laus_cbsa_base %>%
  group_by(state_fips_code, period) %>%
  summarize(labor_force = sum(labor_force, na.rm = TRUE),
            employed = sum(employed, na.rm = TRUE),
            unemployed = sum(unemployed, na.rm = TRUE)) %>%
  ungroup() %>%
  mutate(unemployment_rate_percent = (unemployed / labor_force) * 100,
         geo_level = "State"
         ) %>%
  left_join(state_code, by = c("state_fips_code" = "state_fip")) %>%
  select(geo_level, geo_id = state_fips_code, geo_name = state_abbr, period,
         labor_force, employed, unemployed, unemployment_rate_percent)

# Union DFs together ----
laus <- rbind(
  laus_state,
  laus_cbsa,
  laus_county
)

# Materialize to Silver ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bls_laus_wide"),
                  laus, overwrite = TRUE)

# Shutdown ----
dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
