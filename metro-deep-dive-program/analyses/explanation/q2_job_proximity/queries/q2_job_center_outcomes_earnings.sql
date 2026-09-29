-- LODES earnings bands describe workers at selected workplace tracts. They are
-- shown as separate center context and are never treated as household income.
with selected_centers as (
    select 'strict_core' as center_version, tract_geoid
    from mart_explanation_q2.job_center_candidates_v0
    where cbsa_code = '__CBSA_CODE__' and is_strict_core_seed
    union all
    select 'recommended_core_one_hop', tract_geoid
    from mart_explanation_q2.job_center_candidates_v0
    where cbsa_code = '__CBSA_CODE__' and is_recommended_center
    union all
    select 'no_share_sensitivity', tract_geoid
    from mart_explanation_q2.job_center_candidates_v0
    where cbsa_code = '__CBSA_CODE__' and is_no_share_sensitivity
)
select
    selected_centers.center_version,
    sum(wac.jobs_total) as workplace_jobs,
    sum(wac.jobs_earnings_low) / nullif(sum(wac.jobs_total), 0) as low_earnings_job_share,
    sum(wac.jobs_earnings_mid) / nullif(sum(wac.jobs_total), 0) as mid_earnings_job_share,
    sum(wac.jobs_earnings_high) / nullif(sum(wac.jobs_total), 0) as high_earnings_job_share
from selected_centers
join silver.lehd_lodes_wac wac
  on selected_centers.tract_geoid = wac.geo_id
 and wac.geo_level = 'tract'
 and wac.year = 2023
group by selected_centers.center_version
order by selected_centers.center_version;
