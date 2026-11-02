-- CBSAs that touch NY (2023 delineations), display geometry.
-- Full shapes, including out-of-state parts; clip to the NY outline for drawing only.
SELECT
  c.cbsa_code,
  c.cbsa_name,
  CASE c.LSAD WHEN 'M1' THEN 'metro' WHEN 'M2' THEN 'micro' END AS cbsa_type,
  x.counties AS ny_county_count,
  c.geom_wkb
FROM geo.cbsas AS c
JOIN silver.xwalk_cbsa_state AS x
  ON x.cbsa_code = c.cbsa_code
 AND x.state_fips = '36'
ORDER BY cbsa_type, c.cbsa_name
