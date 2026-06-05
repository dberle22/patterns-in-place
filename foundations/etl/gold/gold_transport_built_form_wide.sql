-- Gold transport + built form mart
-- Grain: one row per geo_level + geo_id + year
-- Built form density uses tract population joined to TIGER tract land area.
-- Coverage for density fields is strongest for tract, county, cbsa, and state.
-- Other geographies retain transport fields but may have null density outputs.

create or replace table patterns_in_place.gold.transport_built_form_wide as
with transport as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        geo_name,
        year,
        commute_workers_total,
        commute_drove_alone,
        commute_carpool,
        commute_public_trans,
        commute_taxicab,
        commute_motorcycle,
        commute_bicycle,
        commute_walked,
        commute_other,
        commute_worked_home,
        pct_commute_drive_alone,
        pct_commute_carpool,
        pct_commute_transit,
        pct_commute_walk,
        pct_commute_wfh,
        veh_total_hh,
        veh_0,
        veh_1,
        veh_2,
        veh_3,
        veh_4_plus,
        pct_hh_0_vehicles,
        pct_hh_1_vehicles,
        pct_hh_2_vehicles,
        pct_hh_3_vehicles,
        pct_hh_4p_vehicles,
        total_travel_time,
        mean_travel_time
    from patterns_in_place.silver.transport_kpi
),

tract_to_county as (
    select
        tract_geoid,
        lpad(state_fip, 2, '0') as state_fip,
        lpad(county_fip, 3, '0') as county_fip,
        concat(lpad(state_fip, 2, '0'), lpad(county_fip, 3, '0')) as county_geoid,
        county_name
    from patterns_in_place.silver.xwalk_tract_county
),

tract_pop as (
    select
        a.year,
        a.geo_id as tract_geoid,
        a.geo_name as tract_name,
        a.pop_total,
        g.land_area_sqmi,
        case
            when g.land_area_sqmi > 0 then a.pop_total / g.land_area_sqmi
            else null
        end as tract_pop_density_sqmi
    from patterns_in_place.silver.age_kpi a
    inner join patterns_in_place.geo.tracts_all_us g
        on a.geo_id = g.tract_geoid
    where lower(a.geo_level) = 'tract'
),

tract_density as (
    select
        'tract' as geo_level,
        tract_geoid as geo_id,
        max(tract_name) as geo_name,
        year,
        sum(pop_total) as density_population,
        sum(land_area_sqmi) as land_area_sqmi,
        case
            when sum(land_area_sqmi) > 0 then sum(pop_total) / sum(land_area_sqmi)
            else null
        end as gross_density_sqmi,
        case
            when sum(pop_total) > 0 then sum(pop_total * tract_pop_density_sqmi) / sum(pop_total)
            else null
        end as pop_weighted_density_sqmi
    from tract_pop
    group by 1, 2, 4

    union all

    select
        'county' as geo_level,
        x.county_geoid as geo_id,
        max(x.county_name) as geo_name,
        t.year,
        sum(t.pop_total) as density_population,
        sum(t.land_area_sqmi) as land_area_sqmi,
        case
            when sum(t.land_area_sqmi) > 0 then sum(t.pop_total) / sum(t.land_area_sqmi)
            else null
        end as gross_density_sqmi,
        case
            when sum(t.pop_total) > 0 then sum(t.pop_total * t.tract_pop_density_sqmi) / sum(t.pop_total)
            else null
        end as pop_weighted_density_sqmi
    from tract_pop t
    inner join tract_to_county x
        on t.tract_geoid = x.tract_geoid
    group by 1, 2, 4

    union all

    select
        'state' as geo_level,
        cs.state_fip as geo_id,
        max(cs.state_abbr) as geo_name,
        t.year,
        sum(t.pop_total) as density_population,
        sum(t.land_area_sqmi) as land_area_sqmi,
        case
            when sum(t.land_area_sqmi) > 0 then sum(t.pop_total) / sum(t.land_area_sqmi)
            else null
        end as gross_density_sqmi,
        case
            when sum(t.pop_total) > 0 then sum(t.pop_total * t.tract_pop_density_sqmi) / sum(t.pop_total)
            else null
        end as pop_weighted_density_sqmi
    from tract_pop t
    inner join tract_to_county x
        on t.tract_geoid = x.tract_geoid
    inner join patterns_in_place.silver.xwalk_county_state cs
        on x.county_geoid = cs.county_geoid
    group by 1, 2, 4

    union all

    select
        'cbsa' as geo_level,
        c.cbsa_code as geo_id,
        max(c.cbsa_name) as geo_name,
        t.year,
        sum(t.pop_total) as density_population,
        sum(t.land_area_sqmi) as land_area_sqmi,
        case
            when sum(t.land_area_sqmi) > 0 then sum(t.pop_total) / sum(t.land_area_sqmi)
            else null
        end as gross_density_sqmi,
        case
            when sum(t.pop_total) > 0 then sum(t.pop_total * t.tract_pop_density_sqmi) / sum(t.pop_total)
            else null
        end as pop_weighted_density_sqmi
    from tract_pop t
    inner join tract_to_county x
        on t.tract_geoid = x.tract_geoid
    inner join patterns_in_place.silver.xwalk_cbsa_county c
        on x.county_geoid = c.county_geoid
    group by 1, 2, 4
)

select
    tr.geo_level,
    tr.geo_id,
    coalesce(tr.geo_name, d.geo_name) as geo_name,
    tr.year,
    tr.commute_workers_total,
    tr.commute_drove_alone,
    tr.commute_carpool,
    tr.commute_public_trans,
    tr.commute_taxicab,
    tr.commute_motorcycle,
    tr.commute_bicycle,
    tr.commute_walked,
    tr.commute_other,
    tr.commute_worked_home,
    tr.pct_commute_drive_alone,
    tr.pct_commute_carpool,
    tr.pct_commute_transit,
    tr.pct_commute_walk,
    tr.pct_commute_wfh,
    coalesce(tr.pct_commute_transit, 0)
        + coalesce(tr.pct_commute_walk, 0)
        + coalesce(tr.pct_commute_wfh, 0) as pct_low_car_commute,
    tr.veh_total_hh,
    tr.veh_0,
    tr.veh_1,
    tr.veh_2,
    tr.veh_3,
    tr.veh_4_plus,
    tr.pct_hh_0_vehicles,
    tr.pct_hh_1_vehicles,
    tr.pct_hh_2_vehicles,
    tr.pct_hh_3_vehicles,
    tr.pct_hh_4p_vehicles,
    tr.total_travel_time,
    tr.mean_travel_time,
    d.density_population,
    d.land_area_sqmi,
    d.gross_density_sqmi,
    d.pop_weighted_density_sqmi
from transport tr
left join tract_density d
    on tr.geo_level = d.geo_level
   and tr.geo_id = d.geo_id
   and tr.year = d.year
;
