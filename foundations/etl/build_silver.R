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
  stop("DB_PATH must be set before running build_silver.R.", call. = FALSE)
}

silver_scripts <- c(
  "geo_crosswalks_silver.R",
  "acs_metadata_silver.R",
  "acs_variable_dictionary_silver.R",
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
  "bea_metric_dictionary.R",
  "bls_laus_silver.R",
  "bps_silver.R",
  "build_social_infra_dictionary.R",
  "hud_fmr_silver.R",
  "irs_migration_silver.R"
)

setup_con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
dbExecute(setup_con, "CREATE SCHEMA IF NOT EXISTS silver;")
dbDisconnect(setup_con)

message("Building silver tables from seeded staging.")
for (script_name in silver_scripts) {
  script_path <- here::here("foundations", "etl", "silver", script_name)
  message(glue("  running {script_name}"))
  source(script_path, local = new.env(parent = globalenv()))
}

message("Silver build complete.")
