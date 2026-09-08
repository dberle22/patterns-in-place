-- Materialize the membership of each benchmark set.
-- Geographic memberships come from gold.dim_geo. Peer-set memberships come from
-- the promoted cross-frame peer fields.

CREATE SCHEMA IF NOT EXISTS mart_benchmarking;

CREATE OR REPLACE TABLE mart_benchmarking.benchmark_set_members AS
WITH target_cbsa AS (
  SELECT
    geo_id AS target_geo_id,
    geo_name AS target_geo_name,
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
member_cbsa AS (
  SELECT
    geo_id AS member_geo_id,
    geo_name AS member_geo_name,
    parent_region_id,
    parent_division_id,
    parent_state_fips
  FROM patterns_in_place.gold.dim_geo
  WHERE geo_level = 'cbsa'
    AND is_metro = TRUE
),
national_members AS (
  SELECT
    CONCAT('cbsa:', t.target_geo_id, '|national') AS comparison_set_id,
    'national' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    t.target_geo_id,
    'cbsa' AS member_geo_level,
    m.member_geo_id,
    m.member_geo_name,
    CASE WHEN t.target_geo_id = m.member_geo_id THEN 0 ELSE NULL END AS member_rank,
    CASE WHEN t.target_geo_id = m.member_geo_id THEN 'target' ELSE 'comparison' END AS member_role,
    'gold.dim_geo' AS membership_source
  FROM target_cbsa AS t
  INNER JOIN member_cbsa AS m
    ON TRUE
),
region_members AS (
  SELECT
    CONCAT('cbsa:', t.target_geo_id, '|region|', t.parent_region_id) AS comparison_set_id,
    'region' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    t.target_geo_id,
    'cbsa' AS member_geo_level,
    m.member_geo_id,
    m.member_geo_name,
    CASE WHEN t.target_geo_id = m.member_geo_id THEN 0 ELSE NULL END AS member_rank,
    CASE WHEN t.target_geo_id = m.member_geo_id THEN 'target' ELSE 'comparison' END AS member_role,
    'gold.dim_geo' AS membership_source
  FROM target_cbsa AS t
  INNER JOIN member_cbsa AS m
    ON t.parent_region_id = m.parent_region_id
  WHERE t.parent_region_id IS NOT NULL
),
division_members AS (
  SELECT
    CONCAT('cbsa:', t.target_geo_id, '|division|', t.parent_division_id) AS comparison_set_id,
    'division' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    t.target_geo_id,
    'cbsa' AS member_geo_level,
    m.member_geo_id,
    m.member_geo_name,
    CASE WHEN t.target_geo_id = m.member_geo_id THEN 0 ELSE NULL END AS member_rank,
    CASE WHEN t.target_geo_id = m.member_geo_id THEN 'target' ELSE 'comparison' END AS member_role,
    'gold.dim_geo' AS membership_source
  FROM target_cbsa AS t
  INNER JOIN member_cbsa AS m
    ON t.parent_division_id = m.parent_division_id
  WHERE t.parent_division_id IS NOT NULL
),
state_primary_members AS (
  SELECT
    CONCAT('cbsa:', t.target_geo_id, '|state_primary|', s.state_fips) AS comparison_set_id,
    'state_primary' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    t.target_geo_id,
    'cbsa' AS member_geo_level,
    m.member_geo_id,
    m.member_geo_name,
    CASE WHEN t.target_geo_id = m.member_geo_id THEN 0 ELSE NULL END AS member_rank,
    CASE WHEN t.target_geo_id = m.member_geo_id THEN 'target' ELSE 'comparison' END AS member_role,
    'gold.dim_geo' AS membership_source
  FROM target_cbsa AS t
  INNER JOIN target_cbsa_states AS s
    ON t.target_geo_id = s.target_geo_id
   AND s.state_rank_in_cbsa = 1
  INNER JOIN member_cbsa AS m
    ON s.state_fips = m.parent_state_fips
),
state_member_members AS (
  SELECT
    CONCAT('cbsa:', t.target_geo_id, '|state_member|', s.state_fips) AS comparison_set_id,
    'state_member' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    t.target_geo_id,
    'cbsa' AS member_geo_level,
    m.member_geo_id,
    m.member_geo_name,
    CASE WHEN t.target_geo_id = m.member_geo_id THEN 0 ELSE NULL END AS member_rank,
    CASE WHEN t.target_geo_id = m.member_geo_id THEN 'target' ELSE 'comparison' END AS member_role,
    'gold.dim_geo' AS membership_source
  FROM target_cbsa AS t
  INNER JOIN target_cbsa_states AS s
    ON t.target_geo_id = s.target_geo_id
  INNER JOIN member_cbsa AS m
    ON s.state_fips = m.parent_state_fips
),
peer_rank_rows AS (
  SELECT
    cf.cbsa_code AS target_geo_id,
    cf.cbsa_name AS target_geo_name,
    v.peer_rank,
    v.peer_cbsa_code AS member_geo_id,
    v.peer_cbsa_name AS member_geo_name
  FROM mart_intelligence.intelligence_cross_frame AS cf
  CROSS JOIN LATERAL (
    VALUES
      (1, cf.top10_peer_1_cbsa_code, cf.top10_peer_1_cbsa_name),
      (2, cf.top10_peer_2_cbsa_code, cf.top10_peer_2_cbsa_name),
      (3, cf.top10_peer_3_cbsa_code, cf.top10_peer_3_cbsa_name),
      (4, cf.top10_peer_4_cbsa_code, cf.top10_peer_4_cbsa_name),
      (5, cf.top10_peer_5_cbsa_code, cf.top10_peer_5_cbsa_name),
      (6, cf.top10_peer_6_cbsa_code, cf.top10_peer_6_cbsa_name),
      (7, cf.top10_peer_7_cbsa_code, cf.top10_peer_7_cbsa_name),
      (8, cf.top10_peer_8_cbsa_code, cf.top10_peer_8_cbsa_name),
      (9, cf.top10_peer_9_cbsa_code, cf.top10_peer_9_cbsa_name),
      (10, cf.top10_peer_10_cbsa_code, cf.top10_peer_10_cbsa_name)
  ) AS v(peer_rank, peer_cbsa_code, peer_cbsa_name)
  WHERE v.peer_cbsa_code IS NOT NULL
),
peer_members AS (
  SELECT
    CONCAT('cbsa:', t.target_geo_id, '|peer_set|cross_frame_top10') AS comparison_set_id,
    'peer_set' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    t.target_geo_id,
    'cbsa' AS member_geo_level,
    t.target_geo_id AS member_geo_id,
    t.target_geo_name AS member_geo_name,
    0 AS member_rank,
    'target' AS member_role,
    'mart_intelligence.intelligence_cross_frame' AS membership_source
  FROM target_cbsa AS t
  INNER JOIN mart_intelligence.intelligence_cross_frame AS cf
    ON t.target_geo_id = cf.cbsa_code

  UNION ALL

  SELECT
    CONCAT('cbsa:', p.target_geo_id, '|peer_set|cross_frame_top10') AS comparison_set_id,
    'peer_set' AS comparison_set_type,
    'cbsa' AS target_geo_level,
    p.target_geo_id,
    'cbsa' AS member_geo_level,
    p.member_geo_id,
    COALESCE(d.geo_name, p.member_geo_name) AS member_geo_name,
    p.peer_rank AS member_rank,
    'comparison' AS member_role,
    'mart_intelligence.intelligence_cross_frame' AS membership_source
  FROM peer_rank_rows AS p
  LEFT JOIN patterns_in_place.gold.dim_geo AS d
    ON d.geo_level = 'cbsa'
   AND d.geo_id = p.member_geo_id
)
SELECT * FROM national_members
UNION ALL
SELECT * FROM region_members
UNION ALL
SELECT * FROM division_members
UNION ALL
SELECT * FROM state_primary_members
UNION ALL
SELECT * FROM state_member_members
UNION ALL
SELECT * FROM peer_members;
