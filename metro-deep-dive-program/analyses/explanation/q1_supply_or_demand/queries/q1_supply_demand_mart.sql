-- Q1's analysis-owned component mart. It keeps raw Gold fields beside clear
-- derived measures so notebook queries never recreate joins or hide grain gaps.
create schema if not exists mart_explanation_q1;

create or replace table mart_explanation_q1.supply_demand_base as
with direct as (
    select
        h.geo_level,
        h.geo_id,
        h.geo_name,
        h.year,
        d.parent_cbsa_code as cbsa_code,
        d.parent_cbsa_code is not null or h.geo_level = 'cbsa' as has_cbsa_membership,
        case when h.geo_level = 'tract' and h.year < 2020 then 2010
             when h.geo_level = 'tract' then 2020 else null end as boundary_vintage,
        'direct' as observation_type,
        h.pop_total,
        p.pop_growth_1yr,
        p.pop_growth_5yr,
        h.hu_total,
        h.occ_occupied,
        h.occ_vacant,
        h.vacancy_rate,
        h.owner_occupied,
        h.renter_occupied,
        h.pct_struct_multifam,
        h.median_gross_rent,
        h.annualized_median_rent,
        h.median_hh_income,
        h.rent_to_income,
        h.median_owner_costs_mortgage,
        h.median_owner_costs_mortgage * 12.0 as annualized_owner_costs_mortgage,
        h.median_owner_costs_no_mortgage,
        h.median_owner_costs_no_mortgage * 12.0 as annualized_owner_costs_no_mortgage,
        h.median_home_value,
        h.value_to_income,
        h.pct_rent_burden_30plus,
        h.permits_total_units,
        h.permits_per_1000_housing_units,
        m.hpi_5yr_pct,
        m.zhvi_annual_avg_yoy_pct,
        m.zori_annual_avg_yoy_pct,
        migration.mobility_rate,
        migration.migration_churn,
        migration.irs_net_migration_rate
    from gold.housing_core_wide h
    left join gold.population_demographics p using (geo_level, geo_id, year)
    left join gold.housing_market_wide m using (geo_level, geo_id, year)
    left join gold.migration_wide migration using (geo_level, geo_id, year)
    left join gold.dim_geo d on h.geo_level = d.geo_level and h.geo_id = d.geo_id
    where h.geo_level in ('cbsa', 'county', 'tract', 'zcta', 'place')
),
windowed as (
    select
        *,
        lag(year, 5) over (partition by geo_level, geo_id order by year) as lag5_year,
        lag(annualized_median_rent, 5) over (partition by geo_level, geo_id order by year) as annualized_median_rent_lag5,
        lag(median_hh_income, 5) over (partition by geo_level, geo_id order by year) as median_hh_income_lag5,
        lag(median_home_value, 5) over (partition by geo_level, geo_id order by year) as median_home_value_lag5,
        lag(median_owner_costs_mortgage, 5) over (partition by geo_level, geo_id order by year) as owner_costs_mortgage_lag5,
        lag(median_owner_costs_no_mortgage, 5) over (partition by geo_level, geo_id order by year) as owner_costs_no_mortgage_lag5,
        lag(pct_rent_burden_30plus, 5) over (partition by geo_level, geo_id order by year) as pct_rent_burden_30plus_lag5,
        lag(hu_total, 5) over (partition by geo_level, geo_id order by year) as hu_total_lag5,
        sum(permits_total_units) over (
            partition by geo_level, geo_id order by year
            rows between 4 preceding and current row
        ) as permits_total_units_5yr,
        count(permits_total_units) over (
            partition by geo_level, geo_id order by year
            rows between 4 preceding and current row
        ) as permits_year_count_5yr
    from direct
),
derived as (
    select
        *,
        -- This market-price proxy uses income for all ACS households, rather
        -- than renter-household income. It must not use a burden threshold.
        case when median_hh_income > 0 then annualized_median_rent / median_hh_income end as median_rent_to_all_hh_income_proxy,
        case when median_hh_income > 0 then annualized_owner_costs_mortgage / median_hh_income end as owner_cost_to_income_mortgage,
        case when median_hh_income > 0 then annualized_owner_costs_no_mortgage / median_hh_income end as owner_cost_to_income_no_mortgage,
        case when lag5_year = year - 5 and hu_total_lag5 > 0 then (hu_total - hu_total_lag5) / hu_total_lag5 end as housing_unit_growth_5yr,
        case when lag5_year = year - 5 and hu_total_lag5 > 0 and permits_year_count_5yr = 5 then permits_total_units_5yr / hu_total_lag5 * 1000.0 end as permits_5yr_per_1000_start_units,
        case when lag5_year = year - 5 and annualized_median_rent_lag5 > 0 then (annualized_median_rent - annualized_median_rent_lag5) / annualized_median_rent_lag5 end as rent_growth_5yr,
        case when lag5_year = year - 5 and median_hh_income_lag5 > 0 then (median_hh_income - median_hh_income_lag5) / median_hh_income_lag5 end as income_growth_5yr,
        case when lag5_year = year - 5 and annualized_median_rent_lag5 > 0 and median_hh_income_lag5 > 0 then
            (annualized_median_rent / median_hh_income) / (annualized_median_rent_lag5 / median_hh_income_lag5) - 1
        end as median_rent_to_all_hh_income_proxy_change_5yr,
        -- ACS B25070 is the renter-household burden measure; its conventional
        -- 30% threshold therefore has a valid household-affordability meaning.
        case when lag5_year = year - 5 and pct_rent_burden_30plus_lag5 is not null then
            pct_rent_burden_30plus - pct_rent_burden_30plus_lag5
        end as pct_rent_burden_30plus_change_5yr,
        case when lag5_year = year - 5 and median_home_value_lag5 > 0 and median_hh_income_lag5 > 0 then
            (median_home_value / median_hh_income) / (median_home_value_lag5 / median_hh_income_lag5) - 1
        end as value_to_income_change_5yr,
        case when lag5_year = year - 5 and owner_costs_mortgage_lag5 > 0 and median_hh_income_lag5 > 0 then
            (median_owner_costs_mortgage / median_hh_income) / (owner_costs_mortgage_lag5 / median_hh_income_lag5) - 1
        end as owner_cost_to_income_mortgage_change_5yr,
        case when lag5_year = year - 5 and owner_costs_no_mortgage_lag5 > 0 and median_hh_income_lag5 > 0 then
            (median_owner_costs_no_mortgage / median_hh_income) / (owner_costs_no_mortgage_lag5 / median_hh_income_lag5) - 1
        end as owner_cost_to_income_no_mortgage_change_5yr
    from windowed
)
select
    *,
    permits_total_units is not null as has_permit_data,
    hpi_5yr_pct is not null or zhvi_annual_avg_yoy_pct is not null as has_price_context,
    pop_growth_5yr is not null as has_five_year_population_growth,
    annualized_median_rent is not null
        and median_hh_income is not null
        and vacancy_rate is not null as has_core_affordability_data
