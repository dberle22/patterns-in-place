-- Structural smoke checks for the first two planned metro footprints. These do
-- not validate a metric; they only confirm governed relationship availability.
select 'Virginia allocation edges' as check_name, count(*) as row_count
from mart_geography.allocation_edges
where source_geo_id like '51%'
union all
select 'Florida allocation edges', count(*)
from mart_geography.allocation_edges
where source_geo_id like '12%'
union all
select 'Virginia 2010-to-2020 temporal edges', count(*)
from mart_geography.temporal_edges
where from_geo_id like '51%'
union all
select 'Florida 2010-to-2020 temporal edges', count(*)
from mart_geography.temporal_edges
where from_geo_id like '12%';
