# In this script we turn the tract-level LEHD LODES staging tables into two
# canonical wide Silver tables:
# 1. `silver.lehd_lodes_wac` for workplace area characteristics
# 2. `silver.lehd_lodes_rac` for residence area characteristics
#
# The staging layer has already aggregated block source files to tract. Silver
# keeps tract as the canonical base geography, validates those tracts against
# the managed geography backbone, then derives county, CBSA, state, and
# division rollups from the validated tract base. The landed Silver contract is
# intentionally narrow: every row keeps only `geo_level`, `geo_id`, `geo_name`,
# and `year` as dimensions, with parent geography relationships and release
# metadata handled outside the fact table.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

division_ref <- tibble::tribble(
  ~census_division, ~division_id,
  "New England", "1",
  "Middle Atlantic", "2",
  "East North Central", "3",
  "West North Central", "4",
  "South Atlantic", "5",
  "East South Central", "6",
  "West South Central", "7",
  "Mountain", "8",
  "Pacific", "9"
)

safe_share <- function(numerator, denominator) {
  dplyr::if_else(denominator > 0, numerator / denominator, NA_real_)
}

check_unique_lodes_grain <- function(df, table_name) {
  dupes <- df %>%
    dplyr::count(.data$geo_level, .data$geo_id, .data$year, name = "row_count") %>%
    dplyr::filter(.data$row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf(
        "%s has duplicate geo_level + geo_id + year rows.",
        table_name
      ),
      call. = FALSE
    )
  }
}

sum_lodes_counts <- function(df, group_cols, count_cols) {
  df %>%
    dplyr::group_by(dplyr::across(dplyr::all_of(group_cols))) %>%
    dplyr::summarise(
      dplyr::across(dplyr::all_of(count_cols), ~ sum(.x, na.rm = TRUE)),
      .groups = "drop"
    )
}

add_lodes_derived_columns <- function(df, total_col, include_wac_only = FALSE) {
  total_values <- df[[total_col]]

  out <- df %>%
    dplyr::mutate(
      pct_age_29_or_younger = safe_share(.data$age_29_or_younger, total_values),
      pct_age_30_54 = safe_share(.data$age_30_54, total_values),
      pct_age_55_plus = safe_share(.data$age_55_plus, total_values),
      pct_earnings_low = safe_share(.data$earnings_low, total_values),
      pct_earnings_mid = safe_share(.data$earnings_mid, total_values),
      pct_earnings_high = safe_share(.data$earnings_high, total_values),
      pct_edu_less_than_hs = safe_share(.data$edu_less_than_hs, total_values),
      pct_edu_hs_or_some_college = safe_share(.data$edu_hs_or_some_college, total_values),
      pct_edu_bachelors_or_advanced = safe_share(.data$edu_bachelors_or_advanced, total_values),
      pct_edu_not_available = safe_share(.data$edu_not_available, total_values),
      pct_ind_ag_forest_fish_hunt = safe_share(.data$ind_ag_forest_fish_hunt, total_values),
      pct_ind_mining_quarry_oil_gas = safe_share(.data$ind_mining_quarry_oil_gas, total_values),
      pct_ind_utilities = safe_share(.data$ind_utilities, total_values),
      pct_ind_construction = safe_share(.data$ind_construction, total_values),
      pct_ind_manufacturing = safe_share(.data$ind_manufacturing, total_values),
      pct_ind_wholesale = safe_share(.data$ind_wholesale, total_values),
      pct_ind_retail = safe_share(.data$ind_retail, total_values),
      pct_ind_transport_warehouse = safe_share(.data$ind_transport_warehouse, total_values),
      pct_ind_information = safe_share(.data$ind_information, total_values),
      pct_ind_finance_insurance = safe_share(.data$ind_finance_insurance, total_values),
      pct_ind_real_estate = safe_share(.data$ind_real_estate, total_values),
      pct_ind_professional_scientific_technical = safe_share(.data$ind_professional_scientific_technical, total_values),
      pct_ind_management_companies = safe_share(.data$ind_management_companies, total_values),
      pct_ind_admin_support_waste = safe_share(.data$ind_admin_support_waste, total_values),
      pct_ind_educational_services = safe_share(.data$ind_educational_services, total_values),
      pct_ind_health_care_social_assistance = safe_share(.data$ind_health_care_social_assistance, total_values),
      pct_ind_arts_entertainment_recreation = safe_share(.data$ind_arts_entertainment_recreation, total_values),
      pct_ind_accommodation_food = safe_share(.data$ind_accommodation_food, total_values),
      pct_ind_other_services = safe_share(.data$ind_other_services, total_values),
      pct_ind_public_administration = safe_share(.data$ind_public_administration, total_values)
    )

  if (include_wac_only) {
    out <- out %>%
      dplyr::mutate(
        pct_firm_age_0_1 = safe_share(.data$firm_age_0_1, total_values),
        pct_firm_age_2_3 = safe_share(.data$firm_age_2_3, total_values),
        pct_firm_age_4_5 = safe_share(.data$firm_age_4_5, total_values),
        pct_firm_age_6_10 = safe_share(.data$firm_age_6_10, total_values),
        pct_firm_age_11_plus = safe_share(.data$firm_age_11_plus, total_values),
        pct_firm_size_0_19 = safe_share(.data$firm_size_0_19, total_values),
        pct_firm_size_20_49 = safe_share(.data$firm_size_20_49, total_values),
        pct_firm_size_50_249 = safe_share(.data$firm_size_50_249, total_values),
        pct_firm_size_250_499 = safe_share(.data$firm_size_250_499, total_values),
        pct_firm_size_500_plus = safe_share(.data$firm_size_500_plus, total_values)
      )
  }

  out
}

