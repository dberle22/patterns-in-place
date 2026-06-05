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

# Check Occupation Vars
occ_vars <- acs_v23 %>%
  filter(str_detect(name,
                    "C24010_"
  ))

# write_csv(occ_vars, "projects/occ_vars.csv")

# Check Industry Vars
ind_vars <- acs_v23 %>%
  filter(str_detect(name,
                    "C24030_"
  ))

# write_csv(ind_vars, "projects/ind_vars.csv")

# Labor (B23025)

vars <- c(
  # 1) Labor Force Population
  pop_16plus          = "B23025_001",  # total 16+
  in_labor_force      = "B23025_002",
  in_lf_civilian      = "B23025_003",
  in_lf_armed_forces  = "B23025_004",
  not_in_labor_force  = "B23025_005",
  employed            = "B23025_007",
  
  # 2) Occupation
  occ_total           = "C24010_001",
  occ_male_mgmt_business_sci_arts   = "C24010_003",
  occ_male_service   = "C24010_019",
  occ_male_sales_office   = "C24010_027",
  occ_male_nat_resources_const_maint = "C24010_030",
  occ_male_prod_transp_material = "C24010_034",
  occ_female_mgmt_business_sci_arts   = "C24010_039",
  occ_female_service   = "C24010_055",
  occ_female_sales_office   = "C24010_063",
  occ_female_nat_resources_const_maint = "C24010_066",
  occ_female_prod_transp_material = "C24010_070",
  
  # 3) Industry
  ind_total                = "C24030_001",
  ind_male_ag_mining       = "C24030_003",
  ind_male_construction    = "C24030_006",
  ind_male_manufacturing   = "C24030_007",
  ind_male_wholesale       = "C24030_008",
  ind_male_retail          = "C24030_009",
  ind_male_transport_util  = "C24030_010",
  ind_male_information     = "C24030_013",
  ind_male_finance_real    = "C24030_014",
  ind_male_professional    = "C24030_017",
  ind_male_educ_health     = "C24030_021",
  ind_male_arts_accomm_food= "C24030_024",
  ind_male_other           = "C24030_027",
  ind_male_public_admin    = "C24030_028",
  ind_female_ag_mining       = "C24030_030",
  ind_female_construction    = "C24030_033",
  ind_female_manufacturing   = "C24030_034",
  ind_female_wholesale       = "C24030_035",
  ind_female_retail          = "C24030_036",
  ind_female_transport_util  = "C24030_037",
  ind_female_information     = "C24030_040",
  ind_female_finance_real    = "C24030_041",
  ind_female_professional    = "C24030_044",
  ind_female_educ_health     = "C24030_048",
  ind_female_arts_accomm_food= "C24030_051",
  ind_female_other           = "C24030_054",
  ind_female_public_admin    = "C24030_055"

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
             DBI::Id(schema = "staging", table = "acs_labor_us"),
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
             DBI::Id(schema = "staging", table = "acs_labor_region"),
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
             DBI::Id(schema = "staging", table = "acs_labor_division"),
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
             DBI::Id(schema = "staging", table = "acs_labor_state"),
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
             DBI::Id(schema = "staging", table = "acs_labor_county"),
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
             DBI::Id(schema = "staging", table = "acs_labor_zcta"),
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
             DBI::Id(schema = "staging", table = "acs_labor_place"),
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
             DBI::Id(schema = "staging", table = "acs_labor_tract"),
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
             DBI::Id(schema = "staging", table = "acs_labor_tract_fl"),
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
             DBI::Id(schema = "staging", table = "acs_labor_tract_nc"),
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
             DBI::Id(schema = "staging", table = "acs_labor_tract_ga"),
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
             DBI::Id(schema = "staging", table = "acs_labor_tract_sc"),
             tract_sc_acs_raw, 
             overwrite = TRUE)

dbDisconnect(con, shutdown = TRUE)
