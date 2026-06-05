# In this script we create a cleaner metric dictionary for BEA

# Set up script ----
# Find our current directory 
getwd()

# Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
bea_key <- get_env_path("BEA_KEY")
db_path <- get_env_path("DB_PATH")

## Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Ingest Line Code Data ----
line_codes <- dbGetQuery(con, "SELECT * FROM staging.bea_regional_line_codes")

# Clean our Line Codes Ref Table ----
line_codes_update <- line_codes %>%
  filter(table_name_ref %in% c("CAINC1","CAINC4","CAGDP2","CAGDP9","MARPP","SARPP")) %>%
  mutate(
    # grab text in the LAST parentheses at the end, if any
    naics_raw = str_match(line_desc_clean, "\\(([^()]*)\\)\\s*$")[, 2],
    # remove that trailing "(...)" from the description
    desc_no_naics = if_else(
      is.na(naics_raw),
      line_desc_clean,
      str_trim(str_remove(line_desc_clean, "\\([^()]*\\)\\s*$"))
    )
  ) %>%
  # for each line_code, keep the version WITH naics_raw if it exists
  arrange(line_code, is.na(naics_raw)) %>%
  group_by(line_code, table_name_ref) %>%
  slice(1) %>%
  ungroup() %>%
  mutate(
    is_aggregate = case_when(
      str_detect(naics_raw, ",") ~ TRUE,
      str_detect(naics_raw, "-") ~ TRUE,
      TRUE ~ FALSE
    )
  )

# Build metric dictionary ----
# Create a simple set of mappings 
# Add a flag for Including in Wide
# Create a topic
# Create a vintage column

