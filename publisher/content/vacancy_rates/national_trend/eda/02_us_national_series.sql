-- EDA 02: pull the full US time series and year-over-year change.

with us_series as (
  select
    year,
    vacancy_rate * 100 as vacancy_rate_pct,
    lag(vacancy_rate * 100) over (order by year) as prior_year_pct
  from gold.housing_core_wide
  where geo_level = 'us'
    and vacancy_rate is not null
)
select
  year,
  round(vacancy_rate_pct, 1) as vacancy_rate_pct,
  round(vacancy_rate_pct - prior_year_pct, 1) as yoy_change_pp
from us_series
order by year;
