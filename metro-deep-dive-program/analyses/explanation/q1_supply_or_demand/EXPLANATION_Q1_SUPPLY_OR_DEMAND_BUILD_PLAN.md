# Explanation Q1 — Supply or Demand Build Plan

**Status:** Operational notebook build and foundational validation complete;
two research closeout tracks remain

## Epic 1 — Audit inputs and prior art

- [x] Confirm housing, population, income, migration, permit, and price-series
  coverage by grain and year.
- [x] Audit the publisher-owned `mart_housing.core_metrics` and
  `mart_housing.overheating_matrix`.
- [x] Confirm that ACS supplies renter costs, owner costs with and without a
  mortgage, household income, and home value.
- [x] Confirm 2010-to-2020 tract temporal edges and their allowable weight
  bases.
- [x] Check Place permit coverage: 39.7% of 2024 Places, but 77.3% when
  population- or housing-unit-weighted.
- [x] Record the findings in [EXPLANATION_Q1_AUDIT.md](EXPLANATION_Q1_AUDIT.md).

**Completed conclusion:** build an analysis-owned mart; use the publisher mart
only as a CBSA/county comparison benchmark.

## Epic 2 — Build the Q1 component mart

- [x] Create `queries/` and add `q1_supply_demand_mart.sql` as the sole build
  definition for `mart_explanation_q1.supply_demand_base`.
- [x] Read from Gold and Geography surfaces only; do not join a publisher mart
  into the base mart.
- [x] Retain source fields, cleaned fields, source/grain coverage flags, and
  per-family metric counts. Validate the `geo_level + geo_id + year` key.
- [x] Add renter affordability: annualized gross rent, median household income,
  rent-to-income, and `30%`/`50%` threshold flags.
- [x] Add owner context: monthly and annualized owner cost with a mortgage,
  owner cost without a mortgage, their separate cost-to-income ratios, median
  home value, and value-to-income.
- [x] Add supply, demand, price-context, migration-context, and permit fields
  only at their observed valid grains. Do not synthesize tract/ZCTA permits.
- [x] Materialize a direct-observation surface and a separately labeled
  tract-2020 harmonized-count surface. Allocate only additive counts using the
  Geography layer's measure-appropriate population or housing-unit weights;
  retain allocation quality metadata.
- [x] Keep medians, rates, ratios, and price indices direct/vintage-labeled.
  Recompute a rate only when both compatible numerator and denominator counts
  have been harmonized.
- [x] Add named SQL readers for coverage, national distributions, maps,
  scatterplots, CBSA/county trend context, tract tables/maps, ZCTA price
  context, and Place context.

**Done when:** a rerunnable SQL build produces one documented Q1 mart with
clear grain, vintage, coverage, and allocation behavior; notebook code does not
repeat its joins or metric definitions.

## Epic 3 — Build the national notebook

- [x] Create `EXPLANATION_Q1_NATIONAL_NOTEBOOK.py` using only named `queries/`
  readers.
- [x] Display row and population-weighted coverage, exclusions, and actual
  metric periods before substantive charts.
- [x] Show renter and owner affordability distributions separately, including
  the 30% baseline and 50% sensitivity threshold.
- [x] Show national supply, demand, price-context, and affordability maps and
  scatter plots without mixing their grains.
- [x] Add an index-methodology section that states the provisional component
  inputs, direction rules, normalization universe, metric-count and
  missing-data rules, and shows how rankings and classifications change under
  reasonable component-weight and threshold alternatives.
- [x] Produce the CBSA typology and a transparent comparison with the publisher
  overheating mart at common CBSA/county grain.
- [x] Identify markets for deeper review; retain a no-signal outcome.

**Done when:** the national notebook is readable as an independent result and
selects Richmond without treating a ranking as a causal conclusion.

## Epic 4 — Build the Richmond market notebook

- [x] Create `EXPLANATION_Q1_MARKET_NOTEBOOK.py`, parameterized by CBSA and
  first run it for Richmond (`40060`).
- [x] Add the Richmond CBSA/county 2014–2024 context, including permits and IRS
  net migration only through 2022.
- [x] Add tract affordability, owner-cost, stock, vacancy, and resident-demand
  views; label direct and harmonized counts distinctly.
