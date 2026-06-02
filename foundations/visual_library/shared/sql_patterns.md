# Common SQL Patterns for Visual Samples

Use this as a chart-local sample SQL recipe book. Keep chart-specific files in
`visual_library/charts/<chart_type>/sample_sql/`, but reuse these patterns so
sample queries stay consistent across chart types.

## Contract Shape

Most chart sample queries should return the chart contract directly, with any
extra fields needed by prep or render.

```sql
SELECT
  '<question_id>'::VARCHAR AS question_id,
  geo_level,
  geo_id,
  geo_name,
  year AS period,
  '<metric_id>'::VARCHAR AS metric_id,
  '<Metric Label>'::VARCHAR AS metric_label,
  metric_value::DOUBLE AS metric_value,
  '<source table or joins>'::VARCHAR AS source,
  '<YYYY-MM-DD>'::VARCHAR AS vintage,
  '<universe description>'::VARCHAR AS "group",
  FALSE AS highlight_flag,
  FALSE AS peer_flag,
  NULL::DOUBLE AS rank,
  '<method note>'::VARCHAR AS note
FROM ...
```

## Target Geography

Use a CTE for the target so the value is easy to scan and replace.

```sql
WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id
)
```

## Fixed Peer Set

Use an explicit `selected_geos` CTE when the story is target-versus-peers. Carry
both `highlight_flag` and `peer_flag` through the result.

```sql
WITH selected_geos AS (
  SELECT '48900'::VARCHAR AS geo_id, TRUE AS highlight_flag UNION ALL
  SELECT '16740'::VARCHAR AS geo_id, FALSE AS highlight_flag UNION ALL
  SELECT '39580'::VARCHAR AS geo_id, FALSE AS highlight_flag
)
SELECT
  ...,
  g.highlight_flag,
  TRUE AS peer_flag
FROM gold.affordability_wide a
JOIN selected_geos g
  ON a.geo_id = g.geo_id
```

## Latest Common Year

When multiple marts are joined, choose the latest year common to all required
inputs instead of assuming one table's max year applies everywhere.

```sql
WITH latest_common_year AS (
  SELECT MIN(max_year) AS year
  FROM (
    SELECT MAX(year) AS max_year FROM gold.affordability_wide WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year FROM gold.population_demographics WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year FROM gold.economics_income_wide WHERE geo_level = 'cbsa'
  )
)
```

## Within-CBSA Counties

Use the xwalk as the universe definition and carry that universe into `group` or
`note`.

```sql
WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id
),
target_counties AS (
  SELECT DISTINCT county_geoid AS geo_id
  FROM silver.xwalk_cbsa_county
  WHERE cbsa_code = (SELECT target_geo_id FROM target_cbsa)
)
SELECT ...
FROM gold.affordability_wide a
JOIN target_counties c
  ON a.geo_id = c.geo_id
WHERE a.geo_level = 'county'
```

## Within-CBSA ZCTAs

Use the ZCTA crosswalk, and set minimum observation rules before display
trimming when the chart spans multiple periods.

```sql
WITH target_zctas AS (
  SELECT DISTINCT zip_geoid AS geo_id
  FROM silver.xwalk_zcta_cbsa
  WHERE cbsa_geoid = '48900'
),
display_zctas AS (
  SELECT a.geo_id
  FROM gold.affordability_wide a
  JOIN target_zctas z
    ON a.geo_id = z.geo_id
  WHERE a.geo_level = 'zcta'
  GROUP BY a.geo_id
  HAVING COUNT(a.metric_value) >= 4
)
```

## Deterministic Ranking

Rank across the full intended universe before trimming the display set. Use
`ROW_NUMBER()` when ties need deterministic ordering for display, and spell out
the tie-break rule in `note`.

```sql
ROW_NUMBER() OVER (
  PARTITION BY year
  ORDER BY metric_value DESC, geo_name, geo_id
)::DOUBLE AS rank
```

Use ascending order for lower-is-better metrics.

```sql
ROW_NUMBER() OVER (
  PARTITION BY year
  ORDER BY value_to_income ASC, geo_name, geo_id
)::DOUBLE AS rank
```

## Fixed End-Period Top-N

For rank-over-time stories, compute ranks or values across the full universe,
select display entities from a stable period, then pull those entities across
all periods.

```sql
WITH ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY year ORDER BY metric_value DESC, geo_name, geo_id) AS rank
  FROM universe
),
display_geos AS (
  SELECT geo_id
  FROM ranked
  WHERE year = 2024
  ORDER BY rank
  LIMIT 10
)
SELECT *
FROM ranked
WHERE geo_id IN (SELECT geo_id FROM display_geos)
```

If prep will compute ranks, return the full universe and let the chart prep
select the fixed top-N after ranking.

## Endpoint Comparisons

Use endpoint CTEs when the chart asks about change, movement, or before/after
selection.

```sql
WITH endpoints AS (
  SELECT
    geo_id,
    MAX(CASE WHEN year = 2018 THEN metric_value END) AS start_value,
    MAX(CASE WHEN year = 2024 THEN metric_value END) AS end_value
  FROM universe
  GROUP BY 1
),
selected_geos AS (
  SELECT geo_id
  FROM endpoints
  WHERE start_value IS NOT NULL
    AND end_value IS NOT NULL
  ORDER BY ABS(end_value - start_value) DESC
  LIMIT 12
)
```

## Multi-Metric Long Form

Use `UNION ALL` to produce a long contract frame from wide marts. Include
`metric_order`, `metric_group`, and `direction` when the chart needs ordered or
polarity-aware comparisons.

```sql
SELECT geo_level, geo_id, geo_name, year, 1 AS metric_order,
       'median_hh_income' AS metric_id,
       'Median household income' AS metric_label,
       'Prosperity' AS metric_group,
       median_hh_income::DOUBLE AS metric_value,
       'higher_is_better' AS direction
FROM base

UNION ALL

SELECT geo_level, geo_id, geo_name, year, 2,
       'pct_rent_burden_30plus',
       'Rent-burdened renter share',
       'Affordability',
       pct_rent_burden_30plus::DOUBLE,
       'lower_is_better'
FROM base
```

## Sample Query Notes

- Keep the ranking universe explicit in `group`, `subtitle`, or `note`.
- Prefer gold-layer marts for sample outputs unless the chart requires geometry
  or a lower-layer construct.
- Use stable review filenames and one SQL file per canonical business question.
- Include source and vintage in every query result.
- Keep chart-specific workarounds in the chart folder rather than hiding them in
  broad shared helpers.
