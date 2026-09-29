# Q4 Amenity-Hub Candidate Method Record

**Method version:** `q4_amenity_hub_grid_v1`  
**Built:** 2026-09-22  
**Promotion status:** `grid_250m_min_20` is selected for the first Q4
workbench review; `grid_500m_min_60` remains a retained sensitivity. Neither
is a basket-specific or cross-analysis promoted classification.

## Candidate universe

All retained POIs with `mapping_status = 'mapped'` are included. Epic 2 has
not yet declared broad-livability or errands/essentials baskets, so this is a
spatial inventory candidate rather than a basket-specific livability result.
Unmapped POIs are excluded from membership but remain a documented coverage state.

## Construction

Each point is projected into the market's declared local CRS and assigned to a
square cell. A cell qualifies only when it meets the version's POI count. Only
qualifying cells that share an edge join one hub; diagonal contact never joins
a hub. Hub geometry is the union of qualifying cells. This is a reviewable
density construction, not a route, travel-time, barrier, or resident-access model.

| Candidate version | Cell size | Minimum POIs/cell | Role |
|---|---:|---:|---|
| `grid_250m_min_20` | 250 m | 20 | recommended for first review |
| `grid_500m_min_60` | 500 m | 60 | compact sensitivity |

## Inputs

- `40060`: `metro-deep-dive-program/engines/poi/outputs/richmond_va/overture-places-40060-2026-08-19-0-20260908T110747Z`
- `27260`: `metro-deep-dive-program/engines/poi/outputs/jacksonville_fl/overture-places-27260-2026-08-19-0-20260909T093431Z`

## Observed candidate counts

| Market | Version | Hubs | Member POIs |
|---|---|---:|---:|
| jacksonville_fl | `grid_250m_min_20` | 436 | 40,474 |
| jacksonville_fl | `grid_500m_min_60` | 157 | 34,285 |
| richmond_va | `grid_250m_min_20` | 286 | 26,493 |
| richmond_va | `grid_500m_min_60` | 93 | 22,512 |

## Required review

- inspect membership and category mix for fragmented hubs and implausible bridges;
- compare both sensitivity versions before treating the selected workbench
  candidate as stable;
- replace the all-mapped universe with declared basket variants in later work; and
- keep Infrastructure as map context only until a separate barrier/network method exists.