build_lodes_base <- function(stage_df, lodes_kind = c("wac", "rac")) {
  lodes_kind <- match.arg(lodes_kind)

  stage_df %>%
    dplyr::transmute(
      state = as.character(.data$state),
      state_fips = as.character(.data$state_fips),
      county_geoid = as.character(.data$county_geoid),
      cbsa_code = dplyr::na_if(as.character(.data$cbsa_code), ""),
      tract_geoid = as.character(.data$tract_geoid),
      year = as.integer(.data$year),
      job_type = as.character(.data$job_type),
      segment = as.character(.data$segment),
      release_vintage = as.character(.data$release_vintage),
      release_format_version = as.character(.data$release_format_version),
      source = if (identical(lodes_kind, "wac")) "LEHD LODES WAC" else "LEHD LODES RAC",
      total = as.double(.data$C000),
      age_29_or_younger = as.double(.data$CA01),
      age_30_54 = as.double(.data$CA02),
      age_55_plus = as.double(.data$CA03),
      earnings_low = as.double(.data$CE01),
      earnings_mid = as.double(.data$CE02),
      earnings_high = as.double(.data$CE03),
      edu_less_than_hs = as.double(.data$CD01),
      edu_hs_or_some_college = as.double(.data$CD02),
      edu_bachelors_or_advanced = as.double(.data$CD03),
      edu_not_available = as.double(.data$CD04),
      ind_ag_forest_fish_hunt = as.double(.data$CNS01),
      ind_mining_quarry_oil_gas = as.double(.data$CNS02),
      ind_utilities = as.double(.data$CNS03),
      ind_construction = as.double(.data$CNS04),
      ind_manufacturing = as.double(.data$CNS05),
      ind_wholesale = as.double(.data$CNS06),
      ind_retail = as.double(.data$CNS07),
      ind_transport_warehouse = as.double(.data$CNS08),
      ind_information = as.double(.data$CNS09),
      ind_finance_insurance = as.double(.data$CNS10),
      ind_real_estate = as.double(.data$CNS11),
      ind_professional_scientific_technical = as.double(.data$CNS12),
      ind_management_companies = as.double(.data$CNS13),
      ind_admin_support_waste = as.double(.data$CNS14),
      ind_educational_services = as.double(.data$CNS15),
      ind_health_care_social_assistance = as.double(.data$CNS16),
      ind_arts_entertainment_recreation = as.double(.data$CNS17),
      ind_accommodation_food = as.double(.data$CNS18),
      ind_other_services = as.double(.data$CNS19),
      ind_public_administration = as.double(.data$CNS20),
      firm_age_0_1 = if (identical(lodes_kind, "wac")) as.double(.data$CFA01) else NULL,
      firm_age_2_3 = if (identical(lodes_kind, "wac")) as.double(.data$CFA02) else NULL,
      firm_age_4_5 = if (identical(lodes_kind, "wac")) as.double(.data$CFA03) else NULL,
      firm_age_6_10 = if (identical(lodes_kind, "wac")) as.double(.data$CFA04) else NULL,
      firm_age_11_plus = if (identical(lodes_kind, "wac")) as.double(.data$CFA05) else NULL,
      firm_size_0_19 = if (identical(lodes_kind, "wac")) as.double(.data$CFS01) else NULL,
      firm_size_20_49 = if (identical(lodes_kind, "wac")) as.double(.data$CFS02) else NULL,
      firm_size_50_249 = if (identical(lodes_kind, "wac")) as.double(.data$CFS03) else NULL,
      firm_size_250_499 = if (identical(lodes_kind, "wac")) as.double(.data$CFS04) else NULL,
      firm_size_500_plus = if (identical(lodes_kind, "wac")) as.double(.data$CFS05) else NULL
    )
}

