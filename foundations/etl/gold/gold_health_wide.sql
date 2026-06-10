-- Gold health mart
-- Grain: one row per geo_level + geo_id + year
-- Notes:
--   * This Gold surface is intentionally the approved CHR Silver contract
--     carried through directly at county + CBSA grain across the annual
--     analytic backfill window.
--   * `air_pollution_pm25` and `adverse_climate_events` remain lagged holdover
--     fields pending direct EPA and FEMA/environment coverage in later tracks.

create or replace table patterns_in_place.gold.health_wide as
with health_base as (
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
        poor_mental_health_days,
        adult_obesity,
        physical_inactivity,
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
),
health_trends as (
    select
        *,
        lag(year, 1) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_year_1,
        lag(year, 5) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_year_5,
        lag(life_expectancy, 1) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_life_expectancy_1,
        lag(life_expectancy, 5) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_life_expectancy_5,
        lag(premature_death_rate, 1) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_premature_death_rate_1,
        lag(premature_death_rate, 5) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_premature_death_rate_5,
        lag(pct_uninsured_adults, 1) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_pct_uninsured_adults_1,
        lag(pct_uninsured_adults, 5) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_pct_uninsured_adults_5,
        lag(adult_obesity, 5) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_adult_obesity_5,
        lag(physical_inactivity, 5) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_physical_inactivity_5,
        lag(poor_mental_health_days, 5) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_poor_mental_health_days_5,
        lag(primary_care_ratio, 5) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_primary_care_ratio_5,
        lag(preventable_hospital_stay_rate, 5) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_preventable_hospital_stay_rate_5,
        lag(air_pollution_pm25, 5) over (
            partition by geo_level, geo_id
            order by year
        ) as prev_air_pollution_pm25_5
    from health_base
)
select
    geo_level,
    geo_id,
    geo_name,
    year,
    life_expectancy,
    case
        when prev_year_1 = year - 1 then life_expectancy - prev_life_expectancy_1
        else null
    end as life_expectancy_change_1yr,
    case
        when prev_year_5 = year - 5 then life_expectancy - prev_life_expectancy_5
        else null
    end as life_expectancy_change_5yr,
    premature_death_rate,
    case
        when prev_year_1 = year - 1 then premature_death_rate - prev_premature_death_rate_1
        else null
    end as premature_death_rate_change_1yr,
    case
        when prev_year_5 = year - 5 then premature_death_rate - prev_premature_death_rate_5
        else null
    end as premature_death_rate_change_5yr,
    premature_age_adjusted_mortality,
    child_mortality_rate,
    infant_mortality_rate,
    drug_overdose_death_rate,
    poor_mental_health_days,
    case
        when prev_year_5 = year - 5 then poor_mental_health_days - prev_poor_mental_health_days_5
        else null
    end as poor_mental_health_days_change_5yr,
    adult_obesity,
    case
        when prev_year_5 = year - 5 then adult_obesity - prev_adult_obesity_5
        else null
    end as adult_obesity_change_5yr,
    physical_inactivity,
    case
        when prev_year_5 = year - 5 then physical_inactivity - prev_physical_inactivity_5
        else null
    end as physical_inactivity_change_5yr,
    pct_uninsured_adults,
    case
        when prev_year_1 = year - 1 then pct_uninsured_adults - prev_pct_uninsured_adults_1
        else null
    end as pct_uninsured_adults_change_1yr,
    case
        when prev_year_5 = year - 5 then pct_uninsured_adults - prev_pct_uninsured_adults_5
        else null
    end as pct_uninsured_adults_change_5yr,
    primary_care_ratio,
    case
        when prev_year_5 = year - 5 then primary_care_ratio - prev_primary_care_ratio_5
        else null
    end as primary_care_ratio_change_5yr,
    mental_health_provider_ratio,
    preventable_hospital_stay_rate,
    case
        when prev_year_5 = year - 5 then preventable_hospital_stay_rate - prev_preventable_hospital_stay_rate_5
        else null
    end as preventable_hospital_stay_rate_change_5yr,
    food_insecurity_rate,
    social_associations_per_10k,
    child_care_cost_burden_rate,
    hs_graduation_rate,
    air_pollution_pm25,
    case
        when prev_year_5 = year - 5 then air_pollution_pm25 - prev_air_pollution_pm25_5
        else null
    end as air_pollution_pm25_change_5yr,
    adverse_climate_events,
    pct_access_to_parks,
    homicide_rate,
    firearm_fatality_rate,
    motor_vehicle_crash_rate,
    reading_score_index,
    math_score_index
from health_trends
;
