# Future Release Notes

This is a short decision register for problems and opportunities found while preparing a
release. It records the next useful investigation, not an event-by-event project history.

## Open investigations

| Topic | What we observed | Why it matters | Next review | Current v1 treatment |
| --- | --- | --- | --- | --- |
| BEA professional GDP share coverage | 334–471 populated CBSAs annually, despite professional activity being a major sector. | Analysts could mistake the field for a near-universal CBSA measure. | Trace CAGDP9 lines 60, 64, and 65 from raw county inputs through suppression handling and county-to-CBSA aggregation; compare each component's coverage and determine whether all-component completeness is unnecessarily restrictive. | Publish as optional with explicit coverage; do not feature it. |
| BEA education/health GDP share coverage | 671–801 populated CBSAs annually. | Coverage is better than professional GDP but still materially below the 935-CBSA universe. | Trace CAGDP9 line 68 through the same source-to-aggregation path and document the specific missingness mechanism. | Publish as optional with explicit coverage; do not feature it. |
| BEA GDP industry HHI | Only 147 CBSAs are populated in 2024. | A concentration headline would be systematically selective. | Reassess only after the sector-coverage review establishes a defensible missing-data policy. | Deferred from v1. |

## Candidate additions after v1 feedback

- BFS, CBP, and QCEW: add only when a demonstrated user need justifies their separate source
  contracts and documentation.
- HUD CHAS, permits, vacancy, and occupancy: consider only with clear handling for their
  coverage and cadence differences.
- A future delineation vintage: publish as a new static crosswalk version, never as a silent
  overwrite of the 2023 lookup.
