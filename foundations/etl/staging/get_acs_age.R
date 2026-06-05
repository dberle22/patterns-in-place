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

# Create our Vars mapping ----
vars_age_sex <- c(
  pop_total              = "B01001_001",
  median_age.            = "B01002_001",
  pop_male_total         = "B01001_002",
  pop_age_male_under5    = "B01001_003",
  pop_age_male_5_9       = "B01001_004",
  pop_age_male_10_14     = "B01001_005",
  pop_age_male_15_17     = "B01001_006",
  pop_age_male_18_19     = "B01001_007",
  pop_age_male_20        = "B01001_008",
  pop_age_male_21        = "B01001_009",
  pop_age_male_22_24     = "B01001_010",
  pop_age_male_25_29     = "B01001_011",
  pop_age_male_30_34     = "B01001_012",
  pop_age_male_35_39     = "B01001_013",
  pop_age_male_40_44     = "B01001_014",
  pop_age_male_45_49     = "B01001_015",
  pop_age_male_50_54     = "B01001_016",
  pop_age_male_55_59     = "B01001_017",
  pop_age_male_60_61     = "B01001_018",
  pop_age_male_62_64     = "B01001_019",
  pop_age_male_65_66     = "B01001_020",
  pop_age_male_67_69     = "B01001_021",
  pop_age_male_70_74     = "B01001_022",
  pop_age_male_75_79     = "B01001_023",
  pop_age_male_80_84     = "B01001_024",
  pop_age_male_85_plus   = "B01001_025",
  pop_female_total       = "B01001_026",
  pop_age_female_under5  = "B01001_027",
  pop_age_female_5_9     = "B01001_028",
  pop_age_female_10_14   = "B01001_029",
  pop_age_female_15_17   = "B01001_030",
  pop_age_female_18_19   = "B01001_031",
  pop_age_female_20      = "B01001_032",
  pop_age_female_21      = "B01001_033",
  pop_age_female_22_24   = "B01001_034",
  pop_age_female_25_29   = "B01001_035",
  pop_age_female_30_34   = "B01001_036",
  pop_age_female_35_39   = "B01001_037",
  pop_age_female_40_44   = "B01001_038",
  pop_age_female_45_49   = "B01001_039",
  pop_age_female_50_54   = "B01001_040",
  pop_age_female_55_59   = "B01001_041",
  pop_age_female_60_61   = "B01001_042",
  pop_age_female_62_64   = "B01001_043",
  pop_age_female_65_66   = "B01001_044",
  pop_age_female_67_69   = "B01001_045",
  pop_age_female_70_74   = "B01001_046",
  pop_age_female_75_79   = "B01001_047",
  pop_age_female_80_84   = "B01001_048",
  pop_age_female_85_plus = "B01001_049"
)

tract_states <- resolve_tract_state_scope()

# Ingest Data ----

# US ----
us_acs_age_raw <- acs_ingest(
  geography = "us",
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_us"),
             us_acs_age_raw, 
             overwrite = TRUE)

# Region ----
region_acs_age_raw <- acs_ingest(
  geography = "region",
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_region"),
             region_acs_age_raw, 
             overwrite = TRUE)


# Division ----
division_acs_age_raw <- acs_ingest(
  geography = "division",
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_division"),
             division_acs_age_raw, 
             overwrite = TRUE)

# State ----
state_acs_age_raw <- acs_ingest(
  geography = "state",
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_state"),
             state_acs_age_raw, 
             overwrite = TRUE)

# County ----
county_acs_age_raw <- acs_ingest(
  geography = "county",
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_county"),
             county_acs_age_raw, 
             overwrite = TRUE)

# ZCTA ----
zcta_acs_age_raw <- acs_ingest(
  geography = "zcta",
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_zcta"),
             zcta_acs_age_raw, 
             overwrite = TRUE)

# Place ----
place_acs_age_raw <- acs_ingest(
  geography = "place",
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_place"),
             place_acs_age_raw, 
             overwrite = TRUE)

# Tract (all supported states) ----
all_tract_acs_age_raw <- acs_ingest(
  geography = "tract",
  state = tract_states,
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_tract"),
             all_tract_acs_age_raw, 
             overwrite = TRUE)

# Legacy: preserve existing state-level tract ingest tables for compatibility

# FL
tract_fl_acs_age_raw <- acs_ingest(
  geography = "tract",
  state = 'FL',
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_tract_fl"),
             tract_fl_acs_age_raw, 
             overwrite = TRUE)

# NC
tract_nc_acs_age_raw <- acs_ingest(
  geography = "tract",
  state = 'NC',
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_tract_nc"),
             tract_nc_acs_age_raw, 
             overwrite = TRUE)

# GA
tract_ga_acs_age_raw <- acs_ingest(
  geography = "tract",
  state = 'GA',
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_tract_ga"),
             tract_ga_acs_age_raw, 
             overwrite = TRUE)

# SC
tract_sc_acs_age_raw <- acs_ingest(
  geography = "tract",
  state = 'SC',
  years     = 2012:2024,
  variables = vars_age_sex,
  survey    = "acs5",
  output    = "wide"
)

# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "staging", table = "acs_age_tract_sc"),
             tract_sc_acs_age_raw, 
             overwrite = TRUE)

dbDisconnect(con, shutdown = TRUE)