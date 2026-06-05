# In this script we land source-faithful annual BLS QCEW rows for state and county geographies.
#
# We now use the annual singlefile download instead of the annual-by-industry ZIP bundle.
# The singlefile preserves the full annual metric payload while avoiding thousands of tiny CSV reads.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "bls", "qcew")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# 2. Define the annual ingest scope and shared lookups ----
qcew_years <- 2010:2024

state_agglvl_codes <- c("50", "51", "52", "53", "54", "55", "56", "57", "58", "96")
county_agglvl_codes <- c("70", "71", "72", "73", "74", "75", "76", "77", "78")

ownership_lookup <- tibble::tribble(
  ~own_code, ~own_title,
  "0", "Total Covered",
  "1", "Federal Government",
  "2", "State Government",
  "3", "Local Government",
  "5", "Private",
  "8", "Total Government"
)

agglvl_lookup <- tibble::tribble(
  ~agglvl_code, ~agglvl_title,
  "50", "State, Total Covered",
  "51", "State, Total -- by ownership sector",
  "52", "State, by Domain -- by ownership sector",
  "53", "State, by Supersector -- by ownership sector",
  "54", "State, NAICS Sector -- by ownership sector",
  "55", "State, NAICS 3-digit -- by ownership sector",
  "56", "State, NAICS 4-digit -- by ownership sector",
  "57", "State, NAICS 5-digit -- by ownership sector",
  "58", "State, NAICS 6-digit -- by ownership sector",
  "70", "County, Total Covered",
  "71", "County, Total -- by ownership sector",
  "72", "County, by Domain -- by ownership sector",
  "73", "County, by Supersector -- by ownership sector",
  "74", "County, NAICS Sector -- by ownership sector",
  "75", "County, NAICS 3-digit -- by ownership sector",
  "76", "County, NAICS 4-digit -- by ownership sector",
  "77", "County, NAICS 5-digit -- by ownership sector",
  "78", "County, NAICS 6-digit -- by ownership sector",
  "96", "Total Government, by State"
)

size_lookup <- tibble::tribble(
  ~size_code, ~size_title,
  "0", "All establishment sizes"
)

industry_lookup <- readr::read_csv(
  here::here("foundations", "etl", "reference", "bls_qcew_industry_map.csv"),
  show_col_types = FALSE,
  col_types = readr::cols(
    industry_code = readr::col_character(),
    industry_title = readr::col_character()
  )
) %>%
  select(industry_code, industry_title) %>%
  distinct()

county_lookup <- dbGetQuery(
  con,
  "SELECT county_geoid, county_name FROM silver.xwalk_county_state"
) %>%
  distinct()

state_lookup <- tibble::tribble(
  ~state_fips_code, ~area_title,
  "01", "Alabama -- Statewide",
  "02", "Alaska -- Statewide",
  "04", "Arizona -- Statewide",
  "05", "Arkansas -- Statewide",
  "06", "California -- Statewide",
  "08", "Colorado -- Statewide",
  "09", "Connecticut -- Statewide",
  "10", "Delaware -- Statewide",
  "11", "District of Columbia",
  "12", "Florida -- Statewide",
  "13", "Georgia -- Statewide",
  "15", "Hawaii -- Statewide",
  "16", "Idaho -- Statewide",
  "17", "Illinois -- Statewide",
  "18", "Indiana -- Statewide",
  "19", "Iowa -- Statewide",
  "20", "Kansas -- Statewide",
  "21", "Kentucky -- Statewide",
  "22", "Louisiana -- Statewide",
  "23", "Maine -- Statewide",
  "24", "Maryland -- Statewide",
  "25", "Massachusetts -- Statewide",
  "26", "Michigan -- Statewide",
  "27", "Minnesota -- Statewide",
  "28", "Mississippi -- Statewide",
  "29", "Missouri -- Statewide",
  "30", "Montana -- Statewide",
  "31", "Nebraska -- Statewide",
  "32", "Nevada -- Statewide",
  "33", "New Hampshire -- Statewide",
  "34", "New Jersey -- Statewide",
  "35", "New Mexico -- Statewide",
  "36", "New York -- Statewide",
  "37", "North Carolina -- Statewide",
  "38", "North Dakota -- Statewide",
  "39", "Ohio -- Statewide",
  "40", "Oklahoma -- Statewide",
  "41", "Oregon -- Statewide",
  "42", "Pennsylvania -- Statewide",
  "44", "Rhode Island -- Statewide",
  "45", "South Carolina -- Statewide",
  "46", "South Dakota -- Statewide",
  "47", "Tennessee -- Statewide",
  "48", "Texas -- Statewide",
  "49", "Utah -- Statewide",
  "50", "Vermont -- Statewide",
  "51", "Virginia -- Statewide",
  "53", "Washington -- Statewide",
  "54", "West Virginia -- Statewide",
  "55", "Wisconsin -- Statewide",
  "56", "Wyoming -- Statewide",
  "72", "Puerto Rico -- Statewide",
  "78", "Virgin Islands -- Statewide"
)

