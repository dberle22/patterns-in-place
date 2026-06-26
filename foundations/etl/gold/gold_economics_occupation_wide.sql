-- Gold occupation structure mart built from the first-pass 2025 OEWS release.
-- Grain: one row per geo_level + geo_id + year.
-- Unlike the ACS-backed economics marts, this table uses the OEWS total row as
-- the geography-year base because the current OEWS release is 2025 while the
-- ACS spine currently ends in 2024.

create or replace table patterns_in_place.gold.economics_occupation_wide as
with base as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        geo_name,
        year,
        soc_code,
        soc_title,
        soc_major_group,
        o_group,
        occupation_bucket,
        is_stem,
        is_total_occupation,
        employment,
        hourly_mean_wage,
        annual_mean_wage,
        employment_not_released,
        any_wage_not_available,
        any_wage_topcoded
    from patterns_in_place.silver.bls_oews
    where lower(geo_level) in ('state', 'cbsa')
),

totals as (
    select
        geo_level,
        geo_id,
        geo_name,
        year,
        employment as oews_emp_total
    from base
    where is_total_occupation
),

detailed as (
    select *
    from base
    where o_group = 'detailed'
),

family_rollup as (
    select
        geo_level,
        geo_id,
        geo_name,
        year,

        sum(case when is_stem then employment else 0 end) as oews_emp_stem,
        sum(case when occupation_bucket = 'management_professional' then employment else 0 end) as oews_emp_management_professional,
        sum(case when occupation_bucket = 'service' then employment else 0 end) as oews_emp_service,
        sum(case when occupation_bucket = 'production_transportation' then employment else 0 end) as oews_emp_production_transportation,
        sum(case when occupation_bucket = 'other' then employment else 0 end) as oews_emp_other,

        sum(case when is_stem and annual_mean_wage is not null then annual_mean_wage * employment else 0 end)
            / nullif(sum(case when is_stem and annual_mean_wage is not null then employment else 0 end), 0) as oews_mean_annual_wage_stem,
        sum(case when occupation_bucket = 'management_professional' and annual_mean_wage is not null then annual_mean_wage * employment else 0 end)
            / nullif(sum(case when occupation_bucket = 'management_professional' and annual_mean_wage is not null then employment else 0 end), 0) as oews_mean_annual_wage_management_professional,
        sum(case when occupation_bucket = 'service' and annual_mean_wage is not null then annual_mean_wage * employment else 0 end)
            / nullif(sum(case when occupation_bucket = 'service' and annual_mean_wage is not null then employment else 0 end), 0) as oews_mean_annual_wage_service,
        sum(case when occupation_bucket = 'production_transportation' and annual_mean_wage is not null then annual_mean_wage * employment else 0 end)
            / nullif(sum(case when occupation_bucket = 'production_transportation' and annual_mean_wage is not null then employment else 0 end), 0) as oews_mean_annual_wage_production_transportation,
        sum(case when occupation_bucket = 'other' and annual_mean_wage is not null then annual_mean_wage * employment else 0 end)
            / nullif(sum(case when occupation_bucket = 'other' and annual_mean_wage is not null then employment else 0 end), 0) as oews_mean_annual_wage_other,

        sum(case when is_stem and hourly_mean_wage is not null then hourly_mean_wage * employment else 0 end)
            / nullif(sum(case when is_stem and hourly_mean_wage is not null then employment else 0 end), 0) as oews_mean_hourly_wage_stem,
        sum(case when occupation_bucket = 'management_professional' and hourly_mean_wage is not null then hourly_mean_wage * employment else 0 end)
            / nullif(sum(case when occupation_bucket = 'management_professional' and hourly_mean_wage is not null then employment else 0 end), 0) as oews_mean_hourly_wage_management_professional,
        sum(case when occupation_bucket = 'service' and hourly_mean_wage is not null then hourly_mean_wage * employment else 0 end)
            / nullif(sum(case when occupation_bucket = 'service' and hourly_mean_wage is not null then employment else 0 end), 0) as oews_mean_hourly_wage_service,
        sum(case when occupation_bucket = 'production_transportation' and hourly_mean_wage is not null then hourly_mean_wage * employment else 0 end)
            / nullif(sum(case when occupation_bucket = 'production_transportation' and hourly_mean_wage is not null then employment else 0 end), 0) as oews_mean_hourly_wage_production_transportation,
        sum(case when occupation_bucket = 'other' and hourly_mean_wage is not null then hourly_mean_wage * employment else 0 end)
            / nullif(sum(case when occupation_bucket = 'other' and hourly_mean_wage is not null then employment else 0 end), 0) as oews_mean_hourly_wage_other,

        sum(case when employment_not_released then 1 else 0 end) as oews_unreleased_emp_soc_count,
        sum(case when any_wage_not_available then 1 else 0 end) as oews_missing_wage_soc_count,
        sum(case when any_wage_topcoded then 1 else 0 end) as oews_topcoded_wage_soc_count
    from detailed
    group by 1, 2, 3, 4
),

