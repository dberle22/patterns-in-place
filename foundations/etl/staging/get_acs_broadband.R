# In this script we get our ACS broadband raw data

# Find our current directory
getwd()

# Set up our environment ----
here::i_am("foundations/etl/staging/get_acs_broadband.R")
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

bronze_acs <- get_env_path("DATA_DEMO_RAW")
db_path <- get_env_path("DB_PATH")

# Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Load ACS Vars ----
acs_v24 <- load_variables(year = "2024", dataset = "acs5", cache = TRUE)

# Broadband (B28002) ----
# This table begins in ACS 2017, so the staging time range starts there.
vars <- c(
  internet_total_hh = "B28002_001",
  internet_with_subscription = "B28002_002",
  internet_dial_up_only = "B28002_003",
  internet_broadband_any = "B28002_004",
  internet_cellular_data_only = "B28002_005",
  internet_cellular_and_other = "B28002_006",
  internet_broadband_and_cellular = "B28002_007",
  internet_broadband_no_cellular = "B28002_008",
  internet_satellite_only = "B28002_009",
  internet_satellite_and_other = "B28002_010",
  internet_other_service = "B28002_011",
  internet_access_no_subscription = "B28002_012",
  internet_no_access = "B28002_013"
)

tract_states <- resolve_tract_state_scope()

write_geo_slice <- function(geography, table_name, years, state = NULL) {
  acs_raw <- acs_ingest(
    geography = geography,
    state = state,
    years = years,
    variables = vars,
    survey = "acs5",
    output = "wide"
  )

  dbWriteTable(
    con,
    DBI::Id(schema = "staging", table = table_name),
    acs_raw,
    overwrite = TRUE
  )
}

# Ingest Data ----
write_geo_slice("us", "acs_broadband_us", 2017:2024)
write_geo_slice("region", "acs_broadband_region", 2017:2024)
write_geo_slice("division", "acs_broadband_division", 2017:2024)
write_geo_slice("state", "acs_broadband_state", 2017:2024)
write_geo_slice("county", "acs_broadband_county", 2017:2024)
write_geo_slice("zcta", "acs_broadband_zcta", 2017:2024)
write_geo_slice("place", "acs_broadband_place", 2017:2024)
write_geo_slice("tract", "acs_broadband_tract", 2017:2024, state = tract_states)

# Legacy: preserve existing state-level tract ingest tables for compatibility
write_geo_slice("tract", "acs_broadband_tract_fl", 2017:2024, state = "FL")
write_geo_slice("tract", "acs_broadband_tract_nc", 2017:2024, state = "NC")
write_geo_slice("tract", "acs_broadband_tract_ga", 2017:2024, state = "GA")
write_geo_slice("tract", "acs_broadband_tract_sc", 2017:2024, state = "SC")

dbDisconnect(con, shutdown = TRUE)
