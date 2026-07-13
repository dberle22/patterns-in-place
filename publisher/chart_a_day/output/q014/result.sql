with base as (
    select
        geo_level,
        geo_id,
        geo_name,
        max(case when year = 2018 then per_capita_income end) as pci_2018,
        max(case when year = 2023 then per_capita_income end) as pci_2023,
        max(case when year = 2023 then pop_total end) as pop_2023
    from gold.housing_core_wide
    where geo_level = 'cbsa'
      and year in (2018, 2023)
    group by 1, 2, 3
),
ranked as (
    select
        *,
        (pci_2023 / nullif(pci_2018, 0)) - 1.0 as growth_rate,
        row_number() over (order by ((pci_2023 / nullif(pci_2018, 0)) - 1.0) desc, geo_name asc) as rank_desc
    from base
    where pci_2018 is not null
      and pci_2023 is not null
      and pop_2023 >= 250000
)
select
    geo_level,
    geo_id,
    geo_name,
    '2018_2023_growth' as time_window,
    'per_capita_income_growth_5yr' as metric_id,
    'Five-year per capita income growth (%)' as metric_label,
    growth_rate * 100.0 as metric_value,
    rank_desc,
    rank_desc <= 5 as highlight_flag,
    'gold.housing_core_wide' as source,
    '2026-07-12' as vintage,
    'Growth compares 2018 vs 2023 per capita income and is limited to CBSAs with population >= 250k in 2023.' as note
from ranked
where rank_desc <= 15
order by rank_desc;
