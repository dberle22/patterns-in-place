-- Cross-frame cluster for a list of CBSAs (cluster labels and names are cleared for print).
SELECT cbsa_code, cbsa_name, cross_frame_cluster_name, cross_frame_cluster_label
FROM mart_intelligence.intelligence_cross_frame
WHERE cbsa_code IN (__CBSA_CODES__)
ORDER BY cbsa_code
