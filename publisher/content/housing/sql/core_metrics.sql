-- Housing section core mart.
-- This is the reusable wide table for the editorial housing package, with one
-- row per geo_level + geo_id + year across the four section geographies we
-- actually plan to analyze first: division, state, CBSA, and county.
--
-- The mart stays source-faithful on purpose:
-- - `gold.housing_core_wide` provides the row surface and housing KPIs.
-- - `gold.population_demographics` adds population growth context.
-- - `gold.economics_income_wide` adds BEA-backed and ACS-backed income context.
-- - `gold.dim_geo` adds parent geography fields so section SQL can avoid
--   repeated joins when filtering, labeling, or rolling up county rows.
--
-- Temporary major-market flags are derived from 2024 CBSA population until a
-- canonical Intelligence Layer flag exists. Counties inherit the flag of their
-- parent CBSA when one is available; state and division rows are always false.
--
-- We carry both income-growth families on purpose:
-- - `income_pc_growth_*` remains the BEA-backed series from Gold.
-- - `acs_income_pc_growth_*` is calculated here so the 2024 snapshot can use a
--   contemporaneous ACS-based income-growth signal without pretending BEA has
--   2024 coverage yet.

create schema if not exists mart_housing;

create or replace table mart_housing.core_metrics as
with base as (
    select
        h.geo_level,
        h.geo_id,
        h.geo_name,
        h.year,
        d.display_name,
        d.region_id,
        d.region_name,
        d.division_id,
        d.division_name,
        d.state_fips,
        d.state_name,
        d.state_abbr,
        d.parent_cbsa_code,
        d.parent_geo_level,
        d.parent_geo_id,
        h.pop_total as housing_pop_total,
        p.pop_total as population_pop_total,
        p.pop_growth_1yr,
        p.pop_growth_3yr,
        p.pop_growth_5yr,
        coalesce(i.median_hh_income, h.median_hh_income) as median_hh_income,
        coalesce(i.acs_income_pc, h.per_capita_income) as acs_income_pc,
        i.calc_income_pc as bea_income_pc,
        coalesce(i.calc_income_pc, i.acs_income_pc, h.per_capita_income) as income_pc,
        i.income_pc_growth_1yr,
        i.income_pc_growth_5yr,
        coalesce(i.pov_rate, h.pov_rate) as pov_rate,
        coalesce(i.gini_index, h.gini_index) as gini_index,
        h.hu_total,
        h.occ_total,
        h.occ_occupied,
        h.occ_vacant,
        h.vacancy_rate,
        h.tenure_total,
        h.owner_occupied,
        h.renter_occupied,
        h.owner_occ_rate,
        h.renter_occ_rate,
        h.median_gross_rent,
        h.annualized_median_rent,
        h.median_home_value,
        h.median_owner_costs_mortgage,
        h.median_owner_costs_no_mortgage,
        h.rent_burden_total,
        h.rent_burden_30plus,
        h.rent_burden_50plus,
        h.pct_rent_burden_30plus,
        h.pct_rent_burden_50plus,
        h.rent_to_income,
        h.value_to_income,
        h.fmr_0br,
        h.fmr_1br,
        h.fmr_2br,
        h.fmr_3br,
        h.fmr_4br,
        h.fmr_gap_2br_vs_median_rent,
        h.rent50_0br,
        h.rent50_1br,
        h.rent50_2br,
        h.rent50_3br,
        h.rent50_4br,
        h.rent50_gap_2br_vs_median_rent,
        h.permits_total_bldgs,
        h.permits_total_units,
        h.permits_total_value,
        h.permits_multifam_bldgs,
        h.permits_multifam_units,
        h.permits_multifam_value,
        h.permits_avg_units_per_bldg,
        h.permits_avg_units_per_mf_bldg,
        h.permits_share_multifam_units,
        h.permits_share_units_5_plus,
        h.permits_share_units_1_unit,
        h.permits_structure_mix,
        h.permits_per_1000_housing_units,
        h.permits_per_1000_population,
        h.multifam_permits_per_1000_housing_units,
        h.struct_total,
        h.struct_1_unit,
        h.struct_sf_det,
        h.struct_small_mf,
        h.struct_mid_mf,
        h.struct_large_mf,
        h.struct_mobile,
        h.pct_struct_1_unit,
        h.pct_struct_sf_det,
        h.pct_struct_small_mf,
        h.pct_struct_mid_mf,
        h.pct_struct_large_mf,
        h.pct_struct_mobile,
        h.pct_struct_multifam
    from gold.housing_core_wide h
    left join gold.population_demographics p
        on h.geo_level = p.geo_level
       and h.geo_id = p.geo_id
       and h.year = p.year
    left join gold.economics_income_wide i
        on h.geo_level = i.geo_level
       and h.geo_id = i.geo_id
       and h.year = i.year
    left join gold.dim_geo d
        on h.geo_level = d.geo_level
       and h.geo_id = d.geo_id
    where h.geo_level in ('division', 'state', 'cbsa', 'county')
),

income_windows as (
    select
        b.*,
        lag(b.acs_income_pc, 1) over (
            partition by b.geo_level, b.geo_id
            order by b.year
        ) as acs_income_pc_lag1,
        lag(b.acs_income_pc, 5) over (
            partition by b.geo_level, b.geo_id
            order by b.year
        ) as acs_income_pc_lag5
    from base b
),

cbsa_dim as (
    select
        geo_id as cbsa_code,
        geo_name as cbsa_name
    from gold.dim_geo
    where geo_level = 'cbsa'
),

major_cbsa_flags_2024 as (
    select
        geo_id as cbsa_code,
        pop_total as cbsa_pop_2024,
        pop_total >= 100000 as major_cbsa_100k_flag,
        pop_total >= 250000 as major_cbsa_250k_flag
    from gold.population_demographics
    where geo_level = 'cbsa'
      and year = 2024
),

enriched as (
    select
        b.geo_level,
        b.geo_id,
        b.geo_name,
        b.year,
        coalesce(b.display_name, b.geo_name) as display_name,
        b.region_id,
        b.region_name,
        b.division_id,
        b.division_name,
        b.state_fips,
        b.state_name,
        b.state_abbr,
        case
            when b.geo_level = 'cbsa' then b.geo_id
            when b.geo_level = 'county' then b.parent_cbsa_code
            else null
        end as cbsa_code,
        case
            when b.geo_level = 'cbsa' then b.geo_name
            when b.geo_level = 'county' then cd.cbsa_name
            else null
        end as cbsa_name,
        b.parent_geo_level,
        b.parent_geo_id,
        coalesce(b.population_pop_total, b.housing_pop_total) as pop_total,
        b.pop_growth_1yr,
        b.pop_growth_3yr,
        b.pop_growth_5yr,
        b.median_hh_income,
        b.acs_income_pc,
        b.bea_income_pc,
        b.income_pc,
        b.income_pc_growth_1yr,
        b.income_pc_growth_5yr,
        case
            when b.acs_income_pc_lag1 > 0 then (b.acs_income_pc - b.acs_income_pc_lag1) / b.acs_income_pc_lag1
            else null
        end as acs_income_pc_growth_1yr,
        case
            when b.acs_income_pc_lag5 > 0 then (b.acs_income_pc - b.acs_income_pc_lag5) / b.acs_income_pc_lag5
            else null
        end as acs_income_pc_growth_5yr,
        b.pov_rate,
        b.gini_index,
        b.hu_total,
        b.occ_total,
        b.occ_occupied,
        b.occ_vacant,
        b.vacancy_rate,
        b.tenure_total,
        b.owner_occupied,
        b.renter_occupied,
        b.owner_occ_rate,
        b.renter_occ_rate,
        b.median_gross_rent,
        b.annualized_median_rent,
        b.median_home_value,
        b.median_owner_costs_mortgage,
        b.median_owner_costs_no_mortgage,
        b.rent_burden_total,
        b.rent_burden_30plus,
        b.rent_burden_50plus,
        b.pct_rent_burden_30plus,
        b.pct_rent_burden_50plus,
        b.rent_to_income,
        b.value_to_income,
        b.fmr_0br,
        b.fmr_1br,
        b.fmr_2br,
        b.fmr_3br,
        b.fmr_4br,
        b.fmr_gap_2br_vs_median_rent,
        b.rent50_0br,
        b.rent50_1br,
        b.rent50_2br,
        b.rent50_3br,
        b.rent50_4br,
        b.rent50_gap_2br_vs_median_rent,
        b.permits_total_bldgs,
        b.permits_total_units,
        b.permits_total_value,
        b.permits_multifam_bldgs,
        b.permits_multifam_units,
        b.permits_multifam_value,
        b.permits_avg_units_per_bldg,
        b.permits_avg_units_per_mf_bldg,
        b.permits_share_multifam_units,
        b.permits_share_units_5_plus,
        b.permits_share_units_1_unit,
        b.permits_structure_mix,
        b.permits_per_1000_housing_units,
        b.permits_per_1000_population,
        b.multifam_permits_per_1000_housing_units,
        b.struct_total,
        b.struct_1_unit,
        b.struct_sf_det,
        b.struct_small_mf,
        b.struct_mid_mf,
        b.struct_large_mf,
        b.struct_mobile,
        b.pct_struct_1_unit,
        b.pct_struct_sf_det,
        b.pct_struct_small_mf,
        b.pct_struct_mid_mf,
        b.pct_struct_large_mf,
        b.pct_struct_mobile,
        b.pct_struct_multifam,
        coalesce(f.cbsa_pop_2024, 0) as cbsa_pop_2024,
        case
            when b.geo_level in ('cbsa', 'county') then coalesce(f.major_cbsa_100k_flag, false)
            else false
        end as major_cbsa_100k_flag,
        case
            when b.geo_level in ('cbsa', 'county') then coalesce(f.major_cbsa_250k_flag, false)
            else false
        end as major_cbsa_250k_flag
    from income_windows b
    left join cbsa_dim cd
        on b.parent_cbsa_code = cd.cbsa_code
    left join major_cbsa_flags_2024 f
        on case
            when b.geo_level = 'cbsa' then b.geo_id
            when b.geo_level = 'county' then b.parent_cbsa_code
            else null
        end = f.cbsa_code
)

select *
from enriched;
