-- EDA 03: measure post-2019 regional change, yearly spread, and whether the
-- rank order of regions changes over time.

with region_series as (
  select
    geo_name,
    year,
    vacancy_rate * 100 as vacancy_rate_pct
  from gold.housing_core_wide
  where geo_level = 'region'
    and vacancy_rate is not null
    and not isnan(vacancy_rate)
    and not isinf(vacancy_rate)
),
paired as (
  select
    a.geo_name,
    a.vacancy_rate_pct as vacancy_2019_pct,
    b.vacancy_rate_pct as vacancy_2024_pct,
    b.vacancy_rate_pct - a.vacancy_rate_pct as change_2019_2024_pp
  from region_series a
  join region_series b
    on a.geo_name = b.geo_name
   and a.year = 2019
   and b.year = 2024
),
spread_by_year as (
  select
    year,
    min(vacancy_rate_pct) as min_region_pct,
    max(vacancy_rate_pct) as max_region_pct,
    max(vacancy_rate_pct) - min(vacancy_rate_pct) as spread_pp
  from region_series
  group by 1
),
ranked as (
  select
    geo_name,
    year,
    vacancy_rate_pct,
    row_number() over (
      partition by year
      order by vacancy_rate_pct asc, geo_name
    ) as tight_rank
  from region_series
)
select
  'change_2019_2024'::varchar as section,
  geo_name,
  2019 as start_year,
  2024 as end_year,
  round(vacancy_2019_pct, 1) as start_pct,
  round(vacancy_2024_pct, 1) as end_pct,
  round(change_2019_2024_pp, 1) as delta_pp,
  null::double as spread_pp,
  null::bigint as best_rank,
  null::bigint as worst_rank
from paired

union all

select
  'spread_by_year'::varchar as section,
  cast(year as varchar) as geo_name,
  null::bigint as start_year,
  null::bigint as end_year,
  round(min_region_pct, 1) as start_pct,
  round(max_region_pct, 1) as end_pct,
  null::double as delta_pp,
  round(spread_pp, 1) as spread_pp,
  null::bigint as best_rank,
  null::bigint as worst_rank
from spread_by_year

union all

select
  'rank_stability'::varchar as section,
  geo_name,
  null::bigint as start_year,
  null::bigint as end_year,
  null::double as start_pct,
  null::double as end_pct,
  null::double as delta_pp,
  null::double as spread_pp,
  min(tight_rank) as best_rank,
  max(tight_rank) as worst_rank
from ranked
group by 1, 2

order by section, geo_name;
