SELECT DISTINCT candidate.recommended_cluster_id AS component_id,
       candidate.tract_geoid, tract.geom_wkb
FROM mart_explanation_q2.job_center_candidates_v0 AS candidate
JOIN geo.tracts_all_us AS tract USING (tract_geoid)
WHERE candidate.cbsa_code='__CBSA_CODE__' AND candidate.is_recommended_center;
