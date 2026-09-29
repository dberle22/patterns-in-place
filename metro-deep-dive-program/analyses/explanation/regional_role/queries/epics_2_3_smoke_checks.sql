-- Structural regression checks for Regional Role Epics 2–3.
-- Run after rebuilding Benchmarking and the Geography regional-lens surfaces.

-- Benchmarking must use Geography's first-named-state primary identity.
SELECT
  COUNT(*) AS primary_state_mismatch_count
FROM mart_benchmarking.benchmark_sets AS benchmark
INNER JOIN gold.dim_geo AS geography
  ON benchmark.target_geo_id = geography.geo_id
 AND geography.geo_level = 'cbsa'
WHERE benchmark.comparison_set_type = 'state_primary'
  AND regexp_extract(benchmark.comparison_set_id, 'state_primary\\|([0-9]{2})', 1)
      <> geography.state_fips;

-- The edge relation must be symmetric and every membership key unique.
SELECT
  (
    SELECT COUNT(*)
    FROM mart_geography.state_adjacency AS edge
    LEFT JOIN mart_geography.state_adjacency AS reverse_edge
      ON edge.state_fips = reverse_edge.adjacent_state_fips
     AND edge.adjacent_state_fips = reverse_edge.state_fips
    WHERE reverse_edge.state_fips IS NULL
  ) AS asymmetric_adjacency_count,
  (
    SELECT COUNT(*)
    FROM (
      SELECT target_cbsa_code, lens_id, parameter_name, parameter_value,
             member_cbsa_code, COUNT(*) AS duplicate_count
      FROM mart_geography.region_lens_membership
      GROUP BY 1, 2, 3, 4, 5
      HAVING COUNT(*) > 1
    )
  ) AS duplicate_membership_key_count;

-- Richmond and a multi-state example make the declared primary-state rule visible.
SELECT lens_id, parameter_value, COUNT(*) AS member_count
FROM mart_geography.region_lens_membership
WHERE target_cbsa_code = '40060'
GROUP BY 1, 2
ORDER BY 1, 2;

SELECT benchmark.comparison_set_id, geography.geo_name, geography.state_fips
FROM mart_benchmarking.benchmark_sets AS benchmark
INNER JOIN gold.dim_geo AS geography
  ON benchmark.target_geo_id = geography.geo_id
 AND geography.geo_level = 'cbsa'
WHERE geography.geo_name LIKE 'Wheeling,%'
  AND benchmark.comparison_set_type = 'state_primary';
