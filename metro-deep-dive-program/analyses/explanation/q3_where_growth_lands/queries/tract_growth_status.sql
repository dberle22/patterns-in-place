-- Tract-level change and geometry for one CBSA and selected horizon.
SELECT
  status.*,
  tracts.geom_wkb
FROM mart_explanation_q3.tract_growth_status AS status
JOIN geo.tracts_all_us AS tracts USING (tract_geoid)
WHERE status.cbsa_code = ?
  AND status.horizon_years = ?;
