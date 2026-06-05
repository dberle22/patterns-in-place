# In this script we model ACS Data to Silver

# 1. Set up our Environment
# 2. Read in our Staging Data to R Data Frames
# 3. Add Geo Level to each table, drop _M, rename columns
# 4. Union our Data Frames together
# 5. Compute buckets and select main columns
# 6. Materialize to Silver

# 1. Set up our Environment ----
# Find our current directory 
getwd()

# Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
bronze_acs <- get_env_path("DATA_DEMO_RAW")
db_path <- get_env_path("DB_PATH")

# Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# 2. Read in our Staging Data to R Data Frames ----
us_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_us")
region_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_region")
division_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_division")
state_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_state")
county_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_county")
place_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_place")
zcta_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_zcta")

# Tracts
tract_all_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_tract")

# tract_fl_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_tract_fl")
# tract_ga_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_tract_ga")
# tract_nc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_tract_nc")
# tract_sc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_income_tract_sc")

## CBSA <> County Xwalk ----
cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")

# 3. Add Geo Level to each table, drop _M, rename columns ----
us_acs_clean <- standardize_acs_df(us_acs_stage, "US", drop_e = FALSE)
region_acs_clean <- standardize_acs_df(region_acs_stage, "Region")
division_acs_clean<- standardize_acs_df(division_acs_stage, "division")
state_acs_clean   <- standardize_acs_df(state_acs_stage, "state")
county_acs_clean  <- standardize_acs_df(county_acs_stage, "county")
place_acs_clean   <- standardize_acs_df(place_acs_stage, "place")
zcta_acs_clean    <- standardize_acs_df(zcta_acs_stage, "zcta")
tract_all_clean    <- standardize_acs_df(tract_all_acs_stage, "tract")

# tract_nc_clean    <- standardize_acs_df(tract_nc_acs_stage, "tract")
# tract_fl_clean    <- standardize_acs_df(tract_fl_acs_stage, "tract")
# tract_ga_clean    <- standardize_acs_df(tract_ga_acs_stage, "tract")
# tract_sc_clean    <- standardize_acs_df(tract_sc_acs_stage, "tract")

# 4. Union our Data Frames together ----
## Create CBSA Rebase ----
## Median HH Income, Per Capita Income and Gini are weighted, the rest are totals
### Join CBSA Xwalk to Counties ----
cbsa_base <- county_acs_clean %>%
  inner_join(cbsa_county_xwalk %>% select(cbsa_code, cbsa_name, county_geoid),
             by = c("geo_id" = "county_geoid"))

### Create Rebased Files ----
cbsa_hh_inc <- sum_pops_by_cbsa(
  df = cbsa_base,
  pop_pattern = "hh_inc_"
)

cbsa_pov <- sum_pops_by_cbsa(
  df = cbsa_base,
  pop_pattern = "pov_"
)

cbsa_weighted_avg <- cbsa_base %>%
  dplyr::group_by(cbsa_code, cbsa_name, year) %>%
  dplyr::summarise(
    median_hh_incomeE = stats::weighted.mean(median_hh_incomeE, hh_inc_totalE, na.rm = TRUE),
    per_capita_incomeE = stats::weighted.mean(per_capita_incomeE, pov_universeE, na.rm = TRUE),
    gini_indexE = stats::weighted.mean(gini_indexE, pov_universeE, na.rm = TRUE),
    .groups = "drop"
  )

### Final CBSA File ----
#### Join staging files and reorder
cbsa_acs_clean <- cbsa_hh_inc %>%
  left_join(cbsa_pov, by = c("cbsa_code", "cbsa_name", "year")) %>%
  left_join(cbsa_weighted_avg, by = c("cbsa_code", "cbsa_name", "year")) %>%
  mutate(geo_level = "cbsa") %>%
  select(geo_level, geo_id = cbsa_code, geo_name = cbsa_name, year,
         median_hh_incomeE, per_capita_incomeE, pov_universeE, pov_belowE,
         hh_inc_totalE:hh_inc_200k_plusE, gini_indexE)

## Union Tracts together ----
# tract_all_clean <- dplyr::bind_rows(
#   tract_nc_clean,
#   tract_fl_clean,
#   tract_ga_clean,
#   tract_sc_clean
# )

## Union all DFs ----
all_acs_clean <- dplyr::bind_rows(
  us_acs_clean,
  region_acs_clean,
  division_acs_clean,
  state_acs_clean,
  cbsa_acs_clean,
  county_acs_clean,
  place_acs_clean,
  zcta_acs_clean,
  tract_all_clean
)

# 5. Compute buckets and select main columns ----
income_silver_kpi <- all_acs_clean %>%
  mutate(
    median_hh_income  = median_hh_incomeE,
    per_capita_income = per_capita_incomeE,
    pov_universe      = pov_universeE,
    pov_below         = pov_belowE,
    pov_rate          = pov_below / pov_universe,
    gini_index        = gini_indexE
  ) %>%
  # optional distribution shares
  mutate(
    pct_hh_lt25k   = (hh_inc_lt10kE + hh_inc_10k_15kE + hh_inc_15k_20kE + hh_inc_20k_25kE) / hh_inc_totalE,
    pct_hh_25k_50k = (hh_inc_25k_30kE + hh_inc_30k_35kE + hh_inc_35k_40kE + hh_inc_40k_45kE + hh_inc_45k_50kE) / hh_inc_totalE,
    pct_hh_50k_100k = (hh_inc_50k_60kE + hh_inc_60k_75kE + hh_inc_75k_100kE) / hh_inc_totalE,
    pct_hh_100k_plus = (hh_inc_100k_125kE + hh_inc_125k_150kE + hh_inc_150k_200kE + hh_inc_200k_plusE) / hh_inc_totalE
  ) %>%
  select(
    geo_level, geo_id, geo_name, year,
    median_hh_income, per_capita_income,
    pov_universe, pov_below, pov_rate, gini_index,
    pct_hh_lt25k, pct_hh_25k_50k, pct_hh_50k_100k, pct_hh_100k_plus
  )

# 6. Materialize to Silver DB ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="income_base"),
                  all_acs_clean, overwrite = TRUE)

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="income_kpi"),
                  income_silver_kpi, overwrite = TRUE)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)