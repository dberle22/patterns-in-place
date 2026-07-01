-- Phase 7 descriptive-only tract audit surface
-- This query intentionally pulls held-out naming / interpretation fields that we
-- decided not to use in the clustering vector. The output is designed to join
-- onto `zone_scores.parquet` by `tract_geoid` so we can pressure-test cluster
-- names without changing the model inputs.

with population_demographics as (
    select
        geo_id as tract_geoid,
        year as population_demographics_year,
        median_age,
        diversity_index,
        pct_white_nh,
        pct_black_nh,
        pct_asian_nh,
        pct_hispanic
    from gold.population_demographics
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.population_demographics
          where geo_level = 'tract'
      )
),

housing_core_wide as (
    select
        geo_id as tract_geoid,
        year as housing_core_wide_year,
        median_home_value
    from gold.housing_core_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.housing_core_wide
          where geo_level = 'tract'
      )
),

economics_income_wide as (
    select
        geo_id as tract_geoid,
        year as economics_income_wide_year,
        median_hh_income
    from gold.economics_income_wide
    where geo_level = 'tract'
      and year = (
          select max(year)
          from gold.economics_income_wide
          where geo_level = 'tract'
      )
)

select
    zone_inputs.tract_geoid,
    zone_inputs.cbsa_code,
    zone_inputs.county_geoid,
    dim_geo.geo_name,
    dim_geo.cbsa_name,
    coalesce(dim_geo.county_name_long, dim_geo.county_name) as county_name,
    population_demographics.median_age,
    population_demographics.diversity_index,
    population_demographics.pct_white_nh,
    population_demographics.pct_black_nh,
    population_demographics.pct_asian_nh,
    population_demographics.pct_hispanic,
    housing_core_wide.median_home_value,
    economics_income_wide.median_hh_income,
    population_demographics.population_demographics_year,
    housing_core_wide.housing_core_wide_year,
    economics_income_wide.economics_income_wide_year
from gold.intelligence_zone_inputs as zone_inputs
left join gold.dim_geo as dim_geo
    on dim_geo.geo_level = 'tract'
   and dim_geo.geo_id = zone_inputs.tract_geoid
left join population_demographics
    on population_demographics.tract_geoid = zone_inputs.tract_geoid
left join housing_core_wide
    on housing_core_wide.tract_geoid = zone_inputs.tract_geoid
left join economics_income_wide
    on economics_income_wide.tract_geoid = zone_inputs.tract_geoid
order by zone_inputs.tract_geoid
