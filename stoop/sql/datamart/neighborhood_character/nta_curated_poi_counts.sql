create or replace table neighborhood_character_mart.nta_curated_poi_counts as

with assigned as (
    select
        a.nta_id,
        b.nta_name,
        b.borough,
        a.category,
        coalesce(nullif(a.subcategory, ''), '__unknown__') as subcategory
    from neighborhood_character_mart.nta_poi_assignments a
    inner join neighborhood_character_mart.nta_boundaries b
        on a.nta_id = b.nta_id
    where a.poi_source = 'curated'
      and a.category is not null
      and a.category <> ''
),
counts as (
    select
        nta_id,
        nta_name,
        borough,
        category,
        subcategory,
        count(*) as poi_count
    from assigned
    group by all
),
category_totals as (
    select
        category,
        count(*) as nyc_category_total
    from assigned
    group by category
)
select
    c.nta_id,
    c.nta_name,
    c.borough,
    c.category,
    c.subcategory,
    c.poi_count,
    t.nyc_category_total
from counts c
inner join category_totals t
    on c.category = t.category;
