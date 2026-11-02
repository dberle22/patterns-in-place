# Phase 7 Rerun After the ACS Labor Fix: Review

**Status:** Done
**Updated:** 2026-10-23

The Phase 7 national tract clusters, rerun on the corrected tract unemployment rate and compared with a control run on the pre-fix inputs. Spec: [PHASE7_LABOR_FIX_RERUN_SPEC.md](PHASE7_LABOR_FIX_RERUN_SPEC.md). Upstream fix: [ACS_LABOR_B23025_FIX_SPEC.md](../../../foundations/etl/ACS_LABOR_B23025_FIX_SPEC.md).

Nothing was promoted. `mart_intelligence.intelligence_zones` and `intelligence_zones_zcta` are untouched.

## Recommendation: hold

k = 7 survives, and five of the seven clusters come through almost unchanged. The two knowledge clusters do not: they reorganise around a different idea. The automatic labeler also breaks on the fixed run. It leaves the largest cluster without a name and moves "Mixed-Income Middle" onto the old Entry-Market cluster.

Promoting as is would write a null `zone_type` to 27,469 tracts and drop "Entry-Market Neighborhoods" from the marts. That meets the spec's hold condition: the structure changed enough to need a fresh naming review, at least for the knowledge pair.

**The fast path to promotion is one decision for Dan: a name map.**
1. Carry the published names forward to the matched clusters (the matching below is unambiguous on both tests). Re-check two names on raw profiles: Emerging Knowledge Districts, which is now a campus and student type, and Knowledge Corridor, which is now twice as broad.
2. Replace the automatic labeler's output with that fixed name map, as the [K6/K7 review](K6_K7_CLUSTER_REVIEW.md) already recommended ("Replace the current heuristic cluster names with a manual review name map"). Otherwise any future input change can reshuffle names again.

The scores are better now whatever happens to the names: they no longer carry the bug. They live in the same mart row as the labels, though, so they wait too.

## What the bug actually put into the model

The pre-fix tract value was (labor force − not in labor force) / labor force, which simplifies to **2 − 1 / LFPR** (correlation with the stored values: 1.000). It wasn't noise: it was a transform of labor force participation. Two consequences:

- **Every tract with LFPR under 50% went negative** (6,783 tracts, a one-to-one match). The frame build turns negatives into NA, so with 629 true nulls, **7,412 tracts (9.5%) were median-imputed at 0.465**. After the fix, 640 tracts (0.8%) are imputed, at 0.045.
- **The clustering was getting a participation signal.** High-participation, educated renter tracts were held together by it. Removing it re-sorts tracts mainly on that axis, which is exactly where the change lands (the knowledge clusters; see below).

## Run setup

| | Control | Fixed |
|---|---|---|
| Code | Current `R/phase7_*.R` (unchanged since the 2026-07-01 commit) | Same |
| Seeds | `set.seed(20270701 + …)` as written | Same |
| Tract frame | `outputs/phase7_tract_frame.parquet` (the July frame) | Live `gold.intelligence_zone_inputs` |
| Output | `outputs_rerun_2026-10/control/` | `outputs_rerun_2026-10/fixed/` |

**Which pre-fix frame:** the July frame. The foundations before-snapshot (`foundations/etl/data/snapshots/acs_labor_fix_2026-10-22/before/gold_intelligence_zone_inputs.parquet`) is equivalent. Its 6,783 differing unemployment values are all negatives, which the frame build turns into NA, and the other 21 KPIs match exactly.

**Fixed vs July frame:** all 21 other KPIs and all tract metadata (CBSA, county, names, Opportunity Zone flag) are identical across all 78,199 tracts. Only `pct_unemployment_rate` differs (77,535 tracts). Every difference below comes from the fix.

Comparison script: [R/phase7_labor_fix_rerun_compare.R](R/phase7_labor_fix_rerun_compare.R). It writes every table to `outputs_rerun_2026-10/comparison/`, which is gitignored like `outputs/`.

## Control reproduction: pass

| Check | Result |
|---|---|
| Tracts | 78,199 control, 78,199 mart |
| Cluster ID agreement with `mart_intelligence.intelligence_zones` | 100% |
| `zone_type` agreement | 100% |
| Max composite score difference | 0 |
| Max national composite percentile difference | 0 |
| ZCTA rollup (control vs `intelligence_zones_zcta`) | 29,282 ZCTAs, 0 dominant or primary changes, 0 Mixed Zone flips |

The model is deterministic, so all the movement below is the fix, not run-to-run noise.

## Calibration: k = 7 holds

Sampled calibration (5,000 tracts, as in the model). The model's own run covers k = 7–10 (`candidate_k`). A side check ran k = 5–6 with the same sample and seeds; its k = 7 row matches the model's own row exactly.

| k | k-means silhouette, control | k-means silhouette, fixed | Ward silhouette, control | Ward silhouette, fixed | Between-SS ratio, control | Between-SS ratio, fixed |
|---|---:|---:|---:|---:|---:|---:|
| 5 | 0.0941 | 0.0944 | 0.0221 | 0.0871 | 0.250 | 0.249 |
| 6 | 0.1002 | 0.0969 | 0.0305 | **0.0916** | 0.287 | 0.287 |
| **7** | **0.1025** | **0.0986** | 0.0385 | 0.0771 | 0.313 | 0.312 |
| 8 | 0.0997 | 0.0778 | 0.0412 | 0.0267 | 0.332 | 0.333 |
| 9 | 0.0956 | 0.0814 | 0.0466 | 0.0328 | 0.351 | 0.351 |
| 10 | 0.0827 | 0.0806 | 0.0497 | 0.0361 | 0.368 | 0.368 |

- **k = 7 is still the best k-means silhouette**, over both 8–10 and 5–6, so the model picks k = 7 on its own rule.
- The margin over k = 6 narrows (0.0017, down from 0.0023), and k = 8 drops away sharply.
- Ward silhouettes rose a lot at k = 5–7 and now peak at k = 6. That is a hierarchical, sample-only signal; the selection rule uses k-means. Worth a sentence in the naming review, not a reason to change k (out of scope).
- **Full 78k-tract fit at k = 7:** within-SS 1,196,335 → 1,195,916; between-SS ratio 0.3046 → 0.3048. Essentially unchanged.
- Smallest cluster at full scale: 69 → 68 (Commercial Core).

## Cluster matching

IDs and automatic labels swap between runs, so clusters are paired by centroid distance on the 21 unchanged KPIs (flipped standardized scale; unemployment left out because its meaning changed). That one-to-one matching **equals the matching that keeps the most tracts together** (65,210). It isn't a judgment call.

| Published name (control) | Control ID | Fixed ID | Fixed automatic label | Centroid distance | Next nearest | Tracts before | Tracts after | Change |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| Entry-Market Neighborhoods | 1 | 1 | **Mixed-Income Middle Neighborhoods** | 0.21 | 3.68 | 9,243 | 9,770 | +5.7% |
| Emerging Knowledge Districts | 2 | 3 | Emerging Knowledge Districts | **2.99** | **3.00** | 6,339 | 2,111 | **−66.7%** |
| Knowledge Corridor | 3 | 2 | Knowledge Corridor | 2.04 | 3.77 | 4,568 | 10,899 | **+138.6%** |
| Established Residential | 4 | 6 | Established Residential | 0.25 | 2.44 | 19,016 | 16,385 | −13.8% |
| Mixed-Income Middle Neighborhoods | 5 | 4 | **NA** | 0.34 | 2.50 | 27,653 | 27,469 | −0.7% |
| Working Neighborhoods | 6 | 5 | Working Neighborhoods | 0.07 | 3.51 | 11,311 | 11,497 | +1.6% |
| Commercial Core / Jobs Center | 7 | 7 | Commercial Core / Jobs Center | 0.23 | 25.99 | 69 | 68 | −1.4% |

Five pairs are tight (distance ≤ 0.34 against a next-nearest of 2.4 or more). The old Emerging Knowledge cluster is almost equidistant from the new Emerging Knowledge (2.99) and the new Knowledge Corridor (3.00): it split between them.

## Assignment stability

| Measure | Value |
|---|---:|
| Tracts unchanged (matched) | **83.4%** (65,210 of 78,199; 12,989 moved) |
| Adjusted Rand index | **0.695** |
| Large CBSAs (≥ 100 tracts) | 142 |
| Share unchanged, large CBSAs | median 84.6%, 10th percentile 77.8%, min 60.6% |
| Large CBSAs under 90% unchanged | 116 of 142 |

**By control cluster:**

| Published name | Tracts | Unchanged | Main destination if moved |
|---|---:|---:|---|
| Commercial Core / Jobs Center | 69 | 98.6% | Emerging Knowledge (1) |
| Working Neighborhoods | 11,311 | 93.9% | Mixed-Income Middle |
| Entry-Market Neighborhoods | 9,243 | 92.0% | Mixed-Income Middle |
| Knowledge Corridor | 4,568 | 90.7% | Working Neighborhoods |
| Mixed-Income Middle Neighborhoods | 27,653 | 86.1% | Knowledge Corridor |
| Established Residential | 19,016 | 84.4% | Mixed-Income Middle |
| **Emerging Knowledge Districts** | 6,339 | **32.0%** | **Knowledge Corridor** |

**Crosstab** (rows: control; columns: fixed cluster under its matched published name):

| Control \ Fixed | Comm. Core | Emerging Knowl. | Entry-Market | Estab. Resid. | Knowl. Corridor | Mixed-Inc. Middle | Working |
|---|---:|---:|---:|---:|---:|---:|---:|
| Commercial Core | 68 | 1 | 0 | 0 | 0 | 0 | 0 |
| Emerging Knowledge | 0 | **2,027** | 591 | 11 | **3,281** | 176 | 253 |
| Entry-Market | 0 | 53 | 8,502 | 139 | 40 | 375 | 134 |
| Established Residential | 0 | 4 | 166 | 16,051 | 13 | **2,713** | 69 |
| Knowledge Corridor | 0 | 22 | 13 | 3 | 4,142 | 135 | 253 |
| Mixed-Income Middle | 0 | 1 | 285 | 150 | **3,245** | 23,802 | 170 |
| Working | 0 | 3 | 213 | 31 | 178 | 268 | 10,618 |

**The three big flows**, profiled on raw medians:

| Flow | Tracts | LFPR | Old imputed value | Poverty | Income | BA+ | Owners | Walk to work | 65+ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Emerging Knowledge → Knowledge Corridor | 3,281 | 77% | 0.70 | 10.8% | $90k | 63% | 31% | 4.0% | 10.7% |
| Emerging Knowledge, stays | 2,027 | 65% | 0.47 (23% imputed) | 24.4% | $57k | 55% | 16% | 23.1% | 6.4% |
| Mixed-Income Middle → Knowledge Corridor | 3,245 | 70% | 0.56 | 6.3% | $117k | 61% | 63% | 1.1% | 16.1% |
| Established Residential → Mixed-Income Middle | 2,713 | 58% | 0.28 | 8.5% | $79k | 31% | 79% | 0.6% | 23.3% |

The old Emerging Knowledge cluster was two populations held together by very high participation: **young-professional renter districts** and **campus and student areas**. Without the participation signal, the young professionals join Knowledge Corridor, and so do the most educated, high-participation suburbs from Mixed-Income Middle. What stays in Emerging Knowledge is the campus and student core.

**Least stable large CBSAs** are the knowledge-economy metros, as that mechanism predicts: Austin 60.6%, Portland 61.3%, Washington 65.2%, Denver 66.5%, Seattle 68.3%, Durham–Chapel Hill 72.1%, San Diego 72.3%, Spokane 73.8%, Palm Bay 74.1%, Salt Lake City 75.0%, Boston 76.4%.

**Largest CBSAs:** New York 81.5%, Los Angeles 82.4%, Chicago 81.1%, Dallas 79.1%, Houston 78.2%, Philadelphia 82.1%, Atlanta 78.2%, Miami 83.5%, Washington 65.2%, Detroit 90.3%, Boston 76.4%, Phoenix 81.7%.

## Centroids (flipped standardized scale)

Polarity-flipped, so for negative KPIs (poverty, unemployment, PM2.5) **negative means high**. Selected KPIs, matched pairs:

| Published name | Run | BA+ | Same house | Owners | Density | Walk | Poverty | Unemp. | Jobs/res. | Pro jobs | Asian | PM2.5 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Emerging Knowledge | control | 0.98 | −1.99 | −1.50 | 0.78 | 1.68 | −0.48 | −0.93 | 0.24 | 0.66 | 0.30 | 0.01 |
| | fixed | 0.86 | **−2.89** | −1.69 | 0.77 | **4.28** | **−1.36** | −0.34 | 0.45 | 0.49 | 0.54 | 0.16 |
| Knowledge Corridor | control | 0.85 | 0.16 | −0.10 | 0.74 | −0.05 | 0.43 | −0.16 | −0.02 | 0.33 | **3.05** | −0.86 |
| | fixed | 1.13 | **−0.43** | −0.48 | 0.71 | 0.08 | 0.37 | 0.17 | 0.04 | **0.80** | **1.40** | −0.42 |
| Mixed-Income Middle | control | 0.51 | 0.18 | 0.45 | 0.13 | −0.24 | 0.56 | −0.33 | −0.04 | 0.23 | −0.10 | 0.17 |
| | fixed | 0.36 | 0.21 | 0.51 | 0.04 | −0.25 | 0.53 | 0.35 | −0.05 | 0.06 | −0.17 | 0.22 |
| Established Residential | control | −0.44 | 0.32 | 0.62 | −1.22 | −0.16 | 0.14 | 0.63 | −0.07 | −0.28 | −0.45 | 0.44 |
| | fixed | −0.49 | 0.34 | 0.64 | −1.37 | −0.15 | 0.11 | 0.21 | −0.07 | −0.29 | −0.47 | 0.47 |
| Entry-Market | control | −0.77 | −0.17 | −0.85 | 0.43 | 0.03 | −1.31 | 0.37 | −0.02 | −0.31 | −0.37 | 0.13 |
| | fixed | −0.73 | −0.28 | −0.91 | 0.45 | 0.03 | −1.30 | **−1.05** | −0.02 | −0.28 | −0.35 | 0.14 |
| Working | control | −0.77 | 0.22 | −0.57 | 0.66 | −0.08 | −0.43 | 0.04 | −0.05 | −0.34 | −0.11 | −0.92 |
| | fixed | −0.76 | 0.20 | −0.58 | 0.67 | −0.07 | −0.42 | −0.34 | −0.05 | −0.34 | −0.05 | −0.94 |
| Commercial Core | control | −0.26 | −0.66 | −0.22 | −0.38 | 0.53 | −0.21 | −0.26 | 25.87 | −0.05 | −0.28 | −0.14 |
| | fixed | −0.27 | −0.57 | −0.20 | −0.38 | 0.46 | −0.16 | −0.25 | 26.04 | −0.07 | −0.30 | −0.15 |

**Largest shifts (excluding unemployment), all in the knowledge pair:**
- Emerging Knowledge: walk to work +2.61, same house −0.90, poverty −0.88 (i.e. higher poverty)
- Knowledge Corridor: Asian share −1.66, same house −0.59, professional-services jobs +0.48, PM2.5 +0.43 (i.e. lower exposure), owners −0.38

The old Knowledge Corridor was partly an Asian-concentration cluster (+3.05 SD). The new one is a broader educated, professional-jobs type (+1.40 SD).

**Unemployment** now reads sensibly on the flipped scale. Entry-Market has the highest unemployment (−1.05) and Mixed-Income Middle the lowest (+0.35); before, the column ranked participation.

## Raw profiles (R32)

Median raw values per matched type. Both runs use the **fixed** unemployment rate, so the difference is membership only. Density is population-weighted people per square mile.

| Published name | Run | Tracts | Poverty | BA+ | Median income | Owners | Density | 65+ | Unemp. (fixed) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Mixed-Income Middle Neighborhoods | control | 27,653 | 6.0% | 44% | $103.6k | 78% | 2,528 | 17.0% | 3.5% |
| | fixed | 27,469 | 6.2% | 41% | $99.2k | 79% | 2,164 | 17.7% | 3.4% |
| Established Residential | control | 19,016 | 10.4% | 24% | $72.7k | 82% | 147 | 21.7% | 3.8% |
| | fixed | 16,385 | 10.7% | 23% | $71.9k | 82% | 110 | 21.4% | 3.8% |
| Working Neighborhoods | control | 11,311 | 16.5% | 18% | $66.2k | 52% | 6,407 | 12.2% | 6.4% |
| | fixed | 11,497 | 16.5% | 18% | $66.3k | 52% | 6,489 | 12.1% | 6.5% |
| Entry-Market Neighborhoods | control | 9,243 | 26.5% | 18% | $45.4k | 44% | 3,823 | 14.5% | 8.3% |
| | fixed | 9,770 | 26.4% | 18% | $45.7k | 42% | 3,955 | 14.0% | 9.0% |
| Knowledge Corridor | control | 4,568 | 6.8% | 53% | $122.6k | 65% | 6,791 | 16.6% | 4.7% |
| | fixed | **10,899** | 7.7% | 59% | **$109.9k** | **53%** | 6,083 | 14.9% | 4.2% |
| Emerging Knowledge Districts | control | 6,339 | 14.5% | 56% | $75.1k | 26% | 7,506 | 9.4% | 4.8% |
| | fixed | **2,111** | **25.1%** | 54% | **$56.4k** | **16%** | 8,075 | **6.7%** | 6.1% |
| Commercial Core / Jobs Center | control | 69 | 12.9% | 24% | $80.2k | 12% | 56 | 8.2% | 1.3% |
| | fixed | 68 | 10.1% | 21% | $78.5k | 11% | 45 | 7.7% | 0.0% |

