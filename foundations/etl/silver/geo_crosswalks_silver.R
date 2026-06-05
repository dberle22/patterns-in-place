# In this script we get our ACS Raw data

# Find our current directory 
getwd()

# Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
bronze_acs <- get_env_path("DATA_DEMO_RAW")
data <- get_env_path("DATA")
db_path <- get_env_path("DB_PATH")

# Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

resolve_tract_state_scope <- function(env_var = "ROF_TRACT_STATE_SCOPE") {
  raw_value <- Sys.getenv(env_var, unset = "")
  if (!nzchar(raw_value)) {
    return(c(state.abb, "DC"))
  }

  states <- raw_value %>%
    stringr::str_split(",") %>%
    purrr::pluck(1) %>%
    stringr::str_trim() %>%
    toupper() %>%
    unique()

  valid_states <- c(state.abb, "DC")
  invalid_states <- setdiff(states, valid_states)
  if (length(invalid_states) > 0) {
    stop(
      sprintf(
        "Invalid %s values: %s",
        env_var,
        paste(invalid_states, collapse = ", ")
      ),
      call. = FALSE
    )
  }

  states
}

# CBSA <> County ---- 
# Read in Raw File
cbsa_county_xwalk_raw <- read_excel(paste0(data, "/demographics/raw/crosswalks/cbsa_county_xwalk_census.xlsx"),
                                skip = 2)
# Standardize Names
cbsa_county_xwalk_clean <- cbsa_county_xwalk_raw %>%
  select(
    cbsa_code      = `CBSA Code`,
    cbsa_name      = `CBSA Title`,
    csa_code       = `CSA Code`,
    csa_name       = `CSA Title`,
    cbsa_type      = `Metropolitan/Micropolitan Statistical Area`,
    county_name    = `County/County Equivalent`,
    state_name     = `State Name`,
    state_fips     = `FIPS State Code`,
    county_fips    = `FIPS County Code`,
    county_flag    = `Central/Outlying County`
  ) %>%
  filter(!is.na(cbsa_name)) %>%
  mutate(
    cbsa_code   = as.character(cbsa_code),
    csa_code    = as.character(csa_code),
    county_geoid = sprintf("%02d%03d", as.integer(state_fips), as.integer(county_fips)),
    vintage     = 2023L,
    source      = "OMB_2023"
  )

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_cbsa_county"),
                  cbsa_county_xwalk_clean, overwrite = TRUE)

# CBSA Primary City ----
# Read in Raw File
cbsa_primary_city_xwalk_raw <- read_excel(paste0(data, "/demographics/raw/crosswalks/cbsa_primary_city_xwalk_census.xlsx"),
                                    skip = 2)

# Standardize Names
cbsa_city_clean <- cbsa_primary_city_xwalk_raw %>%
  select(cbsa_code = `CBSA Code`,
         cbsa_name = `CBSA Title`,
         cbsa_type      = `Metropolitan/Micropolitan Statistical Area`,
         primary_city = `Principal City Name`,
         state_fips = `FIPS State Code`,
         place_fips = `FIPS Place Code`) %>%
  mutate(vintage = 2023L, source = "OMB_2023") %>%
  filter(!is.na(cbsa_name))

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_cbsa_primary_city"),
                  cbsa_city_clean, overwrite = TRUE)

# Tract <> County ----
# Default target is a national 50-state + DC tract backbone.
# Set ROF_TRACT_STATE_SCOPE="FL,GA,NC" (comma-separated) to build a narrower slice.
tract_state_scope <- resolve_tract_state_scope()

# Ingest from Tigris
tracts_2023 <- tigris::tracts(year = 2023, cb = TRUE)

tracts_clean <- tracts_2023 %>%
  sf::st_drop_geometry() %>%
  filter(STUSPS %in% tract_state_scope) %>%
  select(state_fip = STATEFP,
         county_fip = COUNTYFP,
         tract_fip = TRACTCE,
         tract_geoid = GEOID,
         tract_name = NAME,
         tract_name_long = NAMELSAD,
         state_abbr = STUSPS,
         county_name = NAMELSADCO,
         state_name = STATE_NAME,
         lsad = LSAD) %>%
  mutate(
         vintage = 2023L,
         source = "TIGRIS"
  )

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_tract_county"),
                  tracts_clean, overwrite = TRUE)

# Place <> County ----


