-- Coverage is measured against governed tract geometry in a CBSA, not against
-- WAC alone, so missing workplace release coverage stays visible in the cohort.
with latest_wac_year as (
    select max(year) as year
    from silver.lehd_lodes_wac
    where geo_level = 'tract'
), market_counties as (
    select distinct cbsa_code, cbsa_name, county_geoid
    from silver.xwalk_cbsa_county
), market_tracts as (
    select
        mc.cbsa_code,
        mc.cbsa_name,
        g.tract_geoid
    from geo.tracts_all_us g
    join market_counties mc
        on g.county_geoid = mc.county_geoid
), wac_tracts as (
    select geo_id as tract_geoid
    from silver.lehd_lodes_wac
    where geo_level = 'tract'
      and year = (select year from latest_wac_year)
      and jobs_total is not null
), rac_tracts as (
    select geo_id as tract_geoid
    from silver.lehd_lodes_rac
    where geo_level = 'tract'
      and year = (select year from latest_wac_year)
      and workers_total is not null
)
select
    m.cbsa_code,
    m.cbsa_name,
    count(*) as governed_tract_count,
    count(w.tract_geoid) as wac_tract_count,
    count(r.tract_geoid) as rac_tract_count,
    count(w.tract_geoid)::double / nullif(count(*), 0) as wac_geometry_coverage,
    count(r.tract_geoid)::double / nullif(count(*), 0) as rac_geometry_coverage
from market_tracts m
left join wac_tracts w
    on m.tract_geoid = w.tract_geoid
left join rac_tracts r
    on m.tract_geoid = r.tract_geoid
group by m.cbsa_code, m.cbsa_name
order by m.cbsa_code;
