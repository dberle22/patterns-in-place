# Phase 7 `k = 6` vs `k = 7` Cluster Review

*Prepared: 2026-07-01*

This note compares the two serious Sprint 2 candidates for the national tract clustering pass: `k = 6` and `k = 7`.

The goal is not to lock the final answer yet. The goal is to answer four questions:

1. Is `k = 7` meaningfully stronger than `k = 6`, or only marginally stronger?
2. Does `k = 7` reveal a real additional tract type, or mostly fragment an existing one?
3. What does the cluster spread look like nationally and across CBSAs?
4. What should the cluster names be if we keep `k = 7`?

## Bottom Line

The current evidence supports keeping `k = 7` as the leading candidate. The decision-point name set for that `k = 7` solution is now:

- `Entry-Market Neighborhoods`
- `Emerging Knowledge Districts`
- `Knowledge Corridor`
- `Established Residential`
- `Mixed-Income Middle Neighborhoods`
- `Working Neighborhoods`
- `Commercial Core / Jobs Center`

Why:

- `k = 7` is technically stronger than `k = 6` on the current fit metrics.
- The improvement is modest, not dramatic.
- The extra seventh cluster appears to extract a real knowledge / high-BA subtype rather than scrambling the entire map.
- The main problem in the current Sprint 2 output is the naming layer, not clearly the cluster count.

## Fit Comparison

### Sampled calibration (`5,000` tracts, same setup used in Sprint 2)

| `k` | Hierarchical avg silhouette | K-means avg silhouette | K-means between-SS ratio | K-means clusters under `100` |
|---|---:|---:|---:|---:|
| `5` | `0.0221` | `0.0941` | `0.2498` | `1` |
| `6` | `0.0305` | `0.1002` | `0.2871` | `1` |
| `7` | `0.0385` | `0.1025` | `0.3128` | `1` |
| `8` | `0.0412` | `0.0997` | `0.3316` | `1` |
| `9` | `0.0466` | `0.0956` | `0.3506` | `2` |
| `10` | `0.0497` | `0.0827` | `0.3679` | `2` |

Interpretation:

- `k = 7` is the best point on the current k-means silhouette criterion.
- The gain from `6 -> 7` is real but small: `0.1002 -> 0.1025`.
- The gain from `7 -> 8` disappears.
- Values above `8` keep improving Ward-style separation but weaken k-means cohesion and introduce more tiny clusters.

### Full-model fit on the national `78,199`-tract matrix

| `k` | Total within-SS | Between-SS ratio | Smallest cluster | Clusters under `500` |
|---|---:|---:|---:|---:|
| `6` | `1,239,465` | `0.280` | `70` | `1` |
| `7` | `1,196,335` | `0.305` | `69` | `1` |

Interpretation:

- `k = 7` improves full-model separation meaningfully.
- The small extreme tail cluster already exists at `k = 6`, so `7` is not uniquely creating that issue.

## National Size Distribution

### `k = 6`

| Cluster | Tracts | Share |
|---|---:|---:|
| `k6_1` | `12,169` | `15.6%` |
| `k6_2` | `7,229` | `9.2%` |
| `k6_3` | `28,633` | `36.6%` |
| `k6_4` | `70` | `0.09%` |
| `k6_5` | `20,319` | `26.0%` |
| `k6_6` | `9,779` | `12.5%` |

### `k = 7`

| Cluster | Decision-point name | Tracts | Share |
|---|---|---:|---:|
| `k7_1` | `Entry-Market Neighborhoods` | `9,243` | `11.8%` |
| `k7_2` | `Emerging Knowledge Districts` | `6,339` | `8.1%` |
| `k7_3` | `Knowledge Corridor` | `4,568` | `5.8%` |
| `k7_4` | `Established Residential` | `19,016` | `24.3%` |
| `k7_5` | `Mixed-Income Middle Neighborhoods` | `27,653` | `35.4%` |
| `k7_6` | `Working Neighborhoods` | `11,311` | `14.5%` |
| `k7_7` | `Commercial Core / Jobs Center` | `69` | `0.09%` |