national_shares as (
    select
        t.year,
        sum(f.oews_emp_stem) / nullif(sum(t.oews_emp_total), 0) as national_pct_emp_stem,
        sum(f.oews_emp_management_professional) / nullif(sum(t.oews_emp_total), 0) as national_pct_emp_management_professional,
        sum(f.oews_emp_service) / nullif(sum(t.oews_emp_total), 0) as national_pct_emp_service,
        sum(f.oews_emp_production_transportation) / nullif(sum(t.oews_emp_total), 0) as national_pct_emp_production_transportation,
        sum(f.oews_emp_other) / nullif(sum(t.oews_emp_total), 0) as national_pct_emp_other
    from totals t
    left join family_rollup f
      using (geo_level, geo_id, geo_name, year)
    where t.geo_level = 'state'
    group by 1
)

select
    t.geo_level,
    t.geo_id,
    t.geo_name,
    t.year,
    t.oews_emp_total,

    f.oews_emp_stem,
    f.oews_emp_management_professional,
    f.oews_emp_service,
    f.oews_emp_production_transportation,
    f.oews_emp_other,

    f.oews_emp_stem / nullif(t.oews_emp_total, 0) as oews_pct_emp_stem,
    f.oews_emp_management_professional / nullif(t.oews_emp_total, 0) as oews_pct_emp_management_professional,
    f.oews_emp_service / nullif(t.oews_emp_total, 0) as oews_pct_emp_service,
    f.oews_emp_production_transportation / nullif(t.oews_emp_total, 0) as oews_pct_emp_production_transportation,
    f.oews_emp_other / nullif(t.oews_emp_total, 0) as oews_pct_emp_other,

    (f.oews_emp_stem / nullif(t.oews_emp_total, 0)) / nullif(n.national_pct_emp_stem, 0) as oews_lq_stem,
    (f.oews_emp_management_professional / nullif(t.oews_emp_total, 0)) / nullif(n.national_pct_emp_management_professional, 0) as oews_lq_management_professional,
    (f.oews_emp_service / nullif(t.oews_emp_total, 0)) / nullif(n.national_pct_emp_service, 0) as oews_lq_service,
    (f.oews_emp_production_transportation / nullif(t.oews_emp_total, 0)) / nullif(n.national_pct_emp_production_transportation, 0) as oews_lq_production_transportation,
    (f.oews_emp_other / nullif(t.oews_emp_total, 0)) / nullif(n.national_pct_emp_other, 0) as oews_lq_other,

    f.oews_mean_annual_wage_stem,
    f.oews_mean_annual_wage_management_professional,
    f.oews_mean_annual_wage_service,
    f.oews_mean_annual_wage_production_transportation,
    f.oews_mean_annual_wage_other,

    f.oews_mean_hourly_wage_stem,
    f.oews_mean_hourly_wage_management_professional,
    f.oews_mean_hourly_wage_service,
    f.oews_mean_hourly_wage_production_transportation,
    f.oews_mean_hourly_wage_other,

    f.oews_unreleased_emp_soc_count,
    f.oews_missing_wage_soc_count,
    f.oews_topcoded_wage_soc_count
from totals t
left join family_rollup f
  using (geo_level, geo_id, geo_name, year)
left join national_shares n
  using (year);
