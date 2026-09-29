-- Only markets in the published WAC-coverage cohort can enter the outcomes
-- notebook. The label keeps the readable CBSA name beside the query value.
select distinct cbsa_code, cbsa_name
from mart_explanation_q2.job_center_candidates_v0
order by cbsa_name, cbsa_code;
