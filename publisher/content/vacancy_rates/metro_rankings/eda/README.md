# Metro Rankings EDA

This folder holds the exploratory queries and written takeaways for the
`analysis/vacancy_rates/metro_rankings` insight.

## Files

- `01_cbsa_coverage_and_population_filters.sql` +
  `01_cbsa_coverage_and_population_filters_summary.md`
- `02_major_metro_rankings.sql` + `02_major_metro_rankings_summary.md`
- `03_distribution_and_benchmarking.sql` +
  `03_distribution_and_benchmarking_summary.md`
- `04_small_metro_outliers.sql` + `04_small_metro_outliers_summary.md`

## Notes

- Vacancy rate comes from `gold.housing_core_wide`.
- Population filters come from `gold.population_demographics`.
- Join on `geo_level + geo_id + year` when applying the population cutoff.
- `vacancy_rate` is stored as a decimal and should be multiplied by `100` for
  display.
