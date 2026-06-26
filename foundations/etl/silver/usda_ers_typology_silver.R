# In this script we widen the two long USDA ERS staging tables into one
# county-equivalent Silver dimension table. The source files are delivered in
# `attribute` / `value` form, so Silver's main job is to:
# 1. pivot each source family to one row per county-equivalent FIPS
# 2. normalize the coded fields and binary flags into an analyst-friendly shape
# 3. preserve source-coverage signals for rows that only exist in one source
# 4. keep Connecticut legacy-county exceptions visible rather than silently
#    forcing them onto the planning-region backbone
#
# We intentionally stop at county-equivalent rows in this first pass. RUCC is on
# the current planning-region backbone for Connecticut, while County Typology
# still mixes planning regions and legacy counties. Until we agree on a managed
# reconciliation rule, county-wide Silver is defensible and CBSA summaries are
# not.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

rucc_vintage_year <- 2023L
typology_vintage_year <- 2025L

# 2. Helpers ----
normalize_binary_flag <- function(x) {
  dplyr::case_when(
    is.na(x) ~ NA_integer_,
    x %in% c(0, 1) ~ as.integer(x),
    TRUE ~ NA_integer_
  )
}

normalize_industry_dependence_code <- function(x) {
  dplyr::case_when(
    is.na(x) ~ NA_integer_,
    x %in% 0:5 ~ as.integer(x),
    TRUE ~ NA_integer_
  )
}

label_industry_dependence_code <- function(x) {
  dplyr::case_when(
    is.na(x) ~ NA_character_,
    x == 0L ~ "not_dependent",
    x == 1L ~ "farming_dependent",
    x == 2L ~ "mining_dependent",
    x == 3L ~ "manufacturing_dependent",
    x == 4L ~ "government_dependent",
    x == 5L ~ "recreation_dependent",
    TRUE ~ NA_character_
  )
}

check_unique_geo_grain <- function(df, table_name) {
  dupes <- df %>%
    dplyr::count(.data$geo_level, .data$geo_id, name = "row_count") %>%
    dplyr::filter(.data$row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf("%s has duplicate geo_level + geo_id rows", table_name),
      call. = FALSE
    )
  }
}

# 3. Read staging inputs and county backbone helpers ----
rucc_stage <- DBI::dbGetQuery(con, "SELECT * FROM staging.usda_rucc") %>%
  dplyr::mutate(
    vintage_year = as.integer(.data$vintage_year),
    fips = as.character(.data$fips),
    state_abbr = as.character(.data$state_abbr),
    county_name = as.character(.data$county_name),
    attribute = as.character(.data$attribute),
    value_raw = as.character(.data$value_raw),
    value_numeric = as.double(.data$value_numeric)
  )

typology_stage <- DBI::dbGetQuery(con, "SELECT * FROM staging.usda_county_typology") %>%
  dplyr::mutate(
    vintage_year = as.integer(.data$vintage_year),
    fips = as.character(.data$fips),
    state_abbr = as.character(.data$state_abbr),
    county_name = as.character(.data$county_name),
    metro2023 = as.integer(.data$metro2023),
    attribute = as.character(.data$attribute),
    value_raw = as.character(.data$value_raw),
    value_numeric = as.double(.data$value_numeric)
  )

county_backbone <- DBI::dbGetQuery(
  con,
  "
  SELECT
    geo_id AS county_geoid,
    geo_name,
    state_fips,
    state_abbr
  FROM gold.dim_geo
  WHERE geo_level = 'county'
  "
) %>%
  dplyr::mutate(
    county_geoid = as.character(.data$county_geoid),
    geo_name_backbone = as.character(.data$geo_name),
    state_fips_backbone = as.character(.data$state_fips),
    state_abbr_backbone = as.character(.data$state_abbr)
  )

# 4. Widen the source-native attribute/value tables ----
rucc_wide <- rucc_stage %>%
  dplyr::select(
    "fips",
    "state_abbr",
    "county_name",
    "attribute",
    "value_raw",
    "value_numeric"
  ) %>%
  tidyr::pivot_wider(
    id_cols = c("fips", "state_abbr", "county_name"),
    names_from = "attribute",
    values_from = c("value_raw", "value_numeric"),
    values_fn = dplyr::first,
    names_sep = "__"
  ) %>%
  dplyr::transmute(
    fips = .data$fips,
    rucc_state_abbr = .data$state_abbr,
    rucc_county_name = .data$county_name,
    rucc_vintage_year = rucc_vintage_year,
    population_2020 = as.double(.data$value_numeric__Population_2020),
    rucc_2023_code = as.integer(.data$value_numeric__RUCC_2023),
    rucc_2023_description = as.character(.data$value_raw__Description),
    has_rucc = TRUE
  )

