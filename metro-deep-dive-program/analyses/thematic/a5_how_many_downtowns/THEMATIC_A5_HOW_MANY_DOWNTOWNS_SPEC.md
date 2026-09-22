# Thematic A5 — How Many Downtowns Spec

**Status:** Provisional; revise after Epic 1 audit

**Updated:** 2026-09-20

**Family plan:** [THEMATIC_ANALYSES_PLAN.md](../THEMATIC_ANALYSES_PLAN.md)

## 1. Question and purpose

Are metros monocentric, polycentric, or dispersed, and how do employment
structure and housing context differ across those forms?

“Downtown” is the reader-facing hook. The method must define observable
employment centers and subcenters without assuming that every dense job cluster
is a culturally recognized downtown.

**Themes crossed:** Work Geography × Housing & Affordability.

## 2. Provisional claim and alternatives

**Claim direction to review:** U.S. metros differ systematically in the number,
dominance, and spatial distribution of employment centers, and those structures
are associated with different housing and access patterns.

The claim is weakened if center counts are unstable under reasonable density,
employment-floor, tract-size, or adjacency choices, or if the resulting
typology mostly reproduces metro size.

## 3. Analytical unit and universe

- Native input: tract within CBSA, using a declared 2023 LODES WAC surface.
- National result: one or more center-structure measures per covered CBSA.
- Housing/access context: governed tract or CBSA measures aligned without
  redefining the center itself after seeing outcomes.
- Market result: selected CBSA with center membership, hierarchy, component
  evidence, and sensitivity.

The initial analysis is a current structural cross-section. Historical change
requires a managed multi-year workplace panel and is not implied by v0.

## 4. Notebook contracts

### National notebook

The national notebook should:

1. define job density, minimum scale, adjacency, center membership, and center
   dominance
2. distinguish a dominant core, major subcenter, smaller center, and dispersed
   employment only if the evidence supports those categories
3. show center-count and concentration distributions nationally
4. test sensitivity to tract area, metro size, thresholds, and boundary effects
5. relate reviewed center structure to industry and housing context
6. separate method validation from editorial downtown naming
7. identify representative and counterexample metros

### Parameterized market notebook

The market notebook should:

- map and rank the selected CBSA’s identified centers
- show employment scale, density, industry mix, and dominance
- add housing and access context around centers using governed measures
- compare the market’s structure with national, division, and peer results
- expose alternative-threshold results so fragile centers are visible
- distinguish formal Places/local names from analytical center boundaries
- support a dispersed or indeterminate result

## 5. Current repository assets

- 2023 tract LODES WAC/RAC and Gold LODES summaries
- Industry Explorer D2/D3 job-center logic and shortlist prior art
- Explanation Q2 job-center method work and Q6 polycentricity planning
- Position/Internal Structure plans
- Geography tract, Place, CBSA, and display interfaces
- tract housing and transport/built-form context
- POI and Infrastructure governed handoffs as optional interpretation inputs

## 6. Audit findings to verify

- Current LODES supports a static national center analysis but not center change
  over time.
- Existing job-center logic was designed for a market workbench and must be
  tested nationally before reuse.
- Tract size varies dramatically and can distort raw density and adjacency.
- CBSA boundaries can split real labor-market structures or include remote
  areas; boundary sensitivity needs review.
- Q2’s proximity center and A5’s structural center may overlap without being
  identical contracts.
- Place, neighborhood, and editorial downtown labels are context, not method
  truth.

## 7. Provisional outputs

- tract center-membership and center-summary tables
- CBSA center count, dominance, concentration, and dispersion measures
- national typology and threshold sensitivity, only if stable
- selected-market center map, ranking, housing/access context, and caveats
- finding ledger with fragile classifications identified

## 8. Decisions Epic 1 must prepare

- center seed, density, scale, and adjacency rules
- tract area and zero/low-population treatment
- CBSA boundary and edge handling
- center hierarchy and dominance measures
- whether center count or continuous structure measures should lead
- relationship to Q2/Q6 and Industry D3 outputs
- housing/access context measures that do not leak into center construction
- naming and issue-handoff rules

## 9. Non-goals

- assigning official or editorial downtown names nationally
- claiming center growth or decline from 2023 data alone
- treating WAC/RAC balance as an origin-destination flow
- reviving Corridor Intelligence as a required dependency
- building a universal walkability or investment score

