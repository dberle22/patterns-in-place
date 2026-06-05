# In this script we get our TEA Raw Data

# Find our current directory 
getwd()

# Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
bronze <- get_env_path("DATA_RAW")
db_path <- get_env_path("DB_PATH")

# Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Ingest Budget Data ----
## Raw Data ----
tea_budget_2025 <- read_csv(paste0(bronze, "/tea/tea_budget2025.csv"))

## Metadata ----
### Function ----
meta_tea_budget_function_raw <- read_delim(
  file = paste0(bronze, "/tea/budget2025d/FUNCTION_2025F.TXT"),
  delim = ",",
  col_names = FALSE,
  col_types = cols(.default = col_character()),
  trim_ws = TRUE
)

meta_tea_budget_function <- meta_tea_budget_function_raw %>%
  setNames(c(
    "function_code",
    "function_desc",
    "function_desc_long",
    "payroll_elig",
    "budget_elig",
    "actual_elig",
    "dtupdate"
  )) %>%
  mutate(
    function_code = str_pad(function_code, 2, pad = "0"),
    dtupdate = suppressWarnings(as.numeric(dtupdate))
  )

### FUND ----
meta_tea_budget_fund_raw <- read_delim(
  file = paste0(bronze, "/tea/budget2025d/FUND_2025F.TXT"),
  delim = ",",
  col_names = FALSE,
  col_types = cols(.default = col_character()),
  trim_ws = TRUE
)

meta_tea_budget_fund <- meta_tea_budget_fund_raw %>%
  setNames(c(
    "fund_code",
    "fund_desc",
    "fund_desc_long",
    "payroll_elig",
    "budget_elig",
    "actual_elig",
    "ssa_actual_elig",
    "dtupdate"
  )) %>%
  mutate(
    fund_code = str_pad(fund_code, 3, pad = "0"),
    dtupdate = suppressWarnings(as.numeric(dtupdate))
  )


### OBJECT ----
meta_tea_budget_object_raw <- read_delim(
  file = paste0(bronze, "/tea/budget2025d/OBJECT_2025F.TXT"),
  delim = ",",
  col_names = FALSE,
  col_types = cols(.default = col_character()),
  trim_ws = TRUE
)

meta_tea_budget_object <- meta_tea_budget_object_raw %>%
  setNames(c(
    "object_code",
    "object_desc",
    "object_desc_long",
    "payroll_elig",
    "budget_elig",
    "actual_elig",
    "dtupdate"
  )) %>%
  mutate(
    object_code = str_pad(object_code, 4, pad = "0"),
    dtupdate = suppressWarnings(as.numeric(dtupdate))
  )


## District Master ----
tea_school_master_2025_raw <- read_csv(paste0(bronze, "/tea/tea_district_school_master.csv")) %>%
  janitor::clean_names()

## ESEA Title 1 ----
### FY2024 ----
title_1_tx_2024_raw <- read_excel(paste0(bronze, "/tea/fy2024-esea-title-1-tables-texas-109667.xlsx"),
                              skip = 1) %>%
  janitor::clean_names() %>%
  filter(!is.na(lea_id)) %>%
  mutate(lea_id = as.character(lea_id))

## TEA Econ Disadvantage Report
tea_econ_disadvantage_raw <- read_csv(paste0(bronze, "/tea/Economically Disadvantaged Report_Statewide_Districts_2024-2025.csv"),
                                  skip = 4) %>%
  janitor::clean_names() %>%
  filter(!is.na(county_name)) 

# Build District List ----
## We will use the District Master as our Source, gathering key info

## Prep Data ----
tea_district_master_2025 <- tea_school_master_2025_raw %>%
  group_by(county_number, county_name, esc_region_served, district_number, district_name, district_city,
           district_zip, district_type, nces_district_id, district_enrollment_as_of_oct_2024) %>%
  summarize(number_of_schools = n(),
            avg_school_enrollment = mean(school_enrollment_as_of_oct_2024, na.rm = TRUE)) %>%
  ungroup() %>%
  mutate(county_number = str_remove(county_number, "^'"),
         esc_region_served = str_remove(esc_region_served, "^'"),
         district_number = str_remove(district_number, "^'"),
         nces_district_id = str_remove(nces_district_id, "^'"))
  
title_1_tx_2024 <- title_1_tx_2024_raw %>%
  select(lea_id, lea_name, allocations = fy_2024_title_i_allocation_in_dollars_1) %>%
  mutate(year = 2024L)


tea_econ_disadvantage <- tea_econ_disadvantage_raw %>%
  mutate(eligible_for_free_meals_count = na_if(eligible_for_free_meals_count, -999),
         eligible_for_free_meals_percent = na_if(eligible_for_free_meals_percent, -999),
         eligible_for_reduced_price_meals_count = na_if(eligible_for_reduced_price_meals_count, -999),
         eligible_for_reduced_price_meals_percent = na_if(eligible_for_reduced_price_meals_percent, -999),
         other_economically_disadvantaged_count = na_if(other_economically_disadvantaged_count, -999),
         other_economically_disadvantaged_percent = na_if(other_economically_disadvantaged_percent, -999),
         not_economically_disadvantaged_count = na_if(not_economically_disadvantaged_count, -999),
         not_economically_disadvantaged_percent = na_if(not_economically_disadvantaged_percent, -999)
         ) %>%
  mutate(econ_disadvatange_count = 
           eligible_for_free_meals_count +
           eligible_for_reduced_price_meals_count +
           other_economically_disadvantaged_count,
         econ_disadvatange_share = econ_disadvatange_count / total_count,
         economically_disadvantaged_percent = 100 - not_economically_disadvantaged_percent
           ) %>%
  select(region:charter_status, total_count, not_economically_disadvantaged_percent,
         economically_disadvantaged_percent)

## Final Master List ----
tx_districts_2025 <- tea_district_master_2025 %>%
  left_join(title_1_tx_2024, by = c("nces_district_id" = "lea_id")) %>%
  left_join(tea_econ_disadvantage %>% select(district_number, charter_status,
                                             total_count, not_economically_disadvantaged_percent, economically_disadvantaged_percent), 
            by = c("district_number" = "district_number")) %>%
  mutate(year = 2024L)

dbWriteTable(con, 
             DBI::Id(schema = "silver", table = "tx_tea_district_metrics"),
             tx_districts_2025, 
             overwrite = TRUE)

dbDisconnect(con, shutdown = TRUE)