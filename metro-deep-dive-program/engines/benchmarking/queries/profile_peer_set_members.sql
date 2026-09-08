-- Read the materialized peer-set membership for one target CBSA.
-- Use benchmark_engine.py to fetch values and summary stats for any metric.

SELECT
  comparison_set_type,
  member_role,
  member_rank,
  member_geo_id,
  member_geo_name,
  membership_source
FROM mart_benchmarking.benchmark_set_members
WHERE target_geo_level = 'cbsa'
  AND target_geo_id = '__CBSA_CODE__'
  AND comparison_set_type = 'peer_set'
ORDER BY
  member_rank,
  member_geo_name;