# ZCTA <> County ----
zcta_county_xwalk_raw <- read_excel(paste0(data, "/demographics/raw/crosswalks/ZIP_COUNTY_062025.xlsx"))

zcta_county_xwalk_clean <- zcta_county_xwalk_raw %>%
  select(
    zip_geoid = ZIP,
    county_geoid = COUNTY,
    zip_pref_city = USPS_ZIP_PREF_CITY,
    zip_pref_state = USPS_ZIP_PREF_STATE,
    rel_weight_pop = RES_RATIO,      # HUD's preferred pop-ish weight
    rel_weight_bus = BUS_RATIO,      # HUD's preferred pop-ish weight
    rel_weight_hu  = TOT_RATIO,      # or NA, but keeping it is nice
  ) %>%
  mutate(
    zip_geoid   = str_pad(zip_geoid, 5, pad = "0"),
    county_geoid = str_pad(county_geoid, 5, pad = "0"),
    vintage = 2025L,
    source  = "HUD_ZIP_COUNTY_2025Q1"
  )

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_zcta_county"),
                  zcta_county_xwalk_clean, overwrite = TRUE)

# ZCTA <> CBSA ----
zcta_cbsa_xwalk_raw <- read_excel(paste0(data, "/demographics/raw/crosswalks/ZIP_CBSA_062025.xlsx"))

zcta_cbsa_xwalk_clean <- zcta_cbsa_xwalk_raw %>%
  select(
    zip_geoid = ZIP,
    cbsa_geoid = CBSA,
    zip_pref_city = USPS_ZIP_PREF_CITY,
    zip_pref_state = USPS_ZIP_PREF_STATE,
    rel_weight_pop = RES_RATIO,      # HUD's preferred pop-ish weight
    rel_weight_bus = BUS_RATIO,      # HUD's preferred pop-ish weight
    rel_weight_hu  = TOT_RATIO,      # or NA, but keeping it is nice
  ) %>%
  mutate(
    zip_geoid   = str_pad(zip_geoid, 5, pad = "0"),
    cbsa_geoid = str_pad(cbsa_geoid, 5, pad = "0"),
    vintage = 2025L,
    source  = "HUD_ZIP_CBSA_2025Q1"
  )

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_zcta_cbsa"),
                  zcta_cbsa_xwalk_clean, overwrite = TRUE)

# ZCTA <> Tract ----
zcta_tract_xwalk_raw <- read_excel(paste0(data, "/demographics/raw/crosswalks/ZIP_TRACT_062025.xlsx"))

zcta_tract_xwalk_clean <- zcta_tract_xwalk_raw %>%
  select(
    zip_geoid = ZIP,
    tract_geoid = TRACT,
    zip_pref_city = USPS_ZIP_PREF_CITY,
    zip_pref_state = USPS_ZIP_PREF_STATE,
    rel_weight_pop = RES_RATIO,      # HUD's preferred pop-ish weight
    rel_weight_bus = BUS_RATIO,      # HUD's preferred pop-ish weight
    rel_weight_hu  = TOT_RATIO,      # or NA, but keeping it is nice
  ) %>%
  mutate(
    zip_geoid   = str_pad(zip_geoid, 5, pad = "0"),
    tract_geoid = str_pad(tract_geoid, 11, pad = "0"),
    vintage = 2025L,
    source  = "HUD_ZIP_TRACT_2025Q1"
  )

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_zcta_tract"),
                  zcta_tract_xwalk_clean, overwrite = TRUE)

# County <> State ----
# Get all Counties from Tigris
counties_2023 <- tigris::counties(year = 2023, cb = TRUE)

county_state_xwalk_clean <- counties_2023 %>%
  sf::st_drop_geometry() %>%
  select(state_fip = STATEFP,
         county_fip = COUNTYFP,
         county_geoid = GEOID,
         county_name = NAME,
         county_name_long = NAMELSAD,
         state_abbr = STUSPS,
         lsad = LSAD
         ) %>%
  mutate(
    vintage = 2023L,
    source = "TIGRIS"
  )

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_county_state"),
                  county_state_xwalk_clean, overwrite = TRUE)

# CBSA <> State ----
# Select Distinct CBSA Codes, States

