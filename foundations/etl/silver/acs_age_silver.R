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
us_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_us")
region_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_region")
division_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_division")
state_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_state")
county_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_county")
place_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_place")
zcta_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_zcta")

## Commenting out old Tract Data
# tract_fl_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_tract_fl")
# tract_ga_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_tract_ga")
# tract_nc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_tract_nc")
# tract_sc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_tract_sc")

## Tracts
tract_all_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_age_tract")

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
# tract_nc_clean    <- standardize_acs_df(tract_nc_acs_stage, "tract")
# tract_fl_clean    <- standardize_acs_df(tract_fl_acs_stage, "tract")
# tract_ga_clean    <- standardize_acs_df(tract_ga_acs_stage, "tract")
# tract_sc_clean    <- standardize_acs_df(tract_sc_acs_stage, "tract")

## Tracts
tract_all_clean    <- standardize_acs_df(tract_all_acs_stage, "tract")

# 4. Union our Data Frames together ----
## Rebase County Data to CBSA  ----
### Join CBSA Xwalk to Counties ----
cbsa_base <- county_acs_clean %>%
  inner_join(cbsa_county_xwalk %>% select(cbsa_code, cbsa_name, county_geoid),
             by = c("geo_id" = "county_geoid"))

### Create Rebased Files ----
cbsa_pop <- cbsa_base %>%
  group_by(cbsa_code, cbsa_name, year) %>%
  summarise(
    across(
      starts_with("pop"),              # all columns with "pop" in the name
      ~ sum(.x, na.rm = TRUE)
    ),
    .groups = "drop"
  )

cbsa_med_age <- cbsa_base %>%
  group_by(cbsa_code, cbsa_name, year) %>%
  summarise(
    median_age.E = stats::weighted.mean(median_age.E, pop_totalE, na.rm = TRUE),
    .groups = "drop"
  )

### Join to make Final DF
cbsa_acs_clean <- cbsa_pop %>%
  left_join(cbsa_med_age, by = c("cbsa_code", "cbsa_name", "year")) %>%
  mutate(geo_level = "cbsa") %>%
  select(geo_level, geo_id = cbsa_code, geo_name = cbsa_name, year,
         pop_totalE, median_age.E, pop_male_totalE:pop_age_female_85_plusE)

## Union Tracts together (Deprecated )----
  
# tract_all_clean <- dplyr::bind_rows(
#   tract_nc_clean,
#   tract_fl_clean,
#   tract_ga_clean,
#   tract_sc_clean,
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
age_silver_kpi <- all_acs_clean %>%
  mutate(
    # total population
    pop_total = pop_totalE,
    
    # 0–4
    age_0_4  = pop_age_male_under5E +
      pop_age_female_under5E,
    
    # 5–14  (5–9 + 10–14)
    age_5_14 = (pop_age_male_5_9E + pop_age_male_10_14E) +
      (pop_age_female_5_9E + pop_age_female_10_14E),
    
    # 15–17  (15–17 + 18–19 + 20 + 21 + 22–24)
    age_15_17 = (pop_age_male_15_17E) +
      (pop_age_female_15_17E),
    
    # 18-24
    age_18_24 = (pop_age_male_18_19E + pop_age_male_20E + 
                   pop_age_male_21E + pop_age_male_22_24E) + 
      (pop_age_female_18_19E + pop_age_female_20E + 
         pop_age_female_21E + pop_age_female_22_24E),
    
    # 25–34
    age_25_34 = (pop_age_male_25_29E + pop_age_male_30_34E) +
      (pop_age_female_25_29E + pop_age_female_30_34E),
    
    # 35–44
    age_35_44 = (pop_age_male_35_39E + pop_age_male_40_44E) +
      (pop_age_female_35_39E + pop_age_female_40_44E),
    
    # 45–54
    age_45_54 = (pop_age_male_45_49E + pop_age_male_50_54E) +
      (pop_age_female_45_49E + pop_age_female_50_54E),
    
    # 55–64
    age_55_64 = (pop_age_male_55_59E + pop_age_male_60_61E + pop_age_male_62_64E) +
      (pop_age_female_55_59E + pop_age_female_60_61E + pop_age_female_62_64E),
    
    # 65–74
    age_65_74 = (pop_age_male_65_66E + pop_age_male_67_69E + pop_age_male_70_74E) +
      (pop_age_female_65_66E + pop_age_female_67_69E + pop_age_female_70_74E),
    
    # 75–84
    age_75_84 = (pop_age_male_75_79E + pop_age_male_80_84E) +
      (pop_age_female_75_79E + pop_age_female_80_84E),
    
    # 85+
    age_85p  = pop_age_male_85_plusE + pop_age_female_85_plusE,
    
    # workforce-ish band
    age_25_54 = (pop_age_male_25_29E + pop_age_male_30_34E + pop_age_male_35_39E +
                   pop_age_male_40_44E + pop_age_male_45_49E + pop_age_male_50_54E) +
      (pop_age_female_25_29E + pop_age_female_30_34E + pop_age_female_35_39E +
         pop_age_female_40_44E + pop_age_female_45_49E + pop_age_female_50_54E)
  ) %>%
  mutate(
    pct_age_0_4   = age_0_4   / pop_total,
    pct_age_5_14  = age_5_14  / pop_total,
    pct_age_15_17 = age_15_17 / pop_total,
    pct_age_18_24 = age_18_24 / pop_total,
    pct_age_25_34 = age_25_34 / pop_total,
    pct_age_35_44 = age_35_44 / pop_total,
    pct_age_45_54 = age_45_54 / pop_total,
    pct_age_55_64 = age_55_64 / pop_total,
    pct_age_65_74 = age_65_74 / pop_total,
    pct_age_75_84 = age_75_84 / pop_total,
    pct_age_85p   = age_85p   / pop_total,
    pct_age_25_54 = age_25_54 / pop_total
  ) %>%
  select(
    geo_level, geo_id, geo_name, year,
    pop_total, median_age = median_age.E,
    age_0_4, age_5_14, age_15_17, age_18_24, age_25_34, age_35_44, age_45_54,
    age_55_64, age_65_74, age_75_84, age_85p, age_25_54,
    pct_age_0_4, pct_age_5_14, pct_age_15_17, pct_age_18_24, pct_age_25_34, pct_age_35_44,
    pct_age_45_54, pct_age_55_64, pct_age_65_74, pct_age_75_84, pct_age_85p,
    pct_age_25_54
  ) %>%
  mutate(
    aging_index = (age_65_74 + age_75_84 + age_85p) / na_if(age_0_4, 0),
    youth_dependency = (age_0_4 + age_5_14) / na_if(age_25_54, 0),
    old_age_dependency = (age_65_74 + age_75_84 + age_85p) / na_if(age_25_54, 0)
  )

# Add Median Age

# 6. Materialize to Silver DB ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="age_base"),
                  all_acs_clean, overwrite = TRUE)

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="age_kpi"),
                  age_silver_kpi, overwrite = TRUE)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)