SELECT source_state, source_part, coverage_status, source_jobs_total,
       place_jobs_total, geography_match_rate, reconciliation_passed
FROM silver.lehd_lodes_od_place_coverage
WHERE job_type='JT00' AND segment='S000' AND transformation_version='lodes_od_place_v2'
ORDER BY source_state, source_part;
