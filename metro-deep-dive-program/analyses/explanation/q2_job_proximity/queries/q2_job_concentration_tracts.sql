-- Epic 2's national tract surface. WAC supplies workplace jobs; RAC supplies
-- resident-worker context only and does not identify worker origins or flows.
with latest_wac_year as (
    select max(year) as year
    from silver.lehd_lodes_wac
    where geo_level = 'tract'
), market_counties as (
    select distinct cbsa_code, cbsa_name, county_geoid
    from silver.xwalk_cbsa_county
), tract_wac as (
    select
        mc.cbsa_code,
        mc.cbsa_name,
        w.geo_id as tract_geoid,
        w.year as wac_year,
        w.jobs_total,
        g.land_area_sqmi
    from silver.lehd_lodes_wac w
    join geo.tracts_all_us g
        on w.geo_id = g.tract_geoid
    join market_counties mc
        on g.county_geoid = mc.county_geoid
    where w.geo_level = 'tract'
      and w.year = (select year from latest_wac_year)
      and w.jobs_total is not null
), tract_rac as (
    select geo_id as tract_geoid, workers_total
    from silver.lehd_lodes_rac
    where geo_level = 'tract'
      and year = (select year from latest_wac_year)
)
select
    w.cbsa_code,
    w.cbsa_name,
    w.tract_geoid,
    w.wac_year,
    w.jobs_total,
    r.workers_total,
    w.land_area_sqmi,
    case
        when w.land_area_sqmi > 0 then w.jobs_total / w.land_area_sqmi
    end as jobs_per_sqmi
from tract_wac w
left join tract_rac r
    on w.tract_geoid = r.tract_geoid
order by w.cbsa_code, w.jobs_total desc, w.tract_geoid;
