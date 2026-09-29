-- Read-only Epic 2 source surface. WAC stays the workplace-count source; RAC
-- is supporting context and does not imply an origin-destination relationship.
with market_counties as (
    select distinct county_geoid
    from silver.xwalk_cbsa_county
    where cbsa_code = '__CBSA_CODE__'
), latest_wac_year as (
    select max(year) as year
    from silver.lehd_lodes_wac
    where geo_level = 'tract'
)
select
    w.geo_id as tract_geoid,
    w.geo_name as tract_name,
    w.year as wac_year,
    w.jobs_total,
    r.workers_total,
    g.land_area_sqmi,
    case
        when g.land_area_sqmi > 0 then w.jobs_total / g.land_area_sqmi
    end as jobs_per_sqmi,
    g.geom_wkb
from silver.lehd_lodes_wac w
join geo.tracts_all_us g
    on w.geo_id = g.tract_geoid
join market_counties mc
    on g.county_geoid = mc.county_geoid
left join silver.lehd_lodes_rac r
    on w.geo_id = r.geo_id
    and r.geo_level = 'tract'
    and r.year = w.year
where w.geo_level = 'tract'
  and w.year = (select year from latest_wac_year)
order by w.jobs_total desc, w.geo_id;
