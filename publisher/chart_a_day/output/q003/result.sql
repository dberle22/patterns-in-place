-- Which metros have the highest share of cost-burdened renters in 2023?
-- This Chart-A-Day cut keeps the focus on large CBSAs so the ranked list
-- reflects markets with meaningful renter scale rather than small-college or
-- resort metros that can dominate the raw rate distribution.

with us_2023 as (
  select
    pct_rent_burden_30plus * 100 as us_cost_burden_pct
  from gold.housing_core_wide
  where geo_level = 'us'
    and year = 2023
    and pct_rent_burden_30plus is not null
),
major_cbsa_2023 as (
  select
    h.geo_level,
    h.geo_id,
    h.geo_name,
    p.pop_total,
    h.pct_rent_burden_30plus * 100 as metric_value
  from gold.housing_core_wide h
  join gold.population_demographics p
    on h.geo_level = p.geo_level
   and h.geo_id = p.geo_id
   and h.year = p.year
  where h.geo_level = 'cbsa'
    and h.year = 2023
    and p.pop_total >= 250000
    and h.pct_rent_burden_30plus is not null
    and not isnan(h.pct_rent_burden_30plus)
    and not isinf(h.pct_rent_burden_30plus)
),
ranked as (
  select
    'q003'::varchar as question_id,
    geo_level,
    geo_id,
    geo_name,
    2023::integer as year,
    '2023 level'::varchar as time_window,
    'pct_rent_burden_30plus'::varchar as metric_id,
    'Share of renter households spending 30%+ of income on rent'::varchar as metric_label,
    metric_value,
    row_number() over (order by metric_value desc, pop_total desc, geo_name) as rank,
    pop_total,
    'Top 20 CBSAs by renter cost burden (population >= 250k)'::varchar as "group",
    null::varchar as series,
    false as highlight_flag,
    (select us_cost_burden_pct from us_2023)::double as benchmark_value,
    'Population filter removes small-market outliers; benchmark is the US renter burden rate.'::varchar as note
  from major_cbsa_2023
)
select
  question_id,
  geo_level,
  geo_id,
  geo_name,
  year,
  time_window,
  metric_id,
  metric_label,
  metric_value,
  rank,
  pop_total,
  "group",
  series,
  highlight_flag,
  benchmark_value,
  note
from ranked
where rank <= 20
order by rank, geo_name;
