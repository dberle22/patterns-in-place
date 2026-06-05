-- Gold housing core mart
-- Grain: one row per geo_level + geo_id + year
-- Notes:
--   * Uses ACS housing/income as the base contract for all supported geographies.
--   * HUD FMR / HUD median rent are only available for a narrower set of geographies and
--     currently only for 2023, so those fields will be sparse outside that coverage.
--   * BPS carries duplicate rows in the current silver snapshot, so we aggregate to a stable
--     year/geo grain before joining.

create or replace table patterns_in_place.gold.housing_core_wide as
with pop_base as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        geo_name,
        year,
        pop_total
    from patterns_in_place.silver.age_kpi
),

housing as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        geo_name,
        year,
        hu_total,
        occ_total,
        occ_occupied,
        occ_vacant,
        vacancy_rate,
        occupancy_rate,
        tenure_total,
        owner_occupied,
        renter_occupied,
        owner_occ_rate,
        renter_occ_rate,
        median_gross_rent,
        median_home_value,
        median_owner_costs_mortgage,
        median_owner_costs_no_mortgage,
        rent_burden_total,
        rent_burden_30plus,
        rent_burden_50plus,
        pct_rent_burden_30plus,
        pct_rent_burden_50plus,
        struct_total,
        struct_1_unit,
        struct_sf_det,
        struct_small_mf,
        struct_mid_mf,
        struct_large_mf,
        struct_mobile,
        pct_struct_1_unit,
        pct_struct_sf_det,
        pct_struct_small_mf,
        pct_struct_mid_mf,
        pct_struct_large_mf,
        pct_struct_mobile
    from patterns_in_place.silver.housing_kpi
),

income as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        geo_name,
        year,
        median_hh_income,
        per_capita_income,
        pov_rate,
        gini_index,
        pct_hh_lt25k,
        pct_hh_25k_50k,
        pct_hh_50k_100k,
        pct_hh_100k_plus
    from patterns_in_place.silver.income_kpi
),

hud_fmr as (
    select
        case
            when lower(trim(geo_level)) = 'zip code' then 'zcta'
            else lower(trim(geo_level))
        end as geo_level,
        geo_id,
        max(geo_name) as geo_name,
        cast(period as integer) as year,
        max(fmr_0br) as fmr_0br,
        max(fmr_1br) as fmr_1br,
        max(fmr_2br) as fmr_2br,
        max(fmr_3br) as fmr_3br,
        max(fmr_4br) as fmr_4br
    from patterns_in_place.silver.hud_fmr_wide
    group by 1, 2, 4
),

hud_rent50 as (
    select
        case
            when lower(trim(geo_level)) = 'zip code' then 'zcta'
            else lower(trim(geo_level))
        end as geo_level,
        geo_id,
        max(geo_name) as geo_name,
        cast(period as integer) as year,
        max(rent50_0br) as rent50_0br,
        max(rent50_1br) as rent50_1br,
        max(rent50_2br) as rent50_2br,
        max(rent50_3br) as rent50_3br,
        max(rent50_4br) as rent50_4br
    from patterns_in_place.silver.hud_rent50_wide
    group by 1, 2, 4
),

bps as (
    select
        lower(trim(geo_level)) as geo_level,
        geo_id,
        max(geo_name) as geo_name,
        cast(period as integer) as year,
        max(total_bldgs) as permits_total_bldgs,
        max(total_units) as permits_total_units,
        max(total_value) as permits_total_value,
        max(bldgs_multifam) as permits_multifam_bldgs,
        max(units_multifam) as permits_multifam_units,
        max(value_multifam) as permits_multifam_value,
        max(avg_units_per_bldg) as permits_avg_units_per_bldg,
        max(avg_units_per_mf_bldg) as permits_avg_units_per_mf_bldg,
        max(share_multifam_units) as permits_share_multifam_units,
        max(share_units_5_plus) as permits_share_units_5_plus,
        max(share_units_1_unit) as permits_share_units_1_unit,
        max(structure_mix) as permits_structure_mix
    from patterns_in_place.silver.bps_wide
    group by 1, 2, 4
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
    coalesce(b.geo_name, p.geo_name, i.geo_name, f.geo_name, r.geo_name, bp.geo_name) as geo_name,
    b.year,
    p.pop_total,
    h.hu_total,
    h.occ_total,
    h.occ_occupied,
    h.occ_vacant,
    h.vacancy_rate,
    h.occupancy_rate,
    h.tenure_total,
    h.owner_occupied,
    h.renter_occupied,
    h.owner_occ_rate,
    h.renter_occ_rate,
    h.median_gross_rent,
    h.median_gross_rent * 12.0 as annualized_median_rent,
    h.median_home_value,
    h.median_owner_costs_mortgage,
    h.median_owner_costs_no_mortgage,
    h.rent_burden_total,
    h.rent_burden_30plus,
    h.rent_burden_50plus,
    h.pct_rent_burden_30plus,
    h.pct_rent_burden_50plus,
    i.median_hh_income,
    i.per_capita_income,
    i.pov_rate,
    i.gini_index,
    i.pct_hh_lt25k,
    i.pct_hh_25k_50k,
    i.pct_hh_50k_100k,
    i.pct_hh_100k_plus,
    case
        when i.median_hh_income > 0 and h.median_gross_rent is not null
            then (h.median_gross_rent * 12.0) / i.median_hh_income
        else null
    end as rent_to_income,
    case
        when i.median_hh_income > 0 and h.median_home_value is not null
            then h.median_home_value / i.median_hh_income
        else null
    end as value_to_income,
    f.fmr_0br,
    f.fmr_1br,
    f.fmr_2br,
    f.fmr_3br,
    f.fmr_4br,
    r.rent50_0br,
    r.rent50_1br,
    r.rent50_2br,
    r.rent50_3br,
    r.rent50_4br,
    case
        when f.fmr_2br is not null and h.median_gross_rent is not null
            then f.fmr_2br - h.median_gross_rent
        else null
    end as fmr_gap_2br_vs_median_rent,
    case
        when r.rent50_2br is not null and h.median_gross_rent is not null
            then r.rent50_2br - h.median_gross_rent
        else null
    end as rent50_gap_2br_vs_median_rent,
    bp.permits_total_bldgs,
    bp.permits_total_units,
    bp.permits_total_value,
    bp.permits_multifam_bldgs,
    bp.permits_multifam_units,
    bp.permits_multifam_value,
    bp.permits_avg_units_per_bldg,
    bp.permits_avg_units_per_mf_bldg,
    bp.permits_share_multifam_units,
    bp.permits_share_units_5_plus,
    bp.permits_share_units_1_unit,
    bp.permits_structure_mix,
    case
        when h.hu_total > 0 and bp.permits_total_units is not null
            then (bp.permits_total_units * 1000.0) / h.hu_total
        else null
    end as permits_per_1000_housing_units,
    case
        when p.pop_total > 0 and bp.permits_total_units is not null
            then (bp.permits_total_units * 1000.0) / p.pop_total
        else null
    end as permits_per_1000_population,
    case
        when h.hu_total > 0 and bp.permits_multifam_units is not null
            then (bp.permits_multifam_units * 1000.0) / h.hu_total
        else null
    end as multifam_permits_per_1000_housing_units,
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
    coalesce(h.pct_struct_small_mf, 0)
        + coalesce(h.pct_struct_mid_mf, 0)
        + coalesce(h.pct_struct_large_mf, 0) as pct_struct_multifam
from base b
left join pop_base p
    on b.geo_level = p.geo_level
   and b.geo_id = p.geo_id
   and b.year = p.year
left join housing h
    on b.geo_level = h.geo_level
   and b.geo_id = h.geo_id
   and b.year = h.year
left join income i
    on b.geo_level = i.geo_level
   and b.geo_id = i.geo_id
   and b.year = i.year
left join hud_fmr f
    on b.geo_level = f.geo_level
   and b.geo_id = f.geo_id
   and b.year = f.year
left join hud_rent50 r
    on b.geo_level = r.geo_level
   and b.geo_id = r.geo_id
   and b.year = r.year
left join bps bp
    on b.geo_level = bp.geo_level
   and b.geo_id = bp.geo_id
   and b.year = bp.year
;