Interpretation:

- The cluster-size shape is not materially worse at `7`.
- The problem is not the size distribution by itself.
- The main naming risk was concentrated in `k7_5`. That issue is now addressed by treating it as a broad middle-neighborhood cluster rather than an environmental-first tract type.

## How `k = 6` Maps To `k = 7`

This is the strongest argument for keeping `k = 7`.

The seventh cluster does not cause a total remap. Most `k = 6` clusters remain intact, and one additional knowledge-heavy subtype is pulled out of several broader groups.

### Major `k = 6 -> k = 7` transitions

| `k = 6` cluster | Main `k = 7` destination | Share of `k = 6` cluster | Secondary split |
|---|---|---:|---|
| `k6_1` | `k7_6` | `90.9%` | `7.4%` moves to `k7_3` |
| `k6_2` | `k7_2` | `86.4%` | `10.9%` moves to `k7_3` |
| `k6_3` | `k7_5` | `90.0%` | `9.9%` moves to `k7_3` |
| `k6_4` | `k7_7` | `98.6%` | no meaningful split |
| `k6_5` | `k7_4` | `93.3%` | `6.5%` moves to `k7_5` |
| `k6_6` | `k7_1` | `94.4%` | small spill to `k7_5` and `k7_6` |

Interpretation:

- `k7_7` is stable and clearly represents the national jobs-center tail.
- `k7_4` is mostly the same suburban / established-residential cluster that already exists at `k = 6`.
- `k7_1` is also mostly preserved from `k6_6`.
- The substantive change is `k7_3`, which draws a knowledge-heavy slice out of multiple broader `k = 6` clusters.

That is exactly what we would hope to see if `k = 7` is adding a real subtype rather than simply creating noise.

## Cluster Summary Stats

All metrics below are centroid means on the standardized tract KPI scale. Positive values mean above the national tract mean; negative values mean below it.

### `k = 6` key centroids

| Cluster | BA+ | Same-house | Owner-occ | Density | Walkability | Poverty | Unemployment | Jobs/resident | High-wage jobs | Pro-services jobs | EJ PM2.5 | FEMA risk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `k6_1` | `-0.71` | `0.24` | `-0.54` | `0.68` | `0.64` | `-0.37` | `0.04` | `-0.06` | `-0.45` | `-0.34` | `-1.00` | `-0.31` |
| `k6_2` | `1.00` | `-1.82` | `-1.46` | `0.81` | `1.02` | `-0.38` | `-0.91` | `0.21` | `0.50` | `0.66` | `-0.06` | `0.20` |
| `k6_3` | `0.61` | `0.20` | `0.45` | `0.20` | `0.02` | `0.58` | `-0.33` | `-0.04` | `0.14` | `0.28` | `0.08` | `0.24` |
| `k6_4` | `-0.26` | `-0.64` | `-0.21` | `-0.37` | `0.28` | `-0.20` | `-0.26` | `25.68` | `1.41` | `-0.03` | `-0.14` | `0.61` |
| `k6_5` | `-0.43` | `0.31` | `0.62` | `-1.18` | `-0.96` | `0.16` | `0.60` | `-0.07` | `0.00` | `-0.27` | `0.44` | `-0.37` |
| `k6_6` | `-0.77` | `-0.18` | `-0.85` | `0.43` | `0.38` | `-1.29` | `0.36` | `-0.02` | `-0.23` | `-0.31` | `0.14` | `0.31` |

### `k = 7` key centroids

