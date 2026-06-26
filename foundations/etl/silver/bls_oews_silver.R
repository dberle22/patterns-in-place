# In this script we turn the staged OEWS state and metro workbooks into the
# first managed Silver occupation table for Foundations.
#
# The current first pass intentionally keeps only state and metro rows from the
# 2025 cross-industry release, preserves both detailed and major-group SOC rows,
# and parses the note-marked estimate fields carefully so we do not silently
# turn suppression or top-coding markers into real numeric values.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")
data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "bls", "oews")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

download_stem_workbook <- function() {
  stem_path <- file.path(raw_dir, "stem_2025.xlsx")

  if (!file.exists(stem_path)) {
    response <- httr::GET(
      "https://www.bls.gov/oes/special-requests/stem_2025.xlsx",
      httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
    )
    httr::stop_for_status(response)
    writeBin(httr::content(response, "raw"), stem_path)
  }

  stem_path
}

read_stem_codes <- function(stem_path) {
  stem_raw <- readxl::read_xlsx(
    stem_path,
    sheet = "STEM occupations list",
    skip = 4,
    col_names = c("soc_code", "soc_title"),
    col_types = "text"
  ) %>%
    janitor::clean_names()

  stem_raw %>%
    transmute(soc_code = stringr::str_trim(as.character(.data$soc_code))) %>%
    filter(!is.na(.data$soc_code), .data$soc_code != "") %>%
    distinct()
}

parse_oews_numeric <- function(x) {
  x %>%
    stringr::str_trim() %>%
    dplyr::na_if("") %>%
    dplyr::na_if("*") %>%
    dplyr::na_if("**") %>%
    dplyr::na_if("#") %>%
    dplyr::na_if("~") %>%
    stringr::str_replace_all(",", "") %>%
    as.numeric()
}

state_ref <- tibble::tribble(
  ~state_fips, ~state_abbr, ~state_name,
  "01", "AL", "Alabama",
  "02", "AK", "Alaska",
  "04", "AZ", "Arizona",
  "05", "AR", "Arkansas",
  "06", "CA", "California",
  "08", "CO", "Colorado",
  "09", "CT", "Connecticut",
  "10", "DE", "Delaware",
  "11", "DC", "District of Columbia",
  "12", "FL", "Florida",
  "13", "GA", "Georgia",
  "15", "HI", "Hawaii",
  "16", "ID", "Idaho",
  "17", "IL", "Illinois",
  "18", "IN", "Indiana",
  "19", "IA", "Iowa",
  "20", "KS", "Kansas",
  "21", "KY", "Kentucky",
  "22", "LA", "Louisiana",
  "23", "ME", "Maine",
  "24", "MD", "Maryland",
  "25", "MA", "Massachusetts",
  "26", "MI", "Michigan",
  "27", "MN", "Minnesota",
  "28", "MS", "Mississippi",
  "29", "MO", "Missouri",
  "30", "MT", "Montana",
  "31", "NE", "Nebraska",
  "32", "NV", "Nevada",
  "33", "NH", "New Hampshire",
  "34", "NJ", "New Jersey",
  "35", "NM", "New Mexico",
  "36", "NY", "New York",
  "37", "NC", "North Carolina",
  "38", "ND", "North Dakota",
  "39", "OH", "Ohio",
  "40", "OK", "Oklahoma",
  "41", "OR", "Oregon",
  "42", "PA", "Pennsylvania",
  "44", "RI", "Rhode Island",
  "45", "SC", "South Carolina",
  "46", "SD", "South Dakota",
  "47", "TN", "Tennessee",
  "48", "TX", "Texas",
  "49", "UT", "Utah",
  "50", "VT", "Vermont",
  "51", "VA", "Virginia",
  "53", "WA", "Washington",
  "54", "WV", "West Virginia",
  "55", "WI", "Wisconsin",
  "56", "WY", "Wyoming"
)

