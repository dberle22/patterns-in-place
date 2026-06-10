-- Social Infrastructure Gold Wide
-- This mart keeps the Gold contract narrow: household structure, insurance
-- coverage, and household internet access headline metrics only.
-- It uses the recurring ACS social infrastructure panel as the row spine and
-- joins broadband where that newer ACS table is available.

create or replace table patterns_in_place.gold.social_infra_wide as
with social as (
    select
        geo_level,
        geo_id,
        geo_name,
        year,
        hh_total,
        single_households,
        pct_single_households as pct_hh_single_person,
        pct_family_single_parent,
        ins_total,
        ins_insured,
        ins_uninsured,
        pct_health_insured,
        pct_health_uninsured
    from patterns_in_place.silver.social_infra_kpi
),

broadband as (
    select
        geo_level,
        geo_id,
        geo_name,
        year,
        internet_total_hh,
        internet_broadband_subscription,
        internet_cellular_only,
        internet_no_access,
        pct_broadband_subscription,
        pct_cellular_only,
        pct_no_internet_access
    from patterns_in_place.silver.broadband_kpi
)

select
    s.geo_level,
    s.geo_id,
    s.geo_name,
    s.year,
    s.hh_total,
    s.single_households,
    s.pct_hh_single_person,
    s.pct_family_single_parent,
    s.ins_total,
    s.ins_insured,
    s.ins_uninsured,
    s.pct_health_insured,
    s.pct_health_uninsured,
    b.internet_total_hh,
    b.internet_broadband_subscription,
    b.internet_cellular_only,
    b.internet_no_access,
    b.pct_broadband_subscription,
    b.pct_cellular_only,
    b.pct_no_internet_access
from social s
left join broadband b
    on s.geo_level = b.geo_level
   and s.geo_id = b.geo_id
   and s.year = b.year
;