| Cluster | Decision-point name | BA+ | Same-house | Owner-occ | Density | Walkability | Poverty | Unemployment | Jobs/resident | High-wage jobs | Pro-services jobs | EJ PM2.5 | FEMA risk |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `k7_1` | `Entry-Market Neighborhoods` | `-0.77` | `-0.17` | `-0.85` | `0.43` | `0.39` | `-1.31` | `0.37` | `-0.02` | `-0.23` | `-0.31` | `0.13` | `0.30` |
| `k7_2` | `Emerging Knowledge Districts` | `0.98` | `-1.99` | `-1.50` | `0.78` | `1.01` | `-0.48` | `-0.93` | `0.24` | `0.49` | `0.66` | `0.01` | `0.27` |
| `k7_3` | `Knowledge Corridor` | `0.85` | `0.16` | `-0.10` | `0.74` | `0.73` | `0.43` | `-0.16` | `-0.02` | `0.11` | `0.33` | `-0.86` | `-0.39` |
| `k7_4` | `Established Residential` | `-0.44` | `0.32` | `0.62` | `-1.22` | `-0.98` | `0.14` | `0.63` | `-0.07` | `0.00` | `-0.28` | `0.44` | `-0.41` |
| `k7_5` | `Mixed-Income Middle Neighborhoods` | `0.51` | `0.18` | `0.45` | `0.13` | `-0.06` | `0.56` | `-0.33` | `-0.04` | `0.12` | `0.23` | `0.17` | `0.30` |
| `k7_6` | `Working Neighborhoods` | `-0.77` | `0.22` | `-0.57` | `0.66` | `0.61` | `-0.43` | `0.04` | `-0.05` | `-0.44` | `-0.34` | `-0.92` | `-0.29` |
| `k7_7` | `Commercial Core / Jobs Center` | `-0.26` | `-0.66` | `-0.22` | `-0.38` | `0.29` | `-0.21` | `-0.26` | `25.87` | `1.41` | `-0.05` | `-0.14` | `0.60` |

## Interpreting The `k = 7` Clusters

### `k7_7` is real and stable

`k7_7` is easy:

- tiny national tail (`69` tracts)
- extreme `jobs_per_resident`
- high high-wage-job share
- everything else secondary

This is a real jobs-center / commercial-core cluster. `k = 6` already has this tail (`k6_4`), so it is not the reason to prefer one solution over the other.

### `k7_3` is the main new subtype

`k7_3` is the most important reason to keep `k = 7`.

It appears to isolate a tract type that is:

- high BA+
- dense and walkable
- not renter-dominated to the same degree as `k7_2`
- lower environmental risk than the broader middle / legacy groups
- more stable than the pure turnover-heavy urban cluster

That looks like a real subtype. It reads more like an **established knowledge corridor** than a generic “urban high-opportunity” slice.

### `k7_5` is a middle-neighborhood cluster, not an environmental cluster

This is the most important naming conclusion in the review.

The centroid does **not** support reading `k7_5` as a pure environmental cluster:

- BA+ is still above average (`0.51`)
- owner occupancy is above average (`0.45`)
- density is only mildly above average (`0.13`)
- poverty is elevated (`0.56`)
- unemployment is below average (`-0.33`)
- professional-services jobs are above average (`0.23`)
- EJ / FEMA are elevated, but not at an extreme level that justifies making them the primary identity

This looks much more like a **mixed-income middle-neighborhood** cluster with some environmental burden, not a standalone environmental type.

Environmental exposure should be treated as a modifier or overlay, not as the cluster's primary name.

## CBSA Spread

For CBSA spread checks below, “large CBSAs” means CBSAs with at least `100` tracts in the current tract frame.

### Spread summary

| Solution | Median top-zone share in large CBSAs | Average zone count in large CBSAs |
|---|---:|---:|
| `k = 6` | `48.0%` | `4.97` |
| `k = 7` | `48.6%` | `5.51` |

Interpretation:

- `k = 7` increases the average number of tract types present in larger metros.
- It does **not** materially reduce the dominance of the top zone within a metro.
- That means `k = 7` mostly adds nuance rather than flattening metro structure.

### Most concentrated large CBSAs under `k = 6`

Examples:

- McAllen-Edinburg-Mission, TX: top cluster share `96.2%`
- Visalia, CA: `96.1%`
- Brownsville-Harlingen, TX: `93.4%`
- Modesto, CA: `92.0%`
- Fresno, CA: `91.9%`

### Most mixed large CBSAs under `k = 6`

Examples:

- Killeen-Temple, TX: top cluster share `30.4%`
- Lubbock, TX: `31.7%`
- Savannah, GA: `32.1%`
- Greensboro-High Point, NC: `32.4%`
- Tucson, AZ: `34.1%`

### Most mixed large CBSAs under `k = 7`

Examples:

- Greensboro-High Point, NC: top zone share `31.9%`
- Lubbock, TX: `33.3%`
- Savannah, GA: `34.8%`
- Birmingham, AL: `34.9%`
- Houston, TX: `36.6%`
- New York, NY-NJ-PA: `37.0%`

### Current `k = 7` top-zone pattern in large CBSAs

Under the pre-decision placeholder labels:

- `Environmental Risk Zone` was top in `89` large CBSAs
- `Established Residential` was top in `22`
- `Affordable Working Class` was top in `20`
- `Growth Periphery` was top in `8`
- `Knowledge Corridor` was top in `3`

Under the decision-point names, that same broad `k7_5` dominance should be read as:

- `Mixed-Income Middle Neighborhoods` is top in `89` large CBSAs

That is much more believable and much more analytically useful than the old environmental-first interpretation.

## Naming Proposal

This second naming pass starts from a different principle than the first one:

- do not rename a cluster unless the current name is actively misleading, too vague, or materially weaker than an available alternative
- preserve names that already help the user understand the tract type quickly
- avoid names that imply a causal story we have not actually modeled
- avoid names that depend too much on one overlay dimension, like environmental burden

### What the decision-point names get right

Three of the agreed `k = 7` names are already strong and should stay as-is:

| Cluster | Agreed name | Keep? | Why |
|---|---|---|---|
| `k7_3` | `Knowledge Corridor` | Yes | The name is distinctive, memorable, and directionally consistent with the centroid: high BA+, dense, walkable, and professional-job leaning. |
| `k7_4` | `Established Residential` | Yes | This is the cleanest and most intuitive label in the current set. The centroid is stable, owner-heavy, lower-density, and more settled. |
| `k7_7` | `Commercial Core / Jobs Center` | Yes | The centroid is so extreme on `jobs_per_resident` that a jobs-center label is the obvious and best read. |

The remaining names are also defensible as a set, but some are more elegant than others:

| Cluster | Agreed name | Keep? | Why it works | What still feels imperfect |
|---|---|---|---|---|
| `k7_1` | `Entry-Market Neighborhoods` | Yes | It captures lower-cost access to the market without falsely implying classic outer-suburban growth. | It is a little market-speak-heavy and less vivid than some alternatives. |
| `k7_2` | `Emerging Knowledge Districts` | Yes | It captures both the turnover / emerging aspect and the unusually strong BA+ / professional-jobs profile. | It may still sound slightly too urban-core-specific for some metros. |
| `k7_5` | `Mixed-Income Middle Neighborhoods` | Yes | It describes a broad mixed middle cluster without overclaiming environmental or distressed identity. | It is descriptive rather than especially memorable. |
| `k7_6` | `Working Neighborhoods` | Yes | It is shorter, cleaner, and less brittle than the older class-coded label. | It is broad and may understate the cluster's affordability / immigrant / dense-urban flavor in some metros. |

### Main naming rule

Keep environmental burden as a secondary overlay, not a primary type.

That means we should stop using:

- `Environmental Risk Zone`

as a top-level cluster name.

### First-pass proposed names for `k = 7`

| Cluster | Current Sprint 2 name | Proposed review name | Why |
|---|---|---|---|
| `k7_1` | `Growth Periphery` | `Affordable Urban Periphery` | Low BA+, renter-leaning, moderate density, very low poverty, not truly outer-suburban owner-heavy periphery |
| `k7_2` | `Emerging / Transitional` | `Emerging Knowledge Districts` | Very high BA+, dense, walkable, renter-heavy, high professional-job mix, strong turnover |
| `k7_3` | `Knowledge Corridor` | `Established Knowledge Corridors` | High BA+, dense and walkable, but more stable and less renter-dominated than `k7_2` |
| `k7_4` | `Established Residential` | `Established Residential` | Still the cleanest read |
| `k7_5` | `Environmental Risk Zone` | `Legacy Mixed-Income Neighborhoods` | Broad middle / legacy cluster with some environmental burden, not an environmental-only type |
| `k7_6` | `Affordable Working Class` | `Affordable Urban Working Neighborhoods` | Low BA+, renter-leaning, dense / walkable, low-wage service mix |
| `k7_7` | `Jobs Center / Commercial Core` | `Commercial Core / Jobs Center` | Stable and obvious |

### Second-pass refined names for `k = 7`

After another pass, I think a slightly better naming set is:

| Cluster | Current Sprint 2 name | Refined proposed name | Why this is better |
|---|---|---|---|
| `k7_1` | `Growth Periphery` | `Entry-Market Neighborhoods` | This cluster is lower-BA, renter-leaning, moderate-density, and low-poverty. "Entry-market" better captures relatively attainable neighborhoods without implying greenfield suburban growth. |
| `k7_2` | `Emerging / Transitional` | `Emerging Knowledge Districts` | Keeps the dynamism of "emerging" but better reflects the very high BA+, strong walkability, renter orientation, and high professional-jobs profile. |
| `k7_3` | `Knowledge Corridor` | `Knowledge Corridor` | This is still the best name. Adding "established" makes it more precise, but the simpler base label is stronger and easier to use. |
| `k7_4` | `Established Residential` | `Established Residential` | Still the best read and the clearest label in the taxonomy. |
| `k7_5` | `Environmental Risk Zone` | `Civic Middle Neighborhoods` | This cluster reads like the broad middle of the urban system: above-average BA+, above-average owner occupancy, moderate density, elevated poverty, and mixed opportunity signals. "Civic middle" is imperfect, but it keeps the cluster broad without making it sound distressed, suburban, or environmental-first. |
| `k7_6` | `Affordable Working Class` | `Working Neighborhoods` | Shorter and cleaner. It still signals labor-market position and affordability, but avoids overspecifying class identity in a way that can feel brittle. |
| `k7_7` | `Jobs Center / Commercial Core` | `Commercial Core / Jobs Center` | No substantive change; just a slight wording preference. |

### Why these refined names are better

#### `k7_1`: `Entry-Market Neighborhoods` vs `Growth Periphery`

The case against `Growth Periphery`:

- owner occupancy is well below average
- density and walkability are above average, not edge-suburban
- the cluster does not read like classic family-oriented outer growth

The case for `Entry-Market Neighborhoods`:

- low poverty still matters
- lower BA+ and lower wage-job mix suggest more attainable neighborhoods
- the term is broad enough to cover urban fringe and lower-cost in-market neighborhoods

This is a better descriptive name, though it is less vivid than `Growth Periphery`.

#### `k7_2`: `Emerging Knowledge Districts` vs `Emerging / Transitional`

The case for changing it:

- the current name is accurate but generic
- the centroid is too knowledge-heavy to leave that unsaid

The case for the new name:

- it preserves the sense of motion and turnover
- it flags the unusually strong BA+ and professional-jobs signature
- it differentiates this cluster more clearly from `k7_3`

#### `k7_3`: keep `Knowledge Corridor`

This name should stay.

Why:

- it is memorable
- it is already established in the Phase 7 methodology language
- the centroid fits the intended concept well enough
- the simpler name is better than over-tuning it into `Established Knowledge Corridors`

The main caution is that the centroid also has elevated poverty, so the label should not be read as universally affluent. But that does not break the name.

