select
  'q028' as question_id,
  d.geo_level,
  d.geo_id,
  d.geo_name,
  '2023_cross_section' as time_window,
  d.median_age as x_value,
  h.rent_to_income as y_value,
  'Median age' as x_label,
  'Rent-to-income ratio' as y_label,
  false as highlight_flag,
  false as label_flag,
  'Patterns in Place gold tables: population_demographics and housing_core_wide' as source,
  '2023' as vintage,
  'All CBSAs with non-missing 2023 median age and rent-to-income ratio. Hexbin used because the full metro set is too dense for a plain scatter.' as note
from gold.population_demographics d
join gold.housing_core_wide h
  using (geo_level, geo_id, geo_name, year)
where d.geo_level = 'cbsa'
  and d.year = 2023
  and d.median_age is not null
  and h.rent_to_income is not null
order by d.geo_name;
