-- Compare default lens membership sets. The centroid lens uses its declared 250-mile default.
WITH selected_members AS (
  SELECT target_cbsa_code,
         CASE
           WHEN lens_id = 'cbsa_centroid_250mi' THEN 'cbsa_centroid_250mi_250'
           ELSE lens_id
         END AS lens_key,
         member_cbsa_code
  FROM mart_geography.region_lens_membership
  WHERE target_cbsa_code = '__CBSA_CODE__'
    AND (lens_id <> 'cbsa_centroid_250mi' OR parameter_value = '250')
),
lens_sizes AS (
  SELECT lens_key, COUNT(*) AS member_count
  FROM selected_members
  GROUP BY 1
),
pairwise AS (
  SELECT left_set.lens_key AS left_lens,
         right_set.lens_key AS right_lens,
         COUNT(*) AS intersection_count
  FROM selected_members AS left_set
  INNER JOIN selected_members AS right_set
    ON left_set.member_cbsa_code = right_set.member_cbsa_code
  GROUP BY 1, 2
)
SELECT pairwise.left_lens,
       pairwise.right_lens,
       pairwise.intersection_count,
       left_size.member_count AS left_member_count,
       right_size.member_count AS right_member_count,
       pairwise.intersection_count::DOUBLE
         / (left_size.member_count + right_size.member_count - pairwise.intersection_count) AS jaccard_overlap
FROM pairwise
INNER JOIN lens_sizes AS left_size ON pairwise.left_lens = left_size.lens_key
INNER JOIN lens_sizes AS right_size ON pairwise.right_lens = right_size.lens_key
ORDER BY left_lens, right_lens;
