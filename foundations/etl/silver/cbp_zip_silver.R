# In this script we normalize the latest-year CBP ZIP industry-detail staging
# table into a curated ZIP-native Silver table.
#
# 1. Read the staged ZIP detail rows.
# 2. Keep the all-sectors row plus the published broad sector rows that align
#    to our existing Gold industry families.
# 3. Standardize the ZIP rows without forcing a ZIP -> ZCTA reconciliation yet.
# 4. Materialize one long `silver.cbp_zip` analytical table.

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

cbp_zip_stage <- DBI::dbGetQuery(
  con,
  "SELECT * FROM staging.cbp_zip_detail"
) %>%
  mutate(
    year = as.integer(.data$year),
    zip_code = as.character(.data$zip_code),
    zip_name = as.character(.data$zip_name),
    naics_code = as.character(.data$naics_code),
    city = as.character(.data$city),
    state_abbr = as.character(.data$state_abbr),
    county_name = as.character(.data$county_name)
  ) %>%
  filter(.data$naics_code %in% canonical_codes) %>%
  left_join(cbp_industry_map, by = c("naics_code" = "industry_code"))

cbp_zip <- cbp_zip_stage %>%
  transmute(
    geo_level = "zip",
    geo_id = .data$zip_code,
    geo_name = coalesce(.data$zip_name, .data$zip_code),
    period = .data$year,
    zip_code = .data$zip_code,
    zip_name = .data$zip_name,
    city = .data$city,
    state_abbr = .data$state_abbr,
    county_name = .data$county_name,
    industry_code = .data$naics_code,
    industry_title = .data$industry_title,
    silver_rollup_family = .data$silver_rollup_family,
    is_total_row = .data$is_total_row,
    establishments = as.double(.data$establishments),
    est_n_lt_5 = as.double(.data$est_n_lt_5),
    est_n_5_9 = as.double(.data$est_n_5_9),
    est_n_10_19 = as.double(.data$est_n_10_19),
    est_n_20_49 = as.double(.data$est_n_20_49),
    est_n_50_99 = as.double(.data$est_n_50_99),
    est_n_100_249 = as.double(.data$est_n_100_249),
    est_n_250_499 = as.double(.data$est_n_250_499),
    est_n_500_999 = as.double(.data$est_n_500_999),
    est_n_1000_plus = as.double(.data$est_n_1000_plus),
    source = "Census CBP ZIP Detail"
  ) %>%
  arrange(.data$geo_id, .data$period, .data$industry_code)

check_unique_annual_grain(cbp_zip, "silver.cbp_zip")

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "cbp_zip"),
  cbp_zip,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
