-- Industry-role evidence: target sector share/LQ versus the active lens's other CBSAs.
WITH target_year AS (
  SELECT MAX(year) AS year FROM gold.economics_industry_wide
  WHERE geo_level = 'cbsa' AND geo_id = '__CBSA_CODE__'
),
members AS (
  SELECT member_cbsa_code, member_role FROM mart_geography.region_lens_membership
  WHERE target_cbsa_code = '__CBSA_CODE__' AND lens_id = '__LENS_ID__' AND parameter_value = '__PARAMETER_VALUE__'
),
industry_rows AS (
  SELECT industry.geo_id, members.member_role, industry.qcew_private_emp_total,
         industry.lq_manufacturing, industry.lq_information, industry.lq_professional,
         industry.qcew_private_emp_manufacturing, industry.qcew_private_emp_information, industry.qcew_private_emp_professional
  FROM members INNER JOIN gold.economics_industry_wide AS industry
    ON industry.geo_level = 'cbsa' AND industry.geo_id = members.member_cbsa_code
  CROSS JOIN target_year WHERE industry.year = target_year.year
),
sectors AS (
  SELECT geo_id, member_role, 'manufacturing' AS sector, qcew_private_emp_total AS total_emp, qcew_private_emp_manufacturing AS sector_emp, lq_manufacturing AS target_lq FROM industry_rows
  UNION ALL SELECT geo_id, member_role, 'information', qcew_private_emp_total, qcew_private_emp_information, lq_information FROM industry_rows
  UNION ALL SELECT geo_id, member_role, 'professional_services', qcew_private_emp_total, qcew_private_emp_professional, lq_professional FROM industry_rows
)
SELECT sector,
       MAX(CASE WHEN member_role = 'target' THEN sector_emp / NULLIF(total_emp, 0) END) AS target_sector_share,
       MAX(CASE WHEN member_role = 'target' THEN target_lq END) AS target_lq,
       SUM(CASE WHEN member_role = 'comparison' THEN sector_emp END) / NULLIF(SUM(CASE WHEN member_role = 'comparison' THEN total_emp END), 0) AS rest_of_lens_sector_share,
       COUNT(*) FILTER (WHERE member_role = 'comparison' AND sector_emp IS NOT NULL) AS comparison_cbsa_coverage
FROM sectors GROUP BY sector ORDER BY target_lq DESC NULLS LAST;
