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

# Set up Functions ----
sum_pops_by_cbsa <- function(df, pop_pattern = "pop") {
  df %>%
    group_by(cbsa_code, cbsa_name, year) %>%
    summarise(
      across(contains(pop_pattern), ~ sum(.x, na.rm = TRUE)),
      .groups = "drop"
    )
}

weighted_by_cbsa <- function(df, value_col, weight_col) {
  df %>%
    group_by(cbsa_code, cbsa_name, year) %>%
    summarise(
      "{{value_col}}" := stats::weighted.mean(
        .data[[value_col]],
        .data[[weight_col]],
        na.rm = TRUE
      ),
      .groups = "drop"
    )
}

# 2. Read in our Staging Data to R Data Frames ----
us_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_us")
region_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_region")
division_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_division")
state_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_state")
county_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_county")
place_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_place")
zcta_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_zcta")

## Tracts 
# tract_fl_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_tract_fl")
# tract_ga_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_tract_ga")
# tract_nc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_tract_nc")
# tract_sc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_tract_sc")

tract_all_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_edu_tract")

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

tract_all_clean   <- standardize_acs_df(tract_all_acs_stage, "tract")
# tract_nc_clean    <- standardize_acs_df(tract_nc_acs_stage, "tract")
# tract_fl_clean    <- standardize_acs_df(tract_fl_acs_stage, "tract")
# tract_ga_clean    <- standardize_acs_df(tract_ga_acs_stage, "tract")
# tract_sc_clean    <- standardize_acs_df(tract_sc_acs_stage, "tract")

# 4. Union our Data Frames together ----
## Rebase County Data to CBSA  ----
### Join CBSA Xwalk to Counties ----
cbsa_base <- county_acs_clean %>%
  inner_join(cbsa_county_xwalk %>% select(cbsa_code, cbsa_name, county_geoid),
             by = c("geo_id" = "county_geoid"))

### Create Rebased Files ----
cbsa_pop <- sum_pops_by_cbsa(
  df = cbsa_base,
  pop_pattern = "edu"
)

### Final CBSA File ----
cbsa_acs_clean <- cbsa_pop %>%
  mutate(geo_level = "cbsa") %>%
  select(geo_level, geo_id = cbsa_code, geo_name = cbsa_name, year,
         edu_total_25pE:edu_doctorateE)
 
## Union Tracts together ----
# tract_all_clean <- dplyr::bind_rows(
#   tract_nc_clean,
#   tract_fl_clean,
#   tract_ga_clean,
#   tract_sc_clean
# )

## Union all DFs together ----
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
edu_silver_kpi <- all_acs_clean %>%
  mutate(
    edu_total_25p = edu_total_25pE,
    lt_hs_25p = edu_no_schoolingE + edu_nurseryE + edu_kindergartenE + edu_grade1E +
      edu_grade2E + edu_grade3E + edu_grade4E + edu_grade5E +
      edu_grade6E + edu_grade7E + edu_grade8E + edu_grade9E +
      edu_grade10E + edu_grade11E + edu_grade12_no_diplomaE,
    hs_ged_25p = edu_hs_diplomaE + edu_ged_alt_credentialE,
    somecol_assoc_25p = edu_some_college_lt1yrE + edu_some_college_ge1yrE + edu_associatesE,
    ba_25p = edu_bachelorsE ,
    ma_plus_25p = + edu_mastersE + edu_professionalE + edu_doctorateE
  ) %>%
  mutate(
    pct_lt_hs_25p         = lt_hs_25p         / edu_total_25p,
    pct_hs_ged_25p        = hs_ged_25p        / edu_total_25p,
    pct_somecol_assoc_25p = somecol_assoc_25p / edu_total_25p,
    pct_ba_25p            = ba_25p            / edu_total_25p,
    pct_ma_plus_25p       = ma_plus_25p       / edu_total_25p
  ) %>%
  select(
    geo_level, geo_id, geo_name, year,
    edu_total_25p,
    lt_hs_25p, hs_ged_25p, somecol_assoc_25p, ba_25p, ma_plus_25p,
    pct_lt_hs_25p, pct_hs_ged_25p, pct_somecol_assoc_25p, pct_ba_25p, 
    pct_ma_plus_25p
  )

# 6. Materialize to Silver DB ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="education_base"),
                  all_acs_clean, overwrite = TRUE)

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="education_kpi"),
                  edu_silver_kpi, overwrite = TRUE)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)