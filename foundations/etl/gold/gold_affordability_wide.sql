-- Gold affordability mart
-- Grain: one row per geo_level + geo_id + year
-- Consolidates housing cost burden, income context, and RPP-adjusted income where available.
-- MARPP/RPP coverage is currently state + cbsa only, with county backfill to state per DBDesign.md.

create or replace table patterns_in_place.gold.affordability_wide as
with housing as (
    select *
    from patterns_in_place.gold.housing_core_wide
),

income as (
    select *
    from patterns_in_place.gold.economics_income_wide
),

chas as (
    select
        geo_level,
        geo_id,
        year,
        max(case
            when tenure = 'all' and income_band = 'all'
                then pct_cost_burdened
        end) as pct_cost_burdened,
        max(case
            when tenure = 'all' and income_band = 'all'
                then pct_severely_cost_burdened
        end) as pct_severely_cost_burdened,
        max(case
            when tenure = 'renter' and income_band = 'all'
                then pct_severely_cost_burdened
        end) as pct_renter_severely_cost_burdened
    from patterns_in_place.silver.hud_chas_burden
    group by 1, 2, 3
),

rpp_base as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        case
            when lower(geo_level) = 'state' then substr(geo_id, 1, 2)
            else geo_id
        end as geo_id_normalized,
        cast(period as integer) as year,
        rpp_real_pc_income,
        rpp_all_items,
        rpp_price_deflator
    from patterns_in_place.silver.bea_regional_marpp_wide
    where lower(geo_level) in ('state', 'cbsa')
),

county_to_state as (
    select
        county_geoid,
        state_fip as state_fips
    from patterns_in_place.silver.xwalk_county_state
),

rpp_enriched as (
    select
        i.geo_level,
        i.geo_id,
        i.year,
        coalesce(r_cbsa.rpp_real_pc_income, r_direct.rpp_real_pc_income, r_state.rpp_real_pc_income) as rpp_real_pc_income,
        coalesce(r_cbsa.rpp_all_items, r_direct.rpp_all_items, r_state.rpp_all_items) as rpp_all_items,
        coalesce(r_cbsa.rpp_price_deflator, r_direct.rpp_price_deflator, r_state.rpp_price_deflator) as rpp_price_deflator
    from income i
    left join rpp_base r_direct
        on i.geo_level = r_direct.geo_level
       and i.geo_id = r_direct.geo_id_normalized
       and i.year = r_direct.year
    left join patterns_in_place.silver.xwalk_cbsa_county c
        on i.geo_level = 'county'
       and i.geo_id = c.county_geoid
    left join rpp_base r_cbsa
        on r_cbsa.geo_level = 'cbsa'
       and r_cbsa.geo_id = c.cbsa_code
       and r_cbsa.year = i.year
    left join county_to_state cs
        on i.geo_level = 'county'
       and i.geo_id = cs.county_geoid
    left join rpp_base r_state
        on r_state.geo_level = 'state'
       and r_state.geo_id_normalized = case when i.geo_level = 'county' then cs.state_fips else i.geo_id end
       and r_state.year = i.year
),

base as (
    select
        h.geo_level,
        h.geo_id,
        h.geo_name,
        h.year
    from housing h
)

select
    b.geo_level,
    b.geo_id,
    coalesce(b.geo_name, i.geo_name) as geo_name,
    b.year,
    h.pop_total,
    h.hu_total,
    h.median_gross_rent,
    h.annualized_median_rent,
    h.median_home_value,
    h.median_hh_income,
    i.acs_income_pc,
    i.calc_income_pc,
    i.income_pc_growth_1yr,
    i.income_pc_growth_5yr,
    i.income_pc_cagr_5yr,
    i.income_pc_growth_10yr,
    i.income_pc_cagr_10yr,
    i.pi_wage_share,
    r.rpp_real_pc_income,
    r.rpp_all_items,
    r.rpp_price_deflator,
    h.rent_to_income,
    h.value_to_income,
    c.pct_cost_burdened,
    c.pct_severely_cost_burdened,
    c.pct_renter_severely_cost_burdened,
    h.pct_rent_burden_30plus,
    h.pct_rent_burden_50plus,
    h.fmr_2br,
    h.rent50_2br,
    h.fmr_gap_2br_vs_median_rent,
    h.rent50_gap_2br_vs_median_rent,
    h.vacancy_rate,
    h.owner_occ_rate,
    h.renter_occ_rate,
    h.permits_per_1000_housing_units,
    h.permits_per_1000_population,
    case
        when r.rpp_real_pc_income > 0 and h.median_gross_rent is not null
            then (h.median_gross_rent * 12.0) / r.rpp_real_pc_income
        else null
    end as rent_to_rpp_income,
    case
        when r.rpp_real_pc_income > 0 and h.median_home_value is not null
            then h.median_home_value / r.rpp_real_pc_income
        else null
    end as value_to_rpp_income
from base b
left join housing h
    on b.geo_level = h.geo_level
   and b.geo_id = h.geo_id
   and b.year = h.year
left join income i
    on b.geo_level = i.geo_level
   and b.geo_id = i.geo_id
   and b.year = i.year
left join chas c
    on b.geo_level = c.geo_level
   and b.geo_id = c.geo_id
   and b.year = c.year
left join rpp_enriched r
    on b.geo_level = r.geo_level
   and b.geo_id = r.geo_id
   and b.year = r.year
;
