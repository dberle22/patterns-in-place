# Explanation Q1 — Supply or Demand Spec

**Status:** Revised after Epic 1 audit; ready for mart design

**Build order:** E2

**Default market:** Richmond, VA (`40060`)

**Initial method:** `q1_supply_demand_v1`

## Goal

Determine whether relatively inexpensive housing reflects supply that is keeping
up, weak demand, or a mixed/no-clear-signal condition. The analysis must first
make the evidence legible; a composite index is a secondary diagnostic, not the
primary conclusion.

Q1 produces an analysis-owned housing component mart, a national notebook that
uses it to identify markets worth examining, and a market notebook that starts
with Richmond.

## Analytical surfaces

### 1. Analysis-owned mart

The first implementation artifact is a SQL build in `queries/` that reads only
from managed Gold and Geography surfaces. It materializes
`mart_explanation_q1.supply_demand_base`: one row per
`geo_level + geo_id + year`, with raw source fields, cleaned fields,
component-ready fields, data-coverage flags, boundary-vintage metadata, and
metric-count fields. It is Q1-owned rather than a publisher dependency.

The build keeps source fields and derived fields distinct. It may calculate
affordability ratios, growth measures, and component inputs, but does not lock
an overheating composite until the national component results are reviewed.

The `queries/` folder also holds narrow, named SQL queries that read the mart
for each notebook surface: coverage, distributions, maps, scatters, component
tables, trend views, and any later index comparison. Notebook code should not
repeat the mart's joins or metric definitions.

### 2. National notebook

`EXPLANATION_Q1_NATIONAL_NOTEBOOK.py` defines and displays the method before a
market is selected. It must:

- document metric definitions, coverage, grain, vintage, and exclusions;
- show national maps, distributions, scatter plots, and threshold sensitivity;
- compare CBSA/county components with the existing publisher overheating mart;
- identify markets for deeper review without treating a rank as a conclusion.

### 3. Market notebook

`EXPLANATION_Q1_MARKET_NOTEBOOK.py` is parameterized by CBSA and begins with
Richmond. It moves from the broad market to its submarkets, reports the actual
available period for every chart, and preserves a `no clear signal` result.

## Affordability definition

The primary renter affordability measure is:

`annualized_median_gross_rent / median_household_income`

Both inputs are local ACS measures, so no general cost-of-living deflator is
needed for v1. Call this **housing-cost to household-income**, not cost to
wages: the available denominator is household income and can include non-wage
income.

- `<= 0.30`: initially classify as inexpensive under the conventional
  affordability rule.
- `<= 0.50`: report as a stress-test threshold, not as an alternative claim of
  affordability.
- National distributions are comparison context, not a second national-income
  denominator.

Owner housing is a required parallel context, not a substitute for renter
affordability. The mart retains the ACS monthly `median_owner_costs_mortgage`
and `median_owner_costs_no_mortgage` fields, annualizes them, and expresses each
against local median household income. It also retains median home value and
`value_to_income` as asset-price context. Owner-cost results must identify the
mortgage status and may not be blended with renter costs into one ratio.

## Grain and time policy

Use lenses, not a multi-grain combined score.

| Lens | Purpose | Required rule |
|---|---|---|
| CBSA | National typology, 10-year trend, demand and permit context | Direct 2014–2024 values; IRS net migration ends in 2022. |
| County | Within-market permit response and historical context | Direct 2014–2024 values; never allocate to tracts. |
| Tract | Primary submarket affordability, occupancy, stock, and resident demand lens | Use the 2020 tract backbone for harmonizable historical measures. |
| ZCTA | Submarket price-level/appreciation companion | Use managed ZCTA market series and the weighted ZCTA-to-CBSA crosswalk for market membership. |
| Place | Municipal context, including permit response | Retain as its own lens; report both row and population-weighted permit coverage. |

The Geography layer provides 2010-to-2020 tract temporal edges with population,
housing-unit, and land-area weights. Use them to restate **additive counts** to
the 2020 tract backbone, selecting the weight basis that matches the measure and
retaining `change_type` and `quality_flag`.

Do not allocate medians, ratios, percentages, or price indices as though they
were counts. For those metrics, use within-vintage trends, explicit pre/post
2020 comparison, or a separately justified recomputation from harmonized
numerator and denominator counts. The mart must label direct and harmonized
observations separately.

## Component families

Build and inspect families before classifying any market:

- **Cost and strain:** renter cost-to-income, owner-cost-to-income by mortgage
  status, rent burden, value-to-income, and price level.
- **Supply and tightness:** housing stock and occupancy, vacancy, structure
  mix, harmonized housing-unit change where valid, and permit response only at
  valid CBSA/county/Place grains.
- **Demand:** population change, occupancy, ACS mobility/churn as non-net
  context, and county/CBSA IRS net migration through 2022. Price and rent
  appreciation remain separately labeled market-response context, not a proxy
  silently merged into demand.

ZORI is optional because coverage is incomplete. ZHVI is the standard managed
sub-county market-price series; FHFA is supporting context where available.
There is no managed tract price series.

## Classification and index policy

The first classification is component-led: supply-supported affordability,
weak-demand affordability, pressure/shortage, mixed, or no clear signal. It
must state the evidence and the missing inputs that prevent a stronger finding.

Only after the national notebook reviews component behavior may Q1 create a
diagnostic supply/demand or overheating index. If created, it must retain raw
inputs, direction rules, metric counts, score universe, and sensitivity tests.
It will be compared at CBSA/county grain with
`mart_housing.overheating_matrix`, not inherited from it.

## Minimum outputs

- National coverage and exclusion table.
- National affordability, owner-cost, supply, and demand distributions.
- National maps and component scatter plots.
- CBSA typology and publisher-mart comparison.
- Richmond broad-market trend and county permit context.
- Richmond tract table and map, ZCTA price context, and Place context with
  weighted coverage displayed.
- Classification sensitivity and a visible no-signal path.

## Guardrails

- Do not assign county or Place permits to tracts or ZCTAs.
- Do not combine geographic lenses or price level and appreciation silently.
- Do not allocate nonadditive tract measures across the 2010/2020 boundary.
- Do not describe ACS mobility as net migration or require optional ZORI data.
- Do not silently adopt the publisher-owned overheating method.

## References

- [Epic 1 audit](EXPLANATION_Q1_AUDIT.md)
- [Build plan](EXPLANATION_Q1_SUPPLY_OR_DEMAND_BUILD_PLAN.md)
- Section 5.3 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
