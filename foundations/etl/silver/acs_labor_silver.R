# In this script we model ACS Data to Silver

# 1. Set up our Environment
# 2. Read in our Staging Data to R Data Frames
# 3. Add Geo Level to each table, drop _M, rename columns
# 4. Union our Data Frames together
# 5. Compute buckets and select main columns
# 6. Materialize to Silver

# 1. Set up our Environment ----
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

# 2. Read in our Staging Data to R Data Frames ----
us_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_us")
region_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_region")
division_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_division")
state_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_state")
county_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_county")
place_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_place")
zcta_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_zcta")

# Tract
tract_all_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_tract")

# tract_fl_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_tract_fl")
# tract_ga_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_tract_ga")
# tract_nc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_tract_nc")
# tract_sc_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_labor_tract_sc")

## CBSA <> County Xwalk ----
cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")

# 3. Add Geo Level to each table, drop _M, rename columns ----
us_acs_clean <- standardize_acs_df(us_acs_stage, "US", drop_e = FALSE)
region_acs_clean <- standardize_acs_df(region_acs_stage, "Region")
division_acs_clean<- standardize_acs_df(division_acs_stage, "division")
state_acs_clean   <- standardize_acs_df(state_acs_stage, "state")
county_acs_clean  <- standardize_acs_df(county_acs_stage, "county")
place_acs_clean   <- standardize_acs_df(place_acs_stage, "place")
zcta_acs_clean    <- standardize_acs_df(zcta_acs_stage, "zcta")
tract_all_clean    <- standardize_acs_df(tract_all_acs_stage, "tract")

# tract_nc_clean    <- standardize_acs_df(tract_nc_acs_stage, "tract")
# tract_fl_clean    <- standardize_acs_df(tract_fl_acs_stage, "tract")
# tract_ga_clean    <- standardize_acs_df(tract_ga_acs_stage, "tract")
# tract_sc_clean    <- standardize_acs_df(tract_sc_acs_stage, "tract")

# 4. Union our Data Frames together ----
## Rebase County Data to CBSA  ----
### Join CBSA Xwalk to Counties ----
cbsa_base <- county_acs_clean %>%
  inner_join(cbsa_county_xwalk %>% select(cbsa_code, cbsa_name, county_geoid),
             by = c("geo_id" = "county_geoid"))

### Create Rebased Files ----
cbsa_total <- cbsa_base %>%
    dplyr::group_by(cbsa_code, cbsa_name, year) %>%
    dplyr::summarise(
      dplyr::across(
        dplyr::where(is.numeric) & !dplyr::any_of(c("year")),
        ~ sum(.x, na.rm = TRUE)
      ),
      .groups = "drop"
    )

### Make final DF
cbsa_acs_clean <- cbsa_total %>%
  mutate(geo_level = "cbsa") %>%
  select(geo_level, geo_id = cbsa_code, geo_name = cbsa_name, year,
         pop_16plusE:ind_female_public_adminE)


## Union Tracts together ---- 
# tract_all_clean <- dplyr::bind_rows(
#   tract_nc_clean,
#   tract_fl_clean,
#   tract_ga_clean,
#   tract_sc_clean
# )

## Union all DFs together ----
all_acs_clean <- dplyr::bind_rows(
  us_acs_clean,
  region_acs_clean,
  division_acs_clean,
  state_acs_clean,
  cbsa_acs_clean,
  county_acs_clean,
  place_acs_clean,
  zcta_acs_clean,
  tract_all_clean
)

# 5. Compute buckets and select main columns ----
labor_silver_kpi <- all_acs_clean %>%
  # -------------------------
# LABOR (B23025)
# -------------------------
mutate(
  pop_16plus         = pop_16plusE,
  in_labor_force     = in_labor_forceE,
  in_lf_civilian     = in_lf_civilianE,
  in_lf_armed_forces = in_lf_armed_forcesE,
  not_in_labor_force = not_in_labor_forceE,
  employed           = employedE,
  # derive unemployed since we'll trust our own calc
  unemployed         = in_labor_forceE - employedE
) %>%
  mutate(
    lfpr           = in_labor_force / pop_16plus,
    unemp_rate     = unemployed / na_if(in_labor_force, 0),
    emp_pop_ratio  = employed / pop_16plus,
    unemp_rate_civ = unemployed / na_if(in_lf_civilian, 0)
  ) %>%
  
  # -------------------------
