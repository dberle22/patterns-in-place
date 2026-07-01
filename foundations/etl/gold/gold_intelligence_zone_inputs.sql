-- This script materializes the Phase 7 tract KPI frame into Gold so the
-- Streamlit EDA app and later zone-model runners can share one governed input
-- surface instead of rebuilding the wide tract join in application code.

create or replace table patterns_in_place.gold.intelligence_zone_inputs as

with base as (
    select distinct
        xwt.tract_geoid,
        xwc.cbsa_code,
        xwc.county_geoid
    from patterns_in_place.silver.xwalk_tract_county xwt
    join patterns_in_place.silver.xwalk_cbsa_county xwc
        on xwc.county_geoid = (xwt.state_fip || xwt.county_fip)
),

population_demographics as (
    select
        geo_id as tract_geoid,
        year as population_demographics_year,
        diversity_index,
        pct_hispanic,
        pct_black_nh,
        pct_asian_nh,
        pct_age_over_64,
        pct_ba_plus,
        pct_ba_plus_change_3yr,
        pct_ba_plus_change_5yr
    from patterns_in_place.gold.population_demographics
    where geo_level = 'tract'
      and year = (
          select max(year)
          from patterns_in_place.gold.population_demographics
          where geo_level = 'tract'
      )
),

migration_wide as (
    select
        geo_id as tract_geoid,
        year as migration_wide_year,
        pct_foreign_born,
        pct_same_house
    from patterns_in_place.gold.migration_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from patterns_in_place.gold.migration_wide
          where geo_level = 'tract'
      )
),

housing_core_wide as (
    select
        geo_id as tract_geoid,
        year as housing_core_wide_year,
        owner_occ_rate,
        pct_struct_multifam,
        pct_rent_burden_30plus,
        median_gross_rent,
        median_home_value,
        vacancy_rate
    from patterns_in_place.gold.housing_core_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from patterns_in_place.gold.housing_core_wide
          where geo_level = 'tract'
      )
),

social_infra_wide as (
    select
        geo_id as tract_geoid,
        year as social_infra_wide_year,
        pct_no_internet_access
    from patterns_in_place.gold.social_infra_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from patterns_in_place.gold.social_infra_wide
          where geo_level = 'tract'
      )
),

transport_built_form_wide as (
    select
        geo_id as tract_geoid,
        year as transport_built_form_wide_year,
        pop_weighted_density_sqmi,
        pct_hh_0_vehicles,
        pct_commute_walk,
        pct_commute_transit
    from patterns_in_place.gold.transport_built_form_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from patterns_in_place.gold.transport_built_form_wide
          where geo_level = 'tract'
      )
),

transport_built_form_sld as (
    -- SLD is a one-time 2021 baseline, not part of the recurring ACS transport
    -- panel. We still carry the tract fields into Phase 7 because the live
    -- tract join coverage is now high enough to support exploratory use.
    select
        geo_id as tract_geoid,
        year as transport_built_form_sld_year,
        walkability_index,
        jobs_access_45min_transit
    from patterns_in_place.gold.transport_built_form_sld
    where geo_level = 'tract'
      and year = (
          select max(year)
          from patterns_in_place.gold.transport_built_form_sld
          where geo_level = 'tract'
      )
),

environment_ejs as (
    -- EJScreen and FEMA do not currently land on the same tract-year slice.
    -- Pull each metric from its own latest non-null tract vintage so the Phase 7
    -- frame reflects the best available value rather than a table-wide max year.
    select
        geo_id as tract_geoid,
        year as environment_ejs_year,
        ejs_pm25
    from patterns_in_place.gold.environment_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from patterns_in_place.gold.environment_wide
          where geo_level = 'tract'
            and ejs_pm25 is not null
      )
),

environment_fema as (
    select
        geo_id as tract_geoid,
        year as environment_fema_year,
        fema_risk_score
    from patterns_in_place.gold.environment_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from patterns_in_place.gold.environment_wide
          where geo_level = 'tract'
            and fema_risk_score is not null
      )
),

