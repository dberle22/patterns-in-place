        
with soc_base as (        
SELECT
    soc_code,
    year,
    any_value(soc_title) AS soc_title,
    SUM(employment) AS employment,
    COUNT(DISTINCT geo_id) AS metros
FROM silver.bls_oews
WHERE geo_level = 'cbsa' AND o_group = 'detailed'
GROUP BY 1,2

)

SELECT soc_code,
	year,
	soc_title,
	employment as sector_employment,
	sum(employment) over(partition by year) as total_employment,
	employment / sum(employment) over(partition by year) as sector_weight,
	metros,
	max(metros) over(partition by year) as max_metros
FROM soc_base
ORDER BY year, employment DESC, soc_code;