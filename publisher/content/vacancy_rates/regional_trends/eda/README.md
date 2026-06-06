# Regional Trends EDA

This folder holds the exploratory queries and written takeaways for the
`analysis/vacancy_rates/regional_trends` insight.

## Files

- `01_coverage_and_labels.sql` + `01_coverage_and_labels_summary.md`
- `02_us_and_region_series.sql` + `02_us_and_region_series_summary.md`
- `03_regional_change_and_rank_stability.sql` +
  `03_regional_change_and_rank_stability_summary.md`

## Notes

- All queries read from `gold.housing_core_wide`.
- `vacancy_rate` is stored as a decimal and is multiplied by `100` for
  display.
- The clean comparison set for this insight is `geo_level in ('us', 'region')`.
- Regional labels in the source table are `Northeast Region`, `Midwest Region`,
  `South Region`, and `West Region`.
