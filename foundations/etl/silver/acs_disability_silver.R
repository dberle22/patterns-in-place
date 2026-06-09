# In this script we model ACS disability data to Silver
#
# The disability staging family carries age-by-sex disability counts across the
# standard ACS geography ladder. This Silver step standardizes those source
# fields, rebases county counts to CBSA, and then derives a smaller KPI table
# with overall, sex-specific, and lifecycle disability metrics.

# 1. Set up our Environment ----
getwd()

here::i_am("foundations/etl/silver/acs_disability_silver.R")
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

bronze_acs <- get_env_path("DATA_DEMO_RAW")
db_path <- get_env_path("DB_PATH")

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# 2. Read staging ACS disability slices ----
us_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_disability_us")
region_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_disability_region")
division_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_disability_division")
state_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_disability_state")
county_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_disability_county")
place_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_disability_place")
zcta_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_disability_zcta")
tract_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_disability_tract")

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
# Disability staging is entirely count-based, so the CBSA rollup is a direct
# sum across county members.
cbsa_acs_clean <- county_acs_clean %>%
  inner_join(
    cbsa_county_xwalk %>% dplyr::select(cbsa_code, cbsa_name, county_geoid),
    by = c("geo_id" = "county_geoid")
  ) %>%
  sum_pops_by_cbsa(pop_pattern = "disability_") %>%
  mutate(geo_level = "cbsa") %>%
  select(
    geo_level,
    geo_id = cbsa_code,
    geo_name = cbsa_name,
    year,
    disability_totalE:disability_female_75_plus_no_disabilityE
  )

# 5. Build the base and KPI tables ----
disability_base <- dplyr::bind_rows(
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

disability_kpi <- disability_base %>%
  mutate(
    disability_total = disability_totalE,
    disability_male_total = disability_male_totalE,
    disability_female_total = disability_female_totalE,
    disability_male_with = disability_male_under_5_with_disabilityE +
      disability_male_5_17_with_disabilityE +
      disability_male_18_34_with_disabilityE +
      disability_male_35_64_with_disabilityE +
      disability_male_65_74_with_disabilityE +
      disability_male_75_plus_with_disabilityE,
    disability_female_with = disability_female_under_5_with_disabilityE +
      disability_female_5_17_with_disabilityE +
      disability_female_18_34_with_disabilityE +
      disability_female_35_64_with_disabilityE +
      disability_female_65_74_with_disabilityE +
      disability_female_75_plus_with_disabilityE,
    disability_under_5_total = disability_male_under_5_totalE + disability_female_under_5_totalE,
    disability_under_5_with = disability_male_under_5_with_disabilityE + disability_female_under_5_with_disabilityE,
    disability_5_17_total = disability_male_5_17_totalE + disability_female_5_17_totalE,
    disability_5_17_with = disability_male_5_17_with_disabilityE + disability_female_5_17_with_disabilityE,
    disability_18_34_total = disability_male_18_34_totalE + disability_female_18_34_totalE,
    disability_18_34_with = disability_male_18_34_with_disabilityE + disability_female_18_34_with_disabilityE,
    disability_35_64_total = disability_male_35_64_totalE + disability_female_35_64_totalE,
    disability_35_64_with = disability_male_35_64_with_disabilityE + disability_female_35_64_with_disabilityE,
    disability_65_74_total = disability_male_65_74_totalE + disability_female_65_74_totalE,
    disability_65_74_with = disability_male_65_74_with_disabilityE + disability_female_65_74_with_disabilityE,
    disability_75_plus_total = disability_male_75_plus_totalE + disability_female_75_plus_totalE,
    disability_75_plus_with = disability_male_75_plus_with_disabilityE + disability_female_75_plus_with_disabilityE
  ) %>%
  mutate(
    disability_with = disability_male_with + disability_female_with,
    disability_without = disability_total - disability_with,
    disability_under_18_total = disability_under_5_total + disability_5_17_total,
    disability_under_18_with = disability_under_5_with + disability_5_17_with,
    disability_18_64_total = disability_18_34_total + disability_35_64_total,
    disability_18_64_with = disability_18_34_with + disability_35_64_with,
    disability_65_plus_total = disability_65_74_total + disability_75_plus_total,
    disability_65_plus_with = disability_65_74_with + disability_75_plus_with
  ) %>%
  mutate(
    pct_disabled = disability_with / dplyr::na_if(disability_total, 0),
    pct_disabled_male = disability_male_with / dplyr::na_if(disability_male_total, 0),
    pct_disabled_female = disability_female_with / dplyr::na_if(disability_female_total, 0),
    pct_disabled_under_5 = disability_under_5_with / dplyr::na_if(disability_under_5_total, 0),
    pct_disabled_5_17 = disability_5_17_with / dplyr::na_if(disability_5_17_total, 0),
    pct_disabled_18_34 = disability_18_34_with / dplyr::na_if(disability_18_34_total, 0),
    pct_disabled_35_64 = disability_35_64_with / dplyr::na_if(disability_35_64_total, 0),
    pct_disabled_65_74 = disability_65_74_with / dplyr::na_if(disability_65_74_total, 0),
    pct_disabled_75_plus = disability_75_plus_with / dplyr::na_if(disability_75_plus_total, 0),
    pct_disabled_under_18 = disability_under_18_with / dplyr::na_if(disability_under_18_total, 0),
    pct_disabled_18_64 = disability_18_64_with / dplyr::na_if(disability_18_64_total, 0),
    pct_disabled_65_plus = disability_65_plus_with / dplyr::na_if(disability_65_plus_total, 0)
  ) %>%
  select(
    geo_level, geo_id, geo_name, year,
    disability_total,
    disability_with,
    disability_without,
    disability_male_total,
    disability_male_with,
    disability_female_total,
    disability_female_with,
    disability_under_5_total,
    disability_under_5_with,
    disability_5_17_total,
    disability_5_17_with,
    disability_18_34_total,
    disability_18_34_with,
    disability_35_64_total,
    disability_35_64_with,
    disability_65_74_total,
    disability_65_74_with,
    disability_75_plus_total,
    disability_75_plus_with,
    disability_under_18_total,
    disability_under_18_with,
    disability_18_64_total,
    disability_18_64_with,
    disability_65_plus_total,
    disability_65_plus_with,
    pct_disabled,
    pct_disabled_male,
    pct_disabled_female,
    pct_disabled_under_5,
    pct_disabled_5_17,
    pct_disabled_18_34,
    pct_disabled_35_64,
    pct_disabled_65_74,
    pct_disabled_75_plus,
    pct_disabled_under_18,
    pct_disabled_18_64,
    pct_disabled_65_plus
  )

# 6. Materialize to Silver ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "disability_base"),
  disability_base,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "disability_kpi"),
  disability_kpi,
  overwrite = TRUE
)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
