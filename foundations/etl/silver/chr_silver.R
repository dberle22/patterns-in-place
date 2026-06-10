# In this script we normalize the curated CHR historical staging panel into the
# approved Silver contract for county and derived CBSA health outcomes.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Helpers ----
safe_weighted_mean <- function(values, weights) {
  valid <- !is.na(values) & !is.na(weights) & weights > 0

  if (!any(valid)) {
    return(NA_real_)
  }

  stats::weighted.mean(values[valid], weights[valid])
}

append_state_abbr <- function(name, state_abbr) {
  dplyr::if_else(
    !is.na(state_abbr) & state_abbr != "" & !stringr::str_detect(name, ","),
    paste0(name, ", ", state_abbr),
    name
  )
}

check_unique_annual_grain <- function(df, table_name) {
  dupes <- df %>%
    count(geo_level, geo_id, year, name = "row_count") %>%
    filter(row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf(
        "%s has duplicate geo_level + geo_id + year rows",
        table_name
      ),
      call. = FALSE
    )
  }
}

measure_columns <- c(
  "life_expectancy",
  "premature_death_rate",
  "premature_age_adjusted_mortality",
  "child_mortality_rate",
  "infant_mortality_rate",
  "drug_overdose_death_rate",
  "poor_mental_health_days",
  "adult_obesity",
  "physical_inactivity",
  "pct_uninsured_adults",
  "primary_care_ratio",
  "mental_health_provider_ratio",
  "preventable_hospital_stay_rate",
  "food_insecurity_rate",
  "social_associations_per_10k",
  "child_care_cost_burden_rate",
  "hs_graduation_rate",
  "air_pollution_pm25",
  "adverse_climate_events",
  "pct_access_to_parks",
  "homicide_rate",
  "firearm_fatality_rate",
  "motor_vehicle_crash_rate",
  "reading_score_index",
  "math_score_index"
)

school_age_columns <- c("reading_score_index", "math_score_index")
population_columns <- setdiff(measure_columns, school_age_columns)

# 3. Read staging and reference data ----
chr_stage <- DBI::dbGetQuery(con, "SELECT * FROM staging.chr_health_rankings_history")
cbsa_county_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county") %>%
  transmute(
    county_geoid = as.character(county_geoid),
    cbsa_code = as.character(cbsa_code),
    cbsa_name = as.character(cbsa_name)
  ) %>%
  distinct()

county_state_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state") %>%
  transmute(
    county_geoid = as.character(county_geoid),
    county_name_long = as.character(county_name_long),
    state_abbr = as.character(state_abbr)
  ) %>%
  distinct()

population_weights <- DBI::dbGetQuery(
  con,
  "
  SELECT
    geo_id AS county_geoid,
    year,
    pop_total,
    age_5_14,
    age_15_17
  FROM silver.age_kpi
  WHERE geo_level = 'county'
  "
) %>%
  transmute(
    county_geoid = as.character(county_geoid),
    weight_year = as.integer(year),
    total_population = as.double(pop_total),
    school_age_population = as.double(age_5_14) + as.double(age_15_17)
  ) %>%
  mutate(
    school_age_population = dplyr::if_else(
      !is.na(school_age_population) & school_age_population > 0,
      school_age_population,
      total_population
    )
  )

# 4. Standardize county rows ----
# The historical staging panel is already curated to county and county-equivalent
# rows only, so Silver can standardize directly from that annual panel.
chr_county <- chr_stage %>%
  mutate(
    state_fips = as.character(state_fips),
    county_fips = as.character(county_fips),
    fips5 = as.character(fips5)
  ) %>%
  left_join(
    county_state_xwalk,
    by = c("fips5" = "county_geoid")
  ) %>%
  transmute(
    geo_level = "county",
    geo_id = fips5,
    geo_name = append_state_abbr(
      dplyr::coalesce(county_name_long, as.character(county_name)),
      dplyr::coalesce(state_abbr.y, state_abbr.x)
    ),
    year = as.integer(release_year),
    life_expectancy = as.double(life_expectancy),
    premature_death_rate = as.double(premature_death_rate),
    premature_age_adjusted_mortality = as.double(premature_age_adjusted_mortality),
    child_mortality_rate = as.double(child_mortality_rate),
    infant_mortality_rate = as.double(infant_mortality_rate),
    drug_overdose_death_rate = as.double(drug_overdose_death_rate),
    poor_mental_health_days = as.double(poor_mental_health_days),
    adult_obesity = as.double(adult_obesity),
    physical_inactivity = as.double(physical_inactivity),
    pct_uninsured_adults = as.double(pct_uninsured_adults),
    primary_care_ratio = as.double(primary_care_ratio),
    mental_health_provider_ratio = as.double(mental_health_provider_ratio),
    preventable_hospital_stay_rate = as.double(preventable_hospital_stay_rate),
    food_insecurity_rate = as.double(food_insecurity_rate),
    social_associations_per_10k = as.double(social_associations_per_10k),
    child_care_cost_burden_rate = as.double(child_care_cost_burden_rate),
    hs_graduation_rate = as.double(hs_graduation_rate),
    air_pollution_pm25 = as.double(air_pollution_pm25),
    adverse_climate_events = as.double(adverse_climate_events),
    pct_access_to_parks = as.double(pct_access_to_parks),
    homicide_rate = as.double(homicide_rate),
    firearm_fatality_rate = as.double(firearm_fatality_rate),
    motor_vehicle_crash_rate = as.double(motor_vehicle_crash_rate),
    reading_score_index = as.double(reading_score_index),
    math_score_index = as.double(math_score_index)
  ) %>%
  filter(dplyr::if_any(dplyr::all_of(measure_columns), ~ !is.na(.x))) %>%
  distinct()

# 5. Rebase county rows to CBSA using ACS population weights ----
# CHR publishes county-level observations only, so CBSA rows are derived here by
# joining counties to the current OMB county->CBSA crosswalk. We use total ACS
# population weights for the general rates and ratios, and school-age population
# for reading and math because those measures represent student outcomes.
chr_cbsa <- chr_county %>%
  mutate(
    weight_year = pmax(2012L, pmin(as.integer(year), 2024L))
  ) %>%
  left_join(
    cbsa_county_xwalk,
    by = c("geo_id" = "county_geoid")
  ) %>%
  filter(!is.na(cbsa_code), cbsa_code != "") %>%
  left_join(
    population_weights,
    by = c("geo_id" = "county_geoid", "weight_year")
  ) %>%
  group_by(cbsa_code, cbsa_name, year) %>%
  summarize(
    across(
      dplyr::all_of(population_columns),
      ~ safe_weighted_mean(.x, total_population)
    ),
    across(
      dplyr::all_of(school_age_columns),
      ~ safe_weighted_mean(.x, school_age_population)
    ),
    .groups = "drop"
  ) %>%
  transmute(
    geo_level = "cbsa",
    geo_id = cbsa_code,
    geo_name = cbsa_name,
    year = as.integer(year),
    dplyr::across(dplyr::all_of(measure_columns))
  )

# 6. Materialize Silver ----
chr_health_outcomes <- bind_rows(
  chr_county,
  chr_cbsa
) %>%
  arrange(geo_level, geo_id, year)

check_unique_annual_grain(chr_health_outcomes, "silver.chr_health_outcomes")

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "chr_health_outcomes"),
  chr_health_outcomes,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
