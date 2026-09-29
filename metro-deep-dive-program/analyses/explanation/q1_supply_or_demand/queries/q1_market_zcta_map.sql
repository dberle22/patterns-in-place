-- ZCTA display geometry is Census 2020 cartographic-boundary geometry. Values
-- remain direct 2024 ZCTA observations selected through weighted CBSA context.
select q.*, geometry.geom_wkb
from (
    select q.geo_id as zcta, q.geo_name, q.pct_rent_burden_30plus,
           q.median_rent_to_all_hh_income_proxy, q.vacancy_rate,
           q.pop_growth_5yr, q.zhvi_annual_avg_yoy_pct,
           q.zori_annual_avg_yoy_pct
    from mart_explanation_q1.supply_demand_base q
    join silver.xwalk_zcta_cbsa crosswalk on q.geo_id = crosswalk.zip_geoid
    where q.geo_level = 'zcta' and q.year = 2024
      and crosswalk.cbsa_geoid = '__CBSA_CODE__'
      and crosswalk.rel_weight_pop > 0
) q
join geo.zctas_display geometry on q.zcta = geometry.zcta_geoid;