#### `k7_5`: `Civic Middle Neighborhoods` vs `Environmental Risk Zone`

This is the hardest naming problem.

What we know it is not:

- not a pure environmental cluster
- not a pure distressed cluster
- not a pure suburban stability cluster
- not a pure working-class affordability cluster

What it does look like:

- a broad mixed middle
- somewhat civically settled
- somewhat owner-oriented
- moderate density
- elevated poverty but not collapsing labor structure
- some environmental burden that should be treated as an overlay

I do not think `Legacy Mixed-Income Neighborhoods` is bad, but it leans a little too backward-looking and rust-belt-coded. `Civic Middle Neighborhoods` is broader and more neutral, though it is also less common as a phrase.

If we want a more conventional alternative, the fallback option is:

- `Mixed-Income Middle Neighborhoods`

That may actually be the safest publishable option.

#### `k7_6`: `Working Neighborhoods` vs `Affordable Working Class`

The argument for shortening it:

- the current label is conceptually clear
- but it is a little heavy and sociologically loaded
- the centroid supports a working-neighborhood identity more than a rigid class category

`Working Neighborhoods` is cleaner, easier to say, and less brittle.

### Recommended `k = 7` name set after this pass

If I had to pick the best current set today, I would use:

| Cluster | Recommended name |
|---|---|
| `k7_1` | `Entry-Market Neighborhoods` |
| `k7_2` | `Emerging Knowledge Districts` |
| `k7_3` | `Knowledge Corridor` |
| `k7_4` | `Established Residential` |
| `k7_5` | `Mixed-Income Middle Neighborhoods` |
| `k7_6` | `Working Neighborhoods` |
| `k7_7` | `Commercial Core / Jobs Center` |

That set keeps the strongest names, improves the weakest ones, and removes the misleading environmental-first interpretation.

### Proposed names for `k = 6`

If we ultimately publish `k = 6`, the leading names would be:

| Cluster | Proposed review name | Why |
|---|---|---|
| `k6_1` | `Urban Working Neighborhoods` | Dense, walkable, renter-leaning, low poverty, lower wage mix |
| `k6_2` | `Knowledge Districts` | High BA+, walkable, renter-heavy, high pro-job content |
| `k6_3` | `Legacy Mixed-Income Neighborhoods` | Large middle cluster with moderate BA+, moderate owner occupancy, elevated poverty |
| `k6_4` | `Commercial Core / Jobs Center` | Tiny but clear jobs-center tail |
| `k6_5` | `Established Residential` | Owner-heavy, lower-density, stable |
| `k6_6` | `Affordable Urban Periphery` | Low BA+, renter-leaning, moderate density, low poverty |

## Recommendation

### Preferred path

Keep `k = 7` as the leading candidate and fix the labels.

That is the cleaner interpretation of the current evidence because:

- `k = 7` wins on the existing fit criterion
- `k = 7` improves full-model separation
- the seventh cluster is not random fragmentation
- the biggest current issue is label assignment, especially `k7_5`

### What to do next

1. Replace the current heuristic cluster names with a manual review name map.
2. Move environmental burden into an overlay flag or a secondary descriptor rather than a top-level cluster type.
3. Add spread review tables to the Phase 7 notebook:
   - national cluster distribution
   - CBSA cluster spread
   - `k = 6` to `k = 7` crosswalk
4. Only revert to `k = 6` if the manually relabeled `k = 7` solution still fails to produce a substantively clearer taxonomy.

## Practical conclusion

Right now the case is:

- `k = 7` is the better model candidate
- the agreed decision-point name set is:
  - `Entry-Market Neighborhoods`
  - `Emerging Knowledge Districts`
  - `Knowledge Corridor`
  - `Established Residential`
  - `Mixed-Income Middle Neighborhoods`
  - `Working Neighborhoods`
  - `Commercial Core / Jobs Center`
- the next bottleneck is interpretive review and cluster profiling, not cluster-count reduction
