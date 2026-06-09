# In this script we get our ACS disability raw data

# Find our current directory
getwd()

# Set up our environment ----
here::i_am("foundations/etl/staging/get_acs_disability.R")
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

bronze_acs <- get_env_path("DATA_DEMO_RAW")
db_path <- get_env_path("DB_PATH")

# Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Load ACS Vars ----
acs_v24 <- load_variables(year = "2024", dataset = "acs5", cache = TRUE)

# Disability by age and sex (B18101) ----
vars <- c(
  disability_total = "B18101_001",
  disability_male_total = "B18101_002",
  disability_male_under_5_total = "B18101_003",
  disability_male_under_5_with_disability = "B18101_004",
  disability_male_under_5_no_disability = "B18101_005",
  disability_male_5_17_total = "B18101_006",
  disability_male_5_17_with_disability = "B18101_007",
  disability_male_5_17_no_disability = "B18101_008",
  disability_male_18_34_total = "B18101_009",
  disability_male_18_34_with_disability = "B18101_010",
  disability_male_18_34_no_disability = "B18101_011",
  disability_male_35_64_total = "B18101_012",
  disability_male_35_64_with_disability = "B18101_013",
  disability_male_35_64_no_disability = "B18101_014",
  disability_male_65_74_total = "B18101_015",
  disability_male_65_74_with_disability = "B18101_016",
  disability_male_65_74_no_disability = "B18101_017",
  disability_male_75_plus_total = "B18101_018",
  disability_male_75_plus_with_disability = "B18101_019",
  disability_male_75_plus_no_disability = "B18101_020",
  disability_female_total = "B18101_021",
  disability_female_under_5_total = "B18101_022",
  disability_female_under_5_with_disability = "B18101_023",
  disability_female_under_5_no_disability = "B18101_024",
  disability_female_5_17_total = "B18101_025",
  disability_female_5_17_with_disability = "B18101_026",
  disability_female_5_17_no_disability = "B18101_027",
  disability_female_18_34_total = "B18101_028",
  disability_female_18_34_with_disability = "B18101_029",
  disability_female_18_34_no_disability = "B18101_030",
  disability_female_35_64_total = "B18101_031",
  disability_female_35_64_with_disability = "B18101_032",
  disability_female_35_64_no_disability = "B18101_033",
  disability_female_65_74_total = "B18101_034",
  disability_female_65_74_with_disability = "B18101_035",
  disability_female_65_74_no_disability = "B18101_036",
  disability_female_75_plus_total = "B18101_037",
  disability_female_75_plus_with_disability = "B18101_038",
  disability_female_75_plus_no_disability = "B18101_039"
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
write_geo_slice("us", "acs_disability_us", 2012:2024)
write_geo_slice("region", "acs_disability_region", 2012:2024)
write_geo_slice("division", "acs_disability_division", 2012:2024)
write_geo_slice("state", "acs_disability_state", 2012:2024)
write_geo_slice("county", "acs_disability_county", 2012:2024)
write_geo_slice("zcta", "acs_disability_zcta", 2012:2024)
write_geo_slice("place", "acs_disability_place", 2012:2024)
write_geo_slice("tract", "acs_disability_tract", 2012:2024, state = tract_states)

# Legacy: preserve existing state-level tract ingest tables for compatibility
write_geo_slice("tract", "acs_disability_tract_fl", 2012:2024, state = "FL")
write_geo_slice("tract", "acs_disability_tract_nc", 2012:2024, state = "NC")
write_geo_slice("tract", "acs_disability_tract_ga", 2012:2024, state = "GA")
write_geo_slice("tract", "acs_disability_tract_sc", 2012:2024, state = "SC")

dbDisconnect(con, shutdown = TRUE)
