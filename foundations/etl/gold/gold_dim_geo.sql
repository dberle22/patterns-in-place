-- Canonical geography dimension for chatbot and dashboard joins.
-- One row per geography entity across the currently well-modeled levels:
-- us, region, division, state, cbsa, county, tract.

create or replace table patterns_in_place.gold.dim_geo as
with region_lookup as (
    select distinct
        case
            when census_region = 'Northeast' then '1'
            when census_region = 'Midwest' then '2'
            when census_region = 'South' then '3'
            when census_region = 'West' then '4'
        end as region_id,
        census_region as region_name
    from patterns_in_place.silver.xwalk_state_region
),
division_lookup as (
    select distinct
        case
            when census_division = 'New England' then '1'
            when census_division = 'Middle Atlantic' then '2'
            when census_division = 'East North Central' then '3'
            when census_division = 'West North Central' then '4'
            when census_division = 'South Atlantic' then '5'
            when census_division = 'East South Central' then '6'
            when census_division = 'West South Central' then '7'
            when census_division = 'Mountain' then '8'
            when census_division = 'Pacific' then '9'
        end as division_id,
        census_division as division_name,
        case
            when census_region = 'Northeast' then '1'
            when census_region = 'Midwest' then '2'
            when census_region = 'South' then '3'
            when census_region = 'West' then '4'
        end as region_id
    from patterns_in_place.silver.xwalk_state_region
),
state_base as (
    select
        sr.state_fips,
        sr.state_name,
        sr.state_abbr,
        sr.census_region as region_name,
        sr.census_division as division_name,
        case
            when sr.census_region = 'Northeast' then '1'
            when sr.census_region = 'Midwest' then '2'
            when sr.census_region = 'South' then '3'
            when sr.census_region = 'West' then '4'
        end as region_id,
        case
            when sr.census_division = 'New England' then '1'
            when sr.census_division = 'Middle Atlantic' then '2'
            when sr.census_division = 'East North Central' then '3'
            when sr.census_division = 'West North Central' then '4'
            when sr.census_division = 'South Atlantic' then '5'
            when sr.census_division = 'East South Central' then '6'
            when sr.census_division = 'West South Central' then '7'
            when sr.census_division = 'Mountain' then '8'
            when sr.census_division = 'Pacific' then '9'
        end as division_id,
        2023 as vintage,
        'silver.xwalk_state_region' as source
    from patterns_in_place.silver.xwalk_state_region sr
),
county_cbsa as (
    select distinct
        county_geoid,
        cbsa_code,
        cbsa_name,
        cbsa_type,
        county_flag
    from patterns_in_place.silver.xwalk_cbsa_county
),
county_base as (
    select
        cs.county_geoid,
        cs.county_name,
        cs.county_name_long,
        cs.state_fip as state_fips,
        cs.state_abbr,
        cb.cbsa_code,
        cb.cbsa_name,
        cb.cbsa_type,
        cb.county_flag,
        cs.vintage,
        cs.source
    from patterns_in_place.silver.xwalk_county_state cs
    left join county_cbsa cb
        on cs.county_geoid = cb.county_geoid
),
county_enriched as (
    select
        c.county_geoid,
        c.county_name,
        c.county_name_long,
        c.state_fips,
        sb.state_name,
        c.state_abbr,
        sb.region_id,
        sb.region_name,
        sb.division_id,
        sb.division_name,
        c.cbsa_code,
        c.cbsa_name,
        c.cbsa_type,
        c.county_flag,
        c.vintage,
        c.source
    from county_base c
    left join state_base sb
        on c.state_fips = sb.state_fips
),
tract_base as (
    select
        tract_geoid,
        tract_name,
        tract_name_long,
        county_name as county_name_long,
        state_fip as state_fips,
        state_name,
        state_abbr,
        vintage,
        source
    from patterns_in_place.silver.xwalk_tract_county
),
tract_enriched as (
    select
        t.tract_geoid,
        t.tract_name,
        t.tract_name_long,
        c.county_geoid,
        c.county_name,
        c.county_name_long,
        c.county_flag,
        c.cbsa_code,
        c.cbsa_name,
        c.cbsa_type,
        t.state_fips,
        t.state_name,
        t.state_abbr,
        sb.region_id,
        sb.region_name,
        sb.division_id,
        sb.division_name,
        t.vintage,
        t.source
    from tract_base t
    left join county_enriched c
        on t.state_fips = c.state_fips
       and t.county_name_long = c.county_name_long
    left join state_base sb
        on t.state_fips = sb.state_fips
),
cbsa_base as (
    select
        c.cbsa_code,
        c.cbsa_name,
        c.cbsa_type,
        case
            when c.cbsa_type = 'Metropolitan Statistical Area' then 'metro'
            when c.cbsa_type = 'Micropolitan Statistical Area' then 'micro'
            else null
        end as cbsa_type_short,
        case when c.cbsa_type = 'Metropolitan Statistical Area' then true else false end as is_metro,
        case when c.cbsa_type = 'Micropolitan Statistical Area' then true else false end as is_micro,
        min(c.state_fips) filter (where c.state_fips is not null) as state_fips_single_candidate,
        min(c.state_name) filter (where c.state_name is not null) as state_name_single_candidate,
        min(c.state_abbr) filter (where c.state_abbr is not null) as state_abbr_single_candidate,
        min(c.region_id) filter (where c.region_id is not null) as region_id_single_candidate,
        min(c.region_name) filter (where c.region_name is not null) as region_name_single_candidate,
        min(c.division_id) filter (where c.division_id is not null) as division_id_single_candidate,
        min(c.division_name) filter (where c.division_name is not null) as division_name_single_candidate,
        count(distinct c.state_fips) as state_count,
        count(distinct c.region_id) as region_count,
        count(distinct c.division_id) as division_count,
        count(distinct c.county_geoid) as county_count,
        max(c.vintage) as vintage,
        'silver.xwalk_cbsa_county' as source
    from county_enriched c
    where c.cbsa_code is not null
    group by 1, 2, 3, 4, 5, 6
),
cbsa_enriched as (
    select
        cb.cbsa_code,
        cb.cbsa_name,
        cast(null as varchar) as primary_city_name,
        cb.cbsa_type,
        cb.cbsa_type_short,
        cb.is_metro,
        cb.is_micro,
        case when cb.state_count = 1 then cb.state_fips_single_candidate else null end as state_fips,
        case when cb.state_count = 1 then cb.state_name_single_candidate else null end as state_name,
        case when cb.state_count = 1 then cb.state_abbr_single_candidate else null end as state_abbr,
        case when cb.region_count = 1 then cb.region_id_single_candidate else null end as region_id,
        case when cb.region_count = 1 then cb.region_name_single_candidate else null end as region_name,
        case when cb.division_count = 1 then cb.division_id_single_candidate else null end as division_id,
        case when cb.division_count = 1 then cb.division_name_single_candidate else null end as division_name,
        cb.state_count,
        cb.region_count,
        cb.division_count,
        cb.county_count,
        cb.vintage,
        cb.source
    from cbsa_base cb
),
us_row as (
    select
        'us' as geo_level,
        'us' as geo_id,
        'United States' as geo_name,
        'United States' as display_name,
        1 as hierarchy_rank,
        cast(null as varchar) as state_fips,
        cast(null as varchar) as state_name,
        cast(null as varchar) as state_abbr,
        cast(null as varchar) as region_id,
        cast(null as varchar) as region_name,
        cast(null as varchar) as division_id,
        cast(null as varchar) as division_name,
        cast(null as varchar) as cbsa_code,
        cast(null as varchar) as cbsa_name,
        cast(null as varchar) as cbsa_type,
        cast(null as varchar) as cbsa_type_short,
        cast(null as boolean) as is_metro,
        cast(null as boolean) as is_micro,
        cast(null as varchar) as county_geoid,
        cast(null as varchar) as county_name,
        cast(null as varchar) as county_name_long,
        cast(null as varchar) as county_flag,
        cast(null as varchar) as primary_city_name,
        cast(null as varchar) as parent_geo_level,
        cast(null as varchar) as parent_geo_id,
        cast('us' as varchar) as parent_us_id,
        cast(null as varchar) as parent_region_id,
        cast(null as varchar) as parent_division_id,
        cast(null as varchar) as parent_state_fips,
        cast(null as varchar) as parent_cbsa_code,
        cast(1 as integer) as state_count,
        cast(4 as integer) as region_count,
        cast(9 as integer) as division_count,
        cast(null as integer) as county_count,
        2023 as vintage,
        'derived_from_state_region' as source
),
region_rows as (
    select
        'region' as geo_level,
        rl.region_id as geo_id,
        rl.region_name as geo_name,
        rl.region_name as display_name,
        2 as hierarchy_rank,
        cast(null as varchar) as state_fips,
        cast(null as varchar) as state_name,
        cast(null as varchar) as state_abbr,
        rl.region_id,
        rl.region_name,
        cast(null as varchar) as division_id,
        cast(null as varchar) as division_name,
        cast(null as varchar) as cbsa_code,
        cast(null as varchar) as cbsa_name,
        cast(null as varchar) as cbsa_type,
        cast(null as varchar) as cbsa_type_short,
        cast(null as boolean) as is_metro,
        cast(null as boolean) as is_micro,
        cast(null as varchar) as county_geoid,
        cast(null as varchar) as county_name,
        cast(null as varchar) as county_name_long,
        cast(null as varchar) as county_flag,
        cast(null as varchar) as primary_city_name,
        'us' as parent_geo_level,
        'us' as parent_geo_id,
        'us' as parent_us_id,
        cast(null as varchar) as parent_region_id,
        cast(null as varchar) as parent_division_id,
        cast(null as varchar) as parent_state_fips,
        cast(null as varchar) as parent_cbsa_code,
        cast(null as integer) as state_count,
        cast(null as integer) as region_count,
        cast(null as integer) as division_count,
        cast(null as integer) as county_count,
        2023 as vintage,
        'silver.xwalk_state_region' as source
    from region_lookup rl
),
division_rows as (
    select
        'division' as geo_level,
        dl.division_id as geo_id,
        dl.division_name as geo_name,
        dl.division_name as display_name,
        3 as hierarchy_rank,
        cast(null as varchar) as state_fips,
        cast(null as varchar) as state_name,
        cast(null as varchar) as state_abbr,
        dl.region_id,
        rl.region_name,
        dl.division_id,
        dl.division_name,
        cast(null as varchar) as cbsa_code,
        cast(null as varchar) as cbsa_name,
        cast(null as varchar) as cbsa_type,
        cast(null as varchar) as cbsa_type_short,
        cast(null as boolean) as is_metro,
        cast(null as boolean) as is_micro,
        cast(null as varchar) as county_geoid,
        cast(null as varchar) as county_name,
        cast(null as varchar) as county_name_long,
        cast(null as varchar) as county_flag,
        cast(null as varchar) as primary_city_name,
        'region' as parent_geo_level,
        dl.region_id as parent_geo_id,
        'us' as parent_us_id,
        dl.region_id as parent_region_id,
        cast(null as varchar) as parent_division_id,
        cast(null as varchar) as parent_state_fips,
        cast(null as varchar) as parent_cbsa_code,
        cast(null as integer) as state_count,
        cast(null as integer) as region_count,
        cast(null as integer) as division_count,
        cast(null as integer) as county_count,
        2023 as vintage,
        'silver.xwalk_state_region' as source
    from division_lookup dl
    left join region_lookup rl
        on dl.region_id = rl.region_id
),
state_rows as (
    select
        'state' as geo_level,
        sb.state_fips as geo_id,
        sb.state_name as geo_name,
        concat(sb.state_name, ' (', sb.state_abbr, ')') as display_name,
        4 as hierarchy_rank,
        sb.state_fips,
        sb.state_name,
        sb.state_abbr,
        sb.region_id,
        sb.region_name,
        sb.division_id,
        sb.division_name,
        cast(null as varchar) as cbsa_code,
        cast(null as varchar) as cbsa_name,
        cast(null as varchar) as cbsa_type,
        cast(null as varchar) as cbsa_type_short,
        cast(null as boolean) as is_metro,
        cast(null as boolean) as is_micro,
        cast(null as varchar) as county_geoid,
        cast(null as varchar) as county_name,
        cast(null as varchar) as county_name_long,
        cast(null as varchar) as county_flag,
        cast(null as varchar) as primary_city_name,
        'division' as parent_geo_level,
        sb.division_id as parent_geo_id,
        'us' as parent_us_id,
        sb.region_id as parent_region_id,
        sb.division_id as parent_division_id,
        cast(null as varchar) as parent_state_fips,
        cast(null as varchar) as parent_cbsa_code,
        cast(null as integer) as state_count,
        cast(null as integer) as region_count,
        cast(null as integer) as division_count,
        cast(null as integer) as county_count,
        sb.vintage,
        sb.source
    from state_base sb
),
cbsa_rows as (
    select
        'cbsa' as geo_level,
        cb.cbsa_code as geo_id,
        cb.cbsa_name as geo_name,
        cb.cbsa_name as display_name,
        5 as hierarchy_rank,
        cb.state_fips,
        cb.state_name,
        cb.state_abbr,
        cb.region_id,
        cb.region_name,
        cb.division_id,
        cb.division_name,
        cb.cbsa_code,
        cb.cbsa_name,
        cb.cbsa_type,
        cb.cbsa_type_short,
        cb.is_metro,
        cb.is_micro,
        cast(null as varchar) as county_geoid,
        cast(null as varchar) as county_name,
        cast(null as varchar) as county_name_long,
        cast(null as varchar) as county_flag,
        cb.primary_city_name,
        case when cb.state_count = 1 then 'state' else null end as parent_geo_level,
        case when cb.state_count = 1 then cb.state_fips else null end as parent_geo_id,
        'us' as parent_us_id,
        case when cb.region_count = 1 then cb.region_id else null end as parent_region_id,
        case when cb.division_count = 1 then cb.division_id else null end as parent_division_id,
        case when cb.state_count = 1 then cb.state_fips else null end as parent_state_fips,
        cast(null as varchar) as parent_cbsa_code,
        cb.state_count,
        cb.region_count,
        cb.division_count,
        cb.county_count,
        cb.vintage,
        cb.source
    from cbsa_enriched cb
),
county_rows as (
    select
        'county' as geo_level,
        ce.county_geoid as geo_id,
        ce.county_name_long as geo_name,
        ce.county_name_long as display_name,
        6 as hierarchy_rank,
        ce.state_fips,
        ce.state_name,
        ce.state_abbr,
        ce.region_id,
        ce.region_name,
        ce.division_id,
        ce.division_name,
        ce.cbsa_code,
        ce.cbsa_name,
        ce.cbsa_type,
        case
            when ce.cbsa_type = 'Metropolitan Statistical Area' then 'metro'
            when ce.cbsa_type = 'Micropolitan Statistical Area' then 'micro'
            else null
        end as cbsa_type_short,
        case when ce.cbsa_type = 'Metropolitan Statistical Area' then true when ce.cbsa_type is not null then false else null end as is_metro,
        case when ce.cbsa_type = 'Micropolitan Statistical Area' then true when ce.cbsa_type is not null then false else null end as is_micro,
        ce.county_geoid,
        ce.county_name,
        ce.county_name_long,
        ce.county_flag,
        cast(null as varchar) as primary_city_name,
        'state' as parent_geo_level,
        ce.state_fips as parent_geo_id,
        'us' as parent_us_id,
        ce.region_id as parent_region_id,
        ce.division_id as parent_division_id,
        ce.state_fips as parent_state_fips,
        ce.cbsa_code as parent_cbsa_code,
        cast(null as integer) as state_count,
        cast(null as integer) as region_count,
        cast(null as integer) as division_count,
        cast(null as integer) as county_count,
        ce.vintage,
        ce.source
    from county_enriched ce
),
tract_rows as (
    select
        'tract' as geo_level,
        te.tract_geoid as geo_id,
        te.tract_name_long as geo_name,
        te.tract_name_long as display_name,
        7 as hierarchy_rank,
        te.state_fips,
        te.state_name,
        te.state_abbr,
        te.region_id,
        te.region_name,
        te.division_id,
        te.division_name,
        te.cbsa_code,
        te.cbsa_name,
        te.cbsa_type,
        case
            when te.cbsa_type = 'Metropolitan Statistical Area' then 'metro'
            when te.cbsa_type = 'Micropolitan Statistical Area' then 'micro'
            else null
        end as cbsa_type_short,
        case when te.cbsa_type = 'Metropolitan Statistical Area' then true when te.cbsa_type is not null then false else null end as is_metro,
        case when te.cbsa_type = 'Micropolitan Statistical Area' then true when te.cbsa_type is not null then false else null end as is_micro,
        te.county_geoid,
        te.county_name,
        te.county_name_long,
        te.county_flag,
        cast(null as varchar) as primary_city_name,
        'county' as parent_geo_level,
        te.county_geoid as parent_geo_id,
        'us' as parent_us_id,
        te.region_id as parent_region_id,
        te.division_id as parent_division_id,
        te.state_fips as parent_state_fips,
        te.cbsa_code as parent_cbsa_code,
        cast(null as integer) as state_count,
        cast(null as integer) as region_count,
        cast(null as integer) as division_count,
        cast(null as integer) as county_count,
        te.vintage,
        te.source
    from tract_enriched te
)
select * from us_row
union all
select * from region_rows
union all
select * from division_rows
union all
select * from state_rows
union all
select * from cbsa_rows
union all
select * from county_rows
union all
select * from tract_rows
order by hierarchy_rank, geo_name, geo_id;
