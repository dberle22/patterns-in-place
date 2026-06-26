-- This script creates the Gold LEHD J2J labor-fluidity mart.
-- We intentionally keep this table narrow and headline-friendly:
-- one row per state or CBSA year, filtered to the complete-year,
-- all-age, all-industry slice from `silver.lehd_j2j`.
-- Age detail, industry detail, and J2JOD pair flows stay out of Gold.

create or replace table patterns_in_place.gold.labor_j2j_wide as

with j2j_base as (
  select
    lower(geo_level) as geo_level,
    geo_id,
    geo_name,
    year,
    quarters_observed as j2j_quarters_observed,
    has_current_cbsa_match as j2j_has_current_cbsa_match,
    release_id as j2j_release_id,
    keep_start_year as j2j_keep_start_year,
    keep_end_year as j2j_keep_end_year,
    hires_total as j2j_hires_total,
    separations_total as j2j_separations_total,
    job_starts_total as j2j_job_starts_total,
    job_ends_total as j2j_job_ends_total,
    hires_from_employment as j2j_hires_from_employment,
    hires_from_nonemployment as j2j_hires_from_nonemployment,
    separations_to_employment as j2j_separations_to_employment,
    separations_to_nonemployment as j2j_separations_to_nonemployment,
    j2j_hires as j2j_direct_hires,
    j2j_separations as j2j_direct_separations,
    j2j_hire_share as j2j_direct_hire_share,
    j2j_sep_share as j2j_direct_sep_share,
    ee_hire_share as j2j_ee_hire_share,
    ne_hire_share as j2j_ne_hire_share,
    ee_sep_share as j2j_ee_sep_share,
    en_sep_share as j2j_en_sep_share,
    avg_ee_hire_earnings_dest as j2j_avg_ee_hire_earnings_dest,
    avg_ee_sep_earnings_orig as j2j_avg_ee_sep_earnings_orig,
    avg_ee_earnings_delta as j2j_avg_ee_earnings_delta,
    avg_job_stayers_count as j2j_avg_job_stayers_count,
    avg_main_job_beginning_count as j2j_avg_main_job_beginning_count,
    avg_main_job_ending_count as j2j_avg_main_job_ending_count
  from patterns_in_place.silver.lehd_j2j
  where lower(geo_level) in ('state', 'cbsa')
    and demo_code = 'A00'
    and industry_code = '00'
    and is_complete_year = true
)

select *
from j2j_base
order by geo_level, geo_id, year;
