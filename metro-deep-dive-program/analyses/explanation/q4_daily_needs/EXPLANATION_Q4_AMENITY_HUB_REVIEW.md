# Q4 Amenity-Hub Candidate Review

**Method version:** `q4_amenity_hub_grid_v1`  
**Reviewed:** 2026-09-22  
**Reviewer:** Codex preliminary method review

## Decision

Select `grid_250m_min_20` as the first POI-density workbench candidate for
Richmond and Jacksonville. Retain `grid_500m_min_60` as its sensitivity. This
is a review-workbench selection only: it is not a universal amenity-hub
classification, a basket-specific result, or a resident-access claim.

## What was reviewed

Both candidates use retained mapped POIs, projected local coordinates, a
qualifying-cell density screen, and shared-edge-only cell components. The
review checked membership reconciliation, category-mix surfaces, candidate
scale, and cluster fragmentation. SVG maps are included for the next visual
domain review.

| Market | Candidate | Hubs | Member POIs | Median POIs/hub | Largest hub | Largest area |
|---|---|---:|---:|---:|---:|---:|
| Richmond | `grid_250m_min_20` | 286 | 26,493 | 39 | 3,984 | 3.56 km² |
| Richmond | `grid_500m_min_60` | 93 | 22,512 | 123 | 4,199 | 4.50 km² |
| Jacksonville | `grid_250m_min_20` | 436 | 40,474 | 40 | 1,552 | 2.06 km² |
| Jacksonville | `grid_500m_min_60` | 157 | 34,285 | 102 | 3,089 | 4.00 km² |

The 250 m candidate preserves smaller, clearly localized concentrations while
keeping the largest components bounded. The 500 m sensitivity is useful for
testing consolidation, but its larger components should not replace the
selected workbench candidate without a declared basket and further domain
review.

## Review limitations

- The candidate universe is all retained mapped POIs because Epic 2 has not yet
  declared broad-livability or errands/essentials baskets. These results show
  general POI concentration, not yet the composition of a specific basket.
- Unmapped POIs remain a coverage limitation; they are not evidence of an area
  having no amenities.
- Infrastructure was not used to split, merge, or rank hubs. The available
  engine contract does not support a barrier or routing conclusion.
- Tract demographics were not used to construct hubs. Cluster context and
  typologies remain Epic 4 work.

## Review artifacts

The output directory contains map-ready candidate geometry, POI membership,
category mix, SVG review maps, checksums, and the construction record:
`outputs/q4_amenity_hub_grid_v1/`.
