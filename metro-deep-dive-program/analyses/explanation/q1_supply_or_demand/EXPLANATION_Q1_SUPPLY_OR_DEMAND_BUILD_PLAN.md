# Explanation Q1 — Supply or Demand Build Plan

**Status:** Epic 1 complete; mart build is next

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
- [ ] Test known markets and the no-signal path.
- [ ] Decide which mart fields are stable enough for Q2, Q3, and the Housing
  satellite, and whether a later Foundations migration is warranted.

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
