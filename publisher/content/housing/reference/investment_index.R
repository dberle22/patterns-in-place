library(tidyverse)
library(lubridate)
library(magrittr)
library(plotly)
library(tidytext)
library(scales)
library(tidycensus)
library(tigris)
library(sf)
library(readxl)
library(httr)
library(jsonlite)
library(DT)
library(ggbeeswarm)
library(knitr)
library(factoextra)
library(corrplot)
library(leaflet)
library(ggrepel)

# Investment Index ----

# **Purpose:**
#  Score each CBSA for overall investment attractiveness.

# **Steps:**
#  1. Select KPIs (normalized to z-scores or 0-1 scaling). Suggested:
#  2. Assign Weights
#   - Manual
#   - Regression
#   - PCA
# 3. Calculate Score
# 4. Visuals
#   - Top/Bottom 20 CBSAs by Index
#   - Map: Colored by quintile
#   - Scatter Plot: Index vs 1-2 KPIs

## CBSA ----

### Select KPIs ----

# Ingest Z Score KPIs
cbsa_kpi_scaled_z <- read_csv("Desktop/real_estate_investment/data/analytics/cbsa_scaled_z_kpi_core.csv")

# Select Variables
cbsa_kpi_scaled_select <- cbsa_kpi_scaled_z %>%
  filter(cbsa_type == "Metro Area") %>%
  select(GEOID:counties, z_pop_growth_5yr, z_pop_education_rate, 
         z_eco_unemployment_rate, z_eco_unemployment_stability, 
         z_eco_wage_per_worker, z_eco_wage_growth_5yr, 
         z_eco_industry_entropy, z_afford_rental_index, 
         z_afford_hud_rent_price_ratio, z_afford_rpp, 
         z_housing_vacancy_rate, z_housing_hpi_growth_5yr, 
         z_housing_permits_per_1000, z_housing_units_per_capita) 

### Calculate the index with manual weights ----
weights <- c(
  z_pop_growth_5yr = 0.10,
  z_pop_education_rate = 0.05,
  z_eco_unemployment_rate = -0.05,
  z_eco_unemployment_stability = -0.05,
  z_eco_wage_per_worker = 0.10,
  z_eco_wage_growth_5yr = 0.10,
  z_eco_industry_entropy = 0.05,
  z_afford_rental_index = 0.10,
  z_afford_hud_rent_price_ratio = 0.05,
  z_afford_rpp = 0.05,
  z_housing_vacancy_rate = -0.05,
  z_housing_hpi_growth_5yr = 0.15,
  z_housing_permits_per_1000 = 0.05,
  z_housing_units_per_capita = 0.05
)

# Using the input index
index_input <- cbsa_kpi_scaled_select %>%
  rowwise() %>%
  mutate(investment_index = sum(c_across(names(weights)) * weights)) %>%
  ungroup()

# Scale the index from 0-100 for better readability
# Create Index Tiers as simple buckets
index_input <- index_input %>%
  mutate(investment_index_scaled = scales::rescale(investment_index, to = c(0, 100)),
         investment_tier = ntile(investment_index, 5))

# Create an outlier column for data outside of one SD
index_mean <- mean(index_input$investment_index, na.rm = TRUE)
index_sd <- sd(index_input$investment_index, na.rm = TRUE)

index_input <- index_input %>%
  mutate(index_outlier = case_when(
    investment_index >= index_mean + index_sd ~ "High Performer",
    investment_index <= index_mean - index_sd ~ "Under Performer",
    TRUE ~ "Middle Tier"
  ),
  GEOID = as.character(GEOID))

# Create the final DF
cbsa_index_final <- index_input %>%
  select(GEOID, investment_index = investment_index_scaled, 
         investment_tier, index_outlier)

# Write to csv
write_csv(cbsa_index_final, "Desktop/real_estate_investment/data/analytics/cbsa_investmnet_index.csv")