download_qcew_singlefile <- function(year) {
  zip_name <- glue("{year}_annual_singlefile.zip")
  zip_path <- file.path(raw_dir, zip_name)

  if (!file.exists(zip_path)) {
    zip_url <- glue("https://data.bls.gov/cew/data/files/{year}/csv/{zip_name}")

    resp <- httr::GET(
      zip_url,
      httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
    )
    httr::stop_for_status(resp)

    writeBin(httr::content(resp, "raw"), zip_path)
  }

  zip_path
}

read_qcew_singlefile <- function(zip_path, year_value) {
  member_name <- glue("{year_value}.annual.singlefile.csv")

  readr::read_csv(
    unz(zip_path, member_name),
    col_types = cols(
      area_fips = col_character(),
      own_code = col_character(),
      industry_code = col_character(),
      agglvl_code = col_character(),
      size_code = col_character(),
      year = col_integer(),
      qtr = col_character(),
      disclosure_code = col_character(),
      annual_avg_estabs = col_double(),
      annual_avg_emplvl = col_double(),
      total_annual_wages = col_double(),
      taxable_annual_wages = col_double(),
      annual_contributions = col_double(),
      annual_avg_wkly_wage = col_double(),
      avg_annual_pay = col_double(),
      lq_disclosure_code = col_character(),
      lq_annual_avg_estabs = col_double(),
      lq_annual_avg_emplvl = col_double(),
      lq_total_annual_wages = col_double(),
      lq_taxable_annual_wages = col_double(),
      lq_annual_contributions = col_double(),
      lq_annual_avg_wkly_wage = col_double(),
      lq_avg_annual_pay = col_double(),
      oty_disclosure_code = col_character(),
      oty_annual_avg_estabs_chg = col_double(),
      oty_annual_avg_estabs_pct_chg = col_double(),
      oty_annual_avg_emplvl_chg = col_double(),
      oty_annual_avg_emplvl_pct_chg = col_double(),
      oty_total_annual_wages_chg = col_double(),
      oty_total_annual_wages_pct_chg = col_double(),
      oty_taxable_annual_wages_chg = col_double(),
      oty_taxable_annual_wages_pct_chg = col_double(),
      oty_annual_contributions_chg = col_double(),
      oty_annual_contributions_pct_chg = col_double(),
      oty_annual_avg_wkly_wage_chg = col_double(),
      oty_annual_avg_wkly_wage_pct_chg = col_double(),
      oty_avg_annual_pay_chg = col_double(),
      oty_avg_annual_pay_pct_chg = col_double()
    ),
    show_col_types = FALSE,
    progress = FALSE
  )
}

# 3. Read, validate, and materialize one year at a time ----
if (DBI::dbExistsTable(con, DBI::Id(schema = "staging", table = "bls_qcew_state"))) {
  DBI::dbRemoveTable(con, DBI::Id(schema = "staging", table = "bls_qcew_state"))
}

if (DBI::dbExistsTable(con, DBI::Id(schema = "staging", table = "bls_qcew_county"))) {
  DBI::dbRemoveTable(con, DBI::Id(schema = "staging", table = "bls_qcew_county"))
}

