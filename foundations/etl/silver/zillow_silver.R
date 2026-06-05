# In this script we normalize Zillow market data into our Silver layer

# 1. Set up our environment
# 2. Read Zillow staging tables, crosswalks, and ACS housing weights
# 3. Standardize county and ZCTA monthly series
# 4. Rebase county series to CBSA using ACS housing-unit weights
# 5. Materialize Silver Zillow tables

# 1. Set up our environment ----
getwd()

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Helpers ----
safe_weighted_mean <- function(values, weights) {
  valid <- !is.na(values) & !is.na(weights) & weights > 0

  if (!any(valid)) {
    return(NA_real_)
  }

  stats::weighted.mean(values[valid], weights[valid])
}

check_unique_monthly_grain <- function(df, table_name) {
  dupes <- df %>%
    count(geo_level, geo_id, period, name = "row_count") %>%
    filter(row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf(
        "%s has duplicate geo_level + geo_id + period rows",
        table_name
      ),
      call. = FALSE
    )
  }
}

build_direct_zillow <- function(df, geo_level_value, geo_id_col, geo_name_col, value_col) {
  df %>%
    transmute(
      geo_level = geo_level_value,
      geo_id = as.character(.data[[geo_id_col]]),
      geo_name = as.character(.data[[geo_name_col]]),
      period = as.Date(date),
      year = as.integer(year),
      month = as.integer(month),
      !!value_col := as.double(.data[[value_col]])
    ) %>%
    filter(
      year >= 2016,
      !is.na(.data[[value_col]])
    ) %>%
    distinct()
}

build_cbsa_zillow <- function(county_df, cbsa_county_xwalk, housing_weights, value_col) {
  county_df %>%
    mutate(
      county_geoid = as.character(county_geoid),
      period = as.Date(date),
      weight_year = pmax(2012L, pmin(as.integer(year), 2024L))
    ) %>%
    left_join(
      cbsa_county_xwalk %>%
        transmute(
          county_geoid = as.character(county_geoid),
          cbsa_code = as.character(cbsa_code),
          cbsa_name = as.character(cbsa_name)
        ) %>%
        distinct(),
      by = "county_geoid"
    ) %>%
    filter(!is.na(cbsa_code), cbsa_code != "") %>%
    left_join(
      housing_weights,
      by = c("county_geoid", "weight_year")
    ) %>%
    group_by(cbsa_code, cbsa_name, period, year, month) %>%
    summarise(
      value = safe_weighted_mean(.data[[value_col]], housing_units),
      .groups = "drop"
    ) %>%
    transmute(
      geo_level = "cbsa",
      geo_id = cbsa_code,
      geo_name = cbsa_name,
      period,
      year = as.integer(year),
      month = as.integer(month),
      !!value_col := value
    ) %>%
    filter(
      year >= 2016,
      !is.na(.data[[value_col]])
    )
}

# 2. Read staging and reference tables ----
zhvi_county_stage <- dbGetQuery(con, "SELECT * FROM staging.zillow_zhvi_county")
zhvi_zip_stage <- dbGetQuery(con, "SELECT * FROM staging.zillow_zhvi_zip_code")
zori_county_stage <- dbGetQuery(con, "SELECT * FROM staging.zillow_zori_county")
zori_zip_stage <- dbGetQuery(con, "SELECT * FROM staging.zillow_zori_zip_code")

cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")

housing_weights <- dbGetQuery(
  con,
  "
  SELECT
    geo_id AS county_geoid,
    year,
    hu_totalE AS housing_units
  FROM silver.housing_base
  WHERE geo_level = 'county'
  "
) %>%
  transmute(
    county_geoid = as.character(county_geoid),
    weight_year = as.integer(year),
    housing_units = as.double(housing_units)
  )

# 3. Standardize direct county and ZCTA series ----
zhvi_county <- build_direct_zillow(
  df = zhvi_county_stage,
  geo_level_value = "county",
  geo_id_col = "county_geoid",
  geo_name_col = "county_name",
  value_col = "zhvi"
)

zhvi_zcta <- build_direct_zillow(
  df = zhvi_zip_stage %>%
    mutate(
      zip_code = stringr::str_pad(as.character(zip_code), width = 5, side = "left", pad = "0"),
      zip_name = paste("ZIP Code", zip_code)
    ),
  geo_level_value = "zcta",
  geo_id_col = "zip_code",
  geo_name_col = "zip_name",
  value_col = "zhvi"
)

zori_county <- build_direct_zillow(
  df = zori_county_stage,
  geo_level_value = "county",
  geo_id_col = "county_geoid",
  geo_name_col = "county_name",
  value_col = "zori"
)

zori_zcta <- build_direct_zillow(
  df = zori_zip_stage %>%
    mutate(
      zip_code = stringr::str_pad(as.character(zip_code), width = 5, side = "left", pad = "0"),
      zip_name = paste("ZIP Code", zip_code)
    ),
  geo_level_value = "zcta",
  geo_id_col = "zip_code",
  geo_name_col = "zip_name",
  value_col = "zori"
)

# 4. Rebase county series to CBSA using ACS housing-unit weights ----
# Zillow does not ship a clean CBSA table with stable CBSA codes in staging, so we
# roll counties into CBSAs using the county->CBSA crosswalk. Housing-unit weights
# come from silver.housing_base; for Zillow months in 2025 and 2026 we reuse the
# latest available ACS 2024 county housing totals, per the approved Track 1.4 rule.
# We also trim Silver to the last 10 calendar years and drop null-value rows so
# this layer stays compact and analysis-ready rather than preserving a dense panel.
zhvi_cbsa <- build_cbsa_zillow(
  county_df = zhvi_county_stage,
  cbsa_county_xwalk = cbsa_county_xwalk,
  housing_weights = housing_weights,
  value_col = "zhvi"
)

zori_cbsa <- build_cbsa_zillow(
  county_df = zori_county_stage,
  cbsa_county_xwalk = cbsa_county_xwalk,
  housing_weights = housing_weights,
  value_col = "zori"
)

zillow_zhvi <- bind_rows(
  zhvi_county,
  zhvi_zcta,
  zhvi_cbsa
) %>%
  arrange(geo_level, geo_id, period)

zillow_zori <- bind_rows(
  zori_county,
  zori_zcta,
  zori_cbsa
) %>%
  arrange(geo_level, geo_id, period)

check_unique_monthly_grain(zillow_zhvi, "silver.zillow_zhvi")
check_unique_monthly_grain(zillow_zori, "silver.zillow_zori")

# 5. Materialize to Silver ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "zillow_zhvi"),
  zillow_zhvi,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "zillow_zori"),
  zillow_zori,
  overwrite = TRUE
)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
