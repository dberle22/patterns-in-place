-- EDA 04: inspect value ranges by geography and surface high-end outliers.

with finite_rates as (
  select
    geo_level,
    geo_name,
    year,
    hu_total,
    vacancy_rate
  from gold.housing_core_wide
  where vacancy_rate is not null
    and not isnan(vacancy_rate)
    and not isinf(vacancy_rate)
)
select
  geo_level,
  round(min(vacancy_rate) * 100, 1) as min_pct,
  round(avg(vacancy_rate) * 100, 1) as avg_pct,
  round(max(vacancy_rate) * 100, 1) as max_pct,
  count(*) as finite_rows
from finite_rates
group by 1
order by case geo_level
  when 'us' then 1
  when 'region' then 2
  when 'division' then 3
  when 'state' then 4
  when 'cbsa' then 5
  when 'county' then 6
  when 'tract' then 7
  when 'zcta' then 8
  when 'place' then 9
  else 99
end;

select
  geo_level,
  geo_name,
  year,
  round(vacancy_rate * 100, 1) as vacancy_rate_pct,
  hu_total
from finite_rates
where geo_level in ('cbsa', 'county')
order by vacancy_rate desc
limit 10;
