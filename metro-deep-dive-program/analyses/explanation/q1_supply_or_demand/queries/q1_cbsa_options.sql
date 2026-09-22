-- The market notebook uses this canonical list for its standard name-and-code
-- selector; only CBSAs with Q1 evidence appear as selectable markets.
select distinct
    geo_id as cbsa_code,
    geo_name as cbsa_name,
    geo_name || ' (' || geo_id || ')' as display_name
from mart_explanation_q1.supply_demand_base
where geo_level = 'cbsa' and year = 2024
order by cbsa_name, cbsa_code;
