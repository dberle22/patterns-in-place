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

# Race/Ethnicity (B03002)
vars <- c(
  pop_total_b03002     = "B03002_001",
  white_nonhisp        = "B03002_003",
  black_nonhisp        = "B03002_004",
  amind_nonhisp        = "B03002_005",
  asian_nonhisp        = "B03002_006",
  pacisl_nonhisp       = "B03002_007",
  other_nonhisp        = "B03002_008",
  two_plus_nonhisp     = "B03002_009",
  hispanic_any         = "B03002_012"
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
             DBI::Id(schema = "staging", table = "acs_race_us"),
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
             DBI::Id(schema = "staging", table = "acs_race_region"),
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
             DBI::Id(schema = "staging", table = "acs_race_division"),
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
             DBI::Id(schema = "staging", table = "acs_race_state"),
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
             DBI::Id(schema = "staging", table = "acs_race_county"),
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
             DBI::Id(schema = "staging", table = "acs_race_zcta"),
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
             DBI::Id(schema = "staging", table = "acs_race_place"),
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
             DBI::Id(schema = "staging", table = "acs_race_tract"),
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
             DBI::Id(schema = "staging", table = "acs_race_tract_fl"),
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
             DBI::Id(schema = "staging", table = "acs_race_tract_nc"),
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
             DBI::Id(schema = "staging", table = "acs_race_tract_ga"),
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
             DBI::Id(schema = "staging", table = "acs_race_tract_sc"),
             tract_sc_acs_raw, 
             overwrite = TRUE)

dbDisconnect(con, shutdown = TRUE)