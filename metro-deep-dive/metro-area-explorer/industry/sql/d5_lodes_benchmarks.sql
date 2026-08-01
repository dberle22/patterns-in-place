WITH us_rollup AS (
    SELECT
        'us' AS benchmark_scope,
        'us' AS benchmark_geo_id,
        'United States' AS benchmark_geo_name,
        year,
        SUM(jobs_total) AS jobs_total,
        SUM(workers_total) AS workers_total,
        SUM(jobs_minus_workers) AS jobs_minus_workers,
        CASE
            WHEN SUM(workers_total) > 0 THEN SUM(jobs_total) / SUM(workers_total)
            ELSE NULL
        END AS jobs_to_workers_ratio
    FROM patterns_in_place.gold.economics_lodes_wide
    WHERE geo_level = 'state'
    GROUP BY year
),
division_rows AS (
    SELECT
        'division' AS benchmark_scope,
        'division:' || geo_id AS benchmark_geo_id,
        geo_name AS benchmark_geo_name,
        year,
        jobs_total,
        workers_total,
        jobs_minus_workers,
        jobs_to_workers_ratio
    FROM patterns_in_place.gold.economics_lodes_wide
    WHERE geo_level = 'division'
      AND geo_id = CAST(? AS VARCHAR)
)
SELECT *
FROM us_rollup
UNION ALL
SELECT *
FROM division_rows
ORDER BY year, benchmark_scope;
