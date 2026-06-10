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
acs_v12 <- load_variables(year = '2012', dataset = "acs5", cache = TRUE)


# Social Infra
vars <- c(
  # A) Household / family (B11001)
  hh_total        = "B11001_001",
  hh_family       = "B11001_002",
  hh_married      = "B11001_003",
  hh_other_family = "B11001_004",
  hh_nonfamily    = "B11001_007",
  hh_nonfam_alone        = "B11001_008",
  hh_nonfam_not_alone    = "B11001_009",

  # A2) Family type by presence of own children (B11003)
  # B11003 does not provide one direct "all families with own children" field,
  # so we stage only the three component counts we actually need and let Silver
  # derive the total denominator from those pieces.
  family_with_children_married_couple = "B11003_003",
  family_with_children_single_father = "B11003_010",
  family_with_children_single_mother = "B11003_016",
  
  # B) Internet / broadband (B28002) # Historical Data is not full
  # inet_total_hh   = "B28002_001",
  # inet_no_access  = "B28002_013",
  # inet_subscription_accss = "B28002_003",
  # inet_subscription_broadband  = "B28002_004",
  # inet_no_subscription_access  = "B28002_012",
  
  # C) Health insurance (B27010)
  ins_total       = "B27010_001",
  ins_u19_one_plan     = "B27010_003",
  ins_u19_two_plans     = "B27010_010",
  ins_u19_uncovered   = "B27010_017",
  ins_19_34_one_plan     = "B27010_019",
  ins_19_34_two_plans     = "B27010_026",
  ins_19_34_uncovered   = "B27010_033",
  ins_35_64_one_plan     = "B27010_035",
  ins_35_64_two_plans     = "B27010_042",
  ins_35_64_uncovered   = "B27010_050",
  ins_65u_one_plan     = "B27010_052",
  ins_65u_two_plans     = "B27010_058",
  ins_65u_uncovered   = "B27010_066"
)

tract_states <- resolve_tract_state_scope()

# Ingest Data ----

# US ----
us_acs_raw <- acs_ingest(
  geography = "us",
  years     = 2015:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_social_infra_us"),
             us_acs_raw, 
             overwrite = TRUE)

# Region ----
region_acs_raw <- acs_ingest(
  geography = "region",
  years     = 2015:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_social_infra_region"),
             region_acs_raw, 
             overwrite = TRUE)


# Division ----
division_acs_raw <- acs_ingest(
  geography = "division",
  years     = 2015:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_social_infra_division"),
             division_acs_raw, 
             overwrite = TRUE)

# State ----
state_acs_raw <- acs_ingest(
  geography = "state",
  years     = 2015:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_social_infra_state"),
             state_acs_raw, 
             overwrite = TRUE)

# County ----
county_acs_raw <- acs_ingest(
  geography = "county",
  years     = 2015:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_social_infra_county"),
             county_acs_raw, 
             overwrite = TRUE)

# ZCTA ----
zcta_acs_raw <- acs_ingest(
  geography = "zcta",
  years     = 2015:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_social_infra_zcta"),
             zcta_acs_raw, 
             overwrite = TRUE)

# Place ----
place_acs_raw <- acs_ingest(
  geography = "place",
  years     = 2015:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_social_infra_place"),
             place_acs_raw, 
             overwrite = TRUE)

# Tract (all supported states) ----
all_tract_acs_raw <- acs_ingest(
  geography = "tract",
  state = tract_states,
  years     = 2015:2024,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_social_infra_tract"),
             all_tract_acs_raw, 
             overwrite = TRUE)

# Legacy: preserve existing state-level tract ingest tables for compatibility

# # FL
# tract_fl_acs_raw <- acs_ingest(
#   geography = "tract",
#   state = 'FL',
#   years     = 2015:2024,
#   variables = vars,
#   survey    = "acs5",
#   output    = "wide"
# )
# 
# # Name tables Source <> KPI <> Gran
# dbWriteTable(con, 
#              DBI::Id(schema = "staging", table = "acs_social_infra_tract_fl"),
#              tract_fl_acs_raw, 
#              overwrite = TRUE)
# 
# # NC
# tract_nc_acs_raw <- acs_ingest(
#   geography = "tract",
#   state = 'NC',
#   years     = 2015:2024,
#   variables = vars,
#   survey    = "acs5",
#   output    = "wide"
# )
# 
# # Name tables Source <> KPI <> Gran
# dbWriteTable(con, 
#              DBI::Id(schema = "staging", table = "acs_social_infra_tract_nc"),
#              tract_nc_acs_raw, 
#              overwrite = TRUE)
# 
# # GA
# tract_ga_acs_raw <- acs_ingest(
#   geography = "tract",
#   state = 'GA',
#   years     = 2015:2024,
#   variables = vars,
#   survey    = "acs5",
#   output    = "wide"
# )
# 
# # Name tables Source <> KPI <> Gran
# dbWriteTable(con, 
#              DBI::Id(schema = "staging", table = "acs_social_infra_tract_ga"),
#              tract_ga_acs_raw, 
#              overwrite = TRUE)
# 
# # SC
# tract_sc_acs_raw <- acs_ingest(
#   geography = "tract",
#   state = 'SC',
#   years     = 2015:2024,
#   variables = vars,
#   survey    = "acs5",
#   output    = "wide"
# )

# Name tables Source <> KPI <> Gran
# dbWriteTable(con, 
#              DBI::Id(schema = "staging", table = "acs_social_infra_tract_sc"),
#              tract_sc_acs_raw, 
#              overwrite = TRUE)

dbDisconnect(con, shutdown = TRUE)