from derived;

-- Counts can cross the tract-vintage boundary; medians, rates, and price series
-- deliberately do not. Population and housing measures use their matching
-- temporal weight basis and carry the Geography layer's allocation QA fields.
create or replace table mart_explanation_q1.tract_2020_harmonized_counts as
with historical as (
    select
        b.year,
        edge.to_geo_id as geo_id,
        edge.to_boundary_vintage as boundary_vintage,
        string_agg(distinct edge.change_type, ', ' order by edge.change_type) as change_type,
        string_agg(distinct edge.quality_flag, ', ' order by edge.quality_flag) as quality_flag,
        sum(b.pop_total * pop_edge.weight) as pop_total_harmonized,
        sum(b.hu_total * hu_edge.weight) as hu_total_harmonized,
        sum(b.occ_occupied * hu_edge.weight) as occ_occupied_harmonized,
        sum(b.occ_vacant * hu_edge.weight) as occ_vacant_harmonized,
        sum(b.owner_occupied * hu_edge.weight) as owner_occupied_harmonized,
        sum(b.renter_occupied * hu_edge.weight) as renter_occupied_harmonized
    from mart_explanation_q1.supply_demand_base b
    join mart_geography.temporal_edges pop_edge
      on b.geo_id = pop_edge.from_geo_id
     and pop_edge.from_geo_level = 'tract'
     and pop_edge.weight_basis = 'population'
    join mart_geography.temporal_edges hu_edge
      on b.geo_id = hu_edge.from_geo_id
     and hu_edge.to_geo_id = pop_edge.to_geo_id
     and hu_edge.from_geo_level = 'tract'
     and hu_edge.weight_basis = 'housing_units'
    join mart_geography.temporal_edges edge
      on edge.from_geo_id = b.geo_id
     and edge.to_geo_id = pop_edge.to_geo_id
     and edge.from_geo_level = 'tract'
     and edge.weight_basis = 'housing_units'
    where b.geo_level = 'tract' and b.year < 2020
    group by b.year, edge.to_geo_id, edge.to_boundary_vintage
),
current as (
    select year, geo_id, 2020 as boundary_vintage, 'direct_2020' as change_type,
           'exact' as quality_flag, pop_total, hu_total, occ_occupied, occ_vacant,
           owner_occupied, renter_occupied
    from mart_explanation_q1.supply_demand_base
    where geo_level = 'tract' and year >= 2020
)
select
    year,
    geo_id,
    boundary_vintage,
    'harmonized_count' as observation_type,
    change_type,
    quality_flag,
    pop_total_harmonized as pop_total,
    hu_total_harmonized as hu_total,
    occ_occupied_harmonized as occ_occupied,
    occ_vacant_harmonized as occ_vacant,
    owner_occupied_harmonized as owner_occupied,
    renter_occupied_harmonized as renter_occupied,
    occ_vacant_harmonized / nullif(occ_occupied_harmonized + occ_vacant_harmonized, 0) as vacancy_rate_recomputed
from historical
union all
select
    year, geo_id, boundary_vintage, 'harmonized_count', change_type, quality_flag,
    pop_total, hu_total, occ_occupied, occ_vacant, owner_occupied, renter_occupied,
    occ_vacant / nullif(occ_occupied + occ_vacant, 0) as vacancy_rate_recomputed
from current;
