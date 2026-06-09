# In this script we model ACS broadband data to Silver
#
# The staging family lands one wide ACS table per geography slice. This Silver
# step standardizes those slices, rebases county totals to CBSA, and then
# derives a compact KPI table focused on household internet access and
# broadband subscription coverage.

# 1. Set up our Environment ----
getwd()

here::i_am("foundations/etl/silver/acs_broadband_silver.R")
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

bronze_acs <- get_env_path("DATA_DEMO_RAW")
db_path <- get_env_path("DB_PATH")

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# 2. Read staging ACS broadband slices ----
us_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_broadband_us")
region_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_broadband_region")
division_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_broadband_division")
state_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_broadband_state")
county_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_broadband_county")
place_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_broadband_place")
zcta_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_broadband_zcta")
tract_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_broadband_tract")

cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")

# 3. Standardize geography fields and remove MOE columns ----
us_acs_clean <- standardize_acs_df(us_acs_stage, "US", drop_e = FALSE)
region_acs_clean <- standardize_acs_df(region_acs_stage, "Region")
division_acs_clean <- standardize_acs_df(division_acs_stage, "division")
state_acs_clean <- standardize_acs_df(state_acs_stage, "state")
county_acs_clean <- standardize_acs_df(county_acs_stage, "county")
place_acs_clean <- standardize_acs_df(place_acs_stage, "place")
zcta_acs_clean <- standardize_acs_df(zcta_acs_stage, "zcta")
tract_acs_clean <- standardize_acs_df(tract_acs_stage, "tract")

# 4. Rebase county counts to CBSA ----
# Broadband staging columns are all household counts, so the CBSA rollup is a
# straight sum across member counties.
cbsa_acs_clean <- county_acs_clean %>%
  inner_join(
    cbsa_county_xwalk %>% dplyr::select(cbsa_code, cbsa_name, county_geoid),
    by = c("geo_id" = "county_geoid")
  ) %>%
  sum_pops_by_cbsa(pop_pattern = "internet_") %>%
  mutate(geo_level = "cbsa") %>%
  select(
    geo_level,
    geo_id = cbsa_code,
    geo_name = cbsa_name,
    year,
    internet_total_hhE:internet_no_accessE
  )

# 5. Build the base and KPI tables ----
broadband_base <- dplyr::bind_rows(
  us_acs_clean,
  region_acs_clean,
  division_acs_clean,
  state_acs_clean,
  cbsa_acs_clean,
  county_acs_clean,
  place_acs_clean,
  zcta_acs_clean,
  tract_acs_clean
) %>%
  select(-any_of("state"))

broadband_kpi <- broadband_base %>%
  mutate(
    internet_total_hh = internet_total_hhE,
    internet_with_subscription = internet_with_subscriptionE,
    internet_broadband_subscription = internet_broadband_anyE,
    internet_cellular_only = internet_cellular_data_onlyE,
    internet_access_no_subscription = internet_access_no_subscriptionE,
    internet_no_access = internet_no_accessE,
    internet_with_any_access = internet_total_hhE - internet_no_accessE
  ) %>%
  mutate(
    pct_internet_subscription = internet_with_subscription / dplyr::na_if(internet_total_hh, 0),
    pct_broadband_subscription = internet_broadband_subscription / dplyr::na_if(internet_total_hh, 0),
    pct_cellular_only = internet_cellular_only / dplyr::na_if(internet_total_hh, 0),
    pct_access_no_subscription = internet_access_no_subscription / dplyr::na_if(internet_total_hh, 0),
    pct_no_internet_access = internet_no_access / dplyr::na_if(internet_total_hh, 0),
    pct_any_internet_access = internet_with_any_access / dplyr::na_if(internet_total_hh, 0)
  ) %>%
  select(
    geo_level, geo_id, geo_name, year,
    internet_total_hh,
    internet_with_subscription,
    internet_broadband_subscription,
    internet_cellular_only,
    internet_access_no_subscription,
    internet_no_access,
    internet_with_any_access,
    pct_internet_subscription,
    pct_broadband_subscription,
    pct_cellular_only,
    pct_access_no_subscription,
    pct_no_internet_access,
    pct_any_internet_access
  )

# 6. Materialize to Silver ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "broadband_base"),
  broadband_base,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "broadband_kpi"),
  broadband_kpi,
  overwrite = TRUE
)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
