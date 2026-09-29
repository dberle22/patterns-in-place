# Q6 One Metro? — Epic 5 Review

**Reviewed:** 2026-09-23  
**Method:** `q6_one_metro_v1`  
**Purpose:** Calibrate Q6's Place-based anchor read. This is not a national
metro ranking or an editorial conclusion.

## Cases

| Case | Initial result | Why it is useful |
|---|---|---|
| Richmond, VA (`40060`) | `mixed` | The initial 5,000-resident / 1%-of-CBSA rule identifies three distinct reviewed Q2 components, but a higher materiality sensitivity leaves one. The method must preserve that ambiguity. |
| Harrisonburg, VA (`25500`) | `one supported anchor` | One material Place, Harrisonburg city, is associated with one reviewed Q2 component under the initial, lower, and higher materiality rules. |

The comparison demonstrates that Q6 can distinguish a stable one-anchor case
from a case whose number of supported anchors depends on the declared
materiality rule. It does not establish that every multiple-component metro is
polycentric in an editorial or functional-integration sense.

## Materiality sensitivity

| Rule | Richmond candidates / components | Harrisonburg candidates / components |
|---|---:|---:|
| 2,500 residents and 0.5% of CBSA population | 6 / 6 | 1 / 1 |
| 5,000 residents and 1% of CBSA population (initial) | 3 / 3 | 1 / 1 |
| 10,000 residents and 2% of CBSA population | 1 / 1 | 1 / 1 |

Richmond therefore remains `mixed` in the decision matrix. Its initial
candidates are Richmond city, Colonial Heights city, and Bon Air CDP, each
associated with a different reviewed Q2 component. The result is transparent
about materiality sensitivity rather than selecting a preferred answer.

## Q2 handoff

- Q6 reuses Q2's center components and all published distance versions; it does
  not recreate center selection.
- Richmond has visible distance sensitivity across Q2 center versions. Q6's
  result remains dependent on the Place materiality rule as well, so physical
  proximity should stay a contextual evidence layer rather than a definitive
  center or integration claim.
- The Place-to-component association is a population-weighted tract allocation,
  not membership inferred from display geometry.

## A5 reuse

A5 "How many downtowns?" can reuse the Q6 candidate-evidence table, reviewed
Q2 component inventory, declared materiality sensitivity, and the distinction
between `multiple supported anchors` and `mixed`. It must not reuse the result
as a downtown count: Q6 measures Census Place anchor evidence, while A5 has a
separate downtown/thematic interpretation task.

## Relationship-evidence review

- Q6 now reads direct POI-to-Place assignments and retained-feature
  Infrastructure overlaps as separate context tables. POI `no_census_place`
  remains a coverage outcome; Infrastructure line length and surface area
  remain separate measures.
- Q6 reads directional home-Place → work-Place LODES OD `JT00` links as a
  ranked table, with source coverage and endpoint statuses visible before any
  map. `JT02` is a subset of `JT00` and is not added to it.
- None of these layers is an input to the anchor decision matrix.

## Publication posture

The Q6 result is suitable for analyst review: Harrisonburg is a stable
one-supported-anchor case; Richmond is a materially sensitive mixed case. The
next issue-layer workflow must retain the result and caveats rather than
collapsing Richmond to a single editorial answer.
