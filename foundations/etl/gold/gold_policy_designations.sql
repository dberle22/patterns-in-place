-- Gold policy designation dimension
-- Grain: one row per tract designation record.
-- Static Opportunity Zone rows carry null year; annual FHFA underserved rows
-- carry the release year.

create or replace table patterns_in_place.gold.dim_policy_designations as
with oz_rows as (
    select
        geo_level,
        geo_id,
        geo_name,
        cast(null as integer) as year,
        is_opportunity_zone,
        oz_tract_count,
        total_tract_count,
        pct_oz_tracts,
        cast(null as boolean) as is_underserved,
        cast(null as boolean) as is_low_income_area,
        cast(null as boolean) as is_minority_area,
        cast(null as boolean) as is_disaster_area,
        cast(null as integer) as underserved_tract_count,
        cast(null as double) as pct_underserved_tracts
    from patterns_in_place.silver.opportunity_zones
),
fhfa_rows as (
    select
        geo_level,
        geo_id,
        geo_name,
        year,
        cast(null as boolean) as is_opportunity_zone,
        cast(null as integer) as oz_tract_count,
        total_tract_count,
        cast(null as double) as pct_oz_tracts,
        is_underserved,
        is_low_income_area,
        is_minority_area,
        is_disaster_area,
        underserved_tract_count,
        pct_underserved_tracts
    from patterns_in_place.silver.fhfa_underserved
)
select *
from oz_rows

union all

select *
from fhfa_rows
;
