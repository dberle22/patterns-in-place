# property_explorer_gold.fct_nta_features

## Summary

`property_explorer_gold.fct_nta_features` stores one feature summary row per
NYC Neighborhood Tabulation Area. It is the app-friendly neighborhood table for
NTA filters, neighborhood panels, and NTA-level fallback context.

The table is materialized from `property_explorer_gold.fct_tract_features` and
`property_explorer_gold.dim_tract_to_nta`. After the latest tract data refresh,
most NTA rows have populated income, rent, education, and age metrics. Park,
cemetery, industrial, and special-use NTAs are the most common remaining null
metric rows.

## Grain

One row per `nta_id` and `nta_name`, with NTA-level context fields retained.

## Source Tables

- `property_explorer_gold.fct_tract_features`
- `property_explorer_gold.dim_tract_to_nta`

## Columns

| Column | Type | Description |
| --- | --- | --- |
| `nta_id` | `VARCHAR` | NYC 2020 NTA code. Primary neighborhood identifier. |
| `nta_name` | `VARCHAR` | NTA display name. |
| `borough` | `VARCHAR` | Borough name carried from the tract-to-NTA mapping. Cross-borough NTAs are joined as a stable label such as `Bronx / Manhattan`. |
| `tract_count` | `INTEGER` | Count of distinct mapped tracts contributing to the NTA row. |
| `median_income` | `DOUBLE` | Median of mapped tract `median_income` values. |
| `median_rent` | `DOUBLE` | Median of mapped tract `median_rent` values. |
| `median_home_value` | `DOUBLE` | Median of mapped tract `median_home_value` values. |
| `pct_bachelors_plus` | `DOUBLE` | Median of mapped tract `pct_bachelors_plus` values. Expected percent scale is `0-100`; verify upstream source scale before scoring. |
| `median_age` | `DOUBLE` | Median of mapped tract `median_age` values. |
| `crime_rate_proxy` | `DOUBLE` | Deferred MVP crime metric. Median of mapped tract values when available, otherwise null. |

## Business Logic

- Join tract features to `dim_tract_to_nta` on `tract_id`.
- Use the distinct tract-to-NTA mapping columns `tract_id`, `nta_id`,
  `nta_name`, and `borough` before joining.
- Use an inner join so only mapped tracts contribute to NTA summaries.
- Count distinct mapped `tract_id` values into `tract_count`.
- Aggregate all numeric feature columns with `median()`, matching the current
  Python implementation in `build_nta_features`.
- `median()` ignores nulls. When every mapped tract value is null for a metric,
  the NTA metric remains null.
- Numeric `NaN` values from tract features are converted to SQL `NULL` values
  before aggregation.
- Crime remains deferred for MVP scoring and display, even though the column is
  retained for schema compatibility.

## QA And EDA Summary

Profile source: temporary rebuild of local
`data/processed/nyc_property_finder.duckdb` using attached
`metro_deep_dive.duckdb`, queried on 2026-04-20.

| Check | Result |
| --- | ---: |
| Row count | 108 |
| Distinct `nta_id` count | 108 |
| Duplicate NTA rows | 0 |
| Null `nta_id` rows | 0 |
| Null `nta_name` rows | 0 |
| Null `borough` rows | 0 |
| Non-null `median_income` rows | 87 |
| Non-null `median_rent` rows | 87 |
| Non-null `median_home_value` rows | 85 |
| Non-null `pct_bachelors_plus` rows | 90 |
| Non-null `median_age` rows | 89 |
| Null `crime_rate_proxy` rows | 108 |
| `NaN` `pct_bachelors_plus` rows after build | 0 |

Median populated values were `82807.5` for income, `1863.0` for rent, and
`0.4399681686565388` for bachelor's-plus share.

### Suggested QA Queries

```sql
SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT nta_id) AS distinct_ntas,
    SUM(nta_id IS NULL)::INTEGER AS null_nta_id,
    SUM(nta_name IS NULL)::INTEGER AS null_nta_name,
    SUM(median_income IS NULL)::INTEGER AS null_median_income,
    SUM(median_rent IS NULL)::INTEGER AS null_median_rent,
    SUM(median_home_value IS NULL)::INTEGER AS null_median_home_value,
    SUM(pct_bachelors_plus IS NULL)::INTEGER AS null_pct_bachelors_plus,
    SUM(median_age IS NULL)::INTEGER AS null_median_age,
    SUM(crime_rate_proxy IS NULL)::INTEGER AS null_crime_rate_proxy
FROM property_explorer_gold.fct_nta_features;
```

```sql
SELECT
    nta_id,
    nta_name,
    median_income,
    median_rent,
    median_home_value,
    pct_bachelors_plus,
    median_age,
    crime_rate_proxy
FROM property_explorer_gold.fct_nta_features
ORDER BY nta_id
LIMIT 25;
```

```sql
SELECT
    mapping.nta_id,
    mapping.nta_name,
    COUNT(DISTINCT mapping.tract_id) AS mapped_tracts,
    COUNT(DISTINCT tract_features.tract_id) AS tract_feature_rows
FROM property_explorer_gold.dim_tract_to_nta AS mapping
LEFT JOIN property_explorer_gold.fct_tract_features AS tract_features
    ON mapping.tract_id = tract_features.tract_id
WHERE starts_with(mapping.tract_id, '36047')
   OR starts_with(mapping.tract_id, '36061')
GROUP BY 1, 2
ORDER BY 1;
```
