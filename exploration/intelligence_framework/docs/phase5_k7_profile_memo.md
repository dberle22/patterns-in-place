# Phase 5 `k = 7` Review Memo

## Goal

Assess whether the revised Phase 5 cross-frame model remains defensible at `k = 7` after the Livability AQI swap to `aqi_median`, and propose a first-pass semantic label mapping for the seven-cluster solution.

## Bottom Line

`k = 7` is statistically defensible.

It is not the cleanest solution in the revised run, but it is a credible compromise if we want to preserve more nuance than `k = 4` without defaulting back to the current `k = 6` purely for continuity.

The strongest case for `k = 7` is that it surfaces one real extra type that is substantively interpretable rather than purely noise:

- a `9`-metro elite knowledge / global gateway cluster that does not exist cleanly in the `k = 6` solution

The main caution is that `k = 7` introduces one sub-10 cluster, so it is more segmented and slightly less clean than `k = 4`.

## Statistical Read

For the revised `moderate_35_kpi_set`:

| k | k-means avg silhouette | k-means median silhouette | k-means min cluster | k-means clusters under 10 | betweenss ratio |
|---|---:|---:|---:|---:|---:|
| `4` | `0.0949` | `0.0899` | `45` | `0` | `0.1999` |
| `6` | `0.0907` | `0.0951` | `21` | `0` | `0.2666` |
| `7` | `0.0935` | `0.0923` | `9` | `1` | `0.2947` |

### Why `k = 7` is defensible

- Its k-means average silhouette is meaningfully better than `k = 6`.
- Its betweenss ratio is the strongest of the three, which means the clusters are more separated in the feature space.
- It does not create singletons.
- The smallest cluster is `9` metros, which is small but still interpretable at a national typology level.

### Why `k = 7` is not an automatic choice

- `k = 4` still has the best average silhouette.
- `k = 7` introduces one niche cluster, so it is less tidy than `k = 4`.
- Hierarchical support is not especially strong, so the case for `k = 7` rests more on interpretability and k-means separation than on unanimous calibration evidence.

## Recommended Interpretation

If the design goal is:

- **cleanest cross-frame structure**: prefer `k = 4`
- **continuity with the current published system**: prefer `k = 6`
- **more explainable nuance without obvious over-fragmentation**: `k = 7` is a valid choice

Given the stated concern that `k = 4` compresses away too much of the story, `k = 7` is a reasonable alternative to carry forward for semantic review.

## Proposed `k = 7` Label Mapping

These labels are based on the temporary revised `k = 7` run in `phase_5_cross_frame_integration/outputs_aqi_median_review_k7_tmp/`.

### Cluster 1

- Size: `22`
- Frame profile: `Character 20.9`, `Livability 18.3`, `Opportunity 22.1`
- Representative metros:
  - `Fresno, CA`
  - `Modesto, CA`
  - `Bakersfield-Delano, CA`
  - `Salinas, CA`
  - `Yakima, WA`
  - `Visalia, CA`
  - `Yuba City, CA`
  - `Corpus Christi, TX`
- Proposed label: `Entrepreneurial Strain Markets`

Why:
- This is the clearest low-performing combined cluster.
- It keeps the same broad strain-heavy inland / agricultural / lower-opportunity shape as the current interpretation.

### Cluster 2

- Size: `78`
- Frame profile: `Character 79.4`, `Livability 73.3`, `Opportunity 59.4`
- Representative metros:
  - `Columbia, MO`
  - `Harrisburg-Carlisle, PA`
  - `Portland-Vancouver-Hillsboro, OR-WA`
  - `Allentown-Bethlehem-Easton, PA-NJ`
  - `Syracuse, NY`
  - `Rochester, NY`
  - `Olympia-Lacey-Tumwater, WA`
  - `Lansing-East Lansing, MI`
- Proposed label: `High-Amenity Knowledge Civics`

Why:
- This is the strongest broad high-character / high-livability cluster outside the elite gateway group.
- It looks like the most direct home for the current knowledge-civics concept.

### Cluster 3

- Size: `121`
- Frame profile: `Character 37.6`, `Livability 55.7`, `Opportunity 37.8`
- Representative metros:
  - `Canton-Massillon, OH`
  - `Akron, OH`
  - `York-Hanover, PA`
  - `Peoria, IL`
  - `Cleveland, OH`
  - `Dayton-Kettering-Beavercreek, OH`
  - `Fort Wayne, IN`
  - `Hermitage, PA`
- Proposed label: `Stable Affordable Heartland Markets`

Why:
- This is the clearest livability-leading, interior, steadier-market cluster.
- It preserves the old heartland / affordability concept more cleanly than the revised `k = 6` run does.

### Cluster 4

- Size: `60`
- Frame profile: `Character 29.7`, `Livability 20.0`, `Opportunity 30.5`
- Representative metros:
  - `Columbia, SC`
  - `Dothan, AL`
  - `Birmingham, AL`
  - `Augusta-Richmond County, GA-SC`
  - `Hattiesburg, MS`
  - `Gulfport-Biloxi, MS`
  - `Mobile, AL`
  - `Virginia Beach-Chesapeake-Norfolk, VA-NC`
- Proposed label: `Inland Strain Corridors`

Why:
- Despite some coastal metros, the feature profile is still more strain-heavy than growth-led.
- The top feature mix includes firearm fatality, uninsured adults, and weaker labor-market texture, which reads more like structural strain than like an amenity-growth story.

### Cluster 5

- Size: `9`
- Frame profile: `Character 98.1`, `Livability 77.1`, `Opportunity 90.0`
- Representative metros:
  - `Boston-Cambridge-Newton, MA-NH`
  - `Washington-Arlington-Alexandria, DC-VA-MD-WV`
  - `San Francisco-Oakland-Fremont, CA`
  - `Seattle-Tacoma-Bellevue, WA`
  - `Chicago-Naperville-Elgin, IL-IN`
  - `Los Angeles-Long Beach-Anaheim, CA`
  - `San Jose-Sunnyvale-Santa Clara, CA`
  - `Urban Honolulu, HI`
- Proposed label: `Global Knowledge Gateways`

Why:
- This is the main reason `k = 7` is interesting.
- It is not just another high-amenity cluster; it is a concentrated elite national tier with extreme knowledge, migration, and information-economy signals.

### Cluster 6

- Size: `37`
- Frame profile: `Character 57.2`, `Livability 45.9`, `Opportunity 62.8`
- Representative metros:
  - `Deltona-Daytona Beach-Ormond Beach, FL`
  - `Pinehurst-Southern Pines, NC`
  - `Palm Bay-Melbourne-Titusville, FL`
  - `Port St. Lucie, FL`
  - `Asheville, NC`
  - `Panama City-Panama City Beach, FL`
  - `Sebastian-Vero Beach-West Vero Corridor, FL`
  - `Wilmington, NC`
- Proposed label: `Aging Amenity Expansion Markets`

Why:
- Older age structure, vacancy, permit activity, and amenity-heavy Sun Belt / coastal reps fit this label well.
- This cluster is the clearest amenity / retirement-growth segment in the `k = 7` run.

### Cluster 7

- Size: `69`
- Frame profile: `Character 55.3`, `Livability 48.5`, `Opportunity 74.7`
- Representative metros:
  - `Charlotte-Concord-Gastonia, NC-SC`
  - `Reno, NV`
  - `Indianapolis-Carmel-Greenwood, IN`
  - `Kansas City, MO-KS`
  - `Oklahoma City, OK`
  - `Omaha, NE-IA`
  - `Jacksonville, FL`
  - `Charleston-North Charleston, SC`
- Proposed label: `Sun Belt Opportunity Engines`

Why:
- This is the strongest broad opportunity-led growth cluster that is not part of the elite gateway group.
- It preserves the existing opportunity-engine idea with more interpretable membership than the revised `k = 6` labeling.

## First-Pass Mapping Summary

| `k = 7` cluster | Proposed label |
|---|---|
| `1` | `Entrepreneurial Strain Markets` |
| `2` | `High-Amenity Knowledge Civics` |
| `3` | `Stable Affordable Heartland Markets` |
| `4` | `Inland Strain Corridors` |
| `5` | `Global Knowledge Gateways` |
| `6` | `Aging Amenity Expansion Markets` |
| `7` | `Sun Belt Opportunity Engines` |

## Recommendation

If we want to maximize stability and minimize follow-on documentation churn, keep revised Phase 5 at `k = 6`.

If we want the revised model to recover more interpretable nuance after the AQI swap, `k = 7` is defensible enough to promote into a serious candidate. The strongest argument for doing so is the emergence of the separate `Global Knowledge Gateways` cluster, which looks real rather than accidental.
