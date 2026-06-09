-- Gold food access baseline mart
-- Grain: one row per geo_level + geo_id + year
-- Current scope: tract, county, and CBSA rows for the 2019 USDA Food Access
-- Research Atlas baseline

create or replace table patterns_in_place.gold.food_access_wide as
select
    lower(geo_level) as geo_level,
    geo_id,
    geo_name,
    year,
    population_total,
    population_low_access_1,
    population_low_access_1_10,
    population_low_income_low_access_1,
    population_low_income_low_access_1_10,
    total_tract_count,
    lila_tract_count_1_10,
    low_income_tract_count,
    low_access_tract_count_1_10,
    pct_lila_tracts_1_and_10,
    pct_low_income_tracts,
    pct_low_access_tracts_1_and_10,
    pct_population_low_access_1,
    pct_population_low_access_1_10,
    pct_population_low_income_low_access_1,
    pct_population_low_income_low_access_1_10,
    poverty_rate,
    median_family_income
from patterns_in_place.silver.usda_food_atlas
;
