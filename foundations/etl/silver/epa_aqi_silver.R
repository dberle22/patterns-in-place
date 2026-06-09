# In this script we normalize EPA AQI staging rows into one Silver table at the
# canonical `geo_level + geo_id + year` grain. County rows keep EPA's source
# coverage but are assigned normalized county GEOIDs through a name-based
# crosswalk. CBSA rows use the source-published CBSA code directly.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Helpers ----
normalize_text_key <- function(x) {
  x %>%
    enc2utf8() %>%
    stringi::stri_trans_general("Latin-ASCII") %>%
    stringr::str_to_upper() %>%
    stringr::str_replace_all("&", " AND ") %>%
    stringr::str_replace_all("[^A-Z0-9 ]", " ") %>%
    stringr::str_replace_all("\\bSAINTE\\b", "ST") %>%
    stringr::str_replace_all("\\bSAINT\\b", "ST") %>%
    stringr::str_squish()
}

normalize_county_key <- function(x) {
  normalize_text_key(x) %>%
    stringr::str_remove("\\s+(COUNTY|PARISH|BOROUGH|CENSUS AREA|CITY AND BOROUGH|MUNICIPALITY|MUNICIPIO|ISLAND)$") %>%
    stringr::str_squish()
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

# 3. Read staging slices and reference geographies ----
epa_aqi_county_stage <- DBI::dbGetQuery(
  con,
  "SELECT * FROM staging.epa_aqi WHERE geo_level = 'county'"
) %>%
  mutate(
    state_name = as.character(state_name),
    county_name = as.character(county_name)
  )

epa_aqi_cbsa_stage <- DBI::dbGetQuery(
  con,
  "SELECT * FROM staging.epa_aqi WHERE geo_level = 'cbsa'"
) %>%
  mutate(
    cbsa_code = as.character(cbsa_code),
    cbsa_name = as.character(cbsa_name)
  )

county_state_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state") %>%
  transmute(
    state_fips = as.character(state_fip),
    county_fips = as.character(county_fip),
    county_geoid = as.character(county_geoid),
    county_name = as.character(county_name),
    county_name_long = as.character(county_name_long),
    state_abbr = as.character(state_abbr),
    lsad = as.character(lsad)
  ) %>%
  distinct()

state_lookup <- DBI::dbGetQuery(con, "SELECT DISTINCT state_fips, state_name FROM silver.xwalk_cbsa_county") %>%
  transmute(
    state_fips = as.character(state_fips),
    state_name = as.character(state_name)
  ) %>%
  distinct() %>%
  bind_rows(
    tibble::tribble(
      ~state_fips, ~state_name,
      "11", "District of Columbia",
      "72", "Puerto Rico",
      "78", "Virgin Islands"
    )
  ) %>%
  distinct(state_fips, .keep_all = TRUE)

county_lookup <- county_state_xwalk %>%
  left_join(state_lookup, by = "state_fips") %>%
  mutate(
    norm_state_name = normalize_text_key(state_name),
    norm_county_name_short = normalize_county_key(county_name),
    norm_county_name_long = normalize_county_key(county_name_long),
    is_independent_city = lsad == "25"
  ) %>%
  select(
    county_geoid,
    county_name_long,
    state_abbr,
    state_name,
    norm_state_name,
    norm_county_name_short,
    norm_county_name_long,
    is_independent_city
  ) %>%
  distinct()

county_lookup_long <- county_lookup %>%
  transmute(
    norm_state_name,
    norm_county_name = norm_county_name_long,
    county_geoid,
    county_name_long,
    state_abbr
  ) %>%
  filter(!is.na(norm_county_name), norm_county_name != "") %>%
  distinct()

county_lookup_short <- county_lookup %>%
  arrange(is_independent_city) %>%
  transmute(
    norm_state_name,
    norm_county_name = norm_county_name_short,
    county_geoid,
    county_name_long,
    state_abbr,
    is_independent_city
  ) %>%
  filter(!is.na(norm_county_name), norm_county_name != "") %>%
  group_by(norm_state_name, norm_county_name) %>%
  slice(1) %>%
  ungroup() %>%
  select(-is_independent_city) %>%
  distinct()

county_lookup_manual <- tibble::tribble(
  ~norm_state_name, ~norm_county_name, ~county_geoid, ~county_name_long, ~state_abbr,
  "CONNECTICUT", "FAIRFIELD", "09001", "Fairfield County, CT", "CT",
  "CONNECTICUT", "HARTFORD", "09003", "Hartford County, CT", "CT",
  "CONNECTICUT", "LITCHFIELD", "09005", "Litchfield County, CT", "CT",
  "CONNECTICUT", "MIDDLESEX", "09007", "Middlesex County, CT", "CT",
  "CONNECTICUT", "NEW HAVEN", "09009", "New Haven County, CT", "CT",
  "CONNECTICUT", "NEW LONDON", "09011", "New London County, CT", "CT",
  "CONNECTICUT", "TOLLAND", "09013", "Tolland County, CT", "CT",
  "CONNECTICUT", "WINDHAM", "09015", "Windham County, CT", "CT",
  "PUERTO RICO", "MAYAGNEZ", "72097", "Mayaguez Municipio", "PR",
  "VIRGINIA", "CHARLES", "51036", "Charles City County", "VA"
)

cbsa_lookup <- DBI::dbGetQuery(con, "SELECT DISTINCT cbsa_code, cbsa_name FROM silver.xwalk_cbsa_county") %>%
  transmute(
    cbsa_code = stringr::str_pad(as.character(cbsa_code), width = 5, side = "left", pad = "0"),
    cbsa_name = as.character(cbsa_name)
  ) %>%
  distinct()

# 4. Normalize county and CBSA rows ----
epa_aqi_county_joined <- epa_aqi_county_stage %>%
  filter(state_name != "Country Of Mexico") %>%
  mutate(
    norm_state_name = normalize_text_key(state_name),
    norm_county_name = normalize_county_key(county_name)
  ) %>%
  left_join(
    county_lookup_long,
    by = c("norm_state_name", "norm_county_name")
  ) %>%
  rename(
    county_geoid_long = county_geoid,
    county_name_long_long = county_name_long,
    state_abbr_long = state_abbr
  ) %>%
  left_join(
    county_lookup_short,
    by = c("norm_state_name", "norm_county_name")
  ) %>%
  rename(
    county_geoid_short = county_geoid,
    county_name_long_short = county_name_long,
    state_abbr_short = state_abbr
  ) %>%
  left_join(
    county_lookup_manual,
    by = c("norm_state_name", "norm_county_name")
  ) %>%
  transmute(
    source_state_name = state_name,
    source_county_name = county_name,
    geo_level = "county",
    geo_id = dplyr::coalesce(
      county_geoid_long,
      county_geoid_short,
      county_geoid
    ),
    geo_name = dplyr::coalesce(
      county_name_long_long,
      county_name_long_short,
      county_name_long,
      dplyr::if_else(
        !is.na(county_name) & !is.na(dplyr::coalesce(state_abbr_long, state_abbr_short, state_abbr)),
        paste0(county_name, " County, ", dplyr::coalesce(state_abbr_long, state_abbr_short, state_abbr)),
        county_name
      )
    ),
    year = as.integer(year),
    days_with_aqi = as.integer(days_with_aqi),
    good_days = as.integer(good_days),
    moderate_days = as.integer(moderate_days),
    usg_days = as.integer(usg_days),
    unhealthy_days = as.integer(unhealthy_days),
    very_unhealthy_days = as.integer(very_unhealthy_days),
    hazardous_days = as.integer(hazardous_days),
    max_aqi = as.integer(max_aqi),
    aqi_p90 = as.double(aqi_p90),
    aqi_median = as.double(aqi_median),
    days_ozone = as.integer(days_ozone),
    days_pm25 = as.integer(days_pm25)
  )

unmatched_counties <- epa_aqi_county_joined %>%
  filter(is.na(geo_id))

if (nrow(unmatched_counties) > 0) {
  warning(
    sprintf(
      "Dropping %s county rows from silver.epa_aqi because they could not be matched to a canonical county GEOID after normalization.",
      nrow(unmatched_counties)
    ),
    call. = FALSE
  )
}

epa_aqi_county <- epa_aqi_county_joined %>%
  filter(!is.na(geo_id)) %>%
  select(
    -source_state_name,
    -source_county_name
  )

epa_aqi_cbsa <- epa_aqi_cbsa_stage %>%
  mutate(
    cbsa_code = stringr::str_pad(cbsa_code, width = 5, side = "left", pad = "0")
  ) %>%
  left_join(
    cbsa_lookup,
    by = "cbsa_code"
  ) %>%
  transmute(
    geo_level = "cbsa",
    geo_id = cbsa_code,
    geo_name = dplyr::coalesce(cbsa_name.y, cbsa_name.x),
    year = as.integer(year),
    days_with_aqi = as.integer(days_with_aqi),
    good_days = as.integer(good_days),
    moderate_days = as.integer(moderate_days),
    usg_days = as.integer(usg_days),
    unhealthy_days = as.integer(unhealthy_days),
    very_unhealthy_days = as.integer(very_unhealthy_days),
    hazardous_days = as.integer(hazardous_days),
    max_aqi = as.integer(max_aqi),
    aqi_p90 = as.double(aqi_p90),
    aqi_median = as.double(aqi_median),
    days_ozone = as.integer(days_ozone),
    days_pm25 = as.integer(days_pm25)
  )

# 5. Row-bind the normalized geography slices and materialize Silver ----
epa_aqi <- bind_rows(
  epa_aqi_county,
  epa_aqi_cbsa
) %>%
  filter(
    !is.na(geo_id),
    !is.na(geo_name),
    !is.na(year)
  ) %>%
  distinct() %>%
  arrange(geo_level, geo_id, year)

check_unique_annual_grain(epa_aqi, "silver.epa_aqi")

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "epa_aqi"),
  epa_aqi,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
