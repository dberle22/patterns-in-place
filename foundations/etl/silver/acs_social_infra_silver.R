# In this script we model ACS Social Infrastructure data to Silver.
#
# By default this script builds and validates the data frames without writing
# to DuckDB. Set WRITE_TO_DUCKDB=true to materialize the Silver tables.

# 1. Set up our Environment ----
getwd()

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

bronze_acs <- get_env_path("DATA_DEMO_RAW")
db_path <- get_env_path("DB_PATH")

load_social_infra_staging <- function(con) {
  tract_combined_exists <- dbGetQuery(
    con,
    "
    SELECT COUNT(*) AS n
    FROM information_schema.tables
    WHERE table_schema = 'staging'
      AND table_name = 'acs_social_infra_tract'
    "
  )$n[[1]] > 0

  stages <- list(
    us = dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_us"),
    region = dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_region"),
    division = dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_division"),
    state = dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_state"),
    county = dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_county"),
    place = dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_place"),
    zcta = dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_zcta"),
    tract_fl = dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_tract_fl"),
    tract_ga = dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_tract_ga"),
    tract_nc = dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_tract_nc"),
    tract_sc = dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_tract_sc")
  )

  if (tract_combined_exists) {
    stages$tract <- dbGetQuery(con, "SELECT * FROM staging.acs_social_infra_tract")
  }

  stages
}