economics_income_wide as (
    select
        geo_id as tract_geoid,
        year as economics_income_wide_year,
        median_hh_income,
        pov_rate,
        pov_rate_change_3yr,
        pov_rate_change_5yr
    from patterns_in_place.gold.economics_income_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from patterns_in_place.gold.economics_income_wide
          where geo_level = 'tract'
      )
),

economics_labor_wide as (
    select
        geo_id as tract_geoid,
        year as economics_labor_wide_year,
        pct_unemployment_rate
    from patterns_in_place.gold.economics_labor_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from patterns_in_place.gold.economics_labor_wide
          where geo_level = 'tract'
      )
),

economics_lodes_wide as (
    select
        geo_id as tract_geoid,
        year as economics_lodes_wide_year,
        jobs_to_workers_ratio as jobs_per_resident,
        pct_jobs_earnings_high as pct_jobs_high_wage,
        pct_jobs_ind_professional_scientific_technical as pct_jobs_professional_services
    from patterns_in_place.gold.economics_lodes_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from patterns_in_place.gold.economics_lodes_wide
          where geo_level = 'tract'
      )
)

select
    base.tract_geoid,
    base.cbsa_code,
    base.county_geoid,
    population_demographics.diversity_index,
    population_demographics.pct_hispanic,
    population_demographics.pct_black_nh,
    population_demographics.pct_asian_nh,
    population_demographics.pct_age_over_64,
    population_demographics.pct_ba_plus,
    migration_wide.pct_foreign_born,
    migration_wide.pct_same_house,
    housing_core_wide.owner_occ_rate,
    housing_core_wide.pct_struct_multifam,
    transport_built_form_wide.pop_weighted_density_sqmi,
    housing_core_wide.pct_rent_burden_30plus,
    housing_core_wide.median_gross_rent,
    housing_core_wide.median_home_value,
    housing_core_wide.vacancy_rate,
    transport_built_form_wide.pct_hh_0_vehicles,
    transport_built_form_wide.pct_commute_walk,
    transport_built_form_wide.pct_commute_transit,
    transport_built_form_sld.walkability_index,
    transport_built_form_sld.jobs_access_45min_transit,
    social_infra_wide.pct_no_internet_access,
    environment_ejs.ejs_pm25,
    environment_fema.fema_risk_score,
    economics_income_wide.median_hh_income,
    economics_income_wide.pov_rate,
    economics_income_wide.pov_rate_change_3yr,
    economics_labor_wide.pct_unemployment_rate,
    population_demographics.pct_ba_plus_change_3yr,
    economics_lodes_wide.jobs_per_resident,
    economics_lodes_wide.pct_jobs_high_wage,
    economics_lodes_wide.pct_jobs_professional_services,
    population_demographics.population_demographics_year,
    migration_wide.migration_wide_year,
    housing_core_wide.housing_core_wide_year,
    social_infra_wide.social_infra_wide_year,
    transport_built_form_wide.transport_built_form_wide_year,
    transport_built_form_sld.transport_built_form_sld_year,
    environment_ejs.environment_ejs_year,
    environment_fema.environment_fema_year,
    economics_income_wide.economics_income_wide_year,
    economics_labor_wide.economics_labor_wide_year,
    economics_lodes_wide.economics_lodes_wide_year
from base
left join population_demographics
    on population_demographics.tract_geoid = base.tract_geoid
left join migration_wide
    on migration_wide.tract_geoid = base.tract_geoid
left join housing_core_wide
    on housing_core_wide.tract_geoid = base.tract_geoid
left join social_infra_wide
    on social_infra_wide.tract_geoid = base.tract_geoid
left join transport_built_form_wide
    on transport_built_form_wide.tract_geoid = base.tract_geoid
left join transport_built_form_sld
    on transport_built_form_sld.tract_geoid = base.tract_geoid
left join environment_ejs
    on environment_ejs.tract_geoid = base.tract_geoid
left join environment_fema
    on environment_fema.tract_geoid = base.tract_geoid
left join economics_income_wide
    on economics_income_wide.tract_geoid = base.tract_geoid
left join economics_labor_wide
    on economics_labor_wide.tract_geoid = base.tract_geoid
left join economics_lodes_wide
    on economics_lodes_wide.tract_geoid = base.tract_geoid
