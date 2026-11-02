# Intelligence Framework Rerun After the IRS Direction Fix: Review

**Status:** Done
**Updated:** 2026-10-26

Character (Phase 2), Opportunity (Phase 4), cross-frame (Phase 5) and the trajectory engine, rerun on the corrected IRS migration data and compared with a control run on the reversed values. Spec: [IRS_MIGRATION_DIRECTION_FIX_SPEC.md](../../foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md), Part B.

Nothing was promoted. No loader was run, and `mart_intelligence` is untouched.

> **Outcome, 2026-10-26 (Dan):** promoted the IRS fix alone. Opportunity, cross-frame and the engine were rerun with the GDP inputs held at their June values (`*_gdp_frozen`; the GDP-frozen control runs reproduce every current mart exactly), and published names were carried forward by cluster ID. The GDP refresh goes to a broader GDP and clustering refresh (`foundations/ROADMAP.md`). Comparison of the promoted runs: [irs_fix_rerun_2026-10/compare_gdp_frozen/](irs_fix_rerun_2026-10/compare_gdp_frozen/). The findings below are the original review.

## Recommendation: promote, with two decisions first

The fix behaves as the spec predicted. **Cluster memberships and peers don't move at all** (100% in every frame, for all three clustering methods), and scores move where migration matters. On that test, it's a promote.

Two things stop me loading the outputs as they stand:

1. **The automatic namers would put the wrong names on unchanged clusters.** Opportunity and cross-frame names are assigned by rules on cluster averages ("highest Opportunity score is Superstar"), and the corrected migration data changes those averages. On the fixed run, the cluster of New York, Los Angeles, Chicago, DC, Boston, San Francisco and Seattle would be called **Emerging Momentum Markets**, and Dallas, Phoenix, Tampa and Denver would be **Superstar Knowledge Capitals**. Cross-frame swaps Sun Belt Opportunity Engines and Aging Amenity Expansion Markets the same way. Proposed fix: **carry the published names forward by membership** (the map below; the match is unambiguous). The [Phase 7 labor-fix review](phase_7_zone_methodology/PHASE7_LABOR_FIX_RERUN_REVIEW.md) found the same weakness in the zone labeler and recommended a fixed name map, so this could be done once for all three namers. Renaming is out of this spec's scope, so it's Dan's call.
2. **A GDP refresh would ride along.** The control run did not reproduce the current Opportunity, cross-frame and trajectory marts, because BEA county GDP now runs to 2024 (see below). Promoting the fixed outputs also promotes that refresh. It moves about 16% of Opportunity memberships and 10% of cross-frame memberships, which is far more than the IRS fix does (0%), and nobody has reviewed it. Options: (a) promote it with this fix and review it here, or (b) rerun Phases 4 and 5 and the engine with the GDP inputs frozen at the June values, promote only the IRS fix, and take the GDP refresh as its own change.

My suggestion: (b), plus the name map. That keeps this change to "the migration sign is now right", and gives the GDP refresh a review of its own.

## Run setup

| Run | Code | IRS inputs | Everything else | Outputs |
|---|---|---|---|---|
| control | current | before snapshot of `gold.migration_wide` (reversed) | current gold | `<phase>/outputs_irs_fix_2026-10/control/` |
| fixed | current | current gold (fixed) | current gold | `<phase>/outputs_irs_fix_2026-10/fixed/` |

- Phases 2, 4 and 5: [irs_fix_rerun_phase.R](irs_fix_rerun_2026-10/irs_fix_rerun_phase.R) runs one phase in one mode, redirecting the output folder and (in control mode) the IRS pulls, without editing phase code. Phase 5 reads the Phase 2 and Phase 4 outputs from the same mode, and the canonical Phase 3 outputs.
- Trajectory: [irs_fix_rerun_engine.py](../../metro-deep-dive-program/engines/time_series/irs_fix_rerun_engine.py) runs the time-series engine read-only and writes its four tables to Parquet. **The engine, not `phase_6_trajectory/`, builds the `intelligence_trajectory_*` marts**; its NOTES record the Phase 6 R code as legacy evidence. So the engine is what was rerun.
- Comparison: [irs_fix_rerun_compare.py](irs_fix_rerun_2026-10/irs_fix_rerun_compare.py); detail tables in [irs_fix_rerun_2026-10/compare/](irs_fix_rerun_2026-10/compare/).

## Control reproduction