- [x] Add ZCTA price/appreciation context through the weighted ZCTA-to-CBSA
  crosswalk.
- [x] Add Place context, retain the national 77.3% population-weighted 2024
  permit-coverage benchmark, and label Richmond's overlapping Place-membership
  coverage as context rather than a CBSA population partition.
- [x] Build maps, a component table, and classification sensitivity with a
  visible no-clear-signal path.

**Done when:** a reader can move from national selection to Richmond evidence
without an unlabelled grain, source, or boundary-vintage change.

## Epic 5 — Decide on an index and stabilize reuse

- [x] Draft the candidate overheating definition and measurement policy in
  [EXPLANATION_Q1_INDEX_METHOD_NOTE.md](EXPLANATION_Q1_INDEX_METHOD_NOTE.md).
- [x] Review the national and Richmond component results before proposing a
  Q1 supply/demand or overheating index.
- [x] Define the provisional complete-family score universe, direction rules,
  raw inputs,
  metric-count rule, missing-data rule, and threshold sensitivity in SQL.
- [x] Compare the new CBSA result with
  `mart_housing.overheating_matrix`; do not inherit its formula.
- [x] Document the candidate composite as exploratory only; defer selection of
  a Q1 standard index to the deliberate deep dive in Epic 10.

**Done when:** Q1 has either a validated, explicitly provisional diagnostic
index or a documented decision that component-led classification is sufficient.

## What not to do

- Do not assign county or Place permits to tracts or ZCTAs.
- Do not allocate medians, ratios, percentages, or price indices across the
  2010/2020 tract boundary.
- Do not blend renter and owner cost measures or treat household income as a
  wage series.
- Do not make ZORI an inclusion requirement.
- Do not adopt the publisher's overheating method implicitly.

## Revision epics — approved metric-contract and notebook rebuild

These epics preserve the initial work as an auditable foundation. They correct
measure semantics and rebuild presentation/classification behavior; they do not
silently rewrite the history of Epics 1–5.

## Epic 6 — Correct the affordability contract and mart readers

- [x] Replace the primary renter-affordability presentation/classification
  measure with ACS `pct_rent_burden_30plus` and add its valid five-year change.
- [x] Rename `renter_cost_to_income` everywhere it is presented to
  `median-rent-to-all-household-income price proxy` (or an equivalent concise
  label); document its all-household denominator.
- [x] Deprecate `renter_inexpensive_30_flag` and
  `renter_stress_test_50_flag`; no notebook classification or conclusion may
  use either flag.
- [x] Keep annualized median rent and owner costs in the mart. Label owner-cost
  measures as existing-owner context and preserve mortgage status; do not use
  them as current-buyer affordability measures.
- [x] Add or update named readers for renter-burden level/change, value-to-
  income change, fixed FHFA/ACS momentum measures, and their source years.
- [x] Add a metric-contract table to the mart/notebook readers: source,
  numerator, denominator, applicable grain, period, and prohibited inference.

**Done when:** each displayed affordability field has a defensible household or
market-access meaning, and no 30% threshold is applied to a median-rent/all-
household-income proxy.

## Epic 7 — Rebuild the national notebook as a decision sequence

- [x] Start with the question, declared 2024 ACS snapshot, cohort/universe,
  source coverage, exclusions, and metric contract.
- [x] Present national distributions and maps by family before testing
  relationships: renter burden, market access, momentum, supply response,
  demand, and vacancy context.
- [x] Make five-year FHFA HPI the canonical home-price momentum series and
  five-year ACS gross-rent growth the parallel rent series. Keep Zillow results
  as clearly labelled diagnostic context.
- [x] Make momentum-versus-supply-response the primary overheating diagnostic;
  distinguish permits (construction response) from housing-stock growth
  (realized response).
- [x] Show how affordability conditions interact with supply and demand without
  claiming a causal relationship from a cross-sectional scatter.
- [x] Move the candidate index after the component evidence and methodology
  card; retain it only if it contributes information beyond component-led
  findings.
- [x] Use one declared primary CBSA universe for comparable visuals and put
  small-market results in a labelled supplemental view rather than silently
  mixing universes.

**Done when:** a reader can understand the national housing conditions and the
evidence for or against an index without reading the SQL or inferring a metric's
meaning from a chart title.