build_social_infra_silver <- function(materialize = FALSE) {
  con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
  on.exit({
    try(dbExecute(con, "CHECKPOINT"), silent = TRUE)
    try(dbDisconnect(con, shutdown = TRUE), silent = TRUE)
  }, add = TRUE)

  stages <- load_social_infra_staging(con)
  cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")

  us_acs_clean <- standardize_acs_df(stages$us, "US", drop_e = FALSE)
  region_acs_clean <- standardize_acs_df(stages$region, "Region")
  division_acs_clean <- standardize_acs_df(stages$division, "division")
  state_acs_clean <- standardize_acs_df(stages$state, "state")
  county_acs_clean <- standardize_acs_df(stages$county, "county")
  place_acs_clean <- standardize_acs_df(stages$place, "place")
  zcta_acs_clean <- standardize_acs_df(stages$zcta, "zcta")

  if ("tract" %in% names(stages)) {
    tract_all_clean <- standardize_acs_df(stages$tract, "tract")
  } else {
    tract_all_clean <- dplyr::bind_rows(
      standardize_acs_df(stages$tract_nc, "tract"),
      standardize_acs_df(stages$tract_fl, "tract"),
      standardize_acs_df(stages$tract_ga, "tract"),
      standardize_acs_df(stages$tract_sc, "tract")
    )
  }

  cbsa_base <- county_acs_clean %>%
    inner_join(
      cbsa_county_xwalk %>% select(cbsa_code, cbsa_name, county_geoid),
      by = c("geo_id" = "county_geoid")
    )

  cbsa_households <- sum_pops_by_cbsa(
    df = cbsa_base,
    pop_pattern = "hh_"
  )

  cbsa_insurance <- sum_pops_by_cbsa(
    df = cbsa_base,
    pop_pattern = "ins_"
  )

  cbsa_acs_clean <- cbsa_households %>%
    left_join(cbsa_insurance, by = c("cbsa_code", "cbsa_name", "year")) %>%
    mutate(geo_level = "cbsa") %>%
    select(
      geo_level,
      geo_id = cbsa_code,
      geo_name = cbsa_name,
      year,
      hh_totalE:hh_nonfam_not_aloneE,
      ins_totalE:ins_65u_uncoveredE
    )

  social_infra_base <- dplyr::bind_rows(
    us_acs_clean,
    region_acs_clean,
    division_acs_clean,
    state_acs_clean,
    cbsa_acs_clean,
    county_acs_clean,
    place_acs_clean,
    zcta_acs_clean,
    tract_all_clean
  ) %>%
    select(-any_of("state"))

  social_infra_kpi <- social_infra_base %>%
    mutate(
      hh_total = hh_totalE,
      hh_family = hh_familyE,
      hh_married = hh_marriedE,
      hh_other_family = hh_other_familyE,
      hh_nonfamily = hh_nonfamilyE,
      hh_nonfam_alone = hh_nonfam_aloneE,
      hh_nonfam_not_alone = hh_nonfam_not_aloneE,
      single_households = hh_nonfam_aloneE,
      ins_total = ins_totalE,
      ins_u19_total = ins_u19_one_planE + ins_u19_two_plansE + ins_u19_uncoveredE,
      ins_19_34_total = ins_19_34_one_planE + ins_19_34_two_plansE + ins_19_34_uncoveredE,
      ins_35_64_total = ins_35_64_one_planE + ins_35_64_two_plansE + ins_35_64_uncoveredE,
      ins_65u_total = ins_65u_one_planE + ins_65u_two_plansE + ins_65u_uncoveredE,
      ins_u19_covered = ins_u19_one_planE + ins_u19_two_plansE,
      ins_19_34_covered = ins_19_34_one_planE + ins_19_34_two_plansE,
      ins_35_64_covered = ins_35_64_one_planE + ins_35_64_two_plansE,
      ins_65u_covered = ins_65u_one_planE + ins_65u_two_plansE,
      ins_uninsured = ins_u19_uncoveredE + ins_19_34_uncoveredE +
        ins_35_64_uncoveredE + ins_65u_uncoveredE,
      ins_insured = ins_totalE - (
        ins_u19_uncoveredE + ins_19_34_uncoveredE +
          ins_35_64_uncoveredE + ins_65u_uncoveredE
      )
    ) %>%
    mutate(
      pct_hh_family = dplyr::if_else(hh_total > 0, hh_family / hh_total, NA_real_),
      pct_hh_married = dplyr::if_else(hh_total > 0, hh_married / hh_total, NA_real_),
      pct_hh_other_family = dplyr::if_else(hh_total > 0, hh_other_family / hh_total, NA_real_),
      pct_hh_nonfamily = dplyr::if_else(hh_total > 0, hh_nonfamily / hh_total, NA_real_),
      pct_single_households = dplyr::if_else(hh_total > 0, single_households / hh_total, NA_real_),
      pct_nonfamily_alone = dplyr::if_else(hh_nonfamily > 0, hh_nonfam_alone / hh_nonfamily, NA_real_),
      pct_nonfamily_not_alone = dplyr::if_else(
        hh_nonfamily > 0,
        hh_nonfam_not_alone / hh_nonfamily,
        NA_real_
      ),
      pct_health_insured = dplyr::if_else(ins_total > 0, ins_insured / ins_total, NA_real_),
      pct_health_uninsured = dplyr::if_else(ins_total > 0, ins_uninsured / ins_total, NA_real_),
      pct_u19_covered = dplyr::if_else(ins_u19_total > 0, ins_u19_covered / ins_u19_total, NA_real_),
      pct_u19_uncovered = dplyr::if_else(ins_u19_total > 0, ins_u19_uncoveredE / ins_u19_total, NA_real_),
      pct_19_34_covered = dplyr::if_else(
        ins_19_34_total > 0,
        ins_19_34_covered / ins_19_34_total,
        NA_real_
      ),
      pct_19_34_uncovered = dplyr::if_else(
        ins_19_34_total > 0,
        ins_19_34_uncoveredE / ins_19_34_total,
        NA_real_
      ),
      pct_35_64_covered = dplyr::if_else(
        ins_35_64_total > 0,
        ins_35_64_covered / ins_35_64_total,
        NA_real_
      ),
      pct_35_64_uncovered = dplyr::if_else(
        ins_35_64_total > 0,
        ins_35_64_uncoveredE / ins_35_64_total,
        NA_real_
      ),
      pct_65u_covered = dplyr::if_else(ins_65u_total > 0, ins_65u_covered / ins_65u_total, NA_real_),
      pct_65u_uncovered = dplyr::if_else(ins_65u_total > 0, ins_65u_uncoveredE / ins_65u_total, NA_real_)
    ) %>%
    select(
      geo_level, geo_id, geo_name, year,
      hh_total, hh_family, hh_married, hh_other_family, hh_nonfamily,
      hh_nonfam_alone, hh_nonfam_not_alone, single_households,
      pct_hh_family, pct_hh_married, pct_hh_other_family, pct_hh_nonfamily,
      pct_single_households, pct_nonfamily_alone, pct_nonfamily_not_alone,
      ins_total, ins_insured, ins_uninsured,
      pct_health_insured, pct_health_uninsured,
      ins_u19_total, ins_u19_covered, ins_u19_uncovered = ins_u19_uncoveredE,
      pct_u19_covered, pct_u19_uncovered,
      ins_19_34_total, ins_19_34_covered, ins_19_34_uncovered = ins_19_34_uncoveredE,
      pct_19_34_covered, pct_19_34_uncovered,
      ins_35_64_total, ins_35_64_covered, ins_35_64_uncovered = ins_35_64_uncoveredE,
      pct_35_64_covered, pct_35_64_uncovered,
      ins_65u_total, ins_65u_covered, ins_65u_uncovered = ins_65u_uncoveredE,
      pct_65u_covered, pct_65u_uncovered
    )

  validation <- list(
    base_rows = nrow(social_infra_base),
    kpi_rows = nrow(social_infra_kpi),
    base_geo_levels = sort(unique(social_infra_base$geo_level)),
    kpi_geo_levels = sort(unique(social_infra_kpi$geo_level)),
    year_range = c(min(social_infra_base$year, na.rm = TRUE), max(social_infra_base$year, na.rm = TRUE)),
    base_duplicates = social_infra_base %>%
      count(geo_level, geo_id, year) %>%
      filter(n > 1) %>%
      nrow(),
    kpi_duplicates = social_infra_kpi %>%
      count(geo_level, geo_id, year) %>%
      filter(n > 1) %>%
      nrow(),
    household_component_mismatches = social_infra_kpi %>%
      filter(abs(hh_total - (hh_family + hh_nonfamily)) > 1e-6) %>%
      nrow(),
    insurance_component_mismatches = social_infra_kpi %>%
      filter(abs(ins_total - (ins_u19_total + ins_19_34_total + ins_35_64_total + ins_65u_total)) > 1e-6) %>%
      nrow(),
    negative_insured_rows = social_infra_kpi %>%
      filter(ins_insured < 0) %>%
      nrow()
  )

  if (isTRUE(materialize)) {
    DBI::dbWriteTable(
      con,
      DBI::Id(schema = "silver", table = "social_infra_base"),
      social_infra_base,
      overwrite = TRUE
    )

    DBI::dbWriteTable(
      con,
      DBI::Id(schema = "silver", table = "social_infra_kpi"),
      social_infra_kpi,
      overwrite = TRUE
    )
  }

  list(
    social_infra_base = social_infra_base,
    social_infra_kpi = social_infra_kpi,
    validation = validation
  )
}

