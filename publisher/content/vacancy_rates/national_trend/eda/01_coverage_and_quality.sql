-- EDA 01: confirm year coverage, geo coverage, and non-finite values
-- for vacancy_rate before building the national trend chart.

select
  geo_level,
  min(year) as min_year,
  max(year) as max_year,
  count(*) as total_rows,
  count(distinct geo_id) as distinct_geos,
  count_if(vacancy_rate is null) as null_rows,
  count_if(isnan(vacancy_rate)) as nan_rows,
  count_if(isinf(vacancy_rate)) as inf_rows,
  count_if(
    vacancy_rate is not null
    and not isnan(vacancy_rate)
    and not isinf(vacancy_rate)
  ) as finite_rows
from gold.housing_core_wide
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