build_lodes_silver <- function(stage_table, lodes_kind = c("wac", "rac")) {
  lodes_kind <- match.arg(lodes_kind)

  stage_df <- DBI::dbGetQuery(con, glue::glue("SELECT * FROM staging.{stage_table}"))

  tract_xwalk <- DBI::dbGetQuery(
    con,
    "
    SELECT
      tract_geoid,
      tract_name_long,
      county_fip,
      county_name,
      state_fip,
      state_abbr,
      state_name
    FROM silver.xwalk_tract_county
    "
  ) %>%
    dplyr::transmute(
      tract_geoid = as.character(.data$tract_geoid),
      tract_name_long = as.character(.data$tract_name_long),
      county_geoid = stringr::str_c(
        as.character(.data$state_fip),
        as.character(.data$county_fip)
      ),
      county_name = as.character(.data$county_name),
      state_fips = as.character(.data$state_fip),
      state_abbr = as.character(.data$state_abbr),
      state_name = as.character(.data$state_name)
    ) %>%
    dplyr::distinct(.data$tract_geoid, .keep_all = TRUE)

  cbsa_xwalk <- DBI::dbGetQuery(
    con,
    "
    SELECT
      county_geoid,
      cbsa_code,
      cbsa_name
    FROM silver.xwalk_cbsa_county
    "
  ) %>%
    dplyr::transmute(
      county_geoid = as.character(.data$county_geoid),
      cbsa_code = as.character(.data$cbsa_code),
      cbsa_name = as.character(.data$cbsa_name)
    ) %>%
    dplyr::distinct()

  state_region_xwalk <- DBI::dbGetQuery(
    con,
    "
    SELECT
      state_fips,
      state_abbr,
      state_name,
      census_region,
      census_division
    FROM silver.xwalk_state_region
    "
  ) %>%
    dplyr::mutate(dplyr::across(dplyr::everything(), as.character)) %>%
    dplyr::distinct()

  duplicate_cbsa_counties <- cbsa_xwalk %>%
    dplyr::count(.data$county_geoid, name = "cbsa_count") %>%
    dplyr::filter(.data$cbsa_count > 1)

  if (nrow(duplicate_cbsa_counties) > 0) {
    stop(
      sprintf(
        "%s Silver rollups require a one-county-to-one-CBSA crosswalk.",
        toupper(lodes_kind)
      ),
      call. = FALSE
    )
  }

  lodes_base <- build_lodes_base(stage_df, lodes_kind = lodes_kind)

  unmatched_tracts <- lodes_base %>%
    dplyr::anti_join(
      tract_xwalk %>% dplyr::select("tract_geoid"),
      by = "tract_geoid"
    )

  if (nrow(unmatched_tracts) > 0) {
    message(
      "Excluding ",
      nrow(unmatched_tracts),
      " unmatched ",
      toupper(lodes_kind),
      " tract rows from Silver because they do not map to silver.xwalk_tract_county."
    )
  }

  tract_base <- lodes_base %>%
    dplyr::inner_join(
      tract_xwalk,
      by = "tract_geoid",
      suffix = c("", "_xwalk")
    ) %>%
    dplyr::transmute(
      geo_level = "tract",
      geo_id = .data$tract_geoid,
      geo_name = .data$tract_name_long,
      year = .data$year,
      state_fips = .data$state_fips,
      state_abbr = .data$state_abbr,
      state_name = .data$state_name,
      county_geoid = .data$county_geoid_xwalk,
      county_name = .data$county_name,
      cbsa_code = .data$cbsa_code,
      cbsa_name = NA_character_,
      division_id = NA_character_,
      division_name = NA_character_,
      job_type = .data$job_type,
      segment = .data$segment,
      release_vintage = .data$release_vintage,
      release_format_version = .data$release_format_version,
      source = .data$source,
      total = .data$total,
      age_29_or_younger = .data$age_29_or_younger,
      age_30_54 = .data$age_30_54,
      age_55_plus = .data$age_55_plus,
      earnings_low = .data$earnings_low,
      earnings_mid = .data$earnings_mid,
      earnings_high = .data$earnings_high,
      edu_less_than_hs = .data$edu_less_than_hs,
      edu_hs_or_some_college = .data$edu_hs_or_some_college,
      edu_bachelors_or_advanced = .data$edu_bachelors_or_advanced,
      edu_not_available = .data$edu_not_available,
      ind_ag_forest_fish_hunt = .data$ind_ag_forest_fish_hunt,
      ind_mining_quarry_oil_gas = .data$ind_mining_quarry_oil_gas,
      ind_utilities = .data$ind_utilities,
      ind_construction = .data$ind_construction,
      ind_manufacturing = .data$ind_manufacturing,
      ind_wholesale = .data$ind_wholesale,
      ind_retail = .data$ind_retail,
      ind_transport_warehouse = .data$ind_transport_warehouse,
      ind_information = .data$ind_information,
      ind_finance_insurance = .data$ind_finance_insurance,
      ind_real_estate = .data$ind_real_estate,
      ind_professional_scientific_technical = .data$ind_professional_scientific_technical,
      ind_management_companies = .data$ind_management_companies,
      ind_admin_support_waste = .data$ind_admin_support_waste,
      ind_educational_services = .data$ind_educational_services,
      ind_health_care_social_assistance = .data$ind_health_care_social_assistance,
      ind_arts_entertainment_recreation = .data$ind_arts_entertainment_recreation,
      ind_accommodation_food = .data$ind_accommodation_food,
      ind_other_services = .data$ind_other_services,
      ind_public_administration = .data$ind_public_administration,
      firm_age_0_1 = if (identical(lodes_kind, "wac")) .data$firm_age_0_1 else NULL,
      firm_age_2_3 = if (identical(lodes_kind, "wac")) .data$firm_age_2_3 else NULL,
      firm_age_4_5 = if (identical(lodes_kind, "wac")) .data$firm_age_4_5 else NULL,
      firm_age_6_10 = if (identical(lodes_kind, "wac")) .data$firm_age_6_10 else NULL,
      firm_age_11_plus = if (identical(lodes_kind, "wac")) .data$firm_age_11_plus else NULL,
      firm_size_0_19 = if (identical(lodes_kind, "wac")) .data$firm_size_0_19 else NULL,
      firm_size_20_49 = if (identical(lodes_kind, "wac")) .data$firm_size_20_49 else NULL,
      firm_size_50_249 = if (identical(lodes_kind, "wac")) .data$firm_size_50_249 else NULL,
      firm_size_250_499 = if (identical(lodes_kind, "wac")) .data$firm_size_250_499 else NULL,
      firm_size_500_plus = if (identical(lodes_kind, "wac")) .data$firm_size_500_plus else NULL
    )

  count_cols <- setdiff(
    names(tract_base),
    c(
      "geo_level", "geo_id", "geo_name", "year", "state_fips", "state_abbr",
      "state_name", "county_geoid", "county_name", "cbsa_code", "cbsa_name",
      "division_id", "division_name", "job_type", "segment", "release_vintage",
      "release_format_version", "source"
    )
  )

  county_rollup <- tract_base %>%
    sum_lodes_counts(
      group_cols = c(
        "county_geoid", "county_name", "state_fips", "state_abbr", "state_name",
        "year", "job_type", "segment", "release_vintage", "release_format_version", "source"
      ),
      count_cols = count_cols
    ) %>%
    dplyr::transmute(
      geo_level = "county",
      geo_id = .data$county_geoid,
      geo_name = .data$county_name,
      year = .data$year,
      state_fips = .data$state_fips,
      state_abbr = .data$state_abbr,
      state_name = .data$state_name,
      county_geoid = .data$county_geoid,
      county_name = .data$county_name,
      cbsa_code = NA_character_,
      cbsa_name = NA_character_,
      division_id = NA_character_,
      division_name = NA_character_,
      job_type = .data$job_type,
      segment = .data$segment,
      release_vintage = .data$release_vintage,
      release_format_version = .data$release_format_version,
      source = .data$source,
      dplyr::across(dplyr::all_of(count_cols))
    )

  cbsa_rollup <- tract_base %>%
    dplyr::select(-"cbsa_code", -"cbsa_name") %>%
    dplyr::inner_join(cbsa_xwalk, by = "county_geoid") %>%
    sum_lodes_counts(
      group_cols = c(
        "cbsa_code", "cbsa_name", "year", "job_type", "segment",
        "release_vintage", "release_format_version", "source"
      ),
      count_cols = count_cols
    ) %>%
    dplyr::transmute(
      geo_level = "cbsa",
      geo_id = .data$cbsa_code,
      geo_name = .data$cbsa_name,
      year = .data$year,
      state_fips = NA_character_,
      state_abbr = NA_character_,
      state_name = NA_character_,
      county_geoid = NA_character_,
      county_name = NA_character_,
      cbsa_code = .data$cbsa_code,
      cbsa_name = .data$cbsa_name,
      division_id = NA_character_,
      division_name = NA_character_,
      job_type = .data$job_type,
      segment = .data$segment,
      release_vintage = .data$release_vintage,
      release_format_version = .data$release_format_version,
      source = .data$source,
      dplyr::across(dplyr::all_of(count_cols))
    )

  state_rollup <- tract_base %>%
    sum_lodes_counts(
      group_cols = c(
        "state_fips", "state_abbr", "state_name", "year", "job_type", "segment",
        "release_vintage", "release_format_version", "source"
      ),
      count_cols = count_cols
    ) %>%
    dplyr::transmute(
      geo_level = "state",
      geo_id = .data$state_fips,
      geo_name = .data$state_name,
      year = .data$year,
      state_fips = .data$state_fips,
      state_abbr = .data$state_abbr,
      state_name = .data$state_name,
      county_geoid = NA_character_,
      county_name = NA_character_,
      cbsa_code = NA_character_,
      cbsa_name = NA_character_,
      division_id = NA_character_,
      division_name = NA_character_,
      job_type = .data$job_type,
      segment = .data$segment,
      release_vintage = .data$release_vintage,
      release_format_version = .data$release_format_version,
      source = .data$source,
      dplyr::across(dplyr::all_of(count_cols))
    )

  division_rollup <- state_rollup %>%
    # Drop placeholder division fields before we attach the canonical division
    # mapping so the join produces one stable `division_id` column.
    dplyr::select(-"division_id", -"division_name") %>%
    dplyr::inner_join(state_region_xwalk, by = c("state_fips", "state_abbr", "state_name")) %>%
    dplyr::inner_join(division_ref, by = c("census_division")) %>%
    sum_lodes_counts(
      group_cols = c(
        "division_id", "census_division", "year", "job_type", "segment",
        "release_vintage", "release_format_version", "source"
      ),
      count_cols = count_cols
    ) %>%
    dplyr::transmute(
      geo_level = "division",
      geo_id = .data$division_id,
      geo_name = .data$census_division,
      year = .data$year,
      state_fips = NA_character_,
      state_abbr = NA_character_,
      state_name = NA_character_,
      county_geoid = NA_character_,
      county_name = NA_character_,
      cbsa_code = NA_character_,
      cbsa_name = NA_character_,
      division_id = .data$division_id,
      division_name = .data$census_division,
      job_type = .data$job_type,
      segment = .data$segment,
      release_vintage = .data$release_vintage,
      release_format_version = .data$release_format_version,
      source = .data$source,
      dplyr::across(dplyr::all_of(count_cols))
    )

  combined <- dplyr::bind_rows(
    tract_base,
    county_rollup,
    cbsa_rollup,
    state_rollup,
    division_rollup
  )

  total_col <- "total"
  combined <- add_lodes_derived_columns(
    combined,
    total_col = total_col,
    include_wac_only = identical(lodes_kind, "wac")
  )

  if (identical(lodes_kind, "wac")) {
  final_df <- combined %>%
    # The build needs state/county/CBSA/division helpers to produce rollups,
    # but the governed Silver contract keeps only the canonical geography key.
    dplyr::select(
      -"state_fips",
      -"state_abbr",
      -"state_name",
      -"county_geoid",
      -"county_name",
      -"cbsa_code",
      -"cbsa_name",
      -"division_id",
      -"division_name",
      -"job_type",
      -"segment",
      -"release_vintage",
      -"release_format_version",
      -"source"
    ) %>%
    dplyr::rename(
      jobs_total = total,
      jobs_age_29_or_younger = age_29_or_younger,
        jobs_age_30_54 = age_30_54,
        jobs_age_55_plus = age_55_plus,
        jobs_earnings_low = earnings_low,
        jobs_earnings_mid = earnings_mid,
        jobs_earnings_high = earnings_high,
        jobs_edu_less_than_hs = edu_less_than_hs,
        jobs_edu_hs_or_some_college = edu_hs_or_some_college,
        jobs_edu_bachelors_or_advanced = edu_bachelors_or_advanced,
        jobs_edu_not_available = edu_not_available,
        jobs_ind_ag_forest_fish_hunt = ind_ag_forest_fish_hunt,
        jobs_ind_mining_quarry_oil_gas = ind_mining_quarry_oil_gas,
        jobs_ind_utilities = ind_utilities,
        jobs_ind_construction = ind_construction,
        jobs_ind_manufacturing = ind_manufacturing,
        jobs_ind_wholesale = ind_wholesale,
        jobs_ind_retail = ind_retail,
        jobs_ind_transport_warehouse = ind_transport_warehouse,
        jobs_ind_information = ind_information,
        jobs_ind_finance_insurance = ind_finance_insurance,
        jobs_ind_real_estate = ind_real_estate,
        jobs_ind_professional_scientific_technical = ind_professional_scientific_technical,
        jobs_ind_management_companies = ind_management_companies,
        jobs_ind_admin_support_waste = ind_admin_support_waste,
        jobs_ind_educational_services = ind_educational_services,
        jobs_ind_health_care_social_assistance = ind_health_care_social_assistance,
        jobs_ind_arts_entertainment_recreation = ind_arts_entertainment_recreation,
        jobs_ind_accommodation_food = ind_accommodation_food,
        jobs_ind_other_services = ind_other_services,
        jobs_ind_public_administration = ind_public_administration,
        jobs_firm_age_0_1 = firm_age_0_1,
        jobs_firm_age_2_3 = firm_age_2_3,
        jobs_firm_age_4_5 = firm_age_4_5,
        jobs_firm_age_6_10 = firm_age_6_10,
        jobs_firm_age_11_plus = firm_age_11_plus,
        jobs_firm_size_0_19 = firm_size_0_19,
        jobs_firm_size_20_49 = firm_size_20_49,
        jobs_firm_size_50_249 = firm_size_50_249,
        jobs_firm_size_250_499 = firm_size_250_499,
        jobs_firm_size_500_plus = firm_size_500_plus,
        pct_jobs_age_29_or_younger = pct_age_29_or_younger,
        pct_jobs_age_30_54 = pct_age_30_54,
        pct_jobs_age_55_plus = pct_age_55_plus,
        pct_jobs_earnings_low = pct_earnings_low,
        pct_jobs_earnings_mid = pct_earnings_mid,
        pct_jobs_earnings_high = pct_earnings_high,
        pct_jobs_edu_less_than_hs = pct_edu_less_than_hs,
        pct_jobs_edu_hs_or_some_college = pct_edu_hs_or_some_college,
        pct_jobs_edu_bachelors_or_advanced = pct_edu_bachelors_or_advanced,
        pct_jobs_edu_not_available = pct_edu_not_available,
        pct_jobs_ind_ag_forest_fish_hunt = pct_ind_ag_forest_fish_hunt,
        pct_jobs_ind_mining_quarry_oil_gas = pct_ind_mining_quarry_oil_gas,
        pct_jobs_ind_utilities = pct_ind_utilities,
        pct_jobs_ind_construction = pct_ind_construction,
        pct_jobs_ind_manufacturing = pct_ind_manufacturing,
        pct_jobs_ind_wholesale = pct_ind_wholesale,
        pct_jobs_ind_retail = pct_ind_retail,
        pct_jobs_ind_transport_warehouse = pct_ind_transport_warehouse,
        pct_jobs_ind_information = pct_ind_information,
        pct_jobs_ind_finance_insurance = pct_ind_finance_insurance,
        pct_jobs_ind_real_estate = pct_ind_real_estate,
        pct_jobs_ind_professional_scientific_technical = pct_ind_professional_scientific_technical,
        pct_jobs_ind_management_companies = pct_ind_management_companies,
        pct_jobs_ind_admin_support_waste = pct_ind_admin_support_waste,
        pct_jobs_ind_educational_services = pct_ind_educational_services,
        pct_jobs_ind_health_care_social_assistance = pct_ind_health_care_social_assistance,
        pct_jobs_ind_arts_entertainment_recreation = pct_ind_arts_entertainment_recreation,
        pct_jobs_ind_accommodation_food = pct_ind_accommodation_food,
        pct_jobs_ind_other_services = pct_ind_other_services,
        pct_jobs_ind_public_administration = pct_ind_public_administration,
        pct_jobs_firm_age_0_1 = pct_firm_age_0_1,
        pct_jobs_firm_age_2_3 = pct_firm_age_2_3,
        pct_jobs_firm_age_4_5 = pct_firm_age_4_5,
        pct_jobs_firm_age_6_10 = pct_firm_age_6_10,
        pct_jobs_firm_age_11_plus = pct_firm_age_11_plus,
        pct_jobs_firm_size_0_19 = pct_firm_size_0_19,
        pct_jobs_firm_size_20_49 = pct_firm_size_20_49,
        pct_jobs_firm_size_50_249 = pct_firm_size_50_249,
        pct_jobs_firm_size_250_499 = pct_firm_size_250_499,
        pct_jobs_firm_size_500_plus = pct_firm_size_500_plus
      )
  } else {
    final_df <- combined %>%
      dplyr::select(
        -"state_fips",
        -"state_abbr",
        -"state_name",
        -"county_geoid",
        -"county_name",
        -"cbsa_code",
        -"cbsa_name",
        -"division_id",
        -"division_name",
        -"job_type",
        -"segment",
        -"release_vintage",
        -"release_format_version",
        -"source"
      ) %>%
      dplyr::rename(
        workers_total = total,
        workers_age_29_or_younger = age_29_or_younger,
        workers_age_30_54 = age_30_54,
        workers_age_55_plus = age_55_plus,
        workers_earnings_low = earnings_low,
        workers_earnings_mid = earnings_mid,
        workers_earnings_high = earnings_high,
        workers_edu_less_than_hs = edu_less_than_hs,
        workers_edu_hs_or_some_college = edu_hs_or_some_college,
        workers_edu_bachelors_or_advanced = edu_bachelors_or_advanced,
        workers_edu_not_available = edu_not_available,
        workers_ind_ag_forest_fish_hunt = ind_ag_forest_fish_hunt,
        workers_ind_mining_quarry_oil_gas = ind_mining_quarry_oil_gas,
        workers_ind_utilities = ind_utilities,
        workers_ind_construction = ind_construction,
        workers_ind_manufacturing = ind_manufacturing,
        workers_ind_wholesale = ind_wholesale,
        workers_ind_retail = ind_retail,
        workers_ind_transport_warehouse = ind_transport_warehouse,
        workers_ind_information = ind_information,
        workers_ind_finance_insurance = ind_finance_insurance,
        workers_ind_real_estate = ind_real_estate,
        workers_ind_professional_scientific_technical = ind_professional_scientific_technical,
        workers_ind_management_companies = ind_management_companies,
        workers_ind_admin_support_waste = ind_admin_support_waste,
        workers_ind_educational_services = ind_educational_services,
        workers_ind_health_care_social_assistance = ind_health_care_social_assistance,
        workers_ind_arts_entertainment_recreation = ind_arts_entertainment_recreation,
        workers_ind_accommodation_food = ind_accommodation_food,
        workers_ind_other_services = ind_other_services,
        workers_ind_public_administration = ind_public_administration,
        pct_workers_age_29_or_younger = pct_age_29_or_younger,
        pct_workers_age_30_54 = pct_age_30_54,
        pct_workers_age_55_plus = pct_age_55_plus,
        pct_workers_earnings_low = pct_earnings_low,
        pct_workers_earnings_mid = pct_earnings_mid,
        pct_workers_earnings_high = pct_earnings_high,
        pct_workers_edu_less_than_hs = pct_edu_less_than_hs,
        pct_workers_edu_hs_or_some_college = pct_edu_hs_or_some_college,
        pct_workers_edu_bachelors_or_advanced = pct_edu_bachelors_or_advanced,
        pct_workers_edu_not_available = pct_edu_not_available,
        pct_workers_ind_ag_forest_fish_hunt = pct_ind_ag_forest_fish_hunt,
        pct_workers_ind_mining_quarry_oil_gas = pct_ind_mining_quarry_oil_gas,
        pct_workers_ind_utilities = pct_ind_utilities,
        pct_workers_ind_construction = pct_ind_construction,
        pct_workers_ind_manufacturing = pct_ind_manufacturing,
        pct_workers_ind_wholesale = pct_ind_wholesale,
        pct_workers_ind_retail = pct_ind_retail,
        pct_workers_ind_transport_warehouse = pct_ind_transport_warehouse,
        pct_workers_ind_information = pct_ind_information,
        pct_workers_ind_finance_insurance = pct_ind_finance_insurance,
        pct_workers_ind_real_estate = pct_ind_real_estate,
        pct_workers_ind_professional_scientific_technical = pct_ind_professional_scientific_technical,
        pct_workers_ind_management_companies = pct_ind_management_companies,
        pct_workers_ind_admin_support_waste = pct_ind_admin_support_waste,
        pct_workers_ind_educational_services = pct_ind_educational_services,
        pct_workers_ind_health_care_social_assistance = pct_ind_health_care_social_assistance,
        pct_workers_ind_arts_entertainment_recreation = pct_ind_arts_entertainment_recreation,
        pct_workers_ind_accommodation_food = pct_ind_accommodation_food,
        pct_workers_ind_other_services = pct_ind_other_services,
        pct_workers_ind_public_administration = pct_ind_public_administration
      )
  }

  check_unique_lodes_grain(final_df, glue::glue("silver.lehd_lodes_{lodes_kind}"))

  final_df
}

wac_silver <- build_lodes_silver("lehd_lodes_wac", lodes_kind = "wac")
rac_silver <- build_lodes_silver("lehd_lodes_rac", lodes_kind = "rac")

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "lehd_lodes_wac"),
  wac_silver,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "lehd_lodes_rac"),
  rac_silver,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