write_to_duckdb <- tolower(Sys.getenv("WRITE_TO_DUCKDB", "true")) %in% c("true", "1", "yes")
result <- build_social_infra_silver(materialize = write_to_duckdb)

message("Built social infrastructure Silver data frames.")
message("DuckDB materialization: ", write_to_duckdb)
message("Base rows: ", format(result$validation$base_rows, big.mark = ","))
message("KPI rows: ", format(result$validation$kpi_rows, big.mark = ","))
message(
  "Year range: ",
  result$validation$year_range[[1]],
  "-",
  result$validation$year_range[[2]]
)
message(
  "Geo levels: ",
  paste(result$validation$base_geo_levels, collapse = ", ")
)
message("Base duplicate key groups: ", result$validation$base_duplicates)
message("KPI duplicate key groups: ", result$validation$kpi_duplicates)
message("Household component mismatches: ", result$validation$household_component_mismatches)
message("Insurance component mismatches: ", result$validation$insurance_component_mismatches)
message("Negative insured rows: ", result$validation$negative_insured_rows)

print(
  result$social_infra_kpi %>%
    select(
      geo_level, geo_id, geo_name, year,
      hh_total, pct_hh_family,
      ins_total, pct_health_insured, pct_health_uninsured
    ) %>%
    slice_head(n = 10)
)
