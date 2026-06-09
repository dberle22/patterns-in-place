library(DBI)
library(duckdb)
library(glue)
library(here)

source(here::here("foundations", "etl", "R", "generic_functions.R"))

user_renv <- path.expand("~/.Renviron")
if (file.exists(user_renv)) {
  readRenviron(user_renv)
}

if (file.exists(".Renviron")) {
  readRenviron(".Renviron")
}

db_path <- get_env_path("DB_PATH")

if (is.na(db_path)) {
  stop("DB_PATH must be set before running create_DB.R.", call. = FALSE)
}

staging_scripts <- c(
  "get_opportunity_zones.R",
  "get_fhfa_underserved.R",
  "get_epa_aqi.R",
  "get_epa_sld.R",
  "get_cbp.R",
  "get_cbp_zip.R",
  "get_usda_food_atlas.R",
  "get_ejscreen.R",
  "get_fema_nri.R"
)

silver_scripts <- c(
  "geo_crosswalks_silver.R",
  "bea_metric_dictionary.R",
  "opportunity_zones_silver.R",
  "fhfa_underserved_silver.R",
  "epa_aqi_silver.R",
  "epa_sld_silver.R",
  "usda_food_atlas_silver.R",
  "ejscreen_silver.R",
  "fema_nri_silver.R",
  "acs_age_silver.R",
  "acs_edu_silver.R",
  "acs_housing_silver.R",
  "acs_income_silver.R",
  "acs_labor_silver.R",
  "acs_migration_silver.R",
  "acs_race_silver.R",
  "acs_social_infra_silver.R",
  "acs_transport_silver.R",
  "bea_cagdp2_silver.R",
  "bea_cagdp9_silver.R",
  "bea_cainc1_silver.R",
  "bea_cainc4_silver.R",
  "bea_marpp_silver.R",
  "bls_laus_silver.R",
  "bps_silver.R",
  "hud_fmr_silver.R",
  "zillow_silver.R",
  "fhfa_hpi_silver.R",
  "chr_silver.R",
  "cbp_silver.R",
  "acs_variable_dictionary_silver.R",
  "acs_metadata_silver.R"
)

gold_scripts <- c(
  "gold_dim_geo.sql",
  "gold_policy_designations.sql",
  "gold_population_wide.sql",
  "gold_economy_income.sql",
  "gold_economy_gdp.sql",
  "gold_economy_industry.sql",
  "gold_economy_labor.sql",
  "gold_housing_core.sql",
  "gold_housing_market_wide.sql",
  "gold_health_wide.sql",
  "gold_environment_wide.sql",
  "gold_affordability_wide.sql",
  "gold_migration_wide.sql",
  "gold_transport_built_form_wide.sql",
  "gold_transport_built_form_sld.sql",
  "gold_food_access_wide.sql"
)

setup_con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
dbExecute(setup_con, "CREATE SCHEMA IF NOT EXISTS staging;")
dbExecute(setup_con, "CREATE SCHEMA IF NOT EXISTS geo;")
dbExecute(setup_con, "CREATE SCHEMA IF NOT EXISTS silver;")
dbExecute(setup_con, "CREATE SCHEMA IF NOT EXISTS gold;")
dbDisconnect(setup_con)

message("Building staged designation tables from source.")
for (script_name in staging_scripts) {
  script_path <- here::here("foundations", "etl", "staging", script_name)
  message(glue("  running {script_name}"))
  source(script_path, local = new.env(parent = globalenv()))
}

message("Building silver tables from seeded staging.")
for (script_name in silver_scripts) {
  script_path <- here::here("foundations", "etl", "silver", script_name)
  message(glue("  running {script_name}"))
  source(script_path, local = new.env(parent = globalenv()))
}

message("Building gold tables.")
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(dbDisconnect(con), add = TRUE)

for (script_name in gold_scripts) {
  script_path <- here::here("foundations", "etl", "gold", script_name)
  message(glue("  running {script_name}"))
  sql <- paste(readLines(script_path, warn = FALSE), collapse = "\n")
  dbExecute(con, sql)
}

message("Build complete.")
