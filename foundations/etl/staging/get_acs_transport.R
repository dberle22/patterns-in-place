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
db_path <- get_env_path("DB_PATH")

# Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Load ACS Vars ----
acs_v23 <- load_variables(year = '2023', dataset = "acs5", cache = TRUE)
acs_v15 <- load_variables(year = '2015', dataset = "acs5", cache = TRUE)


# Transportation
vars <- c(
  # A) Means of transportation to work (B08301)
  commute_workers_total = "B08301_001",
  commute_car_truck_van = "B08301_002",
  commute_drove_alone   = "B08301_003",
  commute_carpool       = "B08301_004",
  commute_public_trans  = "B08301_010",
  commute_taxicab       = "B08301_016",
  commute_motorcycle    = "B08301_017",
  commute_bicycle       = "B08301_018",
  commute_walked        = "B08301_019",
  commute_other         = "B08301_020",
  commute_worked_home   = "B08301_021",
  
  # B) Household Size by Vehicles (B08201)
  veh_total_hh = "B08201_001",
  veh_0        = "B08201_002",
  veh_1        = "B08201_003",
  veh_2        = "B08201_004",
  veh_3        = "B08201_005",
  veh_4_plus   = "B08201_006",
  
  # C) Mean travel time to work (minutes) — B08013
  total_travel_time = "B08013_001"
)

tract_states <- resolve_tract_state_scope()

# Ingest Data ----

# US ----
us_acs_raw <- acs_ingest(
  geography = "us",
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_us"),
             us_acs_raw, 
             overwrite = TRUE)

# Region ----
region_acs_raw <- acs_ingest(
  geography = "region",
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_region"),
             region_acs_raw, 
             overwrite = TRUE)


# Division ----
division_acs_raw <- acs_ingest(
  geography = "division",
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_division"),
             division_acs_raw, 
             overwrite = TRUE)

# State ----
state_acs_raw <- acs_ingest(
  geography = "state",
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_state"),
             state_acs_raw, 
             overwrite = TRUE)

# County ----
county_acs_raw <- acs_ingest(
  geography = "county",
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_county"),
             county_acs_raw, 
             overwrite = TRUE)

# ZCTA ----
zcta_acs_raw <- acs_ingest(
  geography = "zcta",
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_zcta"),
             zcta_acs_raw, 
             overwrite = TRUE)

# Place ----
place_acs_raw <- acs_ingest(
  geography = "place",
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_place"),
             place_acs_raw, 
             overwrite = TRUE)

# Tract (all supported states) ----
all_tract_acs_raw <- acs_ingest(
  geography = "tract",
  state = tract_states,
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_tract"),
             all_tract_acs_raw, 
             overwrite = TRUE)

# Legacy: preserve existing state-level tract ingest tables for compatibility

# FL
tract_fl_acs_raw <- acs_ingest(
  geography = "tract",
  state = 'FL',
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_tract_fl"),
             tract_fl_acs_raw, 
             overwrite = TRUE)

# NC
tract_nc_acs_raw <- acs_ingest(
  geography = "tract",
  state = 'NC',
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_tract_nc"),
             tract_nc_acs_raw, 
             overwrite = TRUE)

# GA
tract_ga_acs_raw <- acs_ingest(
  geography = "tract",
  state = 'GA',
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_tract_ga"),
             tract_ga_acs_raw, 
             overwrite = TRUE)

# SC
tract_sc_acs_raw <- acs_ingest(
  geography = "tract",
  state = 'SC',
  years     = 2012:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_transport_tract_sc"),
             tract_sc_acs_raw, 
             overwrite = TRUE)

dbDisconnect(con, shutdown = TRUE)