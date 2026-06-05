# In this script we normalize FHFA annual HPI staging rows into one Silver table.
#
# First-pass Silver scope keeps the geographies that are immediately useful for
# market comparisons and Gold joins: U.S., state, CBSA, county, and ZIP5-as-ZCTA.
# Tract rows remain available in staging for future expansion once we decide that
# the heavier tract grain is worth including in the analytical contract.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Helpers ----
safe_growth <- function(current_value, prior_value) {
  dplyr::if_else(
    !is.na(prior_value) & prior_value > 0,
    (current_value - prior_value) / prior_value,
    NA_real_
  )
}

check_unique_annual_grain <- function(df, table_name) {
  dupes <- df %>%
    count(geo_level, geo_id, year, name = "row_count") %>%
    filter(row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf(
        "%s has duplicate geo_level + geo_id + year rows",
        table_name
      ),
      call. = FALSE
    )
  }
}

# 3. Read staging and crosswalks ----
fhfa_us_stage <- dbGetQuery(con, "SELECT * FROM staging.fhfa_hpi_us")
fhfa_state_stage <- dbGetQuery(con, "SELECT * FROM staging.fhfa_hpi_state")
fhfa_cbsa_stage <- dbGetQuery(con, "SELECT * FROM staging.fhfa_hpi_cbsa")
fhfa_county_stage <- dbGetQuery(con, "SELECT * FROM staging.fhfa_hpi_county")
fhfa_zip5_stage <- dbGetQuery(con, "SELECT * FROM staging.fhfa_hpi_zip5")

cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county") %>%
  transmute(
    cbsa_code = as.character(cbsa_code),
    cbsa_name = as.character(cbsa_name)
  ) %>%
  distinct()

county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state") %>%
  transmute(
    county_geoid = as.character(county_geoid),
    county_name_long = as.character(county_name_long)
  ) %>%
  distinct()

# 4. Standardize each geography slice ----
fhfa_us <- fhfa_us_stage %>%
  transmute(
    geo_level = "us",
    geo_id = "US",
    geo_name = "United States",
    year = as.integer(yr),
    hpi_level = as.double(hpi)
  )

fhfa_state <- fhfa_state_stage %>%
  transmute(
    geo_level = "state",
    geo_id = as.character(state_fips),
    geo_name = as.character(state_name),
    year = as.integer(yr),
    hpi_level = as.double(hpi)
  )

# The FHFA CBSA annual file includes non-CBSA residual rows such as state nonmetro
# slices with short pseudo-codes. First-pass Silver keeps only true 5-digit CBSA rows.
fhfa_cbsa <- fhfa_cbsa_stage %>%
  mutate(place_id = as.character(place_id)) %>%
  filter(stringr::str_detect(place_id, "^\\d{5}$")) %>%
  left_join(
    cbsa_county_xwalk,
    by = c("place_id" = "cbsa_code")
  ) %>%
  transmute(
    geo_level = "cbsa",
    geo_id = place_id,
    geo_name = coalesce(cbsa_name, as.character(place_name)),
    year = as.integer(yr),
    hpi_level = as.double(hpi)
  )

fhfa_county <- fhfa_county_stage %>%
  mutate(place_id = as.character(place_id)) %>%
  left_join(
    county_state_xwalk,
    by = c("place_id" = "county_geoid")
  ) %>%
  transmute(
    geo_level = "county",
    geo_id = place_id,
    geo_name = coalesce(county_name_long, as.character(place_name)),
    year = as.integer(yr),
    hpi_level = as.double(hpi)
  )

# We are intentionally using FHFA ZIP5 as a ZCTA proxy in the first-pass Silver contract.
fhfa_zcta <- fhfa_zip5_stage %>%
  mutate(place_id = stringr::str_pad(as.character(place_id), width = 5, side = "left", pad = "0")) %>%
  transmute(
    geo_level = "zcta",
    geo_id = place_id,
    geo_name = paste("ZIP Code", place_id),
    year = as.integer(yr),
    hpi_level = as.double(hpi)
  )

# 5. Combine and compute growth metrics ----
fhfa_hpi_base <- bind_rows(
  fhfa_us,
  fhfa_state,
  fhfa_cbsa,
  fhfa_county,
  fhfa_zcta
) %>%
  filter(
    !is.na(geo_id),
    !is.na(geo_name),
    !is.na(year),
    !is.na(hpi_level)
  ) %>%
  distinct() %>%
  arrange(geo_level, geo_id, year)

fhfa_hpi <- fhfa_hpi_base %>%
  left_join(
    fhfa_hpi_base %>%
      transmute(
        geo_level,
        geo_id,
        year = year + 1L,
        hpi_level_lag1 = hpi_level
      ),
    by = c("geo_level", "geo_id", "year")
  ) %>%
  left_join(
    fhfa_hpi_base %>%
      transmute(
        geo_level,
        geo_id,
        year = year + 5L,
        hpi_level_lag5 = hpi_level
      ),
    by = c("geo_level", "geo_id", "year")
  ) %>%
  left_join(
    fhfa_hpi_base %>%
      transmute(
        geo_level,
        geo_id,
        year = year + 10L,
        hpi_level_lag10 = hpi_level
      ),
    by = c("geo_level", "geo_id", "year")
  ) %>%
  mutate(
    hpi_yoy_pct = safe_growth(hpi_level, hpi_level_lag1),
    hpi_5yr_pct = safe_growth(hpi_level, hpi_level_lag5),
    hpi_10yr_pct = safe_growth(hpi_level, hpi_level_lag10)
  ) %>%
  select(
    geo_level,
    geo_id,
    geo_name,
    year,
    hpi_level,
    hpi_yoy_pct,
    hpi_5yr_pct,
    hpi_10yr_pct
  )

check_unique_annual_grain(fhfa_hpi, "silver.fhfa_hpi")

# 6. Materialize to Silver ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "fhfa_hpi"),
  fhfa_hpi,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
