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
us_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_us")
region_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_region")
division_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_division")
state_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_state")
county_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_county")
place_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_place")
zcta_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_zcta")

# Tracts
tract_all_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_tract")

# tract_fl_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_tract_fl")
# tract_ga_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_tract_ga")
# tract_nc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_tract_nc")
# tract_sc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_migration_tract_sc")

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
## All are Totals
### Join CBSA Xwalk to Counties ----
cbsa_base <- county_acs_clean %>%
  inner_join(cbsa_county_xwalk %>% select(cbsa_code, cbsa_name, county_geoid),
             by = c("geo_id" = "county_geoid"))

### Create Rebased Files ----
cbsa_mig <- sum_pops_by_cbsa(
  df = cbsa_base,
  pop_pattern = "mig_"
)

cbsa_pop <- sum_pops_by_cbsa(
  df = cbsa_base,
  pop_pattern = "pop_"
)

### Final CBSA File ----
#### Join staging files and reorder
cbsa_acs_clean <- cbsa_mig %>%
  left_join(cbsa_pop, by = c("cbsa_code", "cbsa_name", "year")) %>%
  mutate(geo_level = "cbsa") %>%
  select(geo_level, geo_id = cbsa_code, geo_name = cbsa_name, year,
         mig_totalE:pop_foreign_born_citizenE)

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
migration_silver_kpi <- all_acs_clean %>%
  mutate(
    # Migration
    mig_total          = mig_totalE,
    mig_same_house     = mig_same_houseE,
    mig_moved_same_cnty= mig_moved_same_cntyE,
    mig_moved_same_st  = mig_moved_same_stE,
    mig_moved_diff_st  = mig_moved_diff_stE,
    mig_moved_abroad   = mig_moved_abroadE,
    
    # Nativity
    pop_nativity_total = pop_nativity_totalE,
    pop_native = pop_nativeE,
    pop_foreign_born = pop_foreign_bornE,
    pop_foreign_born_citizen = pop_foreign_born_citizenE,
    pop_foreign_born_noncitizen = pop_foreign_born - pop_foreign_born_citizen
    
  ) %>%
  mutate(
    # Migration
    pct_same_house      = mig_same_house / mig_total,
    pct_moved_same_cnty = mig_moved_same_cnty / mig_total,
    pct_moved_same_st   = mig_moved_same_st / mig_total,
    pct_moved_diff_st   = mig_moved_diff_st / mig_total,
    pct_moved_abroad    = mig_moved_abroad / mig_total,
    
    # Nativity
    pct_native = pop_native / pop_nativity_total,
    pct_foreign_born = pop_foreign_born / pop_nativity_total,
    pct_non_citizen = pop_foreign_born_noncitizen / pop_nativity_total
  ) %>%
  select(
    geo_level, geo_id, geo_name, year,
    mig_total,
    mig_same_house, mig_moved_same_cnty,
    mig_moved_same_st, mig_moved_diff_st, mig_moved_abroad,
    pct_same_house, pct_moved_same_cnty,
    pct_moved_same_st, pct_moved_diff_st, pct_moved_abroad,
    pop_nativity_total, pop_native, pop_foreign_born, 
    pop_foreign_born_citizen, pop_foreign_born_noncitizen, 
    pct_native, pct_foreign_born, pct_non_citizen
  )

# 6. Materialize to Silver DB ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="migration_base"),
                  all_acs_clean, overwrite = TRUE)

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="migration_kpi"),
                  migration_silver_kpi, overwrite = TRUE)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)