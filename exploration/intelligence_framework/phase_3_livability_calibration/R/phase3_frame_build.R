build_phase3_livability_frame <- function(con) {
  livability_df <- DBI::dbGetQuery(con, "
with spine as (
    select
        geo_id,
        geo_name,
        pop_total,
        year as spine_year
    from gold.population_demographics
    where geo_level = 'cbsa'
      and year = 2024
      and pop_total >= 100000
      and geo_name not like '%, PR'
),
affordability_latest as (
    select *
    from (
        select
            geo_id,
            year as affordability_year,
            value_to_income,
            pct_rent_burden_30plus,
            row_number() over (partition by geo_id order by year desc) as rn
        from gold.affordability_wide
        where geo_level = 'cbsa'
    )
    where rn = 1
),
income_latest as (
    select *
    from (
        select
            geo_id,
            year as income_year,
            pov_rate,
            row_number() over (partition by geo_id order by year desc) as rn
        from gold.economics_income_wide
        where geo_level = 'cbsa'
    )
    where rn = 1
),
housing_latest as (
    select *
    from (
        select
            geo_id,
            year as housing_year,
            vacancy_rate,
            permits_per_1000_housing_units,
            permits_share_units_5_plus,
            pct_struct_mobile,
            pct_struct_small_mf,
            pct_struct_mid_mf,
            row_number() over (partition by geo_id order by year desc) as rn
        from gold.housing_core_wide
        where geo_level = 'cbsa'
    )
    where rn = 1
),
transport_latest as (
    select *
    from (
        select
            geo_id,
            year as transport_year,
            pct_commute_walk,
            pct_commute_wfh,
            pct_hh_0_vehicles,
            pop_weighted_density_sqmi,
            row_number() over (partition by geo_id order by year desc) as rn
        from gold.transport_built_form_wide
        where geo_level = 'cbsa'
    )
    where rn = 1
),
social_infra_latest as (
    select *
    from (
        select
            geo_id,
            year as social_infra_year,
            pct_no_internet_access,
            row_number() over (partition by geo_id order by year desc) as rn
        from gold.social_infra_wide
        where geo_level = 'cbsa'
    )
    where rn = 1
),
health_latest as (
    select *
    from (
        select
            geo_id,
            year as health_year,
            premature_death_rate,
            mental_health_provider_ratio,
            drug_overdose_death_rate,
            pct_uninsured_adults,
            preventable_hospital_stay_rate,
            firearm_fatality_rate,
            motor_vehicle_crash_rate,
            row_number() over (partition by geo_id order by year desc) as rn
        from gold.health_wide
        where geo_level = 'cbsa'
    )
    where rn = 1
),
environment_latest as (
    select *
    from (
        select
            geo_id,
            year as environment_year,
            unhealthy_days as aqi_unhealthy_days,
            fema_risk_score,
            row_number() over (partition by geo_id order by year desc) as rn
        from gold.environment_wide
        where geo_level = 'cbsa'
    )
    where rn = 1
),
sld_latest as (
    select *
    from (
        select
            geo_id,
            year as sld_year,
            walkability_index,
            jobs_access_45min_transit,
            row_number() over (partition by geo_id order by year desc) as rn
        from gold.transport_built_form_sld
        where geo_level = 'cbsa'
    )
    where rn = 1
),
food_latest as (
    select *
    from (
        select
            geo_id,
            year as food_access_year,
            pct_population_low_income_low_access_1_10,
            row_number() over (partition by geo_id order by year desc) as rn
        from gold.food_access_wide
        where geo_level = 'cbsa'
    )
    where rn = 1
)
select
    spine.geo_id as cbsa_code,
    spine.geo_name as cbsa_name,
    spine.pop_total,
    spine.spine_year,
    affordability.affordability_year,
    income.income_year,
    housing.housing_year,
    transport.transport_year,
    social_infra.social_infra_year,
    health.health_year,
    environment.environment_year,
    sld.sld_year,
    food.food_access_year,
    affordability.value_to_income,
    affordability.pct_rent_burden_30plus,
    income.pov_rate,
    housing.permits_per_1000_housing_units,
    housing.permits_share_units_5_plus,
    housing.pct_struct_mobile,
    housing.pct_struct_small_mf,
    housing.pct_struct_mid_mf,
    health.premature_death_rate,
    health.mental_health_provider_ratio,
    health.drug_overdose_death_rate,
    health.pct_uninsured_adults,
    health.preventable_hospital_stay_rate,
    health.firearm_fatality_rate,
    health.motor_vehicle_crash_rate,
    transport.pct_commute_walk,
    transport.pct_commute_wfh,
    housing.vacancy_rate,
    transport.pct_hh_0_vehicles,
    social_infra.pct_no_internet_access,
    sld.walkability_index,
    sld.jobs_access_45min_transit,
    food.pct_population_low_income_low_access_1_10,
    transport.pop_weighted_density_sqmi,
    environment.aqi_unhealthy_days,
    environment.fema_risk_score
from spine
left join affordability_latest affordability on spine.geo_id = affordability.geo_id
left join income_latest income on spine.geo_id = income.geo_id
left join housing_latest housing on spine.geo_id = housing.geo_id
left join transport_latest transport on spine.geo_id = transport.geo_id
left join social_infra_latest social_infra on spine.geo_id = social_infra.geo_id
left join health_latest health on spine.geo_id = health.geo_id
left join environment_latest environment on spine.geo_id = environment.geo_id
left join sld_latest sld on spine.geo_id = sld.geo_id
left join food_latest food on spine.geo_id = food.geo_id
order by spine.pop_total desc
")

  stopifnot(nrow(livability_df) == 396)
  livability_df
}
