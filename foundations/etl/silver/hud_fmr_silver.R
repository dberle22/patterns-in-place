# In this script we normalize HUD FMR data into our Silver layer

# 1. Set up our Environment
# 2. Read in our Staging Data to R Data Frames
# 3. Build Final Tables
# 3.1. Add XWalks
# 3.2. Compute Rents with Pop Weighting
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
county_fmr <- dbGetQuery(con, "SELECT * FROM staging.hud_fmr_county")
county_rent50 <- dbGetQuery(con, "SELECT * FROM staging.hud_rent50_county")
zip_fmr <- dbGetQuery(con, "SELECT * FROM staging.hud_fmr_zip")

## CBSA <> County Xwalk ----
cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")
county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state")


# 3. Build Final Tables ----
# Geo Level, Geo ID, Geo Name, Period, Metrics

## FMR ----
### 3.1. Add XWalks ----
fmr_base <- county_fmr %>%
  left_join(cbsa_county_xwalk %>% 
              select(cbsa_code, cbsa_name, county_geoid),
            by = c("county_geoid" = "county_geoid"))

### 3.2 Comupte Weighted Averages ----
#### CBSA ----
fmr_cbsa_wide <- fmr_base %>%
  group_by(cbsa_code, cbsa_name, period) %>%
  summarize(fmr_0br = weighted.mean(fmr_0br, w = pop_weight, na.rm = TRUE),
            fmr_1br = weighted.mean(fmr_1br, w = pop_weight, na.rm = TRUE),
            fmr_2br = weighted.mean(fmr_2br, w = pop_weight, na.rm = TRUE),
            fmr_3br = weighted.mean(fmr_3br, w = pop_weight, na.rm = TRUE),
            fmr_4br = weighted.mean(fmr_4br, w = pop_weight, na.rm = TRUE)
            ) %>%
  ungroup() %>%
  mutate(geo_level = "CBSA") %>%
  select(geo_level, geo_id = cbsa_code, geo_name = cbsa_name, period,
         fmr_0br, fmr_1br, fmr_2br, fmr_3br, fmr_4br)

#### State ----
fmr_state_wide <- fmr_base %>%
  group_by(state_fips, state_abbr, period) %>%
  summarize(fmr_0br = weighted.mean(fmr_0br, w = pop_weight, na.rm = TRUE),
            fmr_1br = weighted.mean(fmr_1br, w = pop_weight, na.rm = TRUE),
            fmr_2br = weighted.mean(fmr_2br, w = pop_weight, na.rm = TRUE),
            fmr_3br = weighted.mean(fmr_3br, w = pop_weight, na.rm = TRUE),
            fmr_4br = weighted.mean(fmr_4br, w = pop_weight, na.rm = TRUE)
  ) %>%
  ungroup() %>%
  mutate(geo_level = "State") %>%
  select(geo_level, geo_id = state_fips, geo_name = state_abbr, period,
         fmr_0br, fmr_1br, fmr_2br, fmr_3br, fmr_4br)

#### County ----
# Reshape
fmr_county_wide <- fmr_base %>%
  mutate(geo_level = "County",
         county_name = paste0(county_name, ", ", state_abbr)) %>%
  select(geo_level, geo_id = county_geoid, geo_name = county_name, period,
         fmr_0br, fmr_1br, fmr_2br, fmr_3br, fmr_4br)

#### Zip ----
fmr_zip_wide <- zip_fmr %>%
  mutate(geo_level = "Zip Code") %>%
  select(geo_level, geo_id = zip_geoid, geo_name = zip_geoid, period,
         fmr_0br = safmr_0br, fmr_1br = safmr_1br, 
         fmr_2br = safmr_2br, fmr_3br = safmr_3br, fmr_4br = safmr_4br)

#### Union Together ----
fmr_wide <- rbind(
  fmr_state_wide,
  fmr_cbsa_wide,
  fmr_county_wide,
  fmr_zip_wide
)

#### Write to DB ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="hud_fmr_wide"),
                  fmr_wide, overwrite = TRUE)

## Rent 50th Percentile ----
### 3.1. Add XWalks ----
rent50_base <- county_rent50 %>%
  left_join(cbsa_county_xwalk %>% 
              select(cbsa_code, cbsa_name, county_geoid),
            by = c("county_geoid" = "county_geoid"))

### 3.2 Comupte Weighted Averages ----
#### CBSA ----
rent50_cbsa_wide <- rent50_base %>%
  group_by(cbsa_code, cbsa_name, period) %>%
  summarize(rent50_0br = weighted.mean(rent50_0br, w = pop_weight, na.rm = TRUE),
            rent50_1br = weighted.mean(rent50_1br, w = pop_weight, na.rm = TRUE),
            rent50_2br = weighted.mean(rent50_2br, w = pop_weight, na.rm = TRUE),
            rent50_3br = weighted.mean(rent50_3br, w = pop_weight, na.rm = TRUE),
            rent50_4br = weighted.mean(rent50_4br, w = pop_weight, na.rm = TRUE)
  ) %>%
  ungroup() %>%
  mutate(geo_level = "CBSA") %>%
  select(geo_level, geo_id = cbsa_code, geo_name = cbsa_name, period,
         rent50_0br, rent50_1br, rent50_2br, rent50_3br, rent50_4br)

#### State ----
rent50_state_wide <- rent50_base %>%
  group_by(state_fips, state_abbr, period) %>%
  summarize(rent50_0br = weighted.mean(rent50_0br, w = pop_weight, na.rm = TRUE),
            rent50_1br = weighted.mean(rent50_1br, w = pop_weight, na.rm = TRUE),
            rent50_2br = weighted.mean(rent50_2br, w = pop_weight, na.rm = TRUE),
            rent50_3br = weighted.mean(rent50_3br, w = pop_weight, na.rm = TRUE),
            rent50_4br = weighted.mean(rent50_4br, w = pop_weight, na.rm = TRUE)
  ) %>%
  ungroup() %>%
  mutate(geo_level = "State") %>%
  select(geo_level, geo_id = state_fips, geo_name = state_abbr, period,
         rent50_0br, rent50_1br, rent50_2br, rent50_3br, rent50_4br)

#### County ----
# Reshape
rent50_county_wide <- rent50_base %>%
  mutate(geo_level = "County",
         county_name = paste0(county_name, ", ", state_abbr)) %>%
  select(geo_level, geo_id = county_geoid, geo_name = county_name, period,
         rent50_0br, rent50_1br, rent50_2br, rent50_3br, rent50_4br)


#### Union Together ----
rent50_wide <- rbind(
  rent50_state_wide,
  rent50_cbsa_wide,
  rent50_county_wide
)

#### Write to DB ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="hud_rent50_wide"),
                  rent50_wide, overwrite = TRUE)

# Shutdown ----
dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
