# In this script we normalize BEA CAINC1 data into our Silver layer

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
county_cainc1_stage <- dbGetQuery(con, "SELECT * FROM staging.bea_regional_county_cainc1")
cbsa_cainc1_stage <- dbGetQuery(con, "SELECT * FROM staging.bea_regional_cbsa_cainc1")
state_cainc1_stage <- dbGetQuery(con, "SELECT * FROM staging.bea_regional_state_cainc1")

## CBSA <> County Xwalk ----
cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")

## Reference Tables ----
line_codes_ref <- dbGetQuery(con, "SELECT * FROM silver.bea_regional_metrics_ref")


# 3. Build Final Tables ----
# Column names are already standard and value columns are multiplied

## Define our metrics ----

line_codes_ref %>%
  filter(table == "CAINC1") %>%
  select(line_code, metric_key, line_desc_clean) %>%
  unique()

line_codes_cainc1 <- line_codes_ref %>%
  filter(table == "CAINC1") %>%
  unique()

## County ----
### Add Line Code Refs to the DF and select base columns ----
county_base <- county_cainc1_stage %>%
  mutate(line_code = as.character(line_code)) %>%
  left_join(line_codes_cainc1,
            by = c("table" = "table", "line_code" = "line_code")) %>%
  select(table, code, geo_level, geo_id, geo_name, 
         period, line_desc_clean, metric_key, value, note_ref)

### De-dupe on the county level & calculate totals kpis ----
county_totals <- county_base %>%
  filter(metric_key %in% c("pi_total", "population")) %>%
  group_by(table, code, geo_level, geo_id, geo_name, 
           period, line_desc_clean, metric_key) %>%
  summarize(value = sum(value, na.rm = TRUE)) %>%
  ungroup()

#### Check for dupes - Good to go ----
county_dupe <- county_totals %>%
  select(code, table, geo_id, period, metric_key) %>%
  group_by(geo_id, period, metric_key) %>%
  summarize(records = n()) %>%
  filter(records > 1)

### Pivot table to wide format to calculate income per capita then reform
county_pc <- county_totals %>%
  select(geo_id, geo_name, geo_level, period, table, metric_key, value) %>%
  pivot_wider(
    names_from  = metric_key,   # pi_total, pi_per_capita, population
    values_from = value
  ) %>%
  mutate(pi_per_capita = pi_total / population) %>%
  mutate(code = "CAINC1-3",
         metric_key = "pi_per_capita",
         line_desc_clean = "Per capita personal income") %>%
  select(table, code, geo_level, geo_id, geo_name, period,
         line_desc_clean, metric_key, value = pi_per_capita)

### Bind Rows to make long data frame ----
county_long <- rbind(
  county_totals,
  county_pc
)


## CBSA ----
### Build CBSA based on our County DFs

### Join Counties to XWalk ----
cbsa_rebase_totals <- county_totals %>%
  dplyr::inner_join(
    cbsa_county_xwalk %>%
      select(county_geoid, county_name, county_flag, 
             cbsa_code, cbsa_name, cbsa_type),
    by = c("geo_id" = "county_geoid")
  )

### Recalculate Totals KPIs ----
cbsa_totals <- cbsa_rebase_totals %>%
  filter(metric_key %in% c("pi_total", "population")) %>%
  group_by(table, code, cbsa_code, cbsa_name, 
           period, line_desc_clean, metric_key) %>%
  summarize(value = sum(value, na.rm = TRUE)) %>%
  ungroup() %>%
  mutate(geo_level = "cbsa") %>%
  select(table, code, geo_level, geo_id = cbsa_code, geo_name = cbsa_name,
         period, line_desc_clean, metric_key, value)
 
#### Check for dupes - Good to go ----
cbsa_dupe <- cbsa_totals %>%
  select(code, table, geo_id, period, metric_key) %>%
  group_by(geo_id, period, metric_key) %>%
  summarize(records = n()) %>%
  filter(records > 1)

### Calculate and Reshape Rates ----
cbsa_pc <- cbsa_totals %>%
  select(geo_id, geo_name, geo_level, period, table, metric_key, value) %>%
  pivot_wider(
    names_from  = metric_key,   # pi_total, pi_per_capita, population
    values_from = value
  ) %>%
  mutate(pi_per_capita = pi_total / population) %>%
  mutate(code = "CAINC1-3",
         metric_key = "pi_per_capita",
         line_desc_clean = "Per capita personal income") %>%
  select(table, code, geo_level, geo_id, geo_name, period,
         line_desc_clean, metric_key, value = pi_per_capita)

### Bind Rows to make long data frame ----
cbsa_long <- rbind(
  cbsa_totals,
  cbsa_pc
)

## State
### Join State DF to Line Code Ref, Select final columns
state_base <- state_cainc1_stage %>%
  mutate(line_code = as.character(line_code)) %>%
  left_join(line_codes_cainc1,
            by = c("table" = "table", "line_code" = "line_code")) %>%
select(table, code, geo_level, geo_id, geo_name, 
       period, line_desc_clean, metric_key, value)


## Create Final DFs ----
### Bind Long DFs together ----
long_df <- rbind(
  county_long,
  cbsa_long,
  state_base
)

### Pivot Long DFs wider ----
wide_df <- long_df %>%
  select(geo_level, geo_id, geo_name, period, table, metric_key, value) %>%
  pivot_wider(
    names_from  = metric_key,   # pi_total, pi_per_capita, population
    values_from = value
  )

## Write data frames to our database ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_cainc1_long"),
                  long_df, overwrite = TRUE)

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_cainc1_wide"),
                  wide_df, overwrite = TRUE)

# Disconnect our DB ----
dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
