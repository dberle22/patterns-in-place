-- Selected-market context from the same 2023 WAC tract surface used in the
-- national concentration notebook. This reader reports context only; it does
-- not select a job-center threshold or candidate construction.
with latest_wac_year as (
    select max(year) as year
    from silver.lehd_lodes_wac
    where geo_level = 'tract'
), market_counties as (
    select distinct cbsa_code, cbsa_name, county_geoid
    from silver.xwalk_cbsa_county
    where cbsa_code = '__CBSA_CODE__'
), tract_jobs as (
    select
        mc.cbsa_code,
        mc.cbsa_name,
        w.geo_id as tract_geoid,
        w.jobs_total
    from silver.lehd_lodes_wac w
    join geo.tracts_all_us g
        on w.geo_id = g.tract_geoid
    join market_counties mc
        on g.county_geoid = mc.county_geoid
    where w.geo_level = 'tract'
      and w.year = (select year from latest_wac_year)
      and w.jobs_total is not null
), ranked as (
    select
        *,
        row_number() over (order by jobs_total desc, tract_geoid) as tract_rank,
        count(*) over () as tract_count,
        sum(jobs_total) over () as workplace_jobs
    from tract_jobs
), cumulative as (
    select
        *,
        sum(jobs_total) over (
            order by jobs_total desc, tract_geoid
            rows between unbounded preceding and current row
        ) / workplace_jobs as cumulative_job_share
    from ranked
)
select
    cbsa_code,
    max(cbsa_name) as cbsa_name,
    max(tract_count) as tract_count,
    max(workplace_jobs) as workplace_jobs,
    min(tract_rank) filter (where cumulative_job_share >= 0.50)::double
        / max(tract_count) as tract_share_to_50pct_jobs,
    min(tract_rank) filter (where cumulative_job_share >= 0.80)::double
        / max(tract_count) as tract_share_to_80pct_jobs
from cumulative
group by cbsa_code;
