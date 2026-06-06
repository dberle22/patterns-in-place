create or replace table neighborhood_character_mart.nta_public_poi_counts as

select
    a.nta_id,
    b.nta_name,
    b.borough,
    a.category,
    count(*) as poi_count
from neighborhood_character_mart.nta_poi_assignments a
inner join neighborhood_character_mart.nta_boundaries b
    on a.nta_id = b.nta_id
where a.poi_source = 'public'
  and a.category is not null
  and a.category <> ''
group by
    a.nta_id,
    b.nta_name,
    b.borough,
    a.category;
