-- EDA 02: pull the full US + regional vacancy-rate series and compare each
-- region with the national benchmark from 2019 to 2024.

with series as (
  select
    geo_level,
    geo_name,
    year,
    vacancy_rate * 100 as vacancy_rate_pct
  from gold.housing_core_wide
  where geo_level in ('us', 'region')
    and vacancy_rate is not null
    and not isnan(vacancy_rate)
    and not isinf(vacancy_rate)
),
us_series as (
  select
    year,
    vacancy_rate_pct as us_vacancy_pct
  from series
  where geo_level = 'us'
)
select
  s.geo_level,
  s.geo_name,
  s.year,
  round(s.vacancy_rate_pct, 1) as vacancy_rate_pct,
  round(s.vacancy_rate_pct - u.us_vacancy_pct, 1) as gap_vs_us_pp
from series s
left join us_series u
  on s.year = u.year
order by case s.geo_level
  when 'us' then 1
  when 'region' then 2
  else 99
end, s.geo_name, s.year;
