# property_explorer_gold.fct_tract_features

## Summary

`property_explorer_gold.fct_tract_features` stores one neighborhood feature row
per NYC census tract for the current MVP geography coverage. The table is used
as the tract-level source for neighborhood detail metrics and as the upstream
input to `property_explorer_gold.fct_nta_features`.

The current build targets Brooklyn and Manhattan tracts only. The latest SQL
test against the updated Metro Deep Dive ROF tract layer populated most feature
metrics. Remaining nulls are concentrated in tracts where source metrics are
unavailable.

## Grain

One row per `tract_id`.

## Source Tables

- Preferred source: `metro_deep_dive.rof_features.tract_features` joined to
  `metro_deep_dive.gold.population_demographics` for education and age fields.
- Secondary fallback source: `metro_deep_dive.foundation.tract_features` joined
  to `metro_deep_dive.gold.population_demographics`.
- Tertiary fallback source: `metro_deep_dive.gold.housing_core_wide` joined to
  `metro_deep_dive.gold.population_demographics` for the latest tract year.
- Fallback row source when Metro Deep Dive has no matching rows in the Python
  pipeline: `property_explorer_gold.dim_tract_to_nta`, filtered to Brooklyn and
  Manhattan county GEOIDs, with metric columns set to null.

## Columns

| Column | Type | Description |
| --- | --- | --- |
| `tract_id` | `VARCHAR` | 2020 census tract GEOID. Primary join key to `dim_tract_to_nta`. |
| `median_income` | `DOUBLE` | Median household income in dollars. Sourced from `median_hh_income` when available. |
| `median_rent` | `DOUBLE` | Median gross rent in dollars per month. Sourced from `median_gross_rent` when available. |
| `median_home_value` | `DOUBLE` | Median owner-occupied home value in dollars. |
| `pct_bachelors_plus` | `DOUBLE` | Share of population with bachelor's degree or higher. Expected scale is percent `0-100`; verify source scale before scoring. |
| `median_age` | `DOUBLE` | Median age in years. |
| `crime_rate_proxy` | `DOUBLE` | Deferred MVP crime metric. Retained as a nullable column and excluded from scoring/display logic. |

## Business Logic

- Target county GEOIDs are `36047` for Brooklyn and `36061` for Manhattan.
- The SQL build in `sql/gold/fct_tract_features.sql` expects the local Metro
  Deep Dive DuckDB to be attached as `metro_deep_dive`.
- The build prefers latest-year `rof_features.tract_features` rows for the
  target counties.
- If a tract is absent from ROF features, the build tries latest-year
  `foundation.tract_features`, then latest-year Metro Deep Dive gold housing
  and population tables.
- If no source row exists for a mapped tract, the build creates a null-valued
  tract feature row from `dim_tract_to_nta` for Brooklyn and Manhattan coverage.
- Metric columns are cast to `DOUBLE` to match the gold DDL, even when the
  current replacement table was inferred as nullable integer columns from an
  all-null pandas dataframe.
- Numeric `NaN` values from the attached source are converted to SQL `NULL`
  values during the build so QA checks can use normal null semantics.
- `pct_bachelors_plus` currently arrives from `gold.population_demographics` as
  a `0-1` ratio. Downstream scoring accepts either `0-1` ratios or `0-100`
  percentages, but visual display should format this field as a percent.

## QA And EDA Summary

Profile source: temporary rebuild of local
`data/processed/nyc_property_finder.duckdb` using attached
`metro_deep_dive.duckdb`, queried on 2026-04-20.

| Check | Result |
| --- | ---: |
| Row count | 1,115 |
| Distinct `tract_id` count | 1,115 |
| Duplicate tract rows | 0 |
| Null `tract_id` rows | 0 |
| Brooklyn (`36047`) tract rows | 805 |
| Manhattan (`36061`) tract rows | 310 |
| Non-null `median_income` rows | 1,067 |
| Non-null `median_rent` rows | 1,069 |
| Non-null `median_home_value` rows | 955 |
| Non-null `pct_bachelors_plus` rows | 1,083 |
| Non-null `median_age` rows | 1,082 |
| Null `crime_rate_proxy` rows | 1,115 |
| `NaN` `pct_bachelors_plus` rows after build | 0 |

The tested source table `metro_deep_dive.rof_features.tract_features` has 1,114
target-county rows for tract year `2024`: 804 Brooklyn rows and 310 Manhattan
rows. The final output has 1,115 rows because `dim_tract_to_nta` contains one
additional mapped tract, `36047990100` in `BK1302` Coney Island-Sea Gate, which
is retained as a null-valued fallback row. Median populated output values were
`83920.0` for income, `1896.0` for rent, `981200.0` for home value, and
`0.42488755622188906` for bachelor's-plus share.

### Suggested QA Queries

```sql
SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT tract_id) AS distinct_tracts,
    SUM(tract_id IS NULL)::INTEGER AS null_tract_id,
    SUM(median_income IS NULL)::INTEGER AS null_median_income,
    SUM(median_rent IS NULL)::INTEGER AS null_median_rent,
    SUM(median_home_value IS NULL)::INTEGER AS null_median_home_value,
    SUM(pct_bachelors_plus IS NULL)::INTEGER AS null_pct_bachelors_plus,
    SUM(median_age IS NULL)::INTEGER AS null_median_age,
    SUM(crime_rate_proxy IS NULL)::INTEGER AS null_crime_rate_proxy
FROM property_explorer_gold.fct_tract_features;
```

```sql
SELECT
    LEFT(tract_id, 5) AS county_geoid,
    COUNT(*) AS tract_count
FROM property_explorer_gold.fct_tract_features
GROUP BY 1
ORDER BY 1;
```

```sql
SELECT
    tract_features.tract_id
FROM property_explorer_gold.fct_tract_features AS tract_features
LEFT JOIN property_explorer_gold.dim_tract_to_nta AS mapping
    ON tract_features.tract_id = mapping.tract_id
WHERE mapping.tract_id IS NULL;
```
