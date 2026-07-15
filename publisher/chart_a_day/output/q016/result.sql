select
    p.geo_level,
    p.geo_id,
    p.geo_name,
    p.pop_total as size_value,
    '2018_2023_growth_vs_2023_affordability' as time_window,
    p.pop_growth_5yr * 100.0 as x_value,
    h.rent_to_income * 100.0 as y_value,
    'Five-year population growth (%)' as x_label,
    'Rent-to-income ratio (%)' as y_label,
    d.region_name as "group",
    p.geo_name in (
        'Austin-Round Rock-San Marcos, TX',
        'Miami-Fort Lauderdale-West Palm Beach, FL',
        'Orlando-Kissimmee-Sanford, FL',
        'Provo-Orem-Lehi, UT',
        'Lakeland-Winter Haven, FL'
    ) as label_flag,
    p.geo_name in (
        'Austin-Round Rock-San Marcos, TX',
        'Miami-Fort Lauderdale-West Palm Beach, FL',
        'Orlando-Kissimmee-Sanford, FL'
    ) as highlight_flag,
    'gold.population_demographics + gold.housing_core_wide + gold.dim_geo' as source,
    '2026-07-12' as vintage,
    'Filtered to CBSAs with population >= 500k. X axis uses 2018-2023 population growth; Y axis uses 2023 rent-to-income ratio in percentage points.' as note
from gold.population_demographics p
join gold.housing_core_wide h
  on p.geo_level = h.geo_level
 and p.geo_id = h.geo_id
 and p.year = h.year
join gold.dim_geo d
  on p.geo_level = d.geo_level
 and p.geo_id = d.geo_id
where p.geo_level = 'cbsa'
  and p.year = 2023
  and p.pop_total >= 500000
  and p.pop_growth_5yr is not null
  and h.rent_to_income is not null
order by p.pop_growth_5yr desc, h.rent_to_income desc, p.geo_name asc;
