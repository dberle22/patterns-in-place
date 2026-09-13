-- Candidate four-family overheating diagnostic. Every ranked row has the same
-- complete family set; no partial component averaging is allowed in this V1.
with base as (
    select b.*, d.cbsa_type_short
    from mart_explanation_q1.supply_demand_base b
    left join gold.dim_geo d on d.geo_level = 'cbsa' and d.geo_id = b.geo_id
    where b.geo_level = 'cbsa' and b.year = 2024 and b.pop_total >= 100000
      and hpi_5yr_pct is not null and rent_growth_5yr is not null
      and rent_to_income_change_5yr is not null and value_to_income_change_5yr is not null
      and pop_growth_5yr is not null and housing_unit_growth_5yr is not null
      and permits_5yr_per_1000_start_units is not null and vacancy_rate is not null
),
ranked as (
    select
        *,
        percent_rank() over (order by hpi_5yr_pct) as hpi_momentum_score,
        percent_rank() over (order by rent_growth_5yr) as rent_momentum_score,
        percent_rank() over (order by rent_to_income_change_5yr) as rent_affordability_score,
        percent_rank() over (order by value_to_income_change_5yr) as value_affordability_score,
        percent_rank() over (order by pop_growth_5yr) as demand_score,
        1.0 - percent_rank() over (order by housing_unit_growth_5yr) as housing_constraint_score,
        1.0 - percent_rank() over (order by permits_5yr_per_1000_start_units) as permit_constraint_score,
        1.0 - percent_rank() over (order by vacancy_rate) as vacancy_constraint_score
    from base
),
components as (
    select
        *,
        (hpi_momentum_score + rent_momentum_score) / 2.0 as momentum_component_score,
        (rent_affordability_score + value_affordability_score) / 2.0 as affordability_deterioration_component_score,
        demand_score as demand_component_score,
        (housing_constraint_score + permit_constraint_score + vacancy_constraint_score) / 3.0 as supply_constraint_component_score
    from ranked
),
scored as (
    select
        *,
        (momentum_component_score + affordability_deterioration_component_score
            + demand_component_score + supply_constraint_component_score) / 4.0 as balanced_index,
        0.35 * momentum_component_score + 0.20 * affordability_deterioration_component_score
            + 0.30 * demand_component_score + 0.15 * supply_constraint_component_score as momentum_demand_index,
        0.15 * momentum_component_score + 0.35 * affordability_deterioration_component_score
            + 0.15 * demand_component_score + 0.35 * supply_constraint_component_score as affordability_supply_index
    from components
)
select
    geo_id as cbsa_code, geo_name as cbsa_name, cbsa_type_short, pop_total,
    hpi_5yr_pct, rent_growth_5yr, housing_unit_growth_5yr,
    permits_5yr_per_1000_start_units, vacancy_rate, pop_growth_5yr,
    rent_to_income_change_5yr, value_to_income_change_5yr,
    momentum_component_score, affordability_deterioration_component_score,
    demand_component_score, supply_constraint_component_score,
    balanced_index, momentum_demand_index, affordability_supply_index,
    rank() over (order by balanced_index desc) as balanced_rank,
    rank() over (order by momentum_demand_index desc) as momentum_demand_rank,
    rank() over (order by affordability_supply_index desc) as affordability_supply_rank,
    case
        when renter_cost_to_income <= 0.30 and supply_constraint_component_score <= 0.40 then 'supply-supported affordability'
        when renter_cost_to_income <= 0.30 and demand_component_score <= 0.40 then 'weak-demand affordability'
        when renter_cost_to_income > 0.30 and momentum_component_score >= 0.60
            and demand_component_score >= 0.60 and supply_constraint_component_score >= 0.60 then 'pressure/shortage'
        else 'mixed or no clear signal'
    end as component_classification
from scored;
