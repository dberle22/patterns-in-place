# Explanation Q1 — Supply or Demand Spec

**Status:** Operational notebook build complete; index research and initial
multi-market reads remain

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

## Revision record — metric-contract and notebook rebuild

The first notebook build established the mart and candidate component/index
surfaces. Review found that the notebooks led with exploratory relationships
and a candidate index before establishing the meaning of the underlying housing
measures. The following additions supersede only the affected presentation,
classification, and affordability rules; they retain the completed source,
grain, and tract-harmonization work from Epics 1–5.

- Treat the analysis as a decision sequence: establish housing conditions,
  examine supply/demand interactions, then decide whether a composite adds
  information beyond its components.
- Make the 2024 ACS cross-section the declared national snapshot. Label later
  price-series observations as later context rather than blending them into a
  2024 comparison.
- Use a fixed, parallel momentum pair: five-year FHFA HPI for home-price
  momentum at CBSA/county grain and five-year ACS median-gross-rent growth for
  rent momentum. Zillow series remain optional diagnostic context rather than
  interchangeable primary measures.
- Rebuild the market notebook around a standard CBSA name-and-code selector,
  native-unit broad-market trends, and interactive tract evidence.

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

## Affordability and price-access definition

Use separate measures for household burden, market price/access, and the
existing-owner population. No general cost-of-living deflator is required for
v1 because each measure uses local ACS costs and incomes.

| Question | Primary measure | Interpretation rule |
|---|---|---|
| Are renter households burdened now? | ACS `pct_rent_burden_30plus`, and its five-year change | This is the primary renter-affordability measure. The 30% threshold applies to this household-level burden measure. |
| How does prevailing rent compare with local income? | `annualized_median_gross_rent / median_household_income` | Label as **median-rent-to-all-household-income price proxy**. It uses all-household median income, not renter median income, so it is not a household burden test and has no 30%/50% classification threshold. |
| How accessible is market entry for a buyer? | `median_home_value / median_household_income`, and its five-year change | Label as a value-to-income market-entry proxy, not a monthly payment or owner burden. |
| What costs do existing owners report? | ACS median monthly selected owner costs, separately with and without a mortgage | Present as existing-owner cost context. It is not a current-buyer payment estimate and must retain mortgage status. |

The mart retains annualized rent and owner-cost fields for transparent context.
It must remove the semantic use of the existing `renter_inexpensive_30_flag` and
`renter_stress_test_50_flag`; if retained during transition, they must be
deprecated and never drive a classification or affordability claim.

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

- **Renter affordability and market access:** renter burden at 30% and its
  change, median-rent-to-all-household-income price proxy, value-to-income,
  and their clearly labelled changes. Existing-owner costs are parallel
  context, not a combined affordability score.
- **Momentum:** five-year FHFA HPI and five-year ACS median-gross-rent growth.
  Price levels and appreciation must not be silently combined.
- **Supply response and tightness:** five-year housing-stock growth, five-year
  cumulative permits per starting housing unit, vacancy, occupancy, and
  structure mix. Permits and stock growth remain separate signals; permit
  response is valid only at CBSA/county/Place grains.
- **Demand:** five-year population growth, occupancy, ACS mobility/churn as
  non-net context, and county/CBSA IRS net migration through 2022.

ZORI is optional because coverage is incomplete. ZHVI is the standard managed
sub-county market-price series; FHFA is supporting context where available.
There is no managed tract price series.

## Classification and index policy

The first classification is component-led: supply-supported affordability,
weak-demand affordability, pressure/shortage, mixed, or no clear signal. It
must state the evidence and the missing inputs that prevent a stronger finding.

The first diagnostic view for the proposed overheating question is
momentum-versus-supply-response: high price/rent momentum with weak housing
stock and permit response. It is a hypothesis test, not evidence of causation.
Timing lags and construction responding to earlier pressure must be considered
when interpreting the relationship.

Only after the national notebook reviews that view and the affordability
components may Q1 retain a diagnostic supply/demand or overheating index. If
retained, it must score distinct momentum, affordability-deterioration, demand,
and supply-constraint families; retain raw inputs, direction rules, metric
counts, score universe, complete-family inclusion, and sensitivity tests. It
will be compared at CBSA/county grain with
`mart_housing.overheating_matrix`, not inherited from it.

**Current Q1 use policy:** the existing composite is an exploratory relative-
ranking and navigation aid, not a Q1 standard index. It may help locate markets
in the national distribution, but it is never the conclusion of a market
analysis. Future market-level work must use the observed momentum,
affordability, demand, supply-response, and coverage components as evidence.

### Index options for deliberate follow-up

Q1 has not selected a standard overheating index. The next deep dive must
compare these options against documented market reads before selecting one—or
deciding that none belongs in the standard method.

| Option | What it provides | Decision test |
|---|---|---|
| Component-led diagnosis only | No composite rank; analysts compare the four component families directly | Prefer if a rank obscures materially different market stories. |
| Equal-weight four-family composite | One balanced relative rank across momentum, affordability deterioration, demand, and supply constraint | Retain only if it is stable under reasonable metric/weight changes and adds useful orientation. |
| Scenario composites | Separate momentum/demand and affordability/supply emphasis ranks | Prefer if different policy questions consistently select different markets. |
| Momentum-versus-supply matrix | A non-ranked pressure map, with affordability and demand as overlays | Prefer if the relationship view is clearer and more actionable than a single score. |

Every option remains CBSA/county-only. Tract, ZCTA, and Place analyses remain
component-led because they do not share the same observed price and permit
coverage.

## Minimum outputs

- National coverage and exclusion table.
- National metric contract, coverage/exclusions, and explicitly dated snapshot.
- National renter-burden, market-access, momentum, supply-response, and demand
  distributions.
- National maps and component scatter plots, including
  momentum-versus-supply-response and affordability-condition views.
- CBSA typology and publisher-mart comparison.
- Richmond broad-market native-unit trends and county permit context, with an
  optional standardized comparison view that never shares unlike raw units.
- Richmond interactive tract map/table with a metric selector, ZCTA price
  context, and Place context with
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