**What this means for the names** (for the separate naming decision; nothing renamed here):
- The R32 problems carry over unchanged. Mixed-Income Middle is still the lowest-poverty type ($99k, 6.2%), and Established Residential is still rural (110 per sq mi).
- **Emerging Knowledge Districts** is now a campus and student type: 25% poverty, 16% owners, 6.7% aged 65+, very high walk-to-work, very high turnover. Albany's working name "Students and young professionals" should drop the young professionals.
- **Knowledge Corridor** is now the young-professional and educated-affluent type: 10,899 tracts, 59% BA+, $110k, half owners. "Corridor" still implies a shape the model doesn't measure.
- **Entry-Market** is now the highest-unemployment type (9.0%), which strengthens the case that the name is a euphemism for lower-income urban.

## Automatic labels: two swaps and one null

`build_phase7_provisional_label_map` assigns names by greedy best score across eight scored "families", but its lookup names only seven. **`distressed` has no name.** In the control run that family never wins a cluster. In the fixed run it wins cluster 4 (the matched Mixed-Income Middle cluster, 27,469 tracts): `distressed` scores 0.367, against 0.242 for the family behind "Mixed-Income Middle". The cluster gets name NA, and the cascade follows:

| Matched pair | Published name | Fixed automatic label | |
|---|---|---|---|
| ctrl 5 → fixed 4 | Mixed-Income Middle Neighborhoods | **NA** | `distressed` family won; the unemployment fix raised this cluster's flipped unemployment centroid (−0.33 → +0.35), which feeds the `distressed` score |
| ctrl 1 → fixed 1 | Entry-Market Neighborhoods | **Mixed-Income Middle Neighborhoods** | Swap: picked up the name freed above |
| none | — | Entry-Market Neighborhoods unused | No cluster left for it |
| other 5 pairs | | Same as published | |

Two consequences if promoted as is:
- 27,469 tracts get `zone_type` NA.
- The ZCTA rollup can't place them: 6,455 ZCTAs would get a null primary type, and "Entry-Market" would vanish from the ZCTA mart.

This is a labeler defect the fix exposed, not a fix effect. It is also the R32 problem in code form: the `distressed` score adds *flipped* poverty and unemployment, so it rises when poverty and unemployment are *low*. Fixing the labeler belongs to the naming decision (out of scope); the recommendation above avoids depending on it.

## Scores and percentiles

Only Opportunity contains the unemployment KPI. Character and Livability inputs are unchanged, so their scores are identical. Zone-peer percentiles move for every frame because the peer groups changed.

| Measure | Median absolute change | 90th percentile | Share moving > 10 points |
|---|---:|---:|---:|
| Character, Livability scores | 0 | 0 | — |
| Opportunity score (z units) | 0.132 | 0.323 | — |
| Composite score (z units) | 0.044 | 0.108 | — |
| National Character, Livability percentiles | 0 | 0 | 0% |
| **National Opportunity percentile** | 8.5 | 26.1 | **44.5%** |
| **National composite percentile** | 4.3 | 13.1 | **18.1%** |
| CBSA Opportunity percentile | 8.4 | 26.3 | 44.0% |
| CBSA composite percentile | 5.1 | 15.9 | 24.5% |
| Zone-peer Character percentile | 3.0 | 25.2 | 19.4% |
| Zone-peer Livability percentile | 3.2 | 18.2 | 16.6% |
| Zone-peer Opportunity percentile | 9.6 | 28.5 | 48.5% |
| Zone-peer composite percentile | 6.8 | 22.0 | 35.8% |

