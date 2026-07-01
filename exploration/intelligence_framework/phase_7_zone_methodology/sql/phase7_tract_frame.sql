-- Phase 7 tract KPI frame
-- This query preserves the current app behavior exactly:
--   1. start from the tract-to-county-to-CBSA crosswalk surface
--   2. keep the current broad CBSA scope from the crosswalk
--   3. pull the latest available tract year independently per source table
--   4. left join each source table once onto the tract base
--
-- The `/*__CBSA_FILTER__*/` token is replaced by the app when a CBSA subset is
-- requested. Leaving it blank returns the full tract universe.

with base as (
    select distinct
        xwt.tract_geoid,
        xwc.cbsa_code,
        xwc.county_geoid
    from silver.xwalk_tract_county xwt
    join silver.xwalk_cbsa_county xwc
        on xwc.county_geoid = (xwt.state_fip || xwt.county_fip)
    where 1 = 1
    /*__CBSA_FILTER__*/
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
    from gold.population_demographics
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.population_demographics
          where geo_level = 'tract'
      )
),

migration_wide as (
    select
        geo_id as tract_geoid,
        year as migration_wide_year,
        pct_foreign_born,
        pct_same_house
    from gold.migration_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.migration_wide
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
    from gold.housing_core_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.housing_core_wide
          where geo_level = 'tract'
      )
),

social_infra_wide as (
    select
        geo_id as tract_geoid,
        year as social_infra_wide_year,
        pct_no_internet_access
    from gold.social_infra_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.social_infra_wide
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
    from gold.transport_built_form_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.transport_built_form_wide
          where geo_level = 'tract'
      )
),

transport_built_form_sld as (
    -- SLD is a tract-ready 2021 baseline. We keep it separate from the ACS
    -- transport panel in Gold, but Phase 7 now joins the tract fields directly.
    select
        geo_id as tract_geoid,
        year as transport_built_form_sld_year,
        walkability_index,
        jobs_access_45min_transit
    from gold.transport_built_form_sld
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.transport_built_form_sld
          where geo_level = 'tract'
      )
),

environment_ejs as (
    -- The environment Gold table is mixed-vintage at tract level today, so
    -- Phase 7 pulls each metric from the latest tract year where it is present.
    select
        geo_id as tract_geoid,
        year as environment_ejs_year,
        ejs_pm25
    from gold.environment_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.environment_wide
          where geo_level = 'tract'
            and ejs_pm25 is not null
      )
),

environment_fema as (
    select
        geo_id as tract_geoid,
        year as environment_fema_year,
        fema_risk_score
    from gold.environment_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.environment_wide
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
    from gold.economics_income_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.economics_income_wide
          where geo_level = 'tract'
      )
),

economics_labor_wide as (
    select
        geo_id as tract_geoid,
        year as economics_labor_wide_year,
        pct_unemployment_rate
    from gold.economics_labor_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.economics_labor_wide
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
    from gold.economics_lodes_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.economics_lodes_wide
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

    -- These audit columns make the mixed-vintage contract visible in the
    -- output so downstream checks can assert the current source-year policy.
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
