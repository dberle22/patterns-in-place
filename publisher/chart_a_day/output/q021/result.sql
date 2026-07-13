with metro_universe as (
  select
    pd.geo_id,
    dg.geo_name,
    hc.rent_to_income,
    hc.vacancy_rate,
    pd.pop_growth_5yr,
    hc.pct_rent_burden_30plus as cost_burden_share
  from gold.population_demographics pd
  join gold.housing_core_wide hc
    on pd.geo_id = hc.geo_id
   and pd.geo_level = hc.geo_level
   and pd.year = hc.year
  join gold.dim_geo dg
    on pd.geo_id = dg.geo_id
   and pd.geo_level = dg.geo_level
  where pd.geo_level = 'cbsa'
    and pd.year = 2023
    and pd.pop_total >= 250000
    and hc.rent_to_income is not null
    and hc.vacancy_rate is not null
    and pd.pop_growth_5yr is not null
    and hc.pct_rent_burden_30plus is not null
),
benchmark as (
  select
    median(rent_to_income) as rent_to_income,
    median(vacancy_rate) as vacancy_rate,
    median(pop_growth_5yr) as pop_growth_5yr,
    median(cost_burden_share) as cost_burden_share
  from metro_universe
),
austin as (
  select *
  from metro_universe
  where geo_name = 'Austin-Round Rock-San Marcos, TX'
),
austin_long as (
  select
    'rent_to_income' as metric_id,
    'Rent-to-income ratio' as metric_label,
    'Housing stress' as metric_group,
    0.200513 as dummy_keep
  from austin
  limit 1
),
metrics as (
  select
    a.geo_id,
    a.geo_name,
    'rent_to_income' as metric_id,
    'Rent-to-income ratio' as metric_label,
    'Housing stress' as metric_group,
    a.rent_to_income as metric_value,
    b.rent_to_income as benchmark_value,
    100.0 * (
      select sum(case when u.rent_to_income <= a.rent_to_income then 1 else 0 end) * 1.0 / count(*)
      from metro_universe u
    ) as normalized_value,
    100.0 * (
      select sum(case when u.rent_to_income <= b.rent_to_income then 1 else 0 end) * 1.0 / count(*)
      from metro_universe u
    ) as benchmark_normalized_value,
    1 as metric_order
  from austin a
  cross join benchmark b

  union all

  select
    a.geo_id,
    a.geo_name,
    'vacancy_rate' as metric_id,
    'Vacancy rate' as metric_label,
    'Housing stress' as metric_group,
    a.vacancy_rate as metric_value,
    b.vacancy_rate as benchmark_value,
    100.0 * (
      select sum(case when -u.vacancy_rate <= -a.vacancy_rate then 1 else 0 end) * 1.0 / count(*)
      from metro_universe u
    ) as normalized_value,
    100.0 * (
      select sum(case when -u.vacancy_rate <= -b.vacancy_rate then 1 else 0 end) * 1.0 / count(*)
      from metro_universe u
    ) as benchmark_normalized_value,
    2 as metric_order
  from austin a
  cross join benchmark b

  union all

  select
    a.geo_id,
    a.geo_name,
    'pop_growth_5yr' as metric_id,
    '5-year population growth' as metric_label,
    'Demand pressure' as metric_group,
    a.pop_growth_5yr as metric_value,
    b.pop_growth_5yr as benchmark_value,
    100.0 * (
      select sum(case when u.pop_growth_5yr <= a.pop_growth_5yr then 1 else 0 end) * 1.0 / count(*)
      from metro_universe u
    ) as normalized_value,
    100.0 * (
      select sum(case when u.pop_growth_5yr <= b.pop_growth_5yr then 1 else 0 end) * 1.0 / count(*)
      from metro_universe u
    ) as benchmark_normalized_value,
    3 as metric_order
  from austin a
  cross join benchmark b

  union all

  select
    a.geo_id,
    a.geo_name,
    'cost_burden_share' as metric_id,
    'Cost-burdened renter share' as metric_label,
    'Housing stress' as metric_group,
    a.cost_burden_share as metric_value,
    b.cost_burden_share as benchmark_value,
    100.0 * (
      select sum(case when u.cost_burden_share <= a.cost_burden_share then 1 else 0 end) * 1.0 / count(*)
      from metro_universe u
    ) as normalized_value,
    100.0 * (
      select sum(case when u.cost_burden_share <= b.cost_burden_share then 1 else 0 end) * 1.0 / count(*)
      from metro_universe u
    ) as benchmark_normalized_value,
    4 as metric_order
  from austin a
  cross join benchmark b
)
select
  'q021' as question_id,
  'cbsa' as geo_level,
  geo_id,
  geo_name,
  '2023' as time_window,
  metric_id,
  metric_label,
  metric_value,
  metric_group,
  normalized_value,
  benchmark_value,
  benchmark_normalized_value,
  'Large-metro median benchmark' as benchmark_label,
  true as highlight_flag,
  'higher_is_better' as direction,
  metric_order,
  'Benchmark uses the median across 2023 CBSAs with population >= 250k because the housing-wide Gold table does not expose a full-US row for these metrics. Rightward percentile means more housing stress or demand pressure.' as note,
  'gold.population_demographics + gold.housing_core_wide + gold.dim_geo' as source,
  '2026-07-12' as vintage
from metrics
order by metric_order asc;