# OCCUPATION (C24010)
# 5 big buckets, sum male + female
# -------------------------
mutate(
  occ_total_emp = occ_totalE,
  
  occ_mgmt_business_sci_arts =
    occ_male_mgmt_business_sci_artsE +
    occ_female_mgmt_business_sci_artsE,
  
  occ_service =
    occ_male_serviceE +
    occ_female_serviceE,
  
  occ_sales_office =
    occ_male_sales_officeE +
    occ_female_sales_officeE,
  
  occ_nat_resources_const_maint =
    occ_male_nat_resources_const_maintE +
    occ_female_nat_resources_const_maintE,
  
  occ_prod_transp_material =
    occ_male_prod_transp_materialE +
    occ_female_prod_transp_materialE
) %>%
  mutate(
    pct_occ_mgmt_business_sci_arts = occ_mgmt_business_sci_arts / occ_total_emp,
    pct_occ_service                = occ_service                / occ_total_emp,
    pct_occ_sales_office           = occ_sales_office           / occ_total_emp,
    pct_occ_nat_resources_const_maint = occ_nat_resources_const_maint / occ_total_emp,
    pct_occ_prod_transp_material   = occ_prod_transp_material   / occ_total_emp
  ) %>%
  
  # -------------------------
# INDUSTRY (C24030)
# headline groups, sum male + female
# -------------------------
mutate(
  ind_total_emp = ind_totalE,
  
  ind_ag_mining =
    ind_male_ag_miningE +
    ind_female_ag_miningE,
  
  ind_construction =
    ind_male_constructionE +
    ind_female_constructionE,
  
  ind_manufacturing =
    ind_male_manufacturingE +
    ind_female_manufacturingE,
  
  ind_wholesale =
    ind_male_wholesaleE +
    ind_female_wholesaleE,
  
  ind_retail =
    ind_male_retailE +
    ind_female_retailE,
  
  ind_transport_util =
    ind_male_transport_utilE +
    ind_female_transport_utilE,
  
  ind_information =
    ind_male_informationE +
    ind_female_informationE,
  
  ind_finance_real =
    ind_male_finance_realE +
    ind_female_finance_realE,
  
  ind_professional =
    ind_male_professionalE +
    ind_female_professionalE,
  
  ind_educ_health =
    ind_male_educ_healthE +
    ind_female_educ_healthE,
  
  ind_arts_accomm_food =
    ind_male_arts_accomm_foodE +
    ind_female_arts_accomm_foodE,
  
  ind_other_services =
    ind_male_otherE +
    ind_female_otherE,
  
  ind_public_admin =
    ind_male_public_adminE +
    ind_female_public_adminE
) %>%
  mutate(
    pct_ind_ag_mining        = ind_ag_mining        / ind_total_emp,
    pct_ind_construction     = ind_construction     / ind_total_emp,
    pct_ind_manufacturing    = ind_manufacturing    / ind_total_emp,
    pct_ind_wholesale        = ind_wholesale        / ind_total_emp,
    pct_ind_retail           = ind_retail           / ind_total_emp,
    pct_ind_transport_util   = ind_transport_util   / ind_total_emp,
    pct_ind_information      = ind_information      / ind_total_emp,
    pct_ind_finance_real     = ind_finance_real     / ind_total_emp,
    pct_ind_professional     = ind_professional     / ind_total_emp,
    pct_ind_educ_health      = ind_educ_health      / ind_total_emp,
    pct_ind_arts_accomm_food = ind_arts_accomm_food / ind_total_emp,
    pct_ind_other_services   = ind_other_services   / ind_total_emp,
    pct_ind_public_admin     = ind_public_admin     / ind_total_emp
  ) %>%
  select(
    geo_level, geo_id, geo_name, year,
    
    # labor
    pop_16plus, in_labor_force, in_lf_civilian, in_lf_armed_forces,
    not_in_labor_force, employed, unemployed,
    lfpr, unemp_rate, emp_pop_ratio, unemp_rate_civ,
    
    # occupation
    occ_total_emp,
    occ_mgmt_business_sci_arts, occ_service, occ_sales_office,
    occ_nat_resources_const_maint, occ_prod_transp_material,
    pct_occ_mgmt_business_sci_arts, pct_occ_service, pct_occ_sales_office,
    pct_occ_nat_resources_const_maint, pct_occ_prod_transp_material,
    
    # industry
    ind_total_emp,
    ind_ag_mining, ind_construction, ind_manufacturing,
    ind_wholesale, ind_retail, ind_transport_util,
    ind_information, ind_finance_real, ind_professional,
    ind_educ_health, ind_arts_accomm_food, ind_other_services,
    ind_public_admin,
    pct_ind_ag_mining, pct_ind_construction, pct_ind_manufacturing,
    pct_ind_wholesale, pct_ind_retail, pct_ind_transport_util,
    pct_ind_information, pct_ind_finance_real, pct_ind_professional,
    pct_ind_educ_health, pct_ind_arts_accomm_food, pct_ind_other_services,
    pct_ind_public_admin
  )

# 6. Materialize to Silver DB ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="labor_base"),
                  all_acs_clean, overwrite = TRUE)

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="labor_kpi"),
                  labor_silver_kpi, overwrite = TRUE)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)