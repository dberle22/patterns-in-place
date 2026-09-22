# Q6 One Metro? — Epic 1 Audit

**Completed:** 2026-09-21

**Scope:** Read-only audit of the current warehouse and the completed Q2 and
Regional Role contracts. No Q6 notebook, query, mart, or OD ingestion was
built in this epic.

## Decision summary

| Requirement | Finding | Q6 disposition |
|---|---|---|
| County status | `silver.xwalk_cbsa_county` is an OMB 2023 crosswalk with county-equivalent IDs and a `county_flag`. | Report its Central/Outlying designation as sourced county context; do not recreate it. |
| Census Place profile | `gold.population_demographics` has direct 2024 Place rows, while Geography supplies Place identity and tract-to-Place allocation edges. | Make the Census Place hierarchy the primary Q6 surface; disclose direct versus allocated measures. |
| Workplace-job context | `silver.lehd_lodes_wac` and `gold.economics_lodes_wide` provide 2023 tract evidence, but no direct Place rollup. | Allocate with the declared Geography basis and label the result as allocated context. |
| Named anchor cities | `silver.xwalk_cbsa_primary_city` supplies OMB principal-city identities. | Use it as one orientation field, but start analysis from every covered Census Place. |
| Q2 dependency | `mart_explanation_q2` publishes reviewed job-center candidates, clusters, and tract proximity for 2023 WAC. Its V0 distance is centroid-to-centroid Haversine miles. | Adopt physical proximity unchanged. It is not access, travel time, commuting, or a 15-minute result. |
| Regional Role dependency | Its audit and V1 contract are complete, but its reusable regional-lens and workbench surfaces are not complete. | Reuse its source/interpretation contracts when useful; do not make Q6 wait for an output that does not yet exist. |
| POI and Infrastructure evidence | No direct Place-grain assignment is currently published. | Do not allocate point counts; add after Geography publishes direct Place assignment. |

## County status is sourced context

Q6 reports `silver.xwalk_cbsa_county.county_flag`, the OMB 2023 Central/Outlying
designation, rather than deriving its own county membership rule. For Richmond
(`40060`), the audit confirms 17 member county equivalents with that field
populated. The designation orients the Place analysis; it is not an anchor-city
classification, flow result, or a claim that every Place in a Central county has
the same role.

## Anchor-city classification matrix

The anchor-city read is the primary result. The candidate universe is every
Census Place with declared coverage in the selected CBSA. A supported anchor is
a materially significant Place profile with an associated reviewed Q2
job-center component under the selected Q2 version. Place association must use
a declared Geography relationship or allocation rule; display geometry is not
an analytical substitute.

| Result | Decision rule | Required disclosure |
|---|---|---|
| `one supported anchor` | Exactly one candidate Place has a supported, distinct Q2 component. | Candidate inventory and rejected/sensitivity candidates. |
| `multiple supported anchors` | Two or more candidate Places each have a distinct supported Q2 component. | Component-to-Place mapping and center-version sensitivity. |
| `mixed` | More than one plausible candidate exists, but candidates share one component or the conclusion changes across Q2 versions. | The conflicting components, Place associations, and sensitivity results. |
| `insufficient structure evidence` | Required Place relationship, reviewed Q2 surface, or coverage is unavailable. | The missing input and its effect. |

This is deliberately a reviewable classification, not a polycentricity index or
a composite Place score. The minimum materiality rule for candidate-anchor
review will be calibrated before Epic 3; every covered Place remains visible in
the hierarchy even when it is not an anchor candidate.

## OD ingestion decision

LODES OD should now be ingested as shared Foundations work. The source contract
already documents the state-based `main` and `aux` OD families, block-native
home/work IDs, and 2023 LODES 8 coverage. The initial work should decide,
through a one-state profile and row/size estimates, whether a national
Place-to-Place aggregate can be the durable managed surface. It must preserve
work and home Place direction, source state/part, job type, year, and coverage
flags, while avoiding persistent block-to-block storage unless profiling proves
it necessary. County aggregation may be retained only when it is a low-cost
shared companion surface.

The bounded handoff is in
[LODES_OD_INGEST_AGENT_SCOPE.md](LODES_OD_INGEST_AGENT_SCOPE.md).

## Buildable now and blocked

The Place hierarchy and anchor-city classification are buildable after their
stated Q2 and Geography inputs are available. OD, POI, and Infrastructure are
later relationship evidence; their absence does not block the primary Q6
analysis.

## References

- [Q6 Spec](EXPLANATION_Q6_ONE_METRO_SPEC.md)
- [Q6 Build Plan](EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md)
- [Q2 Job-Center and Proximity Method Spec](../q2_job_proximity/EXPLANATION_Q2_JOB_PROXIMITY_SPEC.md)
- [Regional Role Audit](../regional_role/EXPLANATION_REGIONAL_ROLE_AUDIT.md)
