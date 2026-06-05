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
us_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_us")
region_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_region")
division_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_division")
state_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_state")
county_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_county")
place_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_place")
zcta_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_zcta")

# Tract
tract_all_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_tract")

# tract_fl_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_tract_fl")
# tract_ga_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_tract_ga")
# tract_nc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_tract_nc")
# tract_sc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_transport_tract_sc")

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
cbsa_commute <- sum_pops_by_cbsa(
  df = cbsa_base,
  pop_pattern = "commute_"
)

cbsa_veh <- sum_pops_by_cbsa(
  df = cbsa_base,
  pop_pattern = "veh_"
)

cbsa_weighted_avg <- cbsa_base %>%
  dplyr::group_by(cbsa_code, cbsa_name, year) %>%
  dplyr::summarise(
    total_travel_timeE = sum(total_travel_timeE, na.rm = TRUE),
    .groups = "drop"
  )

### Final CBSA File ----
# Commute and Vehicle are Totals, Mean Travel Time is Weighted
#### Join staging files and reorder
cbsa_acs_clean <- cbsa_commute %>%
  left_join(cbsa_veh, by = c("cbsa_code", "cbsa_name", "year")) %>%
  left_join(cbsa_weighted_avg, by = c("cbsa_code", "cbsa_name", "year")) %>%
  mutate(geo_level = "cbsa") %>%
  select(geo_level, geo_id = cbsa_code, geo_name = cbsa_name, year,
         commute_workers_totalE:commute_worked_homeE, 
         veh_total_hhE:veh_4_plusE, total_travel_timeE)

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
transport_silver_kpi <- all_acs_clean %>%
  # base columns
  mutate(
    # commute
    commute_workers_total = commute_workers_totalE,
    commute_car_truck_van = commute_car_truck_vanE,
    commute_drove_alone   = commute_drove_aloneE,
    commute_carpool       = commute_carpoolE,
    commute_public_trans  = commute_public_transE,
    commute_taxicab       = commute_taxicabE,
    commute_motorcycle    = commute_motorcycleE,
    commute_bicycle       = commute_bicycleE,
    commute_walked        = commute_walkedE,
    commute_other         = commute_otherE,
    commute_worked_home   = commute_worked_homeE,
    
    # vehicles
    veh_total_hh = veh_total_hhE,
    veh_0        = veh_0E,
    veh_1        = veh_1E,
    veh_2        = veh_2E,
    veh_3        = veh_3E,
    veh_4_plus   = veh_4_plusE,
    
    # travel time
    total_travel_time = total_travel_timeE,
    mean_travel_time = total_travel_timeE / commute_workers_totalE
  ) %>%
  # commute shares
  mutate(
    pct_commute_drive_alone = commute_drove_alone   / commute_workers_total,
    pct_commute_carpool     = commute_carpool       / commute_workers_total,
    pct_commute_transit     = commute_public_trans  / commute_workers_total,
    pct_commute_walk        = commute_walked        / commute_workers_total,
    pct_commute_wfh         = commute_worked_home   / commute_workers_total
  ) %>%
  # vehicle shares
  mutate(
    pct_hh_0_vehicles  = veh_0      / veh_total_hh,
    pct_hh_1_vehicles  = veh_1      / veh_total_hh,
    pct_hh_2_vehicles  = veh_2      / veh_total_hh,
    pct_hh_3_vehicles  = veh_3      / veh_total_hh,
    pct_hh_4p_vehicles = veh_4_plus / veh_total_hh
  ) %>%
  select(
    geo_level, geo_id, geo_name, year,
    
    # commute
    commute_workers_total,
    commute_drove_alone, commute_carpool,
    commute_public_trans, commute_taxicab, 
    commute_motorcycle, commute_bicycle, commute_walked,
    commute_other, commute_worked_home,
    pct_commute_drive_alone, pct_commute_carpool,
    pct_commute_transit, pct_commute_walk, pct_commute_wfh,
    
    # vehicles
    veh_total_hh, veh_0, veh_1, veh_2, veh_3, veh_4_plus,
    pct_hh_0_vehicles, pct_hh_1_vehicles,
    pct_hh_2_vehicles, pct_hh_3_vehicles, pct_hh_4p_vehicles,
    
    # travel time
    total_travel_time,
    mean_travel_time
  )

# 6. Materialize to Silver DB ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="transport_base"),
                  all_acs_clean, overwrite = TRUE)

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="transport_kpi"),
                  transport_silver_kpi, overwrite = TRUE)

dbDisconnect(con)