# Explanation Q2 — Job Proximity, Housing, and Affordability Spec

**Status:** Revised after Epic 1 audit; V0 method definition is next

**Build order:** E3 — **gates E5 (Q4), E6 (Q3), and E7 (Q6)**

**Primary surface:** `EXPLANATION_Q2_NOTEBOOK.py` (not yet written)

**Default market:** Richmond, VA (`40060`)

**Initial method:** `q2_job_proximity_v0`

**Dependencies:** LODES WAC/RAC, governed tract geometry, the Q1 2024 tract
housing surface, and OEWS. No new engine is required for the first build.

## How to read this spec

This spec incorporates the completed Epic 1 audit. The audit is the source of
truth for current input readiness and constraints. V0 is deliberately narrow:
it tests physical proximity before any shared access definition is promoted.

This analysis matters beyond its own result. It is the first test of a method
that Q3, Q4, Q6, and Catchment may later re-run with different center inputs.

## The shared access spine: V0 boundary

Most of the numbered questions have the same broad shape:

> define centers → measure distance or access from them → measure what varies
> across that gradient

Q2 is the first test of that shape, using job centers as its center input.

| Analysis | Center input | Measured across the gradient |
|---|---|---|
| Q2 | Job centers from LODES WAC/RAC | Housing cost and housing units |
| Q3 | Prior built footprint and existing centers | Growth: population, units, permits |
| Q4 | POI clusters by category | Daily-needs access |
| Q6 | Anchor cities / candidate downtowns | One center or several |
| Catchment | A declared point | Whatever the point question asks |

The promoted definition must be adoptable without reinterpretation: center
construction rule, reach measure, threshold, and minimum center requirements.
V0 does not meet that promotion bar. It measures straight-line proximity and
must not be described as a 15-minute, travel-time, or commuting method.

## Merged analysis

This absorbs the previous Q5, “Afford to Live Near Jobs.” The analyses share
inputs and a spatial setup, but V0 does not claim a worker-to-household
affordability match. It shows resident-household affordability and workplace
earnings context separately until their comparison standard is defined.

## Goal

Establish whether housing outcomes visibly vary with physical proximity to
current job concentrations, and determine whether the center and proximity
construction is strong enough to advance toward the family’s shared access
method.

## National posture

V0 is a Richmond-first method test. A national run is post-V0 calibration, not
a minimum output. It should begin only after the Richmond output has a stable
center construction, exclusion rule, and no-clear-signal interpretation.

## Audit-confirmed input posture

| Observation | Why it matters | V0 disposition |
|---|---|---|
| LODES WAC/RAC are tract-first and 2023-only | Job locations are buildable; a center time series is not | Use WAC as one current snapshot. |
| D3 ranks tracts above an adjustable default 2,500-job floor | It is display prior art, not center construction | Use its floor only as a named sensitivity candidate. |
| Tract WKB and geometry exist, but no distance projection policy is documented | Raw planar distance would be unsafe | Use centroid-to-centroid Haversine miles. |
| Q1 materializes 2024 tract housing, rent, income, burden, and unit fields | Both cost outcomes are available without duplicate transforms | Read Q1’s tract surface and report incomplete rows. |
| OEWS is 2025 CBSA/state grain | It cannot imply tract wages | Use only as labeled metro context. |
| No managed tract-level market-price series exists | Price appreciation is not a V0 outcome | Use ACS housing-cost levels, not a price trend. |

## Inputs

| Input | Role |
|---|---|
| LODES WAC at tract grain, 2023 | Workplace-concentration candidates and earnings-band composition |
| LODES RAC at tract grain, 2023 | Resident-worker context only; not commute flows |
| Governed tract geometry | Tract centroids for Haversine distance |
| Q1 `supply_demand_base` tract fields, 2024 | Housing cost, units, household income, and burden |
| OEWS at CBSA/state grain, 2025 | Occupational wage context only |
| ZCTA price/rent series | Deferred from V0; no managed tract equivalent |

## V0 method, in order

1. **Construct and disclose center candidates.** Start with workplace-job
   concentration; show the 2,500-job D3 floor as one sensitivity case rather
   than adopting it.
2. **Measure physical proximity.** Calculate Haversine miles from tract centroids
   to the nearest selected center. This is not travel, access, or 15 minutes.
3. **Show the observed gradient.** Plot binned distance against median gross
   rent, median home value, and housing units, with complete-case coverage
   shown beside each outcome.
4. **Fit descriptive models.** Estimate one disclosed, simple distance model per
   outcome and show coefficients, observations, fit, and residuals. This is not
   a causal housing-price estimate.
5. **Keep affordability separate.** Show housing-cost-to-household-income and
   rent burden by distance alongside center earnings-band composition. Do not
   calculate a household-worker mismatch in V0.

Household income, individual job earnings, and occupational wages remain
separate measures. Any bridge between them must be explicit. Network distance
or travel time is a later challenger tested once for the whole family rather
than separately for each question.

## V0 minimum outputs

- Method and coverage note: 2023 WAC snapshot, 2024 ACS/Q1 outcomes, centroid
  origin, Haversine calculation, exclusions, and the non-routing caveat.
- Center-candidate table with the selected rule and the D3 2,500-job-floor
  sensitivity result.
- Selected-market center inventory and map.
- One binned distance curve each for median gross rent, median home value, and
  housing units.
- One descriptive model table and one residual map for the selected primary
  cost outcome; retain the other outcome models in the notebook table.
- Distance-stratified housing-cost-to-household-income and rent-burden context,
  with nearby-center earnings-band composition separately labeled.

National calibration, price-source sensitivity, a residence-versus-workplace
comparison, and a final 15-minute definition are post-V0 work.

## Marimo notebook outline

V0 builds one parameterized market notebook, `EXPLANATION_Q2_NOTEBOOK.py`,
with Richmond (`40060`) as its first run. It reads named analysis queries and
does not recreate their joins in notebook cells.

1. **Purpose, parameters, and guardrails** — CBSA selector; scope statement
   that V0 measures physical proximity, not travel time.
2. **Input coverage and method** — actual source year, row counts, exclusions,
   centroid/Haversine rule, and candidate center rules.
3. **Center review** — candidate/sensitivity table, selected center inventory,
   and center map. The analyst selects a rule here; no hidden default becomes a
   shared method.
4. **Distance-gradient evidence** — binned curves, descriptive model table,
   and primary-cost residual map.
5. **Affordability context** — distance-stratified household-cost measures;
   separate nearby-center earnings-band and CBSA OEWS context.
6. **Readout and handoff** — a result or no-clear-signal statement, limitations,
   and the evidence required before promoting a shared access method.

## Guardrails

- do not infer travel, access, or commuting flows from straight-line proximity
- do not treat Infrastructure as a routing network
- do not blend household income, job earnings, and occupational wages
- do not treat ZCTAs as postal delivery ZIPs
- do not leave a promoted access definition implicit; later analyses must be
  able to adopt it from the written spec

## Post-V0 decisions

- center construction rule, including contiguity and a primary cost outcome
- distance bins, model form, controls, and minimum observations
- whether a proximity result merits a routed travel-time challenger
- affordability standard and household-versus-worker bridge
- wage source hierarchy, tenure treatment, and time alignment

## References

- [Epic 1 audit](EXPLANATION_Q2_AUDIT.md)
- [Build plan](EXPLANATION_Q2_JOB_PROXIMITY_BUILD_PLAN.md)
- Sections 2.5 and 5.4 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