cbsa_state_xwalk_clean <- cbsa_county_xwalk_clean %>%
  group_by(cbsa_code, cbsa_name, state_fips, state_name) %>%
  summarize(counties = n()) %>%
  ungroup() %>%
  mutate(vintage = 2023L,
         source = "DERIVED_FROM_CBSA_COUNTY_XWALK")

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_cbsa_state"),
                  cbsa_state_xwalk_clean, overwrite = TRUE)


# State <> Region <> Division
state_region_division <- tibble::tribble(
  ~state_fips, ~state_abbr, ~state_name,        ~census_region,     ~census_division,
  "01",        "AL",        "Alabama",          "South",            "East South Central",
  "02",        "AK",        "Alaska",           "West",             "Pacific",
  "04",        "AZ",        "Arizona",          "West",             "Mountain",
  "05",        "AR",        "Arkansas",         "South",            "West South Central",
  "06",        "CA",        "California",       "West",             "Pacific",
  "08",        "CO",        "Colorado",         "West",             "Mountain",
  "09",        "CT",        "Connecticut",      "Northeast",        "New England",
  "10",        "DE",        "Delaware",         "South",            "South Atlantic",
  "11",        "DC",        "District of Columbia","South",         "South Atlantic",
  "12",        "FL",        "Florida",          "South",            "South Atlantic",
  "13",        "GA",        "Georgia",          "South",            "South Atlantic",
  "15",        "HI",        "Hawaii",           "West",             "Pacific",
  "16",        "ID",        "Idaho",            "West",             "Mountain",
  "17",        "IL",        "Illinois",         "Midwest",          "East North Central",
  "18",        "IN",        "Indiana",          "Midwest",          "East North Central",
  "19",        "IA",        "Iowa",             "Midwest",          "West North Central",
  "20",        "KS",        "Kansas",           "Midwest",          "West North Central",
  "21",        "KY",        "Kentucky",         "South",            "East South Central",
  "22",        "LA",        "Louisiana",        "South",            "West South Central",
  "23",        "ME",        "Maine",            "Northeast",        "New England",
  "24",        "MD",        "Maryland",         "South",            "South Atlantic",
  "25",        "MA",        "Massachusetts",    "Northeast",        "New England",
  "26",        "MI",        "Michigan",         "Midwest",          "East North Central",
  "27",        "MN",        "Minnesota",        "Midwest",          "West North Central",
  "28",        "MS",        "Mississippi",      "South",            "East South Central",
  "29",        "MO",        "Missouri",         "Midwest",          "West North Central",
  "30",        "MT",        "Montana",          "West",             "Mountain",
  "31",        "NE",        "Nebraska",         "Midwest",          "West North Central",
  "32",        "NV",        "Nevada",           "West",             "Mountain",
  "33",        "NH",        "New Hampshire",    "Northeast",        "New England",
  "34",        "NJ",        "New Jersey",       "Northeast",        "Middle Atlantic",
  "35",        "NM",        "New Mexico",       "West",             "Mountain",
  "36",        "NY",        "New York",         "Northeast",        "Middle Atlantic",
  "37",        "NC",        "North Carolina",   "South",            "South Atlantic",
  "38",        "ND",        "North Dakota",     "Midwest",          "West North Central",
  "39",        "OH",        "Ohio",             "Midwest",          "East North Central",
  "40",        "OK",        "Oklahoma",         "South",            "West South Central",
  "41",        "OR",        "Oregon",           "West",             "Pacific",
  "42",        "PA",        "Pennsylvania",     "Northeast",        "Middle Atlantic",
  "44",        "RI",        "Rhode Island",     "Northeast",        "New England",
  "45",        "SC",        "South Carolina",   "South",            "South Atlantic",
  "46",        "SD",        "South Dakota",     "Midwest",          "West North Central",
  "47",        "TN",        "Tennessee",        "South",            "East South Central",
  "48",        "TX",        "Texas",            "South",            "West South Central",
  "49",        "UT",        "Utah",             "West",             "Mountain",
  "50",        "VT",        "Vermont",          "Northeast",        "New England",
  "51",        "VA",        "Virginia",         "South",            "South Atlantic",
  "53",        "WA",        "Washington",       "West",             "Pacific",
  "54",        "WV",        "West Virginia",    "South",            "South Atlantic",
  "55",        "WI",        "Wisconsin",        "Midwest",          "East North Central",
  "56",        "WY",        "Wyoming",          "West",             "Mountain"
)

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_state_region"),
                  state_region_division, overwrite = TRUE)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
