-- Gold health mart
-- Grain: one row per geo_level + geo_id + year
-- Notes:
--   * This first-pass Gold surface is intentionally the approved CHR Silver
--     contract carried through directly at county + CBSA grain.
--   * `air_pollution_pm25` and `adverse_climate_events` remain lagged holdover
--     fields pending direct EPA and FEMA/environment coverage in later tracks.

create or replace table patterns_in_place.gold.health_wide as
select
    geo_level,
    geo_id,
    geo_name,
    year,
    life_expectancy,
    premature_death_rate,
    premature_age_adjusted_mortality,
    child_mortality_rate,
    infant_mortality_rate,
    drug_overdose_death_rate,
    pct_uninsured_adults,
    primary_care_ratio,
    mental_health_provider_ratio,
    preventable_hospital_stay_rate,
    food_insecurity_rate,
    social_associations_per_10k,
    child_care_cost_burden_rate,
    hs_graduation_rate,
    air_pollution_pm25,
    adverse_climate_events,
    pct_access_to_parks,
    homicide_rate,
    firearm_fatality_rate,
    motor_vehicle_crash_rate,
    reading_score_index,
    math_score_index
from patterns_in_place.silver.chr_health_outcomes
;
