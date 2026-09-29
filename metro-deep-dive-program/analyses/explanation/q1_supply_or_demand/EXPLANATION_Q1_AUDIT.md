# Explanation Q1 — Epic 1 Audit

**Status:** Complete  
**Audit date:** 2026-09-11  
**Warehouse reviewed:** `foundations/etl/data/duckdb/patterns_in_place.duckdb`

## Decision summary

Q1 is feasible as a national-first analysis followed by a Richmond deep dive.
It should use separate, explicitly labeled geographic lenses rather than a
single multi-grain submarket score:

- **CBSA and county:** the 10-year contextual and permit-response lens.
- **Tract:** the primary small-area affordability, occupancy, stock, and
  population-change lens.
- **ZCTA:** the small-area market-price lens, because it is the only available
  sub-county geography with managed Zillow and FHFA price series.
- **Place:** a supplemental municipal lens where its partial permit coverage is
  present; it is not a substitute for tracts or ZCTAs.

The existing publisher overheating mart is useful prior art and a CBSA/county
benchmark. It is not suitable as Q1's governing method or as a tract-level
diagnosis. Q1 should rebuild a transparent, analysis-owned component surface in
this folder, compare its broad-market results with the publisher mart, and keep
any reusable logic local until a later, deliberate Foundations migration.

## What exists in the live warehouse

### Housing, affordability, and population

`gold.housing_core_wide` and `gold.population_demographics` have annual rows
from 2012 through 2024. At tract, ZCTA, Place, county, and CBSA grain, the 2024
housing-unit and vacancy fields are complete. Median household income is also
near-complete or complete, so a local cost-to-income affordability measure is
available without a new source.

2024 coverage for the minimum tract-style affordability and demand set
(`median_gross_rent`, `median_hh_income`, `vacancy_rate`, and five-year
population growth) is:

| Grain | Rows | Complete rows | Complete share |
|---|---:|---:|---:|
| CBSA | 935 | 928 | 99.3% |
| County | 3,222 | 3,203 | 99.4% |
| Place | 32,330 | 21,388 | 66.2% |
| Tract | 84,401 | 57,559 | 68.2% |
| ZCTA | 33,772 | 25,429 | 75.3% |

The tract shortfall is principally the five-year population-growth warm-up,
not a missing current affordability or vacancy measure: 99.1% of 2024 tract
rows have one-year population growth, while 71.4% have five-year growth.

### Income versus wages

The available small-area denominator is `median_hh_income` from ACS, including
at tract, ZCTA, and Place. This supports a defensible **local housing-cost to
household-income** measure. It is not literally a wage measure: household
income can include non-wage income and need not describe the same household as
the median-rent observation.

`gold.economics_labor_wide` has QWI private-sector average earnings at county,
CBSA, and state grain (about 96% coverage in 2024), but none at tract or ZCTA
grain. It is workplace-based rather than a resident-household denominator, so
it should be context only, not the affordability denominator.

### Permits

The BPS-derived permit fields in `gold.housing_core_wide` are present at
county, CBSA, and some Place rows. They are absent at tract and ZCTA grain.

| Grain | 2024 permit-unit coverage |
|---|---:|
| CBSA | 99.6% |
| County | 96.2% |
| Place | 39.7% |
| Tract | 0.0% |
| ZCTA | 0.0% |

Therefore, permits belong in the CBSA/county trend and, where populated, a
clearly labeled Place supplement. They must never be allocated to tracts or
ZCTAs in Q1.

### Price and rent market series

`gold.housing_market_wide` is available from 2016 through 2025 at CBSA,
county, and ZCTA grain only. It has no tract or Place rows.

For 2024, Zillow home-value growth covers 100.0% of CBSA rows, 99.9% of county
rows, and 99.5% of ZCTA rows. FHFA five-year HPI growth covers 99.5%, 85.9%,
and 58.8%, respectively. Zillow rent-growth coverage is materially weaker:
54.6% at CBSA, 28.4% at county, and 19.7% at ZCTA.

Use ZHVI as the standard submarket market-price context, treat FHFA as a
supporting series where present, and treat ZORI as optional rather than an
inclusion condition. A tract price-appreciation signal is not currently
managed.

### Migration and demand

ACS mobility measures are present at the small-area grains (2024 coverage is
100.0% for tracts, 99.6% for ZCTAs, and 99.1% for Places). They measure moving
or churn, not net in-migration; they are supporting demand context rather than
a directional demand signal.

IRS net-migration rates are available at county and CBSA grain through 2022,
with roughly 89% county and 99% CBSA coverage in that final live year. They are
not available at tract, ZCTA, or Place grain, and they are unpopulated for 2023
and 2024. Q1 can use them in the broad-market historical lens only.

### Geography and time

`gold.dim_geo` maps 78,199 of 84,121 tract identities to a parent CBSA; 5,922
tracts lie outside a CBSA. The national tract surface is therefore feasible for
metro tracts, with an explicit nonmetro exclusion rather than a hidden one.
ZCTAs must instead be assigned with the weighted `silver.xwalk_zcta_cbsa`
crosswalk; their direct parent-CBSA field is not a complete membership rule.

The warehouse has 73,056 tract rows annually for 2012–2019 and about 84,400
for 2020–2024. The Census 2020 tract-boundary transition means a raw tract-ID
comparison across 2019/2020 is not safe. `mart_geography.temporal_edges`
contains tract transition edges, but Q1 has not validated an allocation method
for these measures. Until it does, use direct 10-year trends only at CBSA and
county grain; present tract trends within consistent boundary periods or after
an explicit crosswalk validation.

## Prior overheating work

`mart_housing.core_metrics` and `mart_housing.overheating_matrix` are built in
`publisher/content/housing/sql/`, so they are publisher-owned section marts,
not Foundations engines.

`core_metrics` is a reusable wide table at division, state, CBSA, and county
grain for 2012–2024. `overheating_matrix` covers CBSA and county only, for
2016–2024. Its provisional composite averages four within-year,
within-geo-level percentile component scores:

- momentum: FHFA price momentum plus optional Zillow rent momentum;
- pressure: population and ACS per-capita-income growth;
- strain: rent-to-income, value-to-income, and rent burden;
- tightness: vacancy and permit response, direction-adjusted so lower supply
  response means more pressure.

The mart has complete component/composite coverage for its 2024 rows by
averaging whichever raw inputs exist. That is appropriate for a first-pass
metro ranking, but it makes components vary in their evidentiary makeup and it
does not distinguish inexpensive markets caused by weak demand from those
supported by supply. Q1 should not silently adopt its composite.

**Disposition:** reproduce only the components Q1 needs in an
analysis-owned, inspectable build; retain raw fields and per-component metric
counts; use the publisher mart solely as a comparison benchmark at CBSA/county
grain. A later Foundations migration can be considered only after Q1 has
validated its definitions.

## Richmond readiness

Richmond CBSA (`40060`) has one CBSA row, 17 county rows, and 332 tract rows
in 2024. Of the tract rows, 228 meet the initial five-year
affordability/vacancy/population completeness rule. Richmond has 135 ZCTA
relationships in the weighted ZCTA-to-CBSA crosswalk, so its ZCTA view must use
that allocation logic rather than a direct parent join. All 17 county rows
have permits; no tract row has permits or a managed market-price series. The
Richmond notebook is therefore viable as a tract-first diagnosis with county
permit and ZCTA price-context companion views.

## Required updates to the spec and build plan

1. Replace the current “cost versus wages, both local and national” opening
   with a local **annualized median gross rent / median household income**
   measure. Start with `<= 0.30` as inexpensive and report `<= 0.50` as the
   stress-test threshold. Label it household-income affordability, not wages.
   National distributions provide comparison context; they are not a second
   national wage denominator. Add ownership-cost treatment only as a separate
   later decision.
2. Commit to two notebooks: a national notebook that defines the components,
   maps coverage, shows distributions/scatters, tests thresholds, and selects
   markets; then a market notebook parameterized for Richmond first. Do not
   make the national notebook a thin batch runner.
3. State the grain policy above in the spec. Tract is the primary submarket
   lens; ZCTA is the price-series companion and must use the weighted
   ZCTA-to-CBSA crosswalk; Place is supplemental; county is broad-market and
   permit context. Do not combine their values in one score.
4. Change the 10-year requirement to a grain-aware time policy: 2014–2024 at
   CBSA/county; consistent-boundary periods or validated temporal allocation at
   tract. Require the notebook to report its actual period per metric.
5. Change “build an overheating index” into an explicit decision: rebuild a
   Q1 diagnostic index only after component-level results are inspected. It
   must remain secondary to the supply-versus-demand classification and must
   be benchmarked against—not inherited from—the publisher composite.
6. Set inclusion rules separately by lens. For the initial national tract
   lens, require valid rent, household income, vacancy, and selected population
   window, record exclusions, and retain a `no clear signal` outcome. Do not
   drop a market simply because it lacks a tract price or permit signal.
7. Add IRS net migration as county/CBSA historical context through 2022 only;
   do not describe ACS mobility as net demand. Make ZORI optional because of
   its coverage.

## Epic 1 conclusion

Proceed to the revised definition-and-component work. The only prerequisite to
implementation is to lock the grain-aware component and time policies above;
no new upstream engine or data acquisition is required for the first version.