The Opportunity movement is large because one of seven Opportunity KPIs went from a participation transform to the real unemployment rate. The fixed-run zone-peer groups include the NA group, so they'd change again under a name map.

## Albany (CBSA 10580)

251 tracts; **84.9% unchanged**. Rows: control; columns: fixed cluster under its matched published name.

| Control \ Fixed | Emerging Knowl. | Entry-Market | Estab. Resid. | Knowl. Corridor | Mixed-Inc. Middle | Working | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Emerging Knowledge | 13 | 3 | 0 | **10** | 2 | 0 | 28 |
| Entry-Market | 0 | 28 | 0 | 0 | 1 | 1 | 30 |
| Established Residential | 0 | 0 | 39 | 0 | **9** | 0 | 48 |
| Knowledge Corridor | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| Mixed-Income Middle | 0 | 1 | 0 | **11** | 131 | 0 | 143 |
| Working | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| **Total** | 13 | 32 | 39 | **22** | 143 | 2 | 251 |

Raw Albany medians after the fix:

| Type (matched) | Tracts | Poverty | BA+ | Income | Owners | Density | 65+ | Unemp. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Mixed-Income Middle | 143 | 5.9% | 46% | $102k | 75% | 1,428 | 19.2% | 3.2% |
| Established Residential | 39 | 8.0% | 29% | $92k | 86% | 63 | 23.7% | 4.3% |
| Entry-Market | 32 | 32.7% | 20% | $43k | 31% | 8,374 | 12.6% | 11.0% |
| Knowledge Corridor | 22 | 11.4% | 54% | $88k | 41% | 2,562 | 16.5% | 3.9% |
| Emerging Knowledge | 13 | 27.0% | 51% | $52k | 17% | 7,566 | 9.1% | 7.4% |
| Working | 2 | 19.3% | 23% | $64k | 44% | 7,623 | 10.0% | 5.7% |

**Working-name implications** (the [build plan](../../../metro-deep-dive-program/issues/ny_state/metro_deep_dives/albany/part_1/ALBANY_LENS1_VISUALS_BUILD_PLAN.md) Q3 table):
- **Knowledge Corridor goes from 1 tract to 22**, so "too few to test" no longer applies. The 22 are 11 from Mixed-Income Middle (Albany County 6, Saratoga 4, Schenectady 1), 10 from Emerging Knowledge (Albany County 4, Rensselaer 3, Schenectady 3), and the original one. They're educated ($88k, 54% BA+), mixed tenure and moderately dense, so "Affluent urban" is a loose fit. Test it.
- **Emerging Knowledge drops from 28 tracts to 13:** 6 in Albany County, 3 Rensselaer, 2 Schenectady, 1 each in Saratoga and Schoharie. They're poorer (27%) and more renter-heavy (17% owners). "Students and young professionals" becomes "Students" or "Campus neighborhoods". Re-check against campuses once anchors are in.
- **"Comfortable suburbs" keeps 143 tracts** (131 stay; 9 arrive from Established Residential, 2 from Emerging Knowledge, 1 from Entry-Market). Its profile is unchanged, so the split-in-two stress test still stands.
- **Established Residential loses 9 tracts** to Mixed-Income Middle and still fits "Rural and exurban" (63 per sq mi).
- **Entry-Market gains 2 tracts** and fits "Lower-income urban" (11% unemployment).
- The Albany notebook's zone views (`sql/zone_profile.sql`, `zone_name_status.sql`, `metro_tract_profile.sql`) read the marts, so they'll pick this up only after promotion.

## ZCTA rollup

Fixed run rolled up into `fixed/`. Today's crosswalk is the same HUD 2025Q1 vintage the mart was built from, and the control rollup reproduces the mart exactly. Two views:

| Comparison (29,282 ZCTAs) | Dominant type changed | Primary label changed | Flipped to Mixed Zone | Flipped from Mixed Zone |
|---|---:|---:|---:|---:|
| Control vs fixed, **matched names** | 3,218 (11.0%) | 3,472 (11.9%) | 527 | 442 |
| Control vs fixed, automatic labels as is | 3,735 among 22,827 placed | 3,974 | 527 | 442 |

