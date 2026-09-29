# Calibration and portability review

**Status:** execution complete; visual method review and method lock pending.

The physical-evidence method and the declared three-point similarity grid were
run unchanged in Jacksonville (`27260`) and Richmond (`40060`). This record is
the reproducible starting point for the Marimo review; it is not a claim that
the default has been approved.

## Shared runs

| Market | Parameter profile | Tracts | Core | Bridge | Unassigned | Candidates | Corridors | Districts | Unclassified |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Jacksonville | `physical_evidence_v1__baseline_graph_low_similarity_v1` | 340 | 236 | 25 | 79 | 17 | 1 | 15 | 1 |
| Jacksonville | `physical_evidence_v1__baseline_graph_v1` | 340 | 234 | 25 | 81 | 17 | 1 | 14 | 2 |
| Jacksonville | `physical_evidence_v1__baseline_graph_high_similarity_v1` | 340 | 235 | 26 | 79 | 18 | 1 | 15 | 2 |
| Richmond | `physical_evidence_v1__baseline_graph_low_similarity_v1` | 332 | 257 | 16 | 59 | 12 | 0 | 9 | 3 |
| Richmond | `physical_evidence_v1__baseline_graph_v1` | 332 | 258 | 17 | 57 | 12 | 0 | 9 | 3 |
| Richmond | `physical_evidence_v1__baseline_graph_high_similarity_v1` | 332 | 258 | 17 | 57 | 13 | 0 | 10 | 3 |

All six runs passed the required-field, market-coverage, and declared-geometry
checks. Each uses the same Phase 7 snapshot and physical-evidence profile.
The Jacksonville default was also rerun after the sensitivity-output naming
fix; membership, candidate, and edge-evidence records matched the prior run
exactly when the run ID field was excluded.

## Initial reading

The default is deliberately provisional. The small similarity changes alter
Jacksonville modestly (17–18 candidates; 79–81 unassigned tracts) and Richmond
modestly (12–13 candidates; 57–59 unassigned tracts). Richmond has no
candidate currently classified as a corridor under any profile. That may be a
real structural result, or it may expose a classification or scale issue; it
must be judged from the map and evidence traces before changing the method.

The default profile is the review anchor because it is the declared shared
setting, not because its metrics automatically make it preferable. Do not tune
one market independently. A method change is eligible only if the identical
change is reviewed in both markets.

## Reviewer decision

Use the Marimo notebook to examine the default first, then the low and high
profiles. For each questionable candidate, record the candidate ID, map-based
observation, membership role, and edge/bridge evidence. Choose one of:

1. retain the shared default;
2. promote one declared shared sensitivity profile; or
3. change the shared method and rerun both markets.

The unresolved geometry limitation remains explicit: these runs use the
declared legacy cartographic tract geometry with an unknown vintage. The
pending Geography metadata promotion is still required before treating that
geometry as a fully versioned boundary product.
