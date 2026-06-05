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
us_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_us")
region_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_region")
division_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_division")
state_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_state")
county_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_county")
place_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_place")
zcta_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_zcta")

## Tracts
tract_all_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_tract")

# tract_fl_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_tract_fl")
# tract_ga_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_tract_ga")
# tract_nc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_tract_nc")
# tract_sc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_housing_tract_sc")

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
### Join CBSA Xwalk to Counties ----
cbsa_base <- county_acs_clean %>%
  inner_join(cbsa_county_xwalk %>% select(cbsa_code, cbsa_name, county_geoid),
             by = c("geo_id" = "county_geoid"))

### Create Rebased Files ----
cbsa_rent <- sum_pops_by_cbsa(
  df = cbsa_base,
  pop_pattern = "rent_"
)

cbsa_struct <- sum_pops_by_cbsa(
  df = cbsa_base,
  pop_pattern = "struct_"
)

cbsa_housing <- cbsa_base %>%
  group_by(cbsa_code, cbsa_name, year) %>%
  summarise(
    hu_totalE = sum(hu_totalE, na.rm = TRUE),
    occ_totalE = sum(occ_totalE, na.rm = TRUE), 
    occ_occupiedE = sum(occ_occupiedE, na.rm = TRUE), 
    occ_vacantE = sum(occ_vacantE, na.rm = TRUE),
    tenure_totalE = sum(tenure_totalE, na.rm = TRUE),
    owner_occupiedE = sum(owner_occupiedE, na.rm = TRUE),
    renter_occupiedE = sum(renter_occupiedE, na.rm = TRUE),
    .groups = "drop"
  )

cbsa_medians <- weighted_by_cbsa_pattern(
  df = cbsa_base,
  value_pattern = "median_",
  weight_col = "hu_totalE"
)

### Final CBSA File ----
#### Join staging files and reorder
cbsa_acs_clean <- cbsa_rent %>%
  left_join(cbsa_struct, by = c("cbsa_code", "cbsa_name", "year")) %>%
  left_join(cbsa_housing, by = c("cbsa_code", "cbsa_name", "year")) %>%
  left_join(cbsa_medians, by = c("cbsa_code", "cbsa_name", "year")) %>%
  mutate(geo_level = "cbsa") %>%
  select(geo_level, geo_id = cbsa_code, geo_name = cbsa_name, year,
         hu_totalE:renter_occupiedE, median_gross_rentE:median_home_valueE,
         rent_burden_totalE:rent_not_computedE, 
         median_owner_costs_totalE:median_owner_costs_no_mortgageE,
         struct_totalE:struct_otherE)

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
housing_silver_kpi <- all_acs_clean %>%
  mutate(
    # base units
    hu_total        = hu_totalE,
    occ_total       = occ_totalE,
    occ_occupied    = occ_occupiedE,
    occ_vacant      = occ_vacantE,
    
    # tenure
    tenure_total    = tenure_totalE,
    owner_occupied  = owner_occupiedE,
    renter_occupied = renter_occupiedE,
    
    # costs
    median_gross_rent          = median_gross_rentE,
    median_home_value          = median_home_valueE,
    median_owner_costs_mortgage    = median_owner_costs_mortgageE,
    median_owner_costs_no_mortgage = median_owner_costs_no_mortgageE,
    
    # rent burden universe
    rent_burden_total = rent_burden_totalE,
    rent_not_computed = rent_not_computedE
  ) %>%
  mutate(
    vacancy_rate   = occ_vacant / hu_total,
    occupancy_rate = occ_occupied / hu_total,
    owner_occ_rate = owner_occupied / tenure_total,
    renter_occ_rate= renter_occupied / tenure_total
  ) %>%
  mutate(
    rent_denom = pmax(rent_burden_total - rent_not_computed, 0),
    rent_burden_30plus =
      (rent_30_34E + rent_35_39E + rent_40_49E + rent_50_plusE),
    rent_burden_50plus =
      (rent_50_plusE)
  ) %>%
  mutate(
    pct_rent_burden_30plus = dplyr::if_else(rent_denom > 0,
                                            rent_burden_30plus / rent_denom, NA_real_),
    pct_rent_burden_50plus = dplyr::if_else(rent_denom > 0,
                                            rent_burden_50plus / rent_denom, NA_real_)
  ) %>%
  mutate(
    struct_total     = struct_totalE,
    struct_1_unit    = struct_1_detE + struct_1_attE,
    struct_sf_det    = struct_1_detE,
    struct_small_mf  = struct_2_unitsE + struct_3_4_unitsE,
    struct_mid_mf    = struct_5_9_unitsE + struct_10_19E,
    struct_large_mf  = struct_20_49E + struct_50_plusE,
    struct_mobile    = struct_mobileE
  ) %>%
  mutate(
    pct_struct_1_unit   = struct_1_unit / struct_total,
    pct_struct_sf_det   = struct_sf_det / struct_total,
    pct_struct_small_mf = struct_small_mf / struct_total,
    pct_struct_mid_mf   = struct_mid_mf / struct_total,
    pct_struct_large_mf = struct_large_mf / struct_total,
    pct_struct_mobile   = struct_mobile / struct_total
  ) %>%
  select(
    geo_level, geo_id, geo_name, year,
    hu_total, occ_total, occ_occupied, occ_vacant,
    vacancy_rate, occupancy_rate,
    tenure_total, owner_occupied, renter_occupied,
    owner_occ_rate, renter_occ_rate,
    median_gross_rent, median_home_value,
    median_owner_costs_mortgage, median_owner_costs_no_mortgage,
    rent_burden_total, rent_burden_30plus, rent_burden_50plus,
    pct_rent_burden_30plus, pct_rent_burden_50plus,
    struct_total,
    struct_1_unit, struct_sf_det,
    struct_small_mf, struct_mid_mf, struct_large_mf, struct_mobile,
    pct_struct_1_unit, pct_struct_sf_det,
    pct_struct_small_mf, pct_struct_mid_mf, pct_struct_large_mf,
    pct_struct_mobile
  )

# 6. Materialize to Silver DB ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="housing_base"),
                  all_acs_clean, overwrite = TRUE)

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="housing_kpi"),
                  housing_silver_kpi, overwrite = TRUE)

# Shutdown ----
dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)