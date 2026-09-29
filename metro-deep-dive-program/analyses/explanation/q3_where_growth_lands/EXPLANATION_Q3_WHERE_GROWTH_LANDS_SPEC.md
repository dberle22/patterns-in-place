# Explanation Q3 — Where Growth Lands Spec

**Status:** Revised after Epic 1 audit — ready for the Geography dependency and
Epic 2

**Build order:** E6

**Primary surface:** `EXPLANATION_Q3_NOTEBOOK.py` (not yet written)

**Default market:** Richmond, VA (`40060`)

**Initial method:** `q3_growth_location_v1`

**Dependencies:** tract population and housing histories, 2010-to-2020 tract
harmonization, Geography-owned Place-to-CBSA membership, and tract display
geometry. Q2's reviewed job-center physical-proximity output is optional
explanatory context, not an access dependency.

## How to read this spec

**Epic 1 is complete.** This spec incorporates its findings. The build plan
defines the task sequence; this document locks the Q3 method and output
contract.

## Goal

Determine where population and housing-unit growth or decline is landing within
a metro: across tracts, counties, named Census Places, and residual
unincorporated geography. Q3 identifies the observed pattern first —
concentrated or dispersed, near existing job centers, in particular counties,
or in particular Places — before an Issue makes any interpretation.

`Infill` and `greenfield` are not Q3 classifications. They may be considered in
a downstream Issue only when the observed growth pattern and other evidence
support that interpretation.

## National posture: national method, local application

## Locked method frame

### Time and geography

- Use the latest covered ACS release as the end year, currently 2024.
- Calculate 1-, 3-, 5-, and 10-year change against 2023, 2021, 2019, and 2014.
- Restate the 2014 and 2019 tract counts to the 2020 Census tract vintage with
  `silver.xwalk_temporal`; use `population` weights only for population and
  `housing_units` weights only for housing counts.
- Join 2021, 2023, and 2024 counts directly on the 2020 tract identity.
- Retain source and target IDs, weights, change types, and quality flags in
  every historical tract result.

ACS 5-year releases overlap. The 5- and 10-year horizons are the primary
interpretive evidence; 1- and 3-year results are descriptive watchlist signals,
not independent annual growth estimates or stand-alone tract acceleration
claims.

### Native-grain lenses

| Lens | Purpose | Contract |
|---|---|---|
| Harmonized tract | Primary spatial evidence | Map and analyze population and housing-unit change at 2020 tract vintage. |
| County | Exact named-location summary | Use governed county-to-CBSA containment; components can reconcile to the metro ledger. |
| Census Place | Named-location summary | Use Geography-owned Place-to-CBSA membership. Show whole, split, and primary-association status. Direct Place values are not summed into the metro ledger without explicit allocation. |
| Permit data | Construction context | Retain at county, Place, or CBSA grain only. Never assign permits to tracts. |
| Q2 job-center proximity | Optional explanatory gradient | Physical centroid distance only; never access, travel time, commuting, or a 15-minute result. |

Unincorporated and split/ambiguous geography remains visible rather than being
absorbed into a Place summary.

### Growth statuses

Q3 reports levels, absolute change, and percent change separately. It uses
`gain`, `loss`, `no material change`, and `insufficient confidence/coverage`
statuses; it does not force every tract into a location type. Epic 3 selects and
sensitivity-tests the material-change rule, then records it with the method
version.

## Relationship to Q2

Q3 may use Q2's reviewed 2023 job-center output only as an optional explanatory
gradient after the growth geography is established. Its V0 measure is
centroid-to-centroid Haversine physical proximity to a candidate job-center
tract. It is not a travel, commute, access, or 15-minute-city surface.

## Audit-confirmed input posture

| Observation | Why it matters | Q3 disposition |
|---|---|---|
| `silver.xwalk_temporal` has population and housing-unit bases, change types, and quality flags | Q3 can reuse the relationship | Construct the metric-specific panel; do not build another crosswalk. |
| Tract population and housing histories are populated for 2012–2024 | All four declared horizons are supported | Restate only the 2014 and 2019 tract endpoints. |
| Permits are absent at tract/ZCTA, strong at county/CBSA, and partial at Place | Permits remain a separate native-grain lens | Never assign permits to tracts. |
| No governed Place-to-CBSA relationship exists | Place cannot yet be a metro lens safely | Build the Geography-owned membership interface before Q3 consumes Places. |
| Structure and vacancy context exist at tract grain | Useful descriptive context | Do not force a built-footprint or infill/greenfield class. |

## Inputs

| Input | Role | Limitation / treatment |
|---|---|---|
| `gold.housing_core_wide` | Population, housing units, vacancy, and structure context at tract, county, and Place grains | ACS 5-year releases; use the declared horizon posture. |
| `silver.xwalk_temporal` | Restate 2014 and 2019 tract counts to 2020 tracts | Allocation model with quality flags, not observed annual placement. |
| Geography Place-to-CBSA membership | Associate Places with metros | Required before Place results are shown for a selected metro. Split Places remain explicit. |
| `mart_geography.rollup_tract_to_cbsa` and county containment | Define metro tract and county cohorts | Current governed CBSA association. |
| Tract display geometry | Selected-market tract maps | Display only; not used to derive analytical allocation, containment, area, or distance. |
| `silver.bps_wide` / `gold.housing_core_wide` permit fields | Native-grain permit context | No tract or ZCTA permit coverage; Place coverage is partial. |
| Q2 `mart_explanation_q2` output | Optional job-center proximity context | 2023 snapshot; physical distance only. |

## Notebook contract

The notebook is market-first. It accepts a CBSA, selected horizon, and
population/housing-unit measure selector. Its default read is 10-year
housing-unit change with the 5-year read beside it.

| Sequence | Section | Required visual/output | Purpose |
|---|---|---|---|
| 1 | Method and coverage | Method/coverage table | Establish years, geography, crosswalk quality, permits, Q2 availability, and exclusions before interpretation. |
| 2 | Metro change at a glance | Paired annualized horizon-comparison chart | Read population and housing change across 1/3/5/10 years; label short horizons as watchlist signals. |
| 3 | Where change lands | Aligned tract choropleths for population and housing-unit change | Primary spatial evidence. Map absolute contribution by default; expose rate separately to avoid small-base distortion. |
| 4 | Growth concentration | Cumulative concentration curve and 50%/80% tract counts | Distinguish concentrated from dispersed growth without an infill/greenfield classification. |
| 5 | County pattern | Ranked paired county bars for absolute contribution and rate | Identify exact county components of metro change. |
| 6 | Census Place pattern | Ranked Place table/bar chart with membership labels | Identify named growth locations without forcing Place values to reconcile to the metro total. |
| 7 | Context | Native-grain permit comparison; optional job-proximity scatter or binned curve | Provide descriptive context, not causal proof. |
| 8 | Findings and QA | Signal status, residuals, sensitivity, and candidate-finding table | Hand off evidence to downstream Issue development. |

The tract map is the primary spatial visual. Place geometry is not required for
Q3; until a governed Place display-geometry consumer exists, Places are shown
in labeled tabular/bar form rather than on an ungoverned map.

## Minimum outputs

- Provenance, coverage, and tract-harmonization QA for every comparison.
- National method coverage and distribution/sensitivity surfaces, without a
  metro ranking.
- Selected-market metro horizon comparison, tract map pair, concentration read,
  county contribution view, and Place growth lens.
- Native-grain permit context where coverage exists.
- Residual/no-material-change/insufficient-confidence groups in every relevant
  output.
- Candidate findings with a plain-language result status: `strong signal`,
  `mixed`, `no clear signal`, or `insufficient coverage`.

## Guardrails

- do not assign county or Place permits to tracts
- do not represent a Place-to-CBSA association as exact containment
- do not sum direct Place values into the metro ledger without a declared
  allocation method
- do not hide crosswalk allocation error, incomplete coverage, or residual
  geography
- do not infer infill or greenfield from map appearance, density alone, or a
  distance threshold
- do not call Q2's Haversine physical proximity access, travel time, commuting,
  or a 15-minute result
- do not describe overlapping ACS 5-year-release differences as independent
  annual growth

## Remaining implementation decisions

- Set and sensitivity-test the material-change status rule after inspecting the
  national and Richmond distributions.
- Determine in Epic 5 whether short-horizon tract findings need a Q3-scoped
  ACS-MOE reliability check before publication.
- Decide whether Q2 job-center proximity adds useful explanatory evidence after
  the core growth-location result is visible.

## References

- [Epic 1 audit](EXPLANATION_Q3_AUDIT.md)
- [Build plan](EXPLANATION_Q3_WHERE_GROWTH_LANDS_BUILD_PLAN.md)
- Section 5.5 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
