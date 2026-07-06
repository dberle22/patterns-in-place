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

# Overheat Gap Index ----
# Overheated vs. Undervalued Market Detection

## Concept

# - **Overheated Market:** High growth in prices or rents, but without supportive fundamentals (e.g. population, wage, or permit growth).
# 
# - **Undervalued Market:** Lagging prices/rents relative to strong fundamentals might suggest investment upside.
# 
# ## Define Indicators and Scale
# 
# **Price Related KPIs:** Symptoms of Overheating
# 
# - home_value
# - gross_rent
# - rent_growth_5yr
# - hpi_growth_5yr
# 
# **Fundamentals:** Support for Growth
# 
# - pop_growth_5yr - more people = more demand
# - eco_wage_growth_5yr - higher wages support prices
# - housing_permits_per_1000 - permits suggest supply can keep up
# - housing_units_per_capita - more units = less pressure
# - eco_unemployment_stability (low = good) - stable unemployment is good
# - afford_rental_index (low = overpriced) - higher index = more affordable
# - afford_hud_rent_price_ratio (low = overpriced) - higher ratio = rent closer to fair

## CBSA ----

### Ingest and select data ----
# Ingest Z Score KPIs
cbsa_kpi_scaled_z <- read_csv("Desktop/real_estate_investment/data/analytics/cbsa_scaled_z_kpi_core.csv")

# Select Variables
cbsa_kpi_scaled_select <- cbsa_kpi_scaled_z %>%
  filter(cbsa_type == "Metro Area") %>%
  select(GEOID:counties, z_afford_home_value, z_afford_gross_rent, 
         z_afford_rent_growth_5yr, z_housing_hpi_growth_5yr, 
         z_pop_growth_5yr, z_eco_wage_growth_5yr, z_housing_permits_per_1000, 
         z_housing_units_per_capita, z_eco_unemployment_stability, 
         z_afford_rental_index, z_afford_hud_rent_price_ratio) 


### Create Score and Classify Markets  ----
# 
# - Higher overheat_gap → likely Overheated (Higher scores mean Overheated)
# - Lower overheat_gap (negative) → potentially Undervalued
# 
# You can fine-tune directionality as needed, depending on your interpretation. For example, treating economic stability as a negative here.

cbsa_overheat_score <- cbsa_kpi_scaled_select %>%
  mutate(
    overheating_score = z_afford_home_value + z_afford_gross_rent + z_afford_rent_growth_5yr + z_housing_hpi_growth_5yr,
    support_score = z_pop_growth_5yr + z_eco_wage_growth_5yr + z_housing_permits_per_1000 + z_housing_units_per_capita - z_eco_unemployment_stability + z_afford_rental_index + z_afford_hud_rent_price_ratio,
    overheat_gap = overheating_score - support_score,
    market_type = case_when(
      overheat_gap >= quantile(overheat_gap, 0.9, na.rm = TRUE) ~ "Overheated",
      overheat_gap <= quantile(overheat_gap, 0.1, na.rm = TRUE) ~ "Undervalued",
      TRUE ~ "Neutral"
    ),
    overheat_gap_score = scales::rescale(overheat_gap, to = c(0, 100))
  )

### Select final variables ----
cbsa_overheat_score_final <- cbsa_overheat_score %>%
  select(GEOID, overheating_score:overheat_gap_score)

# Write to csv
write_csv(cbsa_overheat_score_final, "Desktop/real_estate_investment/data/analytics/cbsa_overheat_gap_score.csv")