for (year_value in qcew_years) {
  message("Processing QCEW annual singlefile for year: ", year_value)

  zip_path <- download_qcew_singlefile(year_value)

  qcew_year <- read_qcew_singlefile(zip_path, year_value) %>%
    filter(
      qtr == "A",
      size_code == "0",
      !is.na(area_fips),
      stringr::str_length(area_fips) == 5,
      agglvl_code %in% c(state_agglvl_codes, county_agglvl_codes)
    ) %>%
    mutate(
      geo_level = dplyr::if_else(
        agglvl_code %in% state_agglvl_codes,
        "state",
        "county"
      ),
      state_fips_code = stringr::str_sub(area_fips, 1, 2),
      geo_id = dplyr::if_else(geo_level == "state", state_fips_code, area_fips),
      county_fips_code = dplyr::if_else(
        geo_level == "county",
        stringr::str_sub(area_fips, 3, 5),
        NA_character_
      )
    ) %>%
    left_join(industry_lookup, by = "industry_code") %>%
    left_join(ownership_lookup, by = "own_code") %>%
    left_join(agglvl_lookup, by = "agglvl_code") %>%
    left_join(size_lookup, by = "size_code") %>%
    left_join(
      county_lookup,
      by = c("geo_id" = "county_geoid")
    ) %>%
    left_join(state_lookup, by = "state_fips_code") %>%
    mutate(
      county_name = dplyr::if_else(
        geo_level == "county",
        coalesce(county_name, "Unknown County"),
        NA_character_
      ),
      area_title = dplyr::case_when(
        geo_level == "state" ~ area_title,
        county_fips_code == "999" ~ "Unknown County",
        TRUE ~ county_name
      )
    ) %>%
    transmute(
      geo_level,
      geo_id,
      state_fips_code,
      county_fips_code,
      county_name,
      area_title,
      period = as.integer(year),
      own_code,
      own_title,
      industry_code,
      industry_title,
      agglvl_code,
      agglvl_title,
      size_code,
      size_title,
      qtr,
      disclosure_code,
      annual_avg_estabs,
      annual_avg_emplvl,
      total_annual_wages,
      taxable_annual_wages,
      annual_contributions,
      annual_avg_wkly_wage,
      avg_annual_pay,
      lq_disclosure_code,
      lq_annual_avg_estabs,
      lq_annual_avg_emplvl,
      lq_total_annual_wages,
      lq_taxable_annual_wages,
      lq_annual_contributions,
      lq_annual_avg_wkly_wage,
      lq_avg_annual_pay,
      oty_disclosure_code,
      oty_annual_avg_estabs_chg,
      oty_annual_avg_estabs_pct_chg,
      oty_annual_avg_emplvl_chg,
      oty_annual_avg_emplvl_pct_chg,
      oty_total_annual_wages_chg,
      oty_total_annual_wages_pct_chg,
      oty_taxable_annual_wages_chg,
      oty_taxable_annual_wages_pct_chg,
      oty_annual_contributions_chg,
      oty_annual_contributions_pct_chg,
      oty_annual_avg_wkly_wage_chg,
      oty_annual_avg_wkly_wage_pct_chg,
      oty_avg_annual_pay_chg,
      oty_avg_annual_pay_pct_chg,
      src = "BLS QCEW",
      version = "v3_annual_singlefile_all_members"
    )

  qcew_dupes <- qcew_year %>%
    count(
      geo_level,
      geo_id,
      period,
      own_code,
      industry_code,
      agglvl_code,
      size_code,
      qtr
    ) %>%
    filter(n > 1)

  if (nrow(qcew_dupes) > 0) {
    stop(
      sprintf("Duplicate geo-year-ownership-industry-size rows found in QCEW staging for %s.", year_value),
      call. = FALSE
    )
  }

  qcew_state <- qcew_year %>%
    filter(geo_level == "state") %>%
    arrange(geo_id, period, own_code, industry_code, agglvl_code, size_code)

  qcew_county <- qcew_year %>%
    filter(geo_level == "county") %>%
    arrange(geo_id, period, own_code, industry_code, agglvl_code, size_code)

  DBI::dbWriteTable(
    con,
    DBI::Id(schema = "staging", table = "bls_qcew_state"),
    qcew_state,
    overwrite = year_value == min(qcew_years),
    append = year_value != min(qcew_years)
  )

  DBI::dbWriteTable(
    con,
    DBI::Id(schema = "staging", table = "bls_qcew_county"),
    qcew_county,
    overwrite = year_value == min(qcew_years),
    append = year_value != min(qcew_years)
  )
}

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
