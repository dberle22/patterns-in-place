# Patterns in Place: Metro & Micro Panel

A county-first public panel for all current US metropolitan and micropolitan statistical areas:
a static county-to-CBSA crosswalk plus annual economics and affordability measures for 2012–2024.

## Query with DuckDB

Download the v2026.1 files from the [Zenodo record](https://zenodo.org/records/23020706) into
one directory, then run:

```sql
SELECT geo_name, annualized_median_rent, rent_to_income
FROM read_parquet('affordability_wide.parquet')
WHERE year = 2024
ORDER BY rent_to_income DESC
LIMIT 10;
```

The same query pattern works with any local directory containing the release artifacts. A future
distribution mirror may also supply a direct remote-Parquet URL.

## Tables

| Table | Grain | Coverage |
| --- | --- | --- |
| `cbsa_county_crosswalk` | County-to-current-CBSA membership | OMB 2023; 1,915 memberships; 935 CBSAs |
| `economics_industry_wide` | CBSA-year | 2012–2024; ACS employment mix and optional county-derived BEA GDP measures |
| `affordability_wide` | CBSA-year | 2012–2024; ACS housing/income and optional county-derived HUD FMR measures |

## Important caveats

- The crosswalk is static at the 2023 delineation vintage; it does not represent historical
  county membership.
- ACS values are five-year estimates. Adjacent years overlap and should not be read as
  independent annual samples.
- BEA GDP sector shares have uneven coverage. In particular, professional GDP share is available
  for 334–471 CBSAs per year, and education/health GDP share for 671–801. Check field coverage
  before analysis.
- HUD FMR source periods are fiscal years. All optional-field null counts appear in the versioned
  `coverage_report.md`.

## Documentation and citation

Read [Methodology](METHODOLOGY.md), the [table references](docs/),
[release history](RELEASES.md), and [future-release notes](FUTURE_RELEASE_NOTES.md).

Release artifacts and documentation are licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); build code is MIT licensed. Cite:

> Berle, Dan. *Patterns in Place: Metro & Micro Panel*, v2026.1. Patterns in Place.
> https://doi.org/10.5281/zenodo.23020706

For the dataset as a whole across versions, cite the concept DOI
https://doi.org/10.5281/zenodo.23020705.
