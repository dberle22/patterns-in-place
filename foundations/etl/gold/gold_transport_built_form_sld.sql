-- Gold EPA Smart Location baseline mart
-- Grain: one row per geo_level + geo_id + year
-- Current scope: county, CBSA, and state rows for the 2021 baseline

create or replace table patterns_in_place.gold.transport_built_form_sld as
select
    lower(geo_level) as geo_level,
    geo_id,
    geo_name,
    year,
    state_abbr,
    total_population,
    total_employment,
    housing_units,
    households,
    land_acres_unprotected,
    block_group_count,
    block_group_count_transit_non_null,
    block_group_count_walkability_non_null,
    transit_population_coverage_share,
    walkability_population_coverage_share,
    walkability_index,
    employment_housing_mix,
    employment_mix,
    street_intersection_density,
    auto_oriented_intersection_share,
    transit_service_density,
    transit_frequency_peak,
    distance_to_transit,
    jobs_access_45min_transit,
    workers_access_45min_transit,
    jobs_access_45min_auto,
    workers_access_45min_auto,
    employment_density_gross,
    population_density_gross,
    housing_density_gross
from patterns_in_place.silver.epa_sld
;