soc_major_group_ref <- tibble::tribble(
  ~soc_major_group, ~soc_major_group_title,
  "00", "All Occupations",
  "11", "Management Occupations",
  "13", "Business and Financial Operations Occupations",
  "15", "Computer and Mathematical Occupations",
  "17", "Architecture and Engineering Occupations",
  "19", "Life, Physical, and Social Science Occupations",
  "21", "Community and Social Service Occupations",
  "23", "Legal Occupations",
  "25", "Educational Instruction and Library Occupations",
  "27", "Arts, Design, Entertainment, Sports, and Media Occupations",
  "29", "Healthcare Practitioners and Technical Occupations",
  "31", "Healthcare Support Occupations",
  "33", "Protective Service Occupations",
  "35", "Food Preparation and Serving Related Occupations",
  "37", "Building and Grounds Cleaning and Maintenance Occupations",
  "39", "Personal Care and Service Occupations",
  "41", "Sales and Related Occupations",
  "43", "Office and Administrative Support Occupations",
  "45", "Farming, Fishing, and Forestry Occupations",
  "47", "Construction and Extraction Occupations",
  "49", "Installation, Maintenance, and Repair Occupations",
  "51", "Production Occupations",
  "53", "Transportation and Material Moving Occupations"
)

occupation_bucket_ref <- tibble::tribble(
  ~soc_major_group, ~occupation_bucket,
  "11", "management_professional",
  "13", "management_professional",
  "15", "management_professional",
  "17", "management_professional",
  "19", "management_professional",
  "23", "management_professional",
  "27", "management_professional",
  "29", "management_professional",
  "21", "service",
  "31", "service",
  "33", "service",
  "35", "service",
  "37", "service",
  "39", "service",
  "45", "production_transportation",
  "47", "production_transportation",
  "49", "production_transportation",
  "51", "production_transportation",
  "53", "production_transportation",
  "25", "other",
  "41", "other",
  "43", "other",
  "00", "other"
)

stem_codes <- read_stem_codes(download_stem_workbook()) %>%
  mutate(is_stem = TRUE)

state_rows <- DBI::dbGetQuery(
  con,
  "
  SELECT *
  FROM staging.bls_oews_state
  WHERE
    source_area_scope = 'state'
    AND area_type = '2'
    AND naics = '000000'
  "
) %>%
  mutate(
    geo_level = "state",
    geo_id = as.character(.data$area),
    geo_name = as.character(.data$prim_state),
    year = as.integer(.data$release_year),
    source_area_code = as.character(.data$area),
    source_area_title = as.character(.data$area_title)
  ) %>%
  left_join(state_ref, by = c("geo_id" = "state_fips"))

metro_rows <- DBI::dbGetQuery(
  con,
  "
  SELECT *
  FROM staging.bls_oews_metro_nonmetro
  WHERE
    source_area_scope = 'metro'
    AND area_type = '4'
    AND naics = '000000'
  "
) %>%
  mutate(
    geo_level = "cbsa",
    geo_id = as.character(.data$area),
    geo_name = as.character(.data$area_title),
    year = as.integer(.data$release_year),
    source_area_code = as.character(.data$area),
    source_area_title = as.character(.data$area_title),
    state_fips = NA_character_,
    state_name = NA_character_,
    state_abbr = NA_character_
  )

