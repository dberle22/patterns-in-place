# v2026.1 Lineage Audit

**Status:** Allowlist approved; refreshed-source validation pending  
**Audited database:** `foundations/etl/data/duckdb/patterns_in_place.duckdb`  
**Audit rule:** a field is released only when its source variable, transformation, coverage, and Zillow review are recorded in [public_column_lineage.csv](public_column_lineage.csv).

## Confirmed findings

### Scope and source boundary

- The candidate tables are `silver.xwalk_cbsa_county`, `gold.economics_industry_wide`, and `gold.affordability_wide`.
- The selected industry fields trace to ACS 5-year table `C24030`, plus county-derived BEA real GDP total and three broad industry shares. The BEA GDP concentration HHI is deferred to v2 because conservative county-level suppression leaves insufficient coverage. The wider Gold table also contains QCEW, CBP, BFS, and BEA CAINC5N fields, but none are candidates for v2026.1.
- The selected affordability fields trace only to ACS 5-year tables `B25064`, `B25077`, and `B19013`, plus county-derived HUD FMR. BEA MARPP/RPP fields are excluded because they are published at metro/state level rather than constructed from county inputs. The wider Gold table also contains CHAS, rent-50, vacancy/occupancy, and permit fields, but none are candidates for v2026.1.
- `value_to_income` is calculated in `foundations/etl/gold/gold_housing_core.sql` as ACS median home value divided by ACS median household income. It has no Zillow input in its Gold lineage.

### Static crosswalk

- `silver.xwalk_cbsa_county` is an OMB 2023 snapshot (`vintage = 2023`, `source = 'OMB_2023'`) built by `foundations/etl/silver/geo_crosswalks_silver.R`.
- The audited snapshot contains 1,915 memberships, 1,915 distinct counties, and 935 distinct CBSAs: 1,325 central and 590 outlying counties.
- `county_flag` is supplied directly by the OMB workbook. CBSA type, county/state names, FIPS identifiers, and the county-to-CBSA membership are also direct workbook fields.
- The existing `gold.dim_geo` implementation derives the primary state by parsing the first state suffix in the official CBSA title and resolving it against member-state attributes. The live result has a non-null primary state abbreviation and FIPS for every CBSA. The crosswalk therefore reuses this documented rule rather than inventing a second one.
- The audited universe contains 393 metropolitan and 542 micropolitan CBSAs.

### Live coverage observed on 2026-09-24

| Field group | 2012–2021 | 2022 | 2023 | 2024 | Release treatment |
| --- | ---: | ---: | ---: | ---: | --- |
| ACS industry and affordability fields | 928 CBSAs | 935 | 935 | 935 | Include; disclose the 928/935 early-year panel. |
| BEA CAGDP9 real GDP total | 913 CBSAs | 913 | 913 | 913 | Include as an optional, county-derived field; disclose its incomplete coverage. |
| BEA CAGDP9 industry shares | 334–840 CBSAs | 334–803 | 351–796 | 334–788 | Include the three approved shares with field-level coverage; defer BEA HHI. |
| HUD two-bedroom FMR fields | 928 CBSAs | 928 | 928 | 928 | Include as annual HUD fiscal-year fields; disclose fiscal-year source periods. |

The final coverage report must recompute these values from the release candidate. They are an audit baseline, not a permanent contract.

## Required decisions and implementation gaps

1. **CBSA type convenience fields:** `cbsa_type_short`, `is_metro`, and `is_micro` are public convenience fields derived from the OMB `cbsa_type` string. Their exact values and types belong in `config/tables.yml` after the lineage ledger is approved.
2. **Industry HHI reproducibility:** ACS HHI is derived from the complete set of internal ACS sector shares, not solely the public shares. The public table documentation must list the full input family and formula. BEA HHI is deferred from v1 because it has only 147 populated CBSAs in 2024.
3. **Source citation metadata:** confirm the official title and download citation for the locally stored OMB 2023 workbook, HUD FMR release, and BEA vintage used in the audited database before public documentation is generated.

## Next audit steps

- Validate each draft ledger row against the build SQL/R code and live table fields.
- Confirm source citations and release-date metadata.
- Regenerate the release candidate and its machine-derived coverage report after any future
  Foundations handoff; the report, rather than this audit baseline, is authoritative.
- Reconcile the candidate ledger to the approved `config/tables.yml`; no excluded source may be
  added after that point.
