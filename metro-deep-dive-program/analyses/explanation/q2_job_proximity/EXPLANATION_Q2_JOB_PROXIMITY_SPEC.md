# Explanation Q2 — Job-Center and Proximity Method Spec

**Status:** Revised: Q2 is limited to job-center construction and its reusable
proximity surface.

**Default market:** Richmond, VA (`40060`)

## Decision reflected in this spec

Q2 starts with **job centers only**. Its job is to establish a defensible,
reviewed way to identify employment centers from workplace jobs and measure
tract proximity to them. It does not define housing, growth, amenity, or other
types of centers.

The resulting job-center inventory and tract-level proximity surface are then
inputs to a market-specific analytical notebook that asks how proximity relates
to housing supply, cost, affordability, and other approved tract outcomes. Q3,
Q4, and Q6 may later reuse the same surface for their own distinct questions.

## Notebook architecture and order

| Step | Notebook | Purpose | Scope |
|---|---|---|---|
| 1 | `EXPLANATION_Q2_JOB_CONCENTRATION_NOTEBOOK.py` | Explore how WAC workplace jobs concentrate across tracts and CBSAs; establish national context and contrast markets. | National jobs only. |
| 2 | `EXPLANATION_Q2_PROXIMITY_METHOD_NOTEBOOK.py` | In a selected market, compare transparent job-center candidates and record a human-reviewed job-center rule. | Market-specific method selection. |
| 3 | `EXPLANATION_Q2_JOB_CENTER_OUTCOMES_NOTEBOOK.py` | Analyze reviewed job-center proximity against housing, cost, affordability, and other approved tract outcomes. | Market-specific Q2 findings. |

The national job-concentration notebook should come first. It does not choose a
center rule, but it prevents a threshold chosen in one market from quietly
becoming a universal method. There is no need to build a national
job-center-versus-housing, job-center-versus-cost, or job-center-versus-growth
notebook now. A national comparison is a later calibration exercise, opened
only after the local thematic runs show a stable, useful job-center method.

## Q2 method boundary

**Center input:** 2023 LODES WAC workplace jobs at tract grain.

**Primary candidate signals:** tract share of CBSA workplace jobs and
jobs-to-resident-workers. The first makes the candidate relevant to its market;
the second identifies workplace-heavy tracts. An absolute-job floor remains a
required guardrail against small-count signals. Job density is contextual, and
contiguous qualifying tracts are an exploratory district view. Candidate flags
remain independent; none is a selected center merely because it is a notebook
default.

**Recommended V0 construction for review:** use the three signals to identify
strict core seeds, then add only direct shared-edge neighbors that satisfy the
absolute-job and jobs-to-workers guardrails. This one-hop extension lets a
tract such as Richmond `51041100107` join a connected district despite narrowly
missing the market-share gate, while avoiding unlimited outward growth. Strict
core-only and no-market-share screens remain required sensitivities. The method
record, not a notebook default, is the source of the final decision.

## Published V0 job-center versions

The three versions are published together so downstream analysis can show
center-definition sensitivity instead of treating one default as an empirical
fact. All use 2023 tract WAC, a 95% WAC-geometry-coverage CBSA cohort, a
2,500-job guardrail, and a 1.5 jobs-to-resident-workers gate.

| Version | Definition | Intended use |
|---|---|---|
| `strict_core` | Also requires at least 1.0% of CBSA workplace jobs. | High-confidence core-seed sensitivity. |
| `recommended_core_one_hop` | Strict cores plus one direct shared-edge neighbor that passes the job-floor and jobs-to-workers gates. Expansion never recurs. | Recommended V0 construction for market review and primary analytical presentation. |
| `no_share_sensitivity` | Job-floor and jobs-to-workers gates only; market share omitted. | Check for plausible smaller or outlying centers obscured by a large market core. |

`shared edge` means a nonzero shared tract boundary; corner-only contact does
not create a component. This is more interpretable than a DBSCAN radius in V0.
DBSCAN remains a later challenger for explicitly documented near-but-not-
contiguous cases; it must not silently bridge low-employment gaps or barriers.

## Published national mart

`build_q2_job_center_mart.py` materializes the following analysis-owned tables
in `mart_explanation_q2`:

| Table | Grain | Contents |
|---|---|---|
| `job_center_candidates_v0` | CBSA × tract | Source measures, coverage metadata, the three version flags, center role, and recommended component ID. |
| `job_center_clusters_v0` | CBSA × recommended component | Core/extension counts, job mass, market-job share, and whether the component has two or more tracts. |
| `job_center_proximity_v0` | CBSA × tract × center version | Nearest candidate-center tract, candidate-center count, and centroid-to-centroid Haversine miles for each version. |
| `job_center_method_catalog_v0` | method version | Fixed V0 parameters, version definitions, and promotion status. |

The national build uses an STRtree within each CBSA to find shared-edge pairs;
it does not run the notebook's all-pairs tract loop nationwide. The published
cohort contains 74,781 tract rows in 868 coverage-eligible CBSAs. Some smaller
markets have no candidate under one or more versions; their proximity rows stay
present with `has_center_candidate = false` and a null distance. That is a
method result to review, not a zero-distance or no-job claim.

The mart publishes candidate baselines, not a nationally adopted job-center
classification. The analytical outcomes notebook should lead with the
recommended version and report strict-core and no-share results as sensitivity.
Any market-specific promotion remains recorded in
`EXPLANATION_Q2_JOB_CENTER_METHOD_RECORD.md`.

**V0 proximity:** Haversine miles from declared tract centroids to the nearest
reviewed job-center origin. This is physical proximity—not travel time,
commuting behavior, access, or a 15-minute-city measure.

**Reusable Q2 output:** a versioned reviewed job-center specification, center
inventory, map-ready center geometry/origins, coverage/exclusion result, and
tract-level distance-to-nearest-job-center surface.

## National job-concentration notebook

`EXPLANATION_Q2_JOB_CONCENTRATION_NOTEBOOK.py` is the only immediate national
notebook in this sequence. It must retain:

- WAC coverage, eligible-CBSA cohort, exclusions, and 2023 snapshot caveat;
- Pareto curves and tract shares required to reach 50% and 80% of jobs;
- total-job, job-density, and jobs-to-resident-worker distributions with
  denominator safeguards;
- selected-market and contrast-market context; and
- no market ranking or automatic local center selection.

Its output is evidence for method review, not a national finding about housing
or a universal threshold recommendation.

## Market job-center method notebook

`EXPLANATION_Q2_PROXIMITY_METHOD_NOTEBOOK.py` remains the job-center workbench.
It must:

1. begin with the selected market's national job-concentration context;
2. map total workplace jobs, CBSA job share, job density, and
   jobs-to-resident-workers before filtering;
3. compare independent market-job-share, jobs-to-workers, and absolute-job
   guardrail flags, along with their overlap, parameters, and visible omissions
   or fragmentation;
4. record the selected/rejected rule, center representation, centroid origin,
   multiple-center treatment, retained sensitivities, reviewer, and date; and
5. write or expose the reviewed job-center proximity surface for thematic
   market notebooks.

This notebook may show only enough housing or other local context to help a
reviewer detect a clearly implausible job-center construction. It must not
select centers using those outcomes or turn itself into the housing, cost, or
growth analysis.

## Analytical job-center outcomes notebook

`EXPLANATION_Q2_JOB_CENTER_OUTCOMES_NOTEBOOK.py` is the third Q2 notebook. It
is parameterized by CBSA and consumes the reviewed job-center record and its
tract-level proximity surface. It is analytical rather than exploratory: it
must not expose controls that alter center selection.

V0 analyzes the Q1 tract outcomes that share a current, compatible surface:
median gross rent, median home value, housing units, median household income,
rent-to-income, and rent burden. It must show:

- the reviewed job-center method, coverage, inventory/map, and selected
  national job-concentration context;
- outcome-specific complete-case coverage and source-year labels;
- binned distance curves for rent, home value, and housing units;
- disclosed descriptive models, a primary-cost residual map, and a `no clear
  signal` conclusion when warranted; and
- separate affordability context for household cost/income and center
  earnings-band composition, without claiming a household-worker match.

Growth, daily-needs, and metro-structure comparisons remain with Q3, Q4, and
Q6 respectively because they require different time, source, and outcome
contracts. A broader final market synthesis may later combine their reviewed
results, but it is not a fourth Q2 notebook to build now.

## Input posture and guardrails

| Input | Role |
|---|---|
| 2023 LODES WAC | Job-center input. |
| 2023 LODES RAC | Resident-worker context only; not origin-destination flows. |
| Governed tract geometry | Maps, contiguity, tract centroids, and Haversine distance. |
| Q1 `supply_demand_base`, 2024 | A thematic housing/cost outcome surface, not a job-center input. |
| 2025 CBSA/state OEWS | Labeled occupational-wage context only. |

- Do not use housing, cost, income, burden, or growth to select job centers.
- Do not infer worker origins from RAC; that requires LODES OD.
- Do not blend household income, LODES earnings bands, and OEWS wages.
- Do not describe Haversine distance as a route, commute, travel time, or
  15-minute access result.

## References

- [Epic 1 audit](EXPLANATION_Q2_AUDIT.md)
- [Build plan](EXPLANATION_Q2_JOB_PROXIMITY_BUILD_PLAN.md)
- [Family plan](../EXPLANATION_ANALYSES_PLAN.md), especially Sections 2.5 and 5.4
- [Feedback](../EXPLANATION_ANALYSES_FEEDBACK.md), especially the Q2 notes