## Create our base metric ref table ----
line_codes_clean <- line_codes_update %>%
  dplyr::filter(table_name_ref %in% c("CAINC1","CAINC4","CAGDP2","CAGDP9","MARPP","SARPP")) %>%
  dplyr::mutate(
    table       = table_name_ref,
    metric_key  = dplyr::case_when(
      # CAINC1
      table == "CAINC1" & line_code == 1L ~ "pi_total",
      table == "CAINC1" & line_code == 2L ~ "population",
      table == "CAINC1" & line_code == 3L ~ "pi_per_capita",
      
      # CAINC4
      table == "CAINC4" & line_code == 10L ~ "pi_total",
      table == "CAINC4" & line_code == 11L ~ "pi_nonfarm",
      table == "CAINC4" & line_code == 12L ~ "pi_farm",
      table == "CAINC4" & line_code == 20L ~ "population",
      table == "CAINC4" & line_code == 30L ~ "pi_per_capita",
      
      table == "CAINC4" & line_code == 35L ~ "pi_earnings_workplace",
      table == "CAINC4" & line_code == 36L ~ "pi_contrib_social_insurance",
      table == "CAINC4" & line_code == 37L ~ "pi_employee_contrib_social_insurance",
      table == "CAINC4" & line_code == 38L ~ "pi_employer_contrib_social_insurance",
      
      table == "CAINC4" & line_code == 42L ~ "pi_residence_adjustment",
      table == "CAINC4" & line_code == 45L ~ "pi_net_earnings_residence",
      
      table == "CAINC4" & line_code == 46L ~ "pi_dividends_interest_rent",
      table == "CAINC4" & line_code == 47L ~ "pi_transfer_receipts",
      
      table == "CAINC4" & line_code == 50L ~ "pi_wages_salary",
      table == "CAINC4" & line_code == 60L ~ "pi_supplements_wages_salary",
      table == "CAINC4" & line_code == 61L ~ "pi_employer_pension_insurance",
      table == "CAINC4" & line_code == 62L ~ "pi_employer_social_insurance",
      
      table == "CAINC4" & line_code == 70L ~ "pi_proprietors",
      table == "CAINC4" & line_code == 71L ~ "pi_farm_proprietors",
      table == "CAINC4" & line_code == 72L ~ "pi_nonfarm_proprietors",
      
      
      # CAGDP2
      table == "CAGDP2" & line_code == 1L  ~ "gdp_total",
      table == "CAGDP2" & line_code == 2L  ~ "gdp_private",
      table == "CAGDP2" & line_code == 3L  ~ "gdp_agriculture",
      table == "CAGDP2" & line_code == 6L  ~ "gdp_mining",
      table == "CAGDP2" & line_code == 10L ~ "gdp_utilities",
      table == "CAGDP2" & line_code == 11L ~ "gdp_construction",
      table == "CAGDP2" & line_code == 12L ~ "gdp_manufacturing_all",
      table == "CAGDP2" & line_code == 13L ~ "gdp_durable_manufacturing",
      table == "CAGDP2" & line_code == 25L ~ "gdp_nondurable_manufacturing",
      table == "CAGDP2" & line_code == 34L ~ "gdp_wholesale_trade",
      table == "CAGDP2" & line_code == 35L ~ "gdp_retail_trade",
      table == "CAGDP2" & line_code == 36L ~ "gdp_transportation",
      table == "CAGDP2" & line_code == 45L ~ "gdp_information",
      table == "CAGDP2" & line_code == 50L ~ "gdp_finance_real_estate_all",
      table == "CAGDP2" & line_code == 51L ~ "gdp_finance_insurance",
      table == "CAGDP2" & line_code == 56L ~ "gdp_real_estate",
      table == "CAGDP2" & line_code == 59L ~ "gdp_professional_all",
      table == "CAGDP2" & line_code == 60L ~ "gdp_professional_scientific",
      table == "CAGDP2" & line_code == 64L ~ "gdp_professional_management",
      table == "CAGDP2" & line_code == 65L ~ "gdp_professional_admin_support",
      
      table == "CAGDP2" & line_code == 68L ~ "gdp_education_all",
      table == "CAGDP2" & line_code == 69L ~ "gdp_education",
      table == "CAGDP2" & line_code == 70L ~ "gdp_health",
      
      table == "CAGDP2" & line_code == 75L ~ "gdp_arts_food_all",
      table == "CAGDP2" & line_code == 76L ~ "gdp_arts_entertainment",
      table == "CAGDP2" & line_code == 79L ~ "gdp_accomodation_food",
      
      table == "CAGDP2" & line_code == 82L ~ "gdp_other",
      table == "CAGDP2" & line_code == 83L ~ "gdp_gov_enterprises",
      table == "CAGDP2" & line_code == 87L ~ "gdp_natural_resources_all",
      table == "CAGDP2" & line_code == 88L ~ "gdp_trade_all",
      table == "CAGDP2" & line_code == 89L ~ "gdp_transport_utilities_all",
      table == "CAGDP2" & line_code == 90L ~ "gdp_manufacturing_info_all",
      table == "CAGDP2" & line_code == 91L ~ "gdp_private_goods_producing_industries",
      table == "CAGDP2" & line_code == 92L ~ "gdp_private_services_providing_industries",
      
      # CAGDP9 (Real)
      table == "CAGDP9" & line_code == 1L  ~ "real_gdp_total",
      table == "CAGDP9" & line_code == 2L  ~ "real_gdp_private",
      table == "CAGDP9" & line_code == 3L  ~ "real_gdp_agriculture",
      table == "CAGDP9" & line_code == 6L  ~ "real_gdp_mining",
      table == "CAGDP9" & line_code == 10L ~ "real_gdp_utilities",
      table == "CAGDP9" & line_code == 11L ~ "real_gdp_construction",
      table == "CAGDP9" & line_code == 12L ~ "real_gdp_manufacturing_all",
      table == "CAGDP9" & line_code == 13L ~ "real_gdp_durable_manufacturing",
      table == "CAGDP9" & line_code == 25L ~ "real_gdp_nondurable_manufacturing",
      table == "CAGDP9" & line_code == 34L ~ "real_gdp_wholesale_trade",
      table == "CAGDP9" & line_code == 35L ~ "real_gdp_retail_trade",
      table == "CAGDP9" & line_code == 36L ~ "real_gdp_transportation",
      table == "CAGDP9" & line_code == 45L ~ "real_gdp_information",
      table == "CAGDP9" & line_code == 50L ~ "real_gdp_finance_real_estate_all",
      table == "CAGDP9" & line_code == 51L ~ "real_gdp_finance_insurance",
      table == "CAGDP9" & line_code == 56L ~ "real_gdp_real_estate",
      table == "CAGDP9" & line_code == 59L ~ "real_gdp_professional_all",
      table == "CAGDP9" & line_code == 60L ~ "real_gdp_professional_scientific",
      table == "CAGDP9" & line_code == 64L ~ "real_gdp_professional_management",
      table == "CAGDP9" & line_code == 65L ~ "real_gdp_professional_admin_support",
      
      table == "CAGDP9" & line_code == 68L ~ "real_gdp_education_all",
      table == "CAGDP9" & line_code == 69L ~ "real_gdp_education",
      table == "CAGDP9" & line_code == 70L ~ "real_gdp_health",
      
      table == "CAGDP9" & line_code == 75L ~ "real_gdp_arts_food_all",
      table == "CAGDP9" & line_code == 76L ~ "real_gdp_arts_entertainment",
      table == "CAGDP9" & line_code == 79L ~ "real_gdp_accomodation_food",
      
      table == "CAGDP9" & line_code == 82L ~ "real_gdp_other",
      table == "CAGDP9" & line_code == 83L ~ "real_gdp_gov_enterprises",
      table == "CAGDP9" & line_code == 87L ~ "real_gdp_natural_resources_all",
      table == "CAGDP9" & line_code == 88L ~ "real_gdp_trade_all",
      table == "CAGDP9" & line_code == 89L ~ "real_gdp_transport_utilities_all",
      table == "CAGDP9" & line_code == 90L ~ "real_gdp_manufacturing_info_all",
      table == "CAGDP9" & line_code == 91L ~ "real_gdp_private_goods_producing_industries",
      table == "CAGDP9" & line_code == 92L ~ "real_gdp_private_services_providing_industries",
      
      # MARPP
      table == "MARPP" & line_code == 1L ~ "rpp_real_personal_income",
      table == "MARPP" & line_code == 2L ~ "rpp_real_pc_income",
      table == "MARPP" & line_code == 3L ~ "rpp_all_items",
      table == "MARPP" & line_code == 4L ~ "rpp_goods",
      table == "MARPP" & line_code == 5L ~ "rpp_services_rents",
      table == "MARPP" & line_code == 6L ~ "rpp_services_utilities",
      table == "MARPP" & line_code == 7L ~ "rpp_services_other",
      table == "MARPP" & line_code == 8L ~ "rpp_price_deflator",
      
      # SARPP
      table == "SARPP" & line_code == 1L ~ "rpp_real_personal_income",
      table == "SARPP" & line_code == 2L ~ "rpp_real_pc_income",
      table == "SARPP" & line_code == 3L ~ "rpp_real_consumption",
      table == "SARPP" & line_code == 4L ~ "rpp_real_pc_consumption",
      table == "SARPP" & line_code == 5L ~ "rpp_all_items",
      table == "SARPP" & line_code == 6L ~ "rpp_goods",
      table == "SARPP" & line_code == 7L ~ "rpp_services_rents",
      table == "SARPP" & line_code == 8L ~ "rpp_services_utilities",
      table == "SARPP" & line_code == 9L ~ "rpp_services_other",
      table == "SARPP" & line_code == 10L ~ "rpp_price_deflator",
      TRUE ~ stringr::str_to_lower(stringr::str_replace_all(line_desc, "[^A-Za-z0-9]+", "_"))
    ),
    metric_label   = line_desc,
    include_in_wide= dplyr::if_else(table %in% c("CAINC1","CAGDP2","CAGDP9","MARPP","SARPP") & line_code %in% c(1L,2L,3L), TRUE, FALSE),
    topic          = dplyr::case_when(
      table %in% c("CAINC1","CAINC4") ~ "income",
      table %in% c("CAGDP2","CAGDP9") ~ "gdp",
      table == "MARPP"                ~ "prices",
      TRUE ~ "other"
    ),
    vintage  = format(Sys.Date(), "%Y-%m-%d")
  )  %>%
  dplyr::select(table, line_code, line_desc_clean, metric_key, metric_label, include_in_wide, 
                naics_raw, is_aggregate, topic, vintage) %>%
  dplyr::distinct()

## Write back to the Silver layer ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_metrics_ref"),
                  line_codes_clean, overwrite = TRUE)

## Update include_in_wide as needed ----

# Disconnect our DB ----
dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)