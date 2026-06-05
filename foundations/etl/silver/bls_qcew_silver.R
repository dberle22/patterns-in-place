# In this script we turn the raw QCEW staging layer into managed Silver assets.
#
# 1. Read the full county staging table, geography crosswalks, and the QCEW industry metadata seed
# 2. Materialize the stabilized QCEW industry mapping as `silver.bls_qcew_industry_map`
# 3. Filter county staging to the canonical industry subset defined by that map
# 4. Standardize county rows and roll them up to CBSA and state with ownership preserved
# 5. Write the long-form `silver.bls_qcew` table and validate its grain

getwd()

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# 1. Read crosswalks and the mapping seed ----
cbsa_county_xwalk <- dbGetQuery(
  con,
  "SELECT county_geoid, cbsa_code, cbsa_name FROM silver.xwalk_cbsa_county"
)

county_state_xwalk <- dbGetQuery(
  con,
  "SELECT state_fip, county_geoid, state_abbr FROM silver.xwalk_county_state"
)

state_ref <- tibble::tribble(
  ~state_fips_code, ~state_abbr,
  "01", "AL",
  "02", "AK",
  "04", "AZ",
  "05", "AR",
  "06", "CA",
  "08", "CO",
  "09", "CT",
  "10", "DE",
  "11", "DC",
  "12", "FL",
  "13", "GA",
  "15", "HI",
  "16", "ID",
  "17", "IL",
  "18", "IN",
  "19", "IA",
  "20", "KS",
  "21", "KY",
  "22", "LA",
  "23", "ME",
  "24", "MD",
  "25", "MA",
  "26", "MI",
  "27", "MN",
  "28", "MS",
  "29", "MO",
  "30", "MT",
  "31", "NE",
  "32", "NV",
  "33", "NH",
  "34", "NJ",
  "35", "NM",
  "36", "NY",
  "37", "NC",
  "38", "ND",
  "39", "OH",
  "40", "OK",
  "41", "OR",
  "42", "PA",
  "44", "RI",
  "45", "SC",
  "46", "SD",
  "47", "TN",
  "48", "TX",
  "49", "UT",
  "50", "VT",
  "51", "VA",
  "53", "WA",
  "54", "WV",
  "55", "WI",
  "56", "WY",
  "72", "PR",
  "78", "VI"
)

qcew_industry_map <- readr::read_csv(
  here::here("foundations", "etl", "reference", "bls_qcew_industry_map.csv"),
  show_col_types = FALSE,
  col_types = readr::cols(
    industry_code = readr::col_character(),
    industry_title = readr::col_character(),
    first_seen_year = readr::col_integer(),
    last_seen_year = readr::col_integer(),
    years_present = readr::col_character(),
    member_count = readr::col_integer(),
    code_length = readr::col_integer(),
    code_type = readr::col_character(),
    is_aggregate = readr::col_logical(),
    aggregate_components = readr::col_character(),
    keep_in_staging = readr::col_logical(),
    keep_in_silver_canonical = readr::col_logical(),
    silver_rollup_family = readr::col_character(),
    notes = readr::col_character()
  )
)

# 2. Materialize the managed industry mapping table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "bls_qcew_industry_map"),
  qcew_industry_map,
  overwrite = TRUE
)

# 3. Filter county staging to the curated Silver subset ----
# The curated Silver contract keeps one clean total-covered row, uses the
# private-sector slice for the canonical industry rows, and adds Public
# Administration back in as an explicit government-sector exception.
canonical_industry_map <- qcew_industry_map %>%
  filter(keep_in_silver_canonical) %>%
  select(
    industry_code,
    industry_title,
    code_type,
    is_aggregate,
    aggregate_components,
    silver_rollup_family
  )

canonical_qcew_county <- dbGetQuery(
  con,
  "
  SELECT
    s.geo_id,
    s.county_name,
    s.state_fips_code,
    s.period,
    s.own_code,
    s.own_title,
    s.industry_code,
    s.industry_title,
    m.code_type,
    m.is_aggregate,
    m.aggregate_components,
    m.silver_rollup_family,
    s.annual_avg_estabs,
    s.annual_avg_emplvl,
    s.total_annual_wages,
    s.taxable_annual_wages,
    s.annual_contributions,
    s.annual_avg_wkly_wage,
    s.avg_annual_pay,
    s.disclosure_code,
    s.src
  FROM staging.bls_qcew_county s
  INNER JOIN silver.bls_qcew_industry_map m
    ON s.industry_code = m.industry_code
  WHERE
    m.keep_in_silver_canonical = TRUE
    AND (
      (s.industry_code = '10' AND s.own_code = '0' AND s.agglvl_code = '70')
      OR
      (s.industry_code NOT IN ('10', '92') AND s.own_code = '5' AND s.agglvl_code = '74')
      OR
      (s.industry_code = '92' AND s.own_code IN ('1', '2', '3') AND s.agglvl_code = '74')
    )
  "
)

