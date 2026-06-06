# National Trend EDA

This folder holds the exploratory queries and written takeaways for the
`analysis/vacancy_rates/national_trend` insight.

## Files

- `01_coverage_and_quality.sql` + `01_coverage_and_quality_summary.md`
- `02_us_national_series.sql` + `02_us_national_series_summary.md`
- `03_us_vs_cbsa_comparison.sql` + `03_us_vs_cbsa_comparison_summary.md`
- `04_value_range_and_outliers.sql` + `04_value_range_and_outliers_summary.md`

## Notes

- All queries read from `gold.housing_core_wide`
- `vacancy_rate` is stored as a decimal and is multiplied by 100 for display
- The clean national headline should use `geo_level = 'us'`
- The unweighted CBSA average is directionally useful for EDA, but not directly
  comparable to the US series for a headline chart
