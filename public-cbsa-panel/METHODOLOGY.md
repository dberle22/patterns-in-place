# Methodology

## Purpose and release boundary

Patterns in Place: Metro & Micro Panel is a county-first panel for all current US metropolitan and micropolitan statistical areas (CBSAs). Version `v2026.1` contains a static county-to-CBSA crosswalk and annual CBSA measures for 2012–2024. It publishes only the fields documented in the table references; it does not publish Zillow, Regional Price Parities, BFS, CBP, QCEW, CHAS, permit, vacancy, or occupancy measures.

## Geography and crosswalk

The crosswalk uses the OMB 2023 delineation vintage and has 1,915 county-to-CBSA memberships covering 1,915 counties and 935 CBSAs: 393 metropolitan and 542 micropolitan areas. It is a current-vintage lookup, not a historical delineation series. A county can be reconciled to its current CBSA with `county_geoid` and `cbsa_code`.

`county_role` is the OMB central/outlying designation. `primary_state_abbr` and `primary_state_fips` are convenience fields: they select the first state suffix in the official CBSA title after matching that suffix to a member state. They do not replace the full member state information visible in the county rows.

## County-first aggregation

The release derives its CBSA measures from county-source inputs and the static crosswalk. Real GDP is summed across member counties. HUD two-bedroom FMR is a population-weighted mean across member counties. A value can be null when a required county input is suppressed or unavailable; null is not converted to zero or imputed.

## Time and source interpretation

- `year` for ACS fields is the end year of an ACS five-year estimate. Adjacent ACS windows overlap, so year-over-year changes are not independent annual measurements.
- BEA CAGDP9 values are annual real-GDP measures in chained dollars. Sector-to-total ratios are useful descriptive ratios, but chained-dollar components are not additive and should not be treated as nominal revenue shares.
- HUD FMR source periods are fiscal years. They share a numeric `year` with the ACS panel for convenient joining, but an FMR-year comparison should acknowledge that source-calendar difference.
- The crosswalk vintage is 2023. It does not change row by row or year by year.

## Derived measures

All shares below are stored as proportions, not percentages. Multiply by 100 for percentage display.

\[
annualized\_median\_rent = 12 \times median\_gross\_rent
\]

\[
rent\_to\_income = \frac{12 \times median\_gross\_rent}{median\_hh\_income}
\]

\[
value\_to\_income = \frac{median\_home\_value}{median\_hh\_income}
\]

\[
fmr\_gap\_2br\_vs\_median\_rent = hud\_fmr\_2br - median\_gross\_rent
\]

Each published ACS or BEA industry share is its documented industry numerator divided by its corresponding total. `acs_industry_concentration_hhi` is the sum of squared shares across the complete ACS industry family: agriculture/mining, construction, manufacturing, wholesale, retail, transportation/utilities, information, finance/real estate, professional, education/health, arts/accommodation/food, other services, and public administration.

## Coverage and missingness

The fact tables have 928 CBSAs in 2012–2021 and 935 in 2022–2024. Required ACS fields are complete within those table rows. Optional county-derived values have narrower coverage:

| Field family | Observed annual coverage, 2012–2024 |
| --- | --- |
| BEA real GDP total | 913 CBSAs each year |
| BEA manufacturing GDP share | 788–840 CBSAs |
| BEA professional GDP share | 334–471 CBSAs |
| BEA education/health GDP share | 671–801 CBSAs |
| HUD two-bedroom FMR and FMR gap | 928 CBSAs each year |

The release-specific `coverage_report.md` is authoritative: it is generated from the artifacts and shows annual non-null counts for every numeric field. Users should filter or report the available geography count for any optional field rather than assuming a balanced panel.

## Source attribution

The public source family references and upstream variables are in [audit/source_references.md](audit/source_references.md) and the per-table references in [`docs/`](docs/). Federal source data remain subject to their agencies' terms and attribution guidance; see [FEDERAL_SOURCE_ATTRIBUTION.md](FEDERAL_SOURCE_ATTRIBUTION.md).

## Known limitations

BEA professional and education/health GDP shares have unexpectedly low coverage for major sectors. They remain optional, source-faithful fields—not headline measures—until a dedicated review determines whether the gaps arise from upstream suppression, industry-line mapping, or county-to-CBSA aggregation behavior. The investigation plan is in [FUTURE_RELEASE_NOTES.md](FUTURE_RELEASE_NOTES.md).