## Epic 8 — Rebuild the CBSA market notebook, starting with Richmond

- [x] Replace free-text CBSA entry with the standard searchable dropdown
  formatted as CBSA name plus code, defaulting to Richmond, VA (`40060`).
- [x] Lead with a metric-definition note and broad CBSA/county trends using
  native units in separate aligned panels; provide a separately labelled
  standardized comparison only where useful.
- [x] Replace the static tract-centroid scatter with a Marimo-supported
  interactive tract map and table, including a metric selector, stable legend,
  and hover detail.
- [x] Limit tract choices to direct tract-valid measures and maintain explicit
  vintage/allocation labels; never infer tract permits or prices from higher
  grains.
- [x] Repair the ZCTA context cell and test it using the selected CBSA.
- [x] Rework tract classification using renter burden and valid direct
  evidence; retain and explain `no clear signal`.
- [x] Keep ZCTA price and Place permit evidence as context lenses, including
  the overlap/coverage caveat.

**Done when:** Richmond can be investigated from CBSA to tract without mixed
units, a broken context view, or an unsupported affordability classification.

## Epic 9 — Foundational validation and visualization review

- [x] Add population-weighted major-CBSA benchmark lines and unweighted
  25th–75th percentile bands to the broad-market trend charts.
- [x] Replace local-base-year supply co-movement with a national-relative,
  interquartile-range-scaled supply and demand context view.
- [x] Add visible Tract → ZCTA → Place geography lenses, each with direct
  affordability/vacancy context, an interactive map, and a transparent
  descriptive conditions matrix.
- [x] Add opt-in Census cartographic-boundary display geometry for ZCTAs
  (2020 vintage) and Places (2024 vintage) to support those maps without
  approximating their shapes from tract memberships.
- [x] Add KPI-selectable momentum-versus-supply relationships and an
  interactive CBSA/state-outline map so component and composite patterns can
  be reviewed before index retention is decided.
- [x] Reconcile 2024 displayed fields to their ACS-derived Gold sources for
  Richmond, Tampa, and Shreveport. Renter burden, rent proxy, existing-owner
  cost context, value-to-income, FHFA momentum, and population growth matched.
- [x] Confirm every chart's data year/window and reject mixed-year comparisons
  unless explicitly presented as later context.

**Completed validation boundary:** foundational field reconciliation and chart
period/window review are complete. The remaining market tests and index choice
are now tracked as dedicated research work below.

## Epic 10 — Deep dive on overheating composites

- [ ] Compare component-led diagnosis, the equal-weight four-family composite,
  two scenario-weight composites, and the momentum-versus-supply matrix.
- [ ] Test whether rankings remain stable under reasonable metric, weight, and
  threshold changes.
- [ ] Compare candidate outputs with the publisher overheating mart as an
  external benchmark, without inheriting its formula.
- [ ] Decide whether Q1 adopts a standard index, retains a nonstandard
  exploratory rank, or uses component-led diagnosis only.

**Done when:** the Spec records an evidence-backed index decision and its
appropriate scope, or explicitly records the decision not to standardize one.

## Epic 11 — Document initial multi-market notebook reads

- [ ] Run the notebooks for Richmond, contrasting momentum/demand markets,
  and at least one no-signal case.
- [ ] Record the observed components, geographic-lens evidence, data gaps,
  and analyst interpretation for each market.
- [ ] Confirm that the descriptive conditions matrices remain understandable
  and do not imply causal claims at Tract, ZCTA, or Place grain.
- [ ] Identify stable mart fields for Q2/Q3 or the Housing satellite and any
  later Foundations migration candidates.

**Done when:** Q1 has a concise, reviewable initial market-read record and a
documented reuse recommendation.

## Revision completion summary

- **Epics 6–8:** rebuilt the Q1 mart readers and both notebooks around renter
  burden, clearly labelled market-price proxies, fixed price/rent momentum
  measures, native-unit market trends, and interactive tract evidence.
- **Epic 9:** foundational validation complete: values reconcile to Gold,
  chart periods/windows are confirmed, and the revised notebook design is
  operational.
- **Epics 10–11:** remaining deliberate index research and documented
  multi-market reads. No standard Q1 index has been selected.