With the automatic labels, 6,455 ZCTAs would have a null primary type.

**Primary type mix, matched names:** Knowledge Corridor 718 → 2,051 (+1,333); Emerging Knowledge 1,688 → 758 (−930); Established Residential 15,845 → 15,094 (−751); Mixed-Income Middle 6,326 → 6,455 (+129); Entry-Market 1,691 → 1,790 (+99); Mixed Zone 1,034 → 1,119 (+85); Working 1,961 → 1,996 (+35); Commercial Core 19 → 19.

## CBSA-level frames: unaffected

Character, Livability, Opportunity, Cross-Frame (and Trajectory) read CBSA rows, where `pct_unemployment_rate` comes from BLS LAUS. The foundations fix confirmed those rows unchanged.

## Downstream (listed, not changed)

**Readers of `mart_intelligence.intelligence_zones` / `intelligence_zones_zcta`:**
- `metro-deep-dive-program/analyses/position/internal_structure/`: both notebooks and nine queries (tract zone map, zone composition, ZCTA rollup, place-zone matrix, place inventory, POI zone and points, job centers, market and cross-market summaries)
- `metro-deep-dive-program/engines/corridor_intelligence/inputs/corridor_inputs_v1.yml` and `CORRIDOR_INTELLIGENCE_REVIEW_NOTEBOOK.py`
- `metro-deep-dive-program/engines/intelligence_framework/queries/zones_cbsa_summary.sql` (and its `CONTRACT.md`)
- `metro-deep-dive-program/issues/ny_state/metro_deep_dives/albany/`: `sql/zone_profile.sql`, `sql/zone_name_status.sql`, `sql/metro_tract_profile.sql`, and the Lens 1 exploration and visuals notebooks (zone map, composition, working names)
- `foundations/semantic_layer/table_catalog.yml` (catalog entry for both marts)
- `metro-deep-dive/research-tool/dd_db.py` (Legacy area)
- In this folder: `zone_methodology.qmd`, `R/phase7_descriptive_cluster_audit.R` and `sql/phase7_descriptive_cluster_audit.sql` (they read `outputs/`; the `phase7_descriptive_*.csv` files there would go stale)

**Cached zone outputs:**
- `metro-deep-dive-program/engines/corridor_intelligence/outputs/runs/*phase7_2026-07-01*`: eight run folders for Jacksonville (27260) and Richmond (40060), keyed to the July Phase 7 build
- marimo session caches under `issues/ny_state/metro_deep_dives/albany/__marimo__/`, `engines/corridor_intelligence/__marimo__/` and `analyses/position/internal_structure/__marimo__/`

## Code changes in this session

- **Output and input overrides** ([phase7_config.R](R/phase7_config.R), [phase7_tract_frame_build.R](R/phase7_tract_frame_build.R)): `PHASE7_OUTPUT_DIR` sets a repo-relative output folder, and `PHASE7_INPUT_FRAME` replays a saved `phase7_tract_frame.parquet` instead of querying Gold. Both default to today's behaviour.
- **Unplanned fix to the ZCTA rollup** ([phase7_zcta_rollup.R](R/phase7_zcta_rollup.R)): the rollup failed on today's warehouse. Since 2026-09-29, `silver.xwalk_zcta_tract` is a compatibility view over `silver.xwalk_zip_tract` and no longer carries `zip_pref_city` / `zip_pref_state`. The rollup now takes those two labels from `staging.hud_usps_zip_tract`. Weights and logic are unchanged, and the control rollup reproduces the mart exactly.
- **Comparison script:** [R/phase7_labor_fix_rerun_compare.R](R/phase7_labor_fix_rerun_compare.R).

## After Dan's decision

Nothing below has run.
1. Dan decides the name map (carry forward, or rename the knowledge pair), and how the labeler should use it.
2. Rerun the model and rollup into `outputs/` (default settings, no env vars). The result equals `fixed/` plus the name map.
3. Run `foundations/loaders/load_zone_assignments.R`, then `load_zone_scores_zcta.R`. Close marimo kernels first (`lsof` on the DuckDB file).
4. Update this folder's README model overview, and add a dated note to `docs/methodology/intelligence_framework/zone_methodology_notes.md`.
5. Refresh the downstream items above as their areas pick them up: Albany Q3 table first, then the corridor runs and the descriptive audit.
