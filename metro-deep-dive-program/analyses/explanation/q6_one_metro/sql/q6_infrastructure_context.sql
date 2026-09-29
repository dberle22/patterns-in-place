-- The path is resolved from the published Infrastructure artifact; Q6 does not
-- materialize or transform the retained-feature overlap into a shared mart.
SELECT *
FROM read_parquet('__INFRASTRUCTURE_PATH__')
WHERE market_id='__CBSA_CODE__'
ORDER BY overlap_length_m DESC NULLS LAST, overlap_area_sqm DESC NULLS LAST;