summarize_qcew <- function(df, group_cols) {
  df %>%
    group_by(across(all_of(group_cols))) %>%
    summarise(
      annual_avg_estabs = sum(annual_avg_estabs, na.rm = TRUE),
      annual_avg_emplvl = sum(annual_avg_emplvl, na.rm = TRUE),
      total_annual_wages = sum(total_annual_wages, na.rm = TRUE),
      taxable_annual_wages = sum(taxable_annual_wages, na.rm = TRUE),
      annual_contributions = sum(annual_contributions, na.rm = TRUE),
      disclosure_code = case_when(
        any(disclosure_code == "N", na.rm = TRUE) ~ "N",
        TRUE ~ ""
      ),
      .groups = "drop"
    ) %>%
    mutate(
      annual_avg_wkly_wage = if_else(
        annual_avg_emplvl > 0,
        total_annual_wages / annual_avg_emplvl / 52,
        NA_real_
      ),
      avg_annual_pay = if_else(
        annual_avg_emplvl > 0,
        total_annual_wages / annual_avg_emplvl,
        NA_real_
      )
    )
}

# 4. Build county, CBSA, and state slices ----
county_qcew <- canonical_qcew_county %>%
  transmute(
    geo_level = "county",
    geo_id,
    geo_name = county_name,
    period,
    own_code,
    own_title,
    industry_code,
    industry_title,
    code_type,
    is_aggregate,
    aggregate_components,
    silver_rollup_family,
    annual_avg_estabs,
    annual_avg_emplvl,
    total_annual_wages,
    taxable_annual_wages,
    annual_contributions,
    annual_avg_wkly_wage,
    avg_annual_pay,
    disclosure_code,
    source = src
  )

cbsa_qcew <- canonical_qcew_county %>%
  inner_join(
    cbsa_county_xwalk,
    by = c("geo_id" = "county_geoid")
  ) %>%
  summarize_qcew(
    group_cols = c(
      "cbsa_code",
      "cbsa_name",
      "period",
      "own_code",
      "own_title",
      "industry_code",
      "industry_title",
      "code_type",
      "is_aggregate",
      "aggregate_components",
      "silver_rollup_family"
    )
  ) %>%
  transmute(
    geo_level = "cbsa",
    geo_id = cbsa_code,
    geo_name = cbsa_name,
    period,
    own_code,
    own_title,
    industry_code,
    industry_title,
    code_type,
    is_aggregate,
    aggregate_components,
    silver_rollup_family,
    annual_avg_estabs,
    annual_avg_emplvl,
    total_annual_wages,
    taxable_annual_wages,
    annual_contributions,
    annual_avg_wkly_wage,
    avg_annual_pay,
    disclosure_code,
    source = "BLS QCEW"
  )

state_qcew <- canonical_qcew_county %>%
  summarize_qcew(
    group_cols = c(
      "state_fips_code",
      "period",
      "own_code",
      "own_title",
      "industry_code",
      "industry_title",
      "code_type",
      "is_aggregate",
      "aggregate_components",
      "silver_rollup_family"
    )
  ) %>%
  left_join(
    state_ref,
    by = "state_fips_code"
  ) %>%
  transmute(
    geo_level = "state",
    geo_id = state_fips_code,
    geo_name = state_abbr,
    period,
    own_code,
    own_title,
    industry_code,
    industry_title,
    code_type,
    is_aggregate,
    aggregate_components,
    silver_rollup_family,
    annual_avg_estabs,
    annual_avg_emplvl,
    total_annual_wages,
    taxable_annual_wages,
    annual_contributions,
    annual_avg_wkly_wage,
    avg_annual_pay,
    disclosure_code,
    source = "BLS QCEW"
  )

qcew_silver <- bind_rows(
  county_qcew,
  cbsa_qcew,
  state_qcew
) %>%
  arrange(geo_level, geo_id, period, own_code, industry_code)

# 5. Validate the grain and materialize ----
qcew_dupes <- qcew_silver %>%
  count(geo_level, geo_id, period, own_code, industry_code) %>%
  filter(n > 1)

if (nrow(qcew_dupes) > 0) {
  stop("Duplicate geo-year-ownership-industry rows found in silver.bls_qcew.", call. = FALSE)
}

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "bls_qcew"),
  qcew_silver,
  overwrite = TRUE
)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