oews_silver <- bind_rows(state_rows, metro_rows) %>%
  mutate(
    soc_code = as.character(.data$occ_code),
    soc_title = as.character(.data$occ_title),
    soc_major_group = stringr::str_sub(.data$soc_code, 1, 2),
    is_total_occupation = .data$o_group == "total",
    is_major_group = .data$o_group == "major",
    employment_not_released = .data$tot_emp == "**",
    any_wage_not_available = dplyr::if_else(
      .data$h_mean == "*" |
        .data$a_mean == "*" |
        .data$h_pct10 == "*" |
        .data$h_pct25 == "*" |
        .data$h_median == "*" |
        .data$h_pct75 == "*" |
        .data$h_pct90 == "*" |
        .data$a_pct10 == "*" |
        .data$a_pct25 == "*" |
        .data$a_median == "*" |
        .data$a_pct75 == "*" |
        .data$a_pct90 == "*",
      TRUE,
      FALSE,
      missing = FALSE
    ),
    any_wage_topcoded = dplyr::if_else(
      .data$h_mean == "#" |
        .data$a_mean == "#" |
        .data$h_pct10 == "#" |
        .data$h_pct25 == "#" |
        .data$h_median == "#" |
        .data$h_pct75 == "#" |
        .data$h_pct90 == "#" |
        .data$a_pct10 == "#" |
        .data$a_pct25 == "#" |
        .data$a_median == "#" |
        .data$a_pct75 == "#" |
        .data$a_pct90 == "#",
      TRUE,
      FALSE,
      missing = FALSE
    ),
    employment = parse_oews_numeric(.data$tot_emp),
    employment_prse_pct = parse_oews_numeric(.data$emp_prse),
    jobs_per_1000 = parse_oews_numeric(.data$jobs_1000),
    location_quotient = parse_oews_numeric(.data$loc_quotient),
    hourly_mean_wage = parse_oews_numeric(.data$h_mean),
    annual_mean_wage = parse_oews_numeric(.data$a_mean),
    mean_wage_prse_pct = parse_oews_numeric(.data$mean_prse),
    hourly_p10_wage = parse_oews_numeric(.data$h_pct10),
    hourly_p25_wage = parse_oews_numeric(.data$h_pct25),
    hourly_median_wage = parse_oews_numeric(.data$h_median),
    hourly_p75_wage = parse_oews_numeric(.data$h_pct75),
    hourly_p90_wage = parse_oews_numeric(.data$h_pct90),
    annual_p10_wage = parse_oews_numeric(.data$a_pct10),
    annual_p25_wage = parse_oews_numeric(.data$a_pct25),
    annual_median_wage = parse_oews_numeric(.data$a_median),
    annual_p75_wage = parse_oews_numeric(.data$a_pct75),
    annual_p90_wage = parse_oews_numeric(.data$a_pct90),
    annual_note = dplyr::if_else(is.na(.data$annual), NA_character_, as.character(.data$annual)),
    hourly_note = dplyr::if_else(is.na(.data$hourly), NA_character_, as.character(.data$hourly)),
    source_workbook = as.character(.data$source_workbook)
  ) %>%
  left_join(soc_major_group_ref, by = "soc_major_group") %>%
  left_join(occupation_bucket_ref, by = "soc_major_group") %>%
  left_join(stem_codes, by = "soc_code") %>%
  mutate(
    is_stem = dplyr::coalesce(.data$is_stem, FALSE),
    source = "BLS OEWS"
  ) %>%
  select(
    .data$geo_level,
    .data$geo_id,
    .data$geo_name,
    .data$state_fips,
    .data$state_abbr,
    .data$state_name,
    .data$year,
    .data$soc_code,
    .data$soc_title,
    .data$soc_major_group,
    .data$soc_major_group_title,
    .data$o_group,
    .data$occupation_bucket,
    .data$is_stem,
    .data$is_total_occupation,
    .data$is_major_group,
    .data$employment,
    .data$employment_prse_pct,
    .data$jobs_per_1000,
    .data$location_quotient,
    .data$hourly_mean_wage,
    .data$annual_mean_wage,
    .data$mean_wage_prse_pct,
    .data$hourly_p10_wage,
    .data$hourly_p25_wage,
    .data$hourly_median_wage,
    .data$hourly_p75_wage,
    .data$hourly_p90_wage,
    .data$annual_p10_wage,
    .data$annual_p25_wage,
    .data$annual_median_wage,
    .data$annual_p75_wage,
    .data$annual_p90_wage,
    .data$annual_note,
    .data$hourly_note,
    .data$employment_not_released,
    .data$any_wage_not_available,
    .data$any_wage_topcoded,
    .data$source_area_code,
    .data$source_area_title,
    .data$source_workbook,
    .data$source
  )

duplicate_keys <- oews_silver %>%
  count(.data$geo_level, .data$geo_id, .data$year, .data$soc_code, name = "row_count") %>%
  filter(.data$row_count > 1)

if (nrow(duplicate_keys) > 0) {
  stop("silver.bls_oews key is not unique at geo_level + geo_id + year + soc_code.", call. = FALSE)
}

if (DBI::dbExistsTable(con, DBI::Id(schema = "silver", table = "bls_oews"))) {
  DBI::dbRemoveTable(con, DBI::Id(schema = "silver", table = "bls_oews"))
}

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "bls_oews"),
  oews_silver,
  overwrite = TRUE
)

message("Loaded silver.bls_oews")
print(
  oews_silver %>%
    count(.data$geo_level, name = "rows")
)
print(
  oews_silver %>%
    summarise(
      rows = n(),
      distinct_geo = n_distinct(paste(.data$geo_level, .data$geo_id, sep = "|")),
      distinct_soc = n_distinct(.data$soc_code),
      stem_rows = sum(.data$is_stem, na.rm = TRUE)
    )
)

DBI::dbDisconnect(con, shutdown = TRUE)
