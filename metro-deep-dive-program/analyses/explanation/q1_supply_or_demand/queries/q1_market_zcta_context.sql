-- ZCTAs use the weighted HUD-USPS relationship; no ZCTA is treated as exact
-- CBSA containment. Values remain ZCTA-native and are not allocated.
select q.geo_id as zcta, q.geo_name, q.year, crosswalk.rel_weight_pop,
       crosswalk.rel_weight_hu, q.renter_cost_to_income, q.vacancy_rate,
       q.zhvi_annual_avg_yoy_pct, q.hpi_5yr_pct, q.zori_annual_avg_yoy_pct
from mart_explanation_q1.supply_demand_base q
join silver.xwalk_zcta_cbsa crosswalk on q.geo_id = crosswalk.zip_geoid
where q.geo_level = 'zcta' and q.year = 2024
  and crosswalk.cbsa_geoid = '__CBSA_CODE__'
  and crosswalk.rel_weight_pop > 0;
