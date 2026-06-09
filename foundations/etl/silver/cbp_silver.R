# In this script we normalize the source-faithful CBP county staging table
# into a curated long Silver table for county, CBSA, and state business
# structure analysis.
#
# 1. Read the staged county CBP rows and the geography crosswalks.
# 2. Keep the all-sectors row plus the published broad sector rows that align
#    to our existing Gold industry families.
# 3. Standardize county rows and derive CBSA/state rollups from counties.
# 4. Materialize one long `silver.cbp` analytical table.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

check_unique_annual_grain <- function(df, table_name) {
  dupes <- df %>%
    count(.data$geo_level, .data$geo_id, .data$period, .data$industry_code, name = "row_count") %>%
    filter(.data$row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf(
        "%s has duplicate geo_level + geo_id + period + industry_code rows",
        table_name
      ),
      call. = FALSE
    )
  }
}

summarize_cbp <- function(df, group_cols) {
  df %>%
    group_by(across(all_of(group_cols))) %>%
    summarize(
      establishments = sum(.data$establishments, na.rm = TRUE),
      employment_march12 = sum(.data$employment_march12, na.rm = TRUE),
      first_quarter_payroll_k = sum(.data$first_quarter_payroll_k, na.rm = TRUE),
      annual_payroll_k = sum(.data$annual_payroll_k, na.rm = TRUE),
      est_n_lt_5 = sum(.data$est_n_lt_5, na.rm = TRUE),
      est_n_5_9 = sum(.data$est_n_5_9, na.rm = TRUE),
      est_n_10_19 = sum(.data$est_n_10_19, na.rm = TRUE),
      est_n_20_49 = sum(.data$est_n_20_49, na.rm = TRUE),
      est_n_50_99 = sum(.data$est_n_50_99, na.rm = TRUE),
      est_n_100_249 = sum(.data$est_n_100_249, na.rm = TRUE),
      est_n_250_499 = sum(.data$est_n_250_499, na.rm = TRUE),
      est_n_500_999 = sum(.data$est_n_500_999, na.rm = TRUE),
      est_n_1000_plus = sum(.data$est_n_1000_plus, na.rm = TRUE),
      est_n_1000_1499 = sum(.data$est_n_1000_1499, na.rm = TRUE),
      est_n_1500_2499 = sum(.data$est_n_1500_2499, na.rm = TRUE),
      est_n_2500_4999 = sum(.data$est_n_2500_4999, na.rm = TRUE),
      est_n_5000_plus = sum(.data$est_n_5000_plus, na.rm = TRUE),
      has_emp_flag = any(.data$has_emp_flag, na.rm = TRUE),
      has_qp1_flag = any(.data$has_qp1_flag, na.rm = TRUE),
      has_ap_flag = any(.data$has_ap_flag, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    mutate(
      annual_payroll_per_employee = if_else(
        .data$employment_march12 > 0,
        (.data$annual_payroll_k * 1000) / .data$employment_march12,
        NA_real_
      ),
      first_quarter_payroll_per_employee = if_else(
        .data$employment_march12 > 0,
        (.data$first_quarter_payroll_k * 1000) / .data$employment_march12,
        NA_real_
      )
    )
}

# 1. Read staging and crosswalks ----
cbsa_county_xwalk <- DBI::dbGetQuery(
  con,
  "SELECT county_geoid, cbsa_code, cbsa_name FROM silver.xwalk_cbsa_county"
) %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    cbsa_code = as.character(.data$cbsa_code),
    cbsa_name = as.character(.data$cbsa_name)
  ) %>%
  distinct()

county_state_xwalk <- DBI::dbGetQuery(
  con,
  "SELECT state_fip, county_geoid, county_name, state_abbr FROM silver.xwalk_county_state"
) %>%
  transmute(
    state_fips = as.character(.data$state_fip),
    county_geoid = as.character(.data$county_geoid),
    county_name = as.character(.data$county_name),
    state_abbr = as.character(.data$state_abbr)
  ) %>%
  distinct()

state_ref <- county_state_xwalk %>%
  distinct(.data$state_fips, .data$state_abbr)

cbp_industry_map <- tibble::tribble(
  ~industry_code, ~industry_title, ~silver_rollup_family, ~is_total_row,
  "------", "Total for all sectors", "total", TRUE,
  "11----", "Agriculture, forestry, fishing and hunting", "ag_mining", FALSE,
  "21----", "Mining, quarrying, and oil and gas extraction", "ag_mining", FALSE,
  "22----", "Utilities", "transport_util", FALSE,
  "23----", "Construction", "construction", FALSE,
  "31----", "Manufacturing", "manufacturing", FALSE,
  "42----", "Wholesale trade", "wholesale", FALSE,
  "44----", "Retail trade", "retail", FALSE,
  "48----", "Transportation and warehousing", "transport_util", FALSE,
  "51----", "Information", "information", FALSE,
  "52----", "Finance and insurance", "finance_real", FALSE,
  "53----", "Real estate and rental and leasing", "finance_real", FALSE,
  "54----", "Professional, scientific, and technical services", "professional", FALSE,
  "55----", "Management of companies and enterprises", "professional", FALSE,
  "56----", "Administrative and support and waste management", "professional", FALSE,
  "61----", "Educational services", "educ_health", FALSE,
  "62----", "Health care and social assistance", "educ_health", FALSE,
  "71----", "Arts, entertainment, and recreation", "arts_accomm_food", FALSE,
  "72----", "Accommodation and food services", "arts_accomm_food", FALSE,
  "81----", "Other services (except public administration)", "other_services", FALSE
) %>%
  mutate(
    industry_code = as.character(.data$industry_code),
    industry_title = as.character(.data$industry_title),
    silver_rollup_family = as.character(.data$silver_rollup_family)
  )

canonical_codes <- cbp_industry_map$industry_code

cbp_county_stage <- DBI::dbGetQuery(
  con,
  "SELECT * FROM staging.cbp_county"
) %>%
  mutate(
    year = as.integer(.data$year),
    state_fips = as.character(.data$state_fips),
    county_fips = as.character(.data$county_fips),
    naics_code = as.character(.data$naics_code),
    emp_noise_flag = as.character(.data$emp_noise_flag),
    qp1_noise_flag = as.character(.data$qp1_noise_flag),
    ap_noise_flag = as.character(.data$ap_noise_flag)
  ) %>%
  filter(.data$naics_code %in% canonical_codes) %>%
  left_join(cbp_industry_map, by = c("naics_code" = "industry_code"))

# 2. Standardize county rows ----
cbp_county <- cbp_county_stage %>%
  left_join(
    county_state_xwalk,
    by = c("county_fips" = "county_geoid", "state_fips")
  ) %>%
  transmute(
    geo_level = "county",
    geo_id = .data$county_fips,
    geo_name = coalesce(.data$county_name, .data$county_fips),
    period = .data$year,
    state_fips = .data$state_fips,
    state_abbr = .data$state_abbr,
    industry_code = .data$naics_code,
    industry_title = .data$industry_title,
    silver_rollup_family = .data$silver_rollup_family,
    is_total_row = .data$is_total_row,
    establishments = as.double(.data$establishments),
    employment_march12 = as.double(.data$employment_march12),
    first_quarter_payroll_k = as.double(.data$first_quarter_payroll_k),
    annual_payroll_k = as.double(.data$annual_payroll_k),
    est_n_lt_5 = as.double(.data$est_n_lt_5),
    est_n_5_9 = as.double(.data$est_n_5_9),
    est_n_10_19 = as.double(.data$est_n_10_19),
    est_n_20_49 = as.double(.data$est_n_20_49),
    est_n_50_99 = as.double(.data$est_n_50_99),
    est_n_100_249 = as.double(.data$est_n_100_249),
    est_n_250_499 = as.double(.data$est_n_250_499),
    est_n_500_999 = as.double(.data$est_n_500_999),
    est_n_1000_plus = as.double(.data$est_n_1000_plus),
    est_n_1000_1499 = as.double(.data$est_n_1000_1499),
    est_n_1500_2499 = as.double(.data$est_n_1500_2499),
    est_n_2500_4999 = as.double(.data$est_n_2500_4999),
    est_n_5000_plus = as.double(.data$est_n_5000_plus),
    has_emp_flag = !is.na(.data$emp_noise_flag) & .data$emp_noise_flag != "",
    has_qp1_flag = !is.na(.data$qp1_noise_flag) & .data$qp1_noise_flag != "",
    has_ap_flag = !is.na(.data$ap_noise_flag) & .data$ap_noise_flag != "",
    annual_payroll_per_employee = if_else(
      .data$employment_march12 > 0,
      (.data$annual_payroll_k * 1000) / .data$employment_march12,
      NA_real_
    ),
    first_quarter_payroll_per_employee = if_else(
      .data$employment_march12 > 0,
      (.data$first_quarter_payroll_k * 1000) / .data$employment_march12,
      NA_real_
    ),
    source = "Census CBP"
  )

# 3. Derive CBSA and state rollups from counties ----
cbp_cbsa <- cbp_county %>%
  inner_join(
    cbsa_county_xwalk,
    by = c("geo_id" = "county_geoid")
  ) %>%
  summarize_cbp(
    group_cols = c(
      "cbsa_code",
      "cbsa_name",
      "period",
      "industry_code",
      "industry_title",
      "silver_rollup_family",
      "is_total_row"
    )
  ) %>%
  transmute(
    geo_level = "cbsa",
    geo_id = .data$cbsa_code,
    geo_name = .data$cbsa_name,
    period = .data$period,
    state_fips = NA_character_,
    state_abbr = NA_character_,
    industry_code = .data$industry_code,
    industry_title = .data$industry_title,
    silver_rollup_family = .data$silver_rollup_family,
    is_total_row = .data$is_total_row,
    establishments = .data$establishments,
    employment_march12 = .data$employment_march12,
    first_quarter_payroll_k = .data$first_quarter_payroll_k,
    annual_payroll_k = .data$annual_payroll_k,
    est_n_lt_5 = .data$est_n_lt_5,
    est_n_5_9 = .data$est_n_5_9,
    est_n_10_19 = .data$est_n_10_19,
    est_n_20_49 = .data$est_n_20_49,
    est_n_50_99 = .data$est_n_50_99,
    est_n_100_249 = .data$est_n_100_249,
    est_n_250_499 = .data$est_n_250_499,
    est_n_500_999 = .data$est_n_500_999,
    est_n_1000_plus = .data$est_n_1000_plus,
    est_n_1000_1499 = .data$est_n_1000_1499,
    est_n_1500_2499 = .data$est_n_1500_2499,
    est_n_2500_4999 = .data$est_n_2500_4999,
    est_n_5000_plus = .data$est_n_5000_plus,
    has_emp_flag = .data$has_emp_flag,
    has_qp1_flag = .data$has_qp1_flag,
    has_ap_flag = .data$has_ap_flag,
    annual_payroll_per_employee = .data$annual_payroll_per_employee,
    first_quarter_payroll_per_employee = .data$first_quarter_payroll_per_employee,
    source = "Census CBP"
  )

cbp_state <- cbp_county %>%
  summarize_cbp(
    group_cols = c(
      "state_fips",
      "period",
      "industry_code",
      "industry_title",
      "silver_rollup_family",
      "is_total_row"
    )
  ) %>%
  left_join(
    state_ref,
    by = "state_fips"
  ) %>%
  transmute(
    geo_level = "state",
    geo_id = .data$state_fips,
    geo_name = .data$state_abbr,
    period = .data$period,
    state_fips = .data$state_fips,
    state_abbr = .data$state_abbr,
    industry_code = .data$industry_code,
    industry_title = .data$industry_title,
    silver_rollup_family = .data$silver_rollup_family,
    is_total_row = .data$is_total_row,
    establishments = .data$establishments,
    employment_march12 = .data$employment_march12,
    first_quarter_payroll_k = .data$first_quarter_payroll_k,
    annual_payroll_k = .data$annual_payroll_k,
    est_n_lt_5 = .data$est_n_lt_5,
    est_n_5_9 = .data$est_n_5_9,
    est_n_10_19 = .data$est_n_10_19,
    est_n_20_49 = .data$est_n_20_49,
    est_n_50_99 = .data$est_n_50_99,
    est_n_100_249 = .data$est_n_100_249,
    est_n_250_499 = .data$est_n_250_499,
    est_n_500_999 = .data$est_n_500_999,
    est_n_1000_plus = .data$est_n_1000_plus,
    est_n_1000_1499 = .data$est_n_1000_1499,
    est_n_1500_2499 = .data$est_n_1500_2499,
    est_n_2500_4999 = .data$est_n_2500_4999,
    est_n_5000_plus = .data$est_n_5000_plus,
    has_emp_flag = .data$has_emp_flag,
    has_qp1_flag = .data$has_qp1_flag,
    has_ap_flag = .data$has_ap_flag,
    annual_payroll_per_employee = .data$annual_payroll_per_employee,
    first_quarter_payroll_per_employee = .data$first_quarter_payroll_per_employee,
    source = "Census CBP"
  )

# 4. Materialize Silver ----
cbp_silver <- bind_rows(
  cbp_county,
  cbp_cbsa,
  cbp_state
) %>%
  arrange(.data$geo_level, .data$geo_id, .data$period, .data$industry_code)

check_unique_annual_grain(cbp_silver, "silver.cbp")

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "cbp"),
  cbp_silver,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
