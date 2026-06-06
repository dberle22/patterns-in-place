-- EDA 01: confirm complete coverage for the US + four Census regions and
-- inspect the source labels available for charting.

select
  geo_level,
  geo_name,
  min(year) as min_year,
  max(year) as max_year,
  count(*) as total_rows,
  count_if(vacancy_rate is null) as null_rows,
  count_if(vacancy_rate is not null and isnan(vacancy_rate)) as nan_rows,
  count_if(vacancy_rate is not null and isinf(vacancy_rate)) as inf_rows,
  count_if(
    vacancy_rate is not null
    and not isnan(vacancy_rate)
    and not isinf(vacancy_rate)
  ) as finite_rows
from gold.housing_core_wide
where geo_level in ('us', 'region')
group by 1, 2
order by case geo_level
  when 'us' then 1
  when 'region' then 2
  else 99
end, geo_name;
