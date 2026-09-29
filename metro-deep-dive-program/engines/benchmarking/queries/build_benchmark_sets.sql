-- Build one reusable comparison-set definition table per target CBSA.
-- Geographic sets come from gold.dim_geo. Peer sets come from the promoted
-- cross-frame Intelligence Framework peer surface.

CREATE SCHEMA IF NOT EXISTS mart_benchmarking;

CREATE OR REPLACE TABLE mart_benchmarking.benchmark_sets AS
WITH target_cbsa AS (
  SELECT
    geo_id AS target_geo_id,
    geo_name AS target_geo_name,
    state_fips AS primary_state_fips,
    state_name AS primary_state_name,
    parent_region_id,
    parent_division_id,
    parent_state_fips
  FROM patterns_in_place.gold.dim_geo
  WHERE geo_level = 'cbsa'
    AND is_metro = TRUE
),
target_cbsa_states AS (
  SELECT
    d.parent_cbsa_code AS target_geo_id,
    d.state_fips AS state_fips,
    MIN(d.state_name) AS state_name,
    COUNT(*) AS county_count_in_cbsa,
    ROW_NUMBER() OVER (
      PARTITION BY d.parent_cbsa_code
      ORDER BY COUNT(*) DESC, d.state_fips
    ) AS state_rank_in_cbsa
  FROM patterns_in_place.gold.dim_geo AS d
  WHERE d.geo_level = 'county'
    AND d.parent_cbsa_code IS NOT NULL
    AND d.state_fips IS NOT NULL
  GROUP BY 1, 2
),
geographic_sets AS (
  SELECT
    CONCAT('cbsa:', target_geo_id, '|national') AS comparison_set_id,
    'national' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    target_geo_id,
    target_geo_name,
    'All metropolitan CBSAs in the benchmark universe' AS comparison_label,
    'All metro CBSA rows in gold.dim_geo.' AS comparison_description,
    'all_years' AS comparison_year_scope,
    'gold.dim_geo' AS membership_source
  FROM target_cbsa

  UNION ALL

  SELECT
    CONCAT('cbsa:', target_geo_id, '|region|', parent_region_id) AS comparison_set_id,
    'region' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    target_geo_id,
    target_geo_name,
    CONCAT('Census region benchmark for region ', parent_region_id) AS comparison_label,
    'All metro CBSA rows sharing the same Census region as the target.' AS comparison_description,
    'all_years' AS comparison_year_scope,
    'gold.dim_geo' AS membership_source
  FROM target_cbsa
  WHERE parent_region_id IS NOT NULL

  UNION ALL

  SELECT
    CONCAT('cbsa:', target_geo_id, '|division|', parent_division_id) AS comparison_set_id,
    'division' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    target_geo_id,
    target_geo_name,
    CONCAT('Census division benchmark for division ', parent_division_id) AS comparison_label,
    'All metro CBSA rows sharing the same Census division as the target.' AS comparison_description,
    'all_years' AS comparison_year_scope,
    'gold.dim_geo' AS membership_source
  FROM target_cbsa
  WHERE parent_division_id IS NOT NULL

  UNION ALL

  SELECT
    CONCAT('cbsa:', t.target_geo_id, '|state_primary|', t.primary_state_fips) AS comparison_set_id,
    'state_primary' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    t.target_geo_id,
    t.target_geo_name,
    CONCAT('Primary-state benchmark for ', t.primary_state_name, ' (', t.primary_state_fips, ')') AS comparison_label,
    'All metro CBSA rows sharing the target CBSA primary state, defined by the first state named in the official CBSA label.' AS comparison_description,
    'all_years' AS comparison_year_scope,
    'gold.dim_geo' AS membership_source
  FROM target_cbsa AS t
  WHERE t.primary_state_fips IS NOT NULL

  UNION ALL

  SELECT
    CONCAT('cbsa:', t.target_geo_id, '|state_member|', s.state_fips) AS comparison_set_id,
    'state_member' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    t.target_geo_id,
    t.target_geo_name,
    CONCAT('Member-state benchmark for ', s.state_name, ' (', s.state_fips, ')') AS comparison_label,
    'All metro CBSA rows sharing one state that the target CBSA footprint belongs to. Multi-state CBSAs therefore receive one benchmark set per member state.' AS comparison_description,
    'all_years' AS comparison_year_scope,
    'gold.dim_geo' AS membership_source
  FROM target_cbsa AS t
  INNER JOIN target_cbsa_states AS s
    ON t.target_geo_id = s.target_geo_id
),
peer_sets AS (
  SELECT
    CONCAT('cbsa:', d.geo_id, '|peer_set|cross_frame_top10') AS comparison_set_id,
    'peer_set' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    d.geo_id AS target_geo_id,
    d.geo_name AS target_geo_name,
    'Cross-frame peer set benchmark' AS comparison_label,
    'Target CBSA plus its promoted top-10 cross-frame peers from mart_intelligence.' AS comparison_description,
    'all_years' AS comparison_year_scope,
    'mart_intelligence.intelligence_cross_frame' AS membership_source
  FROM patterns_in_place.gold.dim_geo AS d
  INNER JOIN mart_intelligence.intelligence_cross_frame AS cf
    ON d.geo_id = cf.cbsa_code
  WHERE d.geo_level = 'cbsa'
    AND d.is_metro = TRUE
)
SELECT *
FROM geographic_sets
UNION ALL
SELECT *
FROM peer_sets;
