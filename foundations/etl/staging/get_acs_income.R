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

# Income/Poverty
  # Headling Income
  # Per Capita Income
  # Poverty
  # Income Bands
vars <- c(
  # 1) Income levels
  median_hh_income   = "B19013_001",  # Median household income (dollars)
  per_capita_income  = "B19301_001",  # Per capita income (dollars)
  
  # 2) Poverty universe
  pov_universe       = "B17001_001",  # Poverty status in past 12 months: total
  pov_below          = "B17001_002",  # Income in the past 12 months below poverty level
  
  # 3) (Optional but useful now) Household income distribution
  # This is B19001 (Household Income in the Past 12 Months)
  hh_inc_total       = "B19001_001",
  hh_inc_lt10k       = "B19001_002",
  hh_inc_10k_15k     = "B19001_003",
  hh_inc_15k_20k     = "B19001_004",
  hh_inc_20k_25k     = "B19001_005",
  hh_inc_25k_30k     = "B19001_006",
  hh_inc_30k_35k     = "B19001_007",
  hh_inc_35k_40k     = "B19001_008",
  hh_inc_40k_45k     = "B19001_009",
  hh_inc_45k_50k     = "B19001_010",
  hh_inc_50k_60k     = "B19001_011",
  hh_inc_60k_75k     = "B19001_012",
  hh_inc_75k_100k    = "B19001_013",
  hh_inc_100k_125k   = "B19001_014",
  hh_inc_125k_150k   = "B19001_015",
  hh_inc_150k_200k   = "B19001_016",
  hh_inc_200k_plus   = "B19001_017",
  
  # Gini Index
  gini_index         = "B19083_001"
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
             DBI::Id(schema = "staging", table = "acs_income_us"),
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
             DBI::Id(schema = "staging", table = "acs_income_region"),
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
             DBI::Id(schema = "staging", table = "acs_income_division"),
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
             DBI::Id(schema = "staging", table = "acs_income_state"),
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
             DBI::Id(schema = "staging", table = "acs_income_county"),
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
             DBI::Id(schema = "staging", table = "acs_income_zcta"),
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
             DBI::Id(schema = "staging", table = "acs_income_place"),
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
             DBI::Id(schema = "staging", table = "acs_income_tract"),
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
             DBI::Id(schema = "staging", table = "acs_income_tract_fl"),
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
             DBI::Id(schema = "staging", table = "acs_income_tract_nc"),
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
             DBI::Id(schema = "staging", table = "acs_income_tract_ga"),
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
             DBI::Id(schema = "staging", table = "acs_income_tract_sc"),
             tract_sc_acs_raw, 
             overwrite = TRUE)

dbDisconnect(con, shutdown = TRUE)