-- EDA for Insight 3: State vacancy map
-- Purpose:
--   1. Validate state-level coverage for 2019 and 2024
--   2. Inspect the 2024 distribution of vacancy rates
--   3. Compare 2019 vs 2024 levels and identify largest changes
--   4. Confirm contiguous-US map scope decisions before final chart SQL

with state_years as (
  select
    h.geo_id,
    h.geo_name,
    h.year,
    h.vacancy_rate * 100 as vacancy_rate_pct
  from gold.housing_core_wide h
  where h.geo_level = 'state'
    and h.year in (2019, 2024)
    and h.vacancy_rate is not null
    and not isnan(h.vacancy_rate)
    and not isinf(h.vacancy_rate)
),
state_change as (
  select
    y2024.geo_id,
    y2024.geo_name,
    y2019.vacancy_rate_pct as vacancy_rate_2019_pct,
    y2024.vacancy_rate_pct as vacancy_rate_2024_pct,
    y2024.vacancy_rate_pct - y2019.vacancy_rate_pct as vacancy_rate_change_pp
  from state_years y2019
  join state_years y2024
    on y2019.geo_id = y2024.geo_id
   and y2019.year = 2019
   and y2024.year = 2024
),
with_region as (
  select
    sc.*,
    sr.census_region,
    sr.census_division
  from state_change sc
  left join silver.xwalk_state_region sr
    on lpad(sc.geo_id, 2, '0') = sr.state_fips
),
contiguous_plus_dc as (
  select *
  from with_region
  where geo_name not in ('Alaska', 'Hawaii', 'Puerto Rico')
)

-- 1. Coverage check: should return 52 rows (50 states + DC + PR)
select
  'coverage_full_state_file' as eda_section,
  count(*) as state_count
from with_region

union all

-- 2. Coverage check for default contiguous national map footprint:
--    lower 48 states + DC = 49 rows
select
  'coverage_contiguous_plus_dc' as eda_section,
  count(*) as state_count
from contiguous_plus_dc
;


with state_years as (
  select
    h.geo_id,
    h.geo_name,
    h.year,
    h.vacancy_rate * 100 as vacancy_rate_pct
  from gold.housing_core_wide h
  where h.geo_level = 'state'
    and h.year in (2019, 2024)
    and h.vacancy_rate is not null
    and not isnan(h.vacancy_rate)
    and not isinf(h.vacancy_rate)
),
state_change as (
  select
    y2024.geo_id,
    y2024.geo_name,
    y2019.vacancy_rate_pct as vacancy_rate_2019_pct,
    y2024.vacancy_rate_pct as vacancy_rate_2024_pct,
    y2024.vacancy_rate_pct - y2019.vacancy_rate_pct as vacancy_rate_change_pp
  from state_years y2019
  join state_years y2024
    on y2019.geo_id = y2024.geo_id
   and y2019.year = 2019
   and y2024.year = 2024
),
contiguous_plus_dc as (
  select *
  from state_change
  where geo_name not in ('Alaska', 'Hawaii', 'Puerto Rico')
)

-- 3. Tightest states in 2024 for the contiguous map
select
  geo_name,
  round(vacancy_rate_2024_pct, 1) as vacancy_rate_2024_pct
from contiguous_plus_dc
order by vacancy_rate_2024_pct asc, geo_name
limit 10
;


with state_years as (
  select
    h.geo_id,
    h.geo_name,
    h.year,
    h.vacancy_rate * 100 as vacancy_rate_pct
  from gold.housing_core_wide h
  where h.geo_level = 'state'
    and h.year in (2019, 2024)
    and h.vacancy_rate is not null
    and not isnan(h.vacancy_rate)
    and not isinf(h.vacancy_rate)
),
state_change as (
  select
    y2024.geo_id,
    y2024.geo_name,
    y2019.vacancy_rate_pct as vacancy_rate_2019_pct,
    y2024.vacancy_rate_pct as vacancy_rate_2024_pct,
    y2024.vacancy_rate_pct - y2019.vacancy_rate_pct as vacancy_rate_change_pp
  from state_years y2019
  join state_years y2024
    on y2019.geo_id = y2024.geo_id
   and y2019.year = 2019
   and y2024.year = 2024
),
contiguous_plus_dc as (
  select *
  from state_change
  where geo_name not in ('Alaska', 'Hawaii', 'Puerto Rico')
)

-- 4. Loosest states in 2024 for the contiguous map
select
  geo_name,
  round(vacancy_rate_2024_pct, 1) as vacancy_rate_2024_pct
from contiguous_plus_dc
order by vacancy_rate_2024_pct desc, geo_name
limit 10
;


with state_years as (
  select
    h.geo_id,
    h.geo_name,
    h.year,
    h.vacancy_rate * 100 as vacancy_rate_pct
  from gold.housing_core_wide h
  where h.geo_level = 'state'
    and h.year in (2019, 2024)
    and h.vacancy_rate is not null
    and not isnan(h.vacancy_rate)
    and not isinf(h.vacancy_rate)
),
state_change as (
  select
    y2024.geo_id,
    y2024.geo_name,
    y2019.vacancy_rate_pct as vacancy_rate_2019_pct,
    y2024.vacancy_rate_pct as vacancy_rate_2024_pct,
    y2024.vacancy_rate_pct - y2019.vacancy_rate_pct as vacancy_rate_change_pp
  from state_years y2019
  join state_years y2024
    on y2019.geo_id = y2024.geo_id
   and y2019.year = 2019
   and y2024.year = 2024
),
contiguous_plus_dc as (
  select *
  from state_change
  where geo_name not in ('Alaska', 'Hawaii', 'Puerto Rico')
)

-- 5. Largest 2019 to 2024 vacancy-rate declines
select
  geo_name,
  round(vacancy_rate_2019_pct, 1) as vacancy_rate_2019_pct,
  round(vacancy_rate_2024_pct, 1) as vacancy_rate_2024_pct,
  round(vacancy_rate_change_pp, 1) as vacancy_rate_change_pp
from contiguous_plus_dc
order by vacancy_rate_change_pp asc, geo_name
limit 10
;


with state_years as (
  select
    h.geo_id,
    h.geo_name,
    h.year,
    h.vacancy_rate * 100 as vacancy_rate_pct
  from gold.housing_core_wide h
  where h.geo_level = 'state'
    and h.year in (2019, 2024)
    and h.vacancy_rate is not null
    and not isnan(h.vacancy_rate)
    and not isinf(h.vacancy_rate)
),
state_change as (
  select
    y2024.geo_id,
    y2024.geo_name,
    y2019.vacancy_rate_pct as vacancy_rate_2019_pct,
    y2024.vacancy_rate_pct as vacancy_rate_2024_pct,
    y2024.vacancy_rate_pct - y2019.vacancy_rate_pct as vacancy_rate_change_pp
  from state_years y2019
  join state_years y2024
    on y2019.geo_id = y2024.geo_id
   and y2019.year = 2019
   and y2024.year = 2024
),
contiguous_plus_dc as (
  select *
  from state_change
  where geo_name not in ('Alaska', 'Hawaii', 'Puerto Rico')
)

-- 6. Distribution summary and count of declining states
select
  round(avg(vacancy_rate_2024_pct), 1) as avg_2024_pct,
  round(median(vacancy_rate_2024_pct), 1) as median_2024_pct,
  round(min(vacancy_rate_2024_pct), 1) as min_2024_pct,
  round(max(vacancy_rate_2024_pct), 1) as max_2024_pct,
  round(avg(vacancy_rate_change_pp), 1) as avg_change_pp,
  round(median(vacancy_rate_change_pp), 1) as median_change_pp,
  round(min(vacancy_rate_change_pp), 1) as min_change_pp,
  round(max(vacancy_rate_change_pp), 1) as max_change_pp,
  sum(case when vacancy_rate_change_pp < 0 then 1 else 0 end) as declined_states,
  sum(case when vacancy_rate_change_pp > 0 then 1 else 0 end) as increased_states
from contiguous_plus_dc
;


with state_years as (
  select
    h.geo_id,
    h.geo_name,
    h.year,
    h.vacancy_rate * 100 as vacancy_rate_pct
  from gold.housing_core_wide h
  where h.geo_level = 'state'
    and h.year in (2019, 2024)
    and h.vacancy_rate is not null
    and not isnan(h.vacancy_rate)
    and not isinf(h.vacancy_rate)
),
state_change as (
  select
    y2024.geo_id,
    y2024.geo_name,
    y2019.vacancy_rate_pct as vacancy_rate_2019_pct,
    y2024.vacancy_rate_pct as vacancy_rate_2024_pct,
    y2024.vacancy_rate_pct - y2019.vacancy_rate_pct as vacancy_rate_change_pp
  from state_years y2019
  join state_years y2024
    on y2019.geo_id = y2024.geo_id
   and y2019.year = 2019
   and y2024.year = 2024
),
with_region as (
  select
    sc.*,
    sr.census_region
  from state_change sc
  left join silver.xwalk_state_region sr
    on lpad(sc.geo_id, 2, '0') = sr.state_fips
)

-- 7. Regional pattern check for narrative framing
select
  census_region,
  round(avg(vacancy_rate_2024_pct), 1) as avg_2024_pct,
  round(avg(vacancy_rate_change_pp), 1) as avg_change_pp,
  count(*) as state_count
from with_region
where census_region is not null
  and geo_name not in ('Puerto Rico')
group by census_region
order by avg_2024_pct asc
;