| Frame | Control vs current mart | Why |
|---|---|---|
| Character | **pass**: all 114 shared columns identical | |
| Opportunity | **fail** | `productivity_growth_5yr`, `industry_concentration_hhi`, `pct_real_gdp_information` |
| Cross-frame | **fail** | follows Opportunity |
| Trajectory | **fail**: 4,652 series rows | `industry_concentration_hhi`, `pct_real_gdp_information` only; the IRS series are identical |

The three Opportunity inputs come from `gold.economics_industry_wide`, which now takes BEA CAGDP2 county GDP through 2024 (the 2026-02-05 vintage). The June run used 2023. Each phase takes a metro's latest non-null year, so 386 metros moved from 2023 to 2024 values, and a few now fall back to 2017 or 2020. Correlation with the old values is 0.78 (productivity growth), 0.98 (HHI) and 0.995 (information share). The refresh also revised history, which is what moves the trajectory series.

None of this involves IRS, and control and fixed share it, so **control vs fixed still isolates the IRS fix.**

## Clusters

| Frame | Method | Agreement | k |
|---|---|---|---|
| Character | hclust, k-means, GMM | 100% | 7 → 7 |
| Opportunity | hclust, k-means, GMM | 100% | 6 → 6 |
| Cross-frame | hclust, k-means, GMM | 100% | 7 → 7 |

Standardizing turns the sign flip into an exact negation of one column per IRS metric. That leaves distances, seeds and median imputation unchanged, as the spec predicted.

**Names.** Character names come from a fixed map by cluster ID, so they're unchanged. The Opportunity and cross-frame namers are rule-based and move:

| Frame | Cluster (members) | Control name | Fixed run name | Proposed |
|---|---|---|---|---|
| Opportunity | 5 (9: New York, Los Angeles, Chicago, DC, Boston, San Francisco, Seattle…) | Superstar Knowledge Capitals | Emerging Momentum Markets | **Superstar Knowledge Capitals** |
| Opportunity | 6 (67: Dallas, Miami, Phoenix, Tampa, Denver, Orlando, Charlotte…) | Broad-Based Opportunity Hubs | Superstar Knowledge Capitals | **Emerging Momentum Markets** |
| Opportunity | 2 (133: Houston, Philadelphia, Atlanta, Detroit, Minneapolis, San Diego, Albany…) | Emerging Momentum Markets | Broad-Based Opportunity Hubs | **Broad-Based Opportunity Hubs** |
| Cross-frame | 2 (93: Dallas, Houston, Atlanta, Miami, Phoenix, Detroit…) | Sun Belt Opportunity Engines | Aging Amenity Expansion Markets | **Sun Belt Opportunity Engines** |
| Cross-frame | 6 (33: Sarasota, Cape Coral, Daytona, Port St. Lucie, Asheville, Ocala…) | Aging Amenity Expansion Markets | Sun Belt Opportunity Engines | **Aging Amenity Expansion Markets** |

The "Proposed" column is the published name of the matching current-mart cluster (best match: 119 of 133 for Broad-Based, 51 of 67 for Emerging Momentum, 9 of 9 for Superstar, 68 of 93 for Sun Belt, 33 of 33 for Aging Amenity). Read the right way round, it also fits the descriptions better: Emerging Momentum is "fast-growing … population, income and business-formation momentum", which is the Sun Belt cluster that gains migrants.

Why the rules flip: the 9 superstar metros lose domestic migrants. Read correctly, their average Opportunity percentile falls from 96 to 75, and the "highest Opportunity score" rule moves to the Sun Belt cluster (85). The cross-frame "Sun Belt" rule is "highest Opportunity percentile among the remaining clusters", and the Florida retirement cluster's Opportunity percentile rises from 62 to 77.

The automatic "Type N: … strength, … drag" labels also change (Opportunity 49% agreement, cross-frame 92%), because subject-score rankings move within clusters.

## Peers

| Frame | Ordered top-10 unchanged | Same peer set | Max similarity change |
|---|---|---|---|
| Character | 100% | 100% | 0 |
| Opportunity | 100% | 100% | 0 |
| Cross-frame | 100% | 100% | 0 |

**Albany (10580)** keeps every peer list. Its top three: Character Madison, Bloomington IL, Lincoln; Opportunity Poughkeepsie-Newburgh, Buffalo, Louisville; cross-frame Buffalo, Worcester, Providence.

## Cluster descriptions

The extreme-metric profiles (top and bottom metrics per cluster) change wherever an IRS metric is near the edge, because its sign flips. Ten Opportunity lists and four Character lists change (`compare/cluster_extremes.csv`). The ones that touch a name:

- **Character cluster 1, Retirement And Lifestyle Havens:** `irs_net_migration_rate` moves from its bottom list to its top list. Read correctly, these metros are strong net in-migration destinations, which fits "migration-driven" in the README. The interpretation text ("lower civic-mobility churn") is worth a reread.
- **Character cluster 2, Global Knowledge Capitals,** and **cluster 4, College And Civic Anchors:** `irs_net_migration_rate` enters their bottom lists. Both names still hold, but both are now net domestic out-migration profiles.
- **Opportunity cluster 5 (superstars):** both IRS metrics move into the bottom list. The written interpretation ("strong overall opportunity despite thinner near-term housing appreciation") should mention net out-migration.
- **Opportunity cluster 6 (Sun Belt):** `irs_net_migration_rate` enters the top list, which supports "Emerging Momentum" for this cluster.
- **Cross-frame cluster 3:** one extreme-metric swap (`hpi_5yr_pct` out, `permits_share_units_5_plus` in); its name (Global Knowledge Gateways) is unaffected.

## Scores

Percentile points, control → fixed, across 396 metros:

| Score | Median change | Moving > 10 pts | Max | Albany |
|---|---|---|---|---|
| `character_percentile` | 2.5 | 4.8% | 31 | 88.4 → 88.4 |
| `opportunity_percentile` | 2.8 | 13.4% | 61 | 73.7 → 73.9 |
| `cross_frame_percentile` | 0.5 | 1.8% | 29 | 87.6 → 90.6 |
| Character topic: residential stability | 15.2 | 69% | 99 | 40 → 42 |
| Opportunity topic: migration and wealth flows | 50.0 | 90% | 100 | 38 → 62 |
| Opportunity subject: market opportunity | 7.5 | 40% | 100 | 66 → 67 |

(Topic and subject scores are compared as rank percentiles.)

Biggest movers (full top 20 each way in `compare/score_movers.csv`):

- **Opportunity up:** Wildwood 21 → 74, Lakeland 47 → 85, Punta Gorda 36 → 72, Cape Coral 40 → 76, Lake Havasu City 33 → 65, Ocala 57 → 85, Prescott Valley 54 → 82, Naples 60 → 87
- **Opportunity down:** New York 99 → 38, Chicago 86 → 29, Los Angeles 95 → 59, Detroit 69 → 47, Champaign 65 → 44, Washington 91 → 71, Ithaca 82 → 63, Ann Arbor 84 → 67
- **Character up:** Myrtle Beach 37 → 68, Seaford 47 → 73, Wildwood 63 → 89, Lakeland 8 → 32, Port St. Lucie 53 → 76
- **Character down:** Mankato 70 → 59, Manhattan KS 86 → 76, San Angelo 36 → 27, Detroit 60 → 51, Syracuse 66 → 58
- **Cross-frame:** El Centro 100 → 71, Hammond 98 → 71, El Paso 98 → 73, Kankakee 81 → 54 down; Akron 81 → 94, Homosassa Springs 85 → 94 up

This is the direction you'd expect: Florida and Arizona destination metros were being scored down for gaining migrants, and the big coastal metros were being scored up for losing them.

## Trajectory

**No change.** All five IRS registry entries (Character `irs_net_migration_rate`; Opportunity `irs_net_migration_rate_opportunity` and `irs_net_agi`, five-year and one-year) are `insufficient_history` for all 396 metros. IRS data stops at 2022, and the engine's common end vintage is 2023 (the engine NOTES already record this). They feed no momentum score, label, tier or turn signal:

- Frame labels, directions and tiers: 0 changes in every frame and window
- Turn signals: 0 changes
- Non-IRS metric rows: 0 changes

The only difference after a rebuild is that the IRS rows in `intelligence_trajectory_series` carry the corrected raw values for 2018–2022. The engine rebuild would, however, publish the GDP refresh (decision 2): 4,652 series rows across two GDP metrics, and the frame scores that use them.

## Not rerun

- **Phase 3 Livability:** no IRS input; the canonical outputs are reused.
- **`phase_6_trajectory/`:** legacy; it doesn't feed the marts (see Run setup).

## Next step (Part C)

Once Dan decides on names and GDP: if needed, rerun with GDP frozen and apply the name map. Then copy the approved outputs into each phase's `outputs/`, run `load_character_scores.R`, `load_opportunity_scores.R`, `load_cross_frame_scores.R` and `build_time_series_engine.py`, and continue with spec step 12.