typology_wide <- typology_stage %>%
  dplyr::select(
    "fips",
    "state_abbr",
    "county_name",
    "metro2023",
    "attribute",
    "value_numeric"
  ) %>%
  tidyr::pivot_wider(
    id_cols = c("fips", "state_abbr", "county_name", "metro2023"),
    names_from = "attribute",
    values_from = "value_numeric",
    values_fn = dplyr::first
  ) %>%
  dplyr::mutate(
    industry_dependence_raw = as.integer(.data$Industry_Dependence_2025),
    persistent_poverty_raw = as.integer(.data$Persistent_Poverty_1721),
    has_typology_exception_values =
      !is.na(.data$industry_dependence_raw) & !.data$industry_dependence_raw %in% c(0:5) |
      !is.na(.data$persistent_poverty_raw) & !.data$persistent_poverty_raw %in% c(0L, 1L)
  ) %>%
  dplyr::transmute(
    fips = .data$fips,
    typology_state_abbr = .data$state_abbr,
    typology_county_name = .data$county_name,
    typology_vintage_year = typology_vintage_year,
    metro2023_flag = normalize_binary_flag(as.integer(.data$metro2023)),
    high_farming_flag = normalize_binary_flag(.data$High_Farming_2025),
    high_government_flag = normalize_binary_flag(.data$High_Government_2025),
    high_manufacturing_flag = normalize_binary_flag(.data$High_Manufacturing_2025),
    high_mining_flag = normalize_binary_flag(.data$High_Mining_2025),
    high_recreation_flag = normalize_binary_flag(.data$High_Recreation_2025),
    housing_stress_flag = normalize_binary_flag(.data$Housing_Stress_2025),
    low_employment_flag = normalize_binary_flag(.data$Low_Employment_2025),
    low_postsecondary_ed_flag = normalize_binary_flag(.data$Low_PostSecondary_Ed_2025),
    nonspecialized_flag = normalize_binary_flag(.data$Nonspecialized_2025),
    population_loss_flag = normalize_binary_flag(.data$Population_Loss_2025),
    retirement_destination_flag = normalize_binary_flag(.data$Retirement_Destination_2025),
    persistent_poverty_raw = .data$persistent_poverty_raw,
    persistent_poverty_flag = normalize_binary_flag(.data$persistent_poverty_raw),
    industry_dependence_raw = .data$industry_dependence_raw,
    industry_dependence_code = normalize_industry_dependence_code(.data$industry_dependence_raw),
    industry_dependence_label = label_industry_dependence_code(normalize_industry_dependence_code(.data$industry_dependence_raw)),
    has_typology_exception_values = dplyr::coalesce(.data$has_typology_exception_values, FALSE),
    has_typology = TRUE
  )

# 5. Build the county-wide Silver table ----
silver_usda_county_typology <- dplyr::full_join(
  rucc_wide,
  typology_wide,
  by = "fips"
) %>%
  dplyr::mutate(
    geo_level = "county",
    geo_id = .data$fips,
    state_fips_source = stringr::str_sub(.data$fips, 1, 2),
    state_abbr_source = dplyr::coalesce(.data$rucc_state_abbr, .data$typology_state_abbr),
    county_name_source = dplyr::coalesce(.data$rucc_county_name, .data$typology_county_name),
    has_rucc = dplyr::coalesce(.data$has_rucc, FALSE),
    has_typology = dplyr::coalesce(.data$has_typology, FALSE)
  ) %>%
  dplyr::left_join(
    county_backbone,
    by = c("geo_id" = "county_geoid")
  ) %>%
  dplyr::mutate(
    in_current_county_backbone = !is.na(.data$geo_name_backbone),
    geo_name = dplyr::coalesce(.data$geo_name_backbone, .data$county_name_source)
  ) %>%
  dplyr::transmute(
    geo_level = .data$geo_level,
    geo_id = .data$geo_id,
    geo_name = .data$geo_name,
    state_fips = .data$state_fips_source,
    state_abbr = dplyr::coalesce(.data$state_abbr_source, .data$state_abbr_backbone),
    has_rucc = .data$has_rucc,
    has_typology = .data$has_typology,
    in_current_county_backbone = .data$in_current_county_backbone,
    rucc_vintage_year = .data$rucc_vintage_year,
    rucc_2023_code = .data$rucc_2023_code,
    rucc_2023_description = .data$rucc_2023_description,
    population_2020 = .data$population_2020,
    typology_vintage_year = .data$typology_vintage_year,
    metro2023_flag = .data$metro2023_flag,
    high_farming_flag = .data$high_farming_flag,
    high_government_flag = .data$high_government_flag,
    high_manufacturing_flag = .data$high_manufacturing_flag,
    high_mining_flag = .data$high_mining_flag,
    high_recreation_flag = .data$high_recreation_flag,
    housing_stress_flag = .data$housing_stress_flag,
    low_employment_flag = .data$low_employment_flag,
    low_postsecondary_ed_flag = .data$low_postsecondary_ed_flag,
    nonspecialized_flag = .data$nonspecialized_flag,
    population_loss_flag = .data$population_loss_flag,
    retirement_destination_flag = .data$retirement_destination_flag,
    persistent_poverty_raw = .data$persistent_poverty_raw,
    persistent_poverty_flag = .data$persistent_poverty_flag,
    industry_dependence_raw = .data$industry_dependence_raw,
    industry_dependence_code = .data$industry_dependence_code,
    industry_dependence_label = .data$industry_dependence_label,
    has_typology_exception_values = .data$has_typology_exception_values
  ) %>%
  dplyr::arrange(.data$geo_id)

# 6. Contract checks ----
check_unique_geo_grain(silver_usda_county_typology, "silver.usda_county_typology")

if (dplyr::n_distinct(silver_usda_county_typology$geo_id) != 3243L) {
  stop(
    "silver.usda_county_typology does not contain the expected 3,243 distinct county-equivalent FIPS keys.",
    call. = FALSE
  )
}

# 7. Materialize the Silver table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "usda_county_typology"),
  silver_usda_county_typology,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
