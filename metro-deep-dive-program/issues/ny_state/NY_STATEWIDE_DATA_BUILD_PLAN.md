# NY Statewide Data Build Plan

**Status:** Done
**Updated:** 2026-11-02

Get POIs and physical context for all of New York in one pass, so later pieces don't wait on engine runs.

**Finished 2026-11-02.** Gates 1, 2 and 3 were approved and the results are in the warehouse. What's left is under Deferred, and the run log is at the bottom.

## Scope

| In | Out for now |
|---|---|
| Overture POIs for 26 more CBSAs and the 11 non-CBSA counties | Core Place overlap and the Q6 notebook fix (see Deferred) |
| OSM airports, campuses, hospitals, prisons, parks, protected areas | OSM industrial land and ports |
| OSM stations and terminals | Q4 and Corridor Intelligence market wiring |
| | LODES OD ingest and B2 state institution sources |

Decisions made:

- **One run per CBSA**, not one statewide market, because consumers filter on `cbsa_code`.
- **Non-CBSA counties share `cbsa_code = 'SYNTH-NY'`.** The key is deliberately synthetic and never joins to a real CBSA.
- **NYC keeps its NJ counties**, because its zones include 1,583 NJ tracts. Statewide queries filter on county assignment `geo_id LIKE '36%'`.
- **Stay on Overture release `2026-10-21.0`**, so Albany needs no rerun. Run before Overture retires it.
- **Warehouse publishes are append-only.** Nothing is deleted, and core infrastructure files are not overwritten.
- **OSM layers get their own tables**, so they can't change Overture category counts or current consumers.

## Estimate

About 1 hour of machine time and 2.3 GB of permanent storage, plus an optional 19.5 GB backup. About 79 GB was free on 2026-11-02.

NYC is the only heavy market: about 17 minutes, with the assign step using nearly all CPU cores and about 5 GB of memory. NYC timings were measured in the scratchpad. Taxonomy validation, publishing into the full warehouse, the non-CBSA path and the OSM layers are untimed.

## 1. POI code changes

- [x] Declare the 26 CBSAs and `ny_non_cbsa` in [overture_places.yml](../../engines/poi/sources/overture_places.yml)
- [x] Allow the non-numeric `SYNTH-NY` ID in `resolve_market`
- [x] Support a county-list boundary in acquire, normalize and assign
- [x] Add a batch runner ([run_poi_markets.py](../../engines/poi/run_poi_markets.py)) that skips finished markets, stops on failure and never publishes
- [x] Add a new append-only publish script ([publish_poi_append.py](../../engines/poi/publish_poi_append.py)) and leave `publish_poi_mart.py` unchanged. It never deletes, refuses any market that already has rows, inserts by column name and publishes each market in one transaction
- [x] Fix the row-accounting check in `assign_poi_geography.py`, which failed any market with a boundary-ambiguous point

**Checks:**

- [x] Albany dry run still returns 47,047, and rebuilding its assignments shows no differences (no regression)
- [x] Hudson (`26460`) runs end to end and returns 3,893
- [x] `ny_non_cbsa` runs end to end and returns 27,025, with every point assigned to one of the 11 counties
- [x] In a throwaway database, the append-only script publishes `SYNTH-NY`, refuses reruns, and keeps geometry as `GEOMETRY`

## 2. POI run, local only

Run order per market: acquire → normalize → classify → taxonomy profile → validate taxonomy → assign.

- [x] Run NYC first, so any scale problem shows up early
- [x] Run the other 25 CBSAs

### Gate 1: review before publishing

Approved 2026-11-02.

| Check | Expected | Result |
|---|---|---|
| New run folders | 27, all on release `2026-10-21.0` | 27 |
| Retained POIs per market | Within 0.1% of the table below | All within 0.05% |
| New POIs in total | About 1,408,846 | 1,408,844 |
| NY POIs, including Albany | About 1,105,844 by county assignment | 1,105,844 |
| NJ POIs | About 350,049 | 350,047 |
| Rejected records | 0, or each one explained | 0 |
| Tract and county assignment | 100% | 100% in every market |
| Taxonomy invariant violations | 0; any other result is a hard stop | 0 |
| `source_id` in more than one market | None, or listed for review | None |
| Unmapped category values | Reviewed | 6 values, 187 POIs (see below) |
| POIs with no Overture category | Reported by market | About 2–3% in most markets; Corning 22.3%, NYC 7.3%, non-CBSA 6.8%, Rochester 6.0% (see below) |

**Taxonomy validation reports `fail` in 23 of 27 markets.** The only cause is these category values with no taxonomy rule: `waterfall` (131), `education_office` (32), `services_and_business` (16), `rest_stop` (4), `class_venue` (2), `utility_energy_infrastructure` (2). They stay in the data as unmapped.

**Decided: low-confidence POIs stay in the warehouse.** Overture's `confidence` is below 0.3 for 9.1% of NY-series POIs (131,934), 98.8% of them Meta-sourced. They cluster unevenly and include obvious junk such as `Sports Love` and `Sports Trending`.

| Market | POIs | Confidence below 0.3 | Confidence 0.5 or higher |
|---|---:|---:|---:|
| Corning | 9,926 | 56.4% | 4,071 |
| Non-CBSA counties | 27,025 | 17.7% | |
| Rochester | 60,296 | 13.2% | |
| NYC | 1,077,103 | 9.3% | |
| Batavia | 3,375 | 9.0% | |
| Most other markets | | About 5% | |
| Elmira, for comparison | 4,140 | | 3,714 |

76,763 of these have a category, so they count toward Services, Retail, Healthcare and other category totals. Any raw POI comparison across markets would overstate Corning, Rochester and the non-CBSA counties.

**Cause.** Most of the excess is 9,306 records with the invalid postal code `10000`, 99% of them in nine counties around the western Finger Lakes (3,318 in Steuben alone), plus low-confidence records with no postal code. Average confidence is 0.10, and many names look like unrelated pages or generated text. Low-confidence records also cluster in Manhattan, the Bronx and Staten Island.

**Candidate filter, not applied.** Every record is published, as the POI contract requires, and no table or query filters them. This is the starting point for the future review listed under Deferred:

```sql
try_cast(json_extract_string(source_attributes, '$.confidence') AS DOUBLE) >= 0.3
AND coalesce(json_extract_string(source_attributes, '$.operating_status'), '') <> 'permanently_closed'
AND mapping_status = 'mapped'
```

It keeps 913,155 of 1,105,844 NY POIs (82.6%). Steuben falls from 107.2 to 45.2 POIs per 1,000 residents and Livingston from 100.5 to 47.7, in line with Chemung (45.7) and Monroe (46.0). It keeps 97.5% of hospital-tagged and 91.3% of grocery-tagged records. A 0.77 threshold alone would drop 39% of hospital-tagged records. The threshold was set from those comparisons and small record samples, not from a ground-truth list, so check it against known places in a first analysis.

Closed records were also found at this stage: 49,831 NY POIs (4.5%) are marked `permanently_closed`, mostly from BrightQuery. Existing analysis queries apply none of these conditions, including Internal Structure and Albany Part 1's `sql/`.

## 3. POI publish

### Gate 2: Dan approves publishing

Approved 2026-11-02.

- [x] Close marimo and anything else holding the warehouse (three idle kernels)
- [x] Back up the warehouse, on the internal disk; deleted after step 5
- [x] Publish each market with the append-only script

| Table | Rows now | Rows after |
|---|---:|---:|
| `mart_poi.poi_source_place` | 195,493 | 1,604,337 |
| `mart_poi.poi_classified_place` | 195,493 | 1,604,337 |
| `mart_poi.poi_geography_assignment` | 781,972 | 6,417,348 |
| `mart_poi.poi_taxonomy_hierarchy_tag_profile` | 14,440 | 92,153 |

**Checks:**

- [x] Row counts match the table above
- [x] Albany, Richmond and Jacksonville row counts are unchanged (47,047 / 61,513 / 86,933)
- [x] Re-running a published market is refused and changes nothing
- [x] `poi_geography_assignment` has exactly 4 rows per POI
- [x] Geometry is still `GEOMETRY`, not `BLOB`
- [x] Internal Structure's POI queries return results for Rochester; the notebook itself was not opened

## 4. OSM layers

Read from the cached [Geofabrik file](../../engines/infrastructure/sources/osm_infrastructure.yml), with no new download.

| Layer | Raw statewide count | Goes to |
|---|---:|---|
| Parks and reserves | 10,008 | Infrastructure |
| Protected areas | 2,301 | Infrastructure |
| Campuses | 329 | Infrastructure |
| Hospitals | 238 | Infrastructure |
| Airports | 114 | Infrastructure |
| Prisons | 95 | Infrastructure |
| Bus stations and depots | 46 polygons, 43 points | Both, by geometry |
| Subway entrances | 2,081 | POI |
| Rail stations | 755 | POI |
| Ferry terminals | 130 | POI |

Counts are before clipping to the state and may overlap.

- [x] Add the polygon selectors as a **separate run** ([acquire_osm_context.py](../../engines/infrastructure/acquire_osm_context.py)), with no overwrite option and its own output folder
- [x] Add a new mapping version for these layers ([osm_context_mappings_v1.yml](../../engines/infrastructure/sources/osm_context_mappings_v1.yml)), approved as initial mappings
- [x] Dry run the polygon selectors; results are in the run log

### Gate 3: Dan approves the mappings

Approved as initial mappings 2026-11-02, with further review expected as analyses use them.

- [x] Build the validated polygon layer
- [x] Add the OSM point source to the POI engine, in its own lane ([build_osm_anchors.py](../../engines/poi/build_osm_anchors.py))
- [x] Append points to a new table, `mart_poi.poi_osm_anchor`: 2,963 rows
- [x] Append polygons to a new schema and table, `mart_infrastructure.infrastructure_context_feature`: 11,172 rows

**Checks:**

- [x] The four Overture POI tables have the same row counts before and after
- [x] Core run files are byte-identical afterward (13 files hashed), because Series Intro Map 2 and Albany read them
- [x] Layer counts fall within the raw counts above. Ferry terminals dropped from 130 to 86 and 46 anchors in total fell outside the state boundary
- [x] No features rejected for missing source IDs; 22 invalid source polygons were repaired and counted
- [x] Spot check named landmarks: JFK, Albany International, Cornell, Jones Beach and Sing Sing in the polygons; New York Penn Station, Albany-Rensselaer, Grand Central entrances, Whitehall and St. George in the anchors
- [x] Compare against Overture, in NY: airports 644 vs OSM 113, hospitals 2,801 vs 238, colleges 3,292 vs 328, prisons 132 vs 95, rail stations 1,314 vs 753

**Known limits:**

- Anchors cover New York only, so NYC's NJ counties have none.
- 15 ferry terminals on piers sit outside every county polygon. They take the nearest county, labelled `nearest_county`, and have no tract.

## 5. Close out

- [x] Record the run and any surprises in [POI NOTES](../../engines/poi/NOTES.md) and [Infrastructure NOTES](../../engines/infrastructure/NOTES.md)
- [x] Add the taxonomy profile step and batch runner to the [POI README](../../engines/poi/README.md)
- [x] Fix [question_bank.md](question_bank.md), uncommitted with the folder restructure
- [x] Update [STATUS.md](../../../docs/STATUS.md), uncommitted with the folder restructure
- [x] Delete the warehouse backup

## Deferred

| Item | Why | Pick up when |
|---|---|---|
| Core Place overlap for NY (26 sec) | Only the Q6 notebook reads it. It would become the first file the notebook picks up, blanking Richmond's infrastructure context | A NY piece needs infrastructure by Census Place; do it together with the Q6 fix |
| Q6 notebook infrastructure fix | Only needed once the overlap exists | Same |
| Q4 market wiring | Markets are hardcoded in four places | A NY piece needs Q4 |
| Corridor Intelligence inputs | Needs per-market entries, a mapping version update and CBSA-level NY infrastructure | A NY piece needs corridors |
| **POI filter review** | Raw counts overstate some markets until this is done. Test the candidate filter against known places; decide its threshold and its closed-record and unmapped conditions; decide where it lives (shared view or each query); then check Internal Structure, other POI queries and Albany Part 1's posted POI counts | Before the first cross-market POI comparison |
| Rules for 6 unmapped category values | 187 POIs, mostly `waterfall`; review with the taxonomy | Next taxonomy update |
| Ports | Barely present in OSM tags; would need mapping review | A NY piece needs ports |
| Fix Internal Structure Part 2 notebook | Fails for every market, including Richmond. See [Notebook fixes](#notebook-fixes) | A NY piece needs the notebook |
| Fix Infrastructure Explorer notebook | Can't start, for any market. See [Notebook fixes](#notebook-fixes) | A NY piece needs the notebook |

## Notebook fixes

Found by headless testing on 2026-11-02. No fix has been made, and the line numbers are as of that date. The bugs predate this work. Until they're fixed, query the marts and Parquet outputs directly.

**[Internal Structure Part 2](../../analyses/position/internal_structure/POSITION_INTERNAL_STRUCTURE_PART2_NOTEBOOK.py)**

| Line | Problem | Effect | Fix |
|---|---|---|---|
| 130, 163, 199 | Multi-select defaults pass option values, but marimo expects labels | Crashes for every market | Pass labels as the defaults |
| 190 | `axis_off=True` isn't valid in `axis.set()` | Crashes the map cell | Call `integrated_axis.set_axis_off()` |
| 177 | Labels WGS84 infrastructure as EPSG:26918 | Richmond's map is mostly blank | Label it EPSG:4326 |
| 115 | Only finds runs named for a CBSA, not the `new_york_state` run | NY markets show no infrastructure | Point it at the statewide run and clip to the market, or build CBSA-level runs. Decide when picking this up |

**[Infrastructure Explorer](../../engines/infrastructure/INFRASTRUCTURE_EXPLORATION_NOTEBOOK.py)**

| Line | Problem | Effect | Fix |
|---|---|---|---|
| 37, 144 | `validation` is defined in two cells | Won't start | Rename one, or make both private with `_validation` |
| 31, 32, 114 | Line 114 returns the selected paths without naming them, so later cells get the loop's `feature_path` and `rejected_path` | Queries read the last run in the loop, not the one selected | Assign both names from `selected_run`, return those, and make the loop variables private |
| 28 | Only lists `osm_core_v1` runs | Context polygons don't appear | Also list `osm_context_v1` runs if a piece needs them there |

**Testing.** Both notebooks ran headless through `app.run()` with these bugs worked around outside the repo, so they haven't been opened in the marimo interface. After fixing them, rerun without workarounds:

- Part 2: Rochester, Corning, NYC and Richmond, viewing each map. Only Rochester's and Richmond's maps have been viewed so far.
- Explorer: New York State and Richmond, confirming that changing the selected run changes the results.

## Next

Once this branch is merged to `main`, review the Albany folder restructure, which is still uncommitted. `docs/STATUS.md` and `question_bank.md` hold edits for this work and ship with it.

## Expected POIs by market

From a county-level sizing query on 2026-11-02. Actual counts will differ slightly because runs clip to tract boundaries (NYC: 1,077,103 vs 1,077,105).

| Market | Code | POIs |
|---|---|---:|
| New York-Newark-Jersey City, NY-NJ | 35620 | 1,077,105 |
| Rochester | 40380 | 60,297 |
| Buffalo-Cheektowaga | 15380 | 57,300 |
| Kiryas Joel-Poughkeepsie-Newburgh | 28880 | 35,174 |
| Syracuse | 45060 | 33,112 |
| Utica-Rome | 46540 | 13,927 |
| Binghamton | 13780 | 11,220 |
| Kingston | 28740 | 10,813 |
| Corning | 18500 | 9,926 |
| Glens Falls | 24020 | 8,354 |
| Jamestown-Dunkirk | 27460 | 7,076 |
| Watertown-Fort Drum | 48060 | 6,194 |
| Ithaca | 27060 | 5,835 |
| Massena-Ogdensburg | 32390 | 5,115 |
| Plattsburgh | 38460 | 4,272 |
| Elmira | 21300 | 4,140 |
| Monticello | 33910 | 4,131 |
| Olean | 36460 | 3,999 |
| Hudson | 26460 | 3,893 |
| Oneonta | 36580 | 3,611 |
| Auburn | 12180 | 3,608 |
| Batavia | 12860 | 3,374 |
| Gloversville | 24100 | 2,564 |
| Amsterdam | 11220 | 2,461 |
| Cortland | 18660 | 2,438 |
| Seneca Falls | 42900 | 1,881 |
| Non-CBSA counties | SYNTH-NY | 27,026 |
| **New POIs** | | **1,408,846** |
| Albany-Schenectady-Troy (already published) | 10580 | 47,047 |

Non-CBSA counties: Allegany, Chenango, Delaware, Essex, Franklin, Greene, Hamilton, Lewis, Schuyler, Wyoming, Yates.

## Run log

| Date | Step | Result | Notes |
|---|---|---|---|
| 2026-11-02 | NYC benchmark, scratchpad only | 1,077,103 POIs; 0 rejected; tract and county 100%; publish test added 1.08 GB | No repo or warehouse changes |
| 2026-11-02 | Smoke runs, local only | Hudson 3,893; `ny_non_cbsa` 27,025; Albany dry run still 47,047 and its assignment rebuild has no differences | Also fixed the row-accounting check in `assign_poi_geography.py`, which would have failed NYC |
| 2026-11-02 | Statewide POI batch, local only | 27 markets in 1,542 sec; 1,408,844 POIs; 0 rejected; NYC assign 891 sec; local files now 880 MB in total | Nothing published. Low-confidence finding raised at Gate 1 |
| 2026-11-02 | OSM context polygons, dry run only | 11,172 retained after clipping to NY; 69 outside the boundary; 0 rejected; 22 invalid source polygons repaired | Nothing written. Airports 113, campuses 328, hospitals 238, prisons 95, bus facilities 47, protected areas 2,292, parks 8,059. Each feature falls in one group, with protected area taking precedence over a park tag (1,885 carry both) |
| 2026-11-02 | Gate 2: POI publish | 27 markets in 155 sec; warehouse grew 0.88 GB; existing markets unchanged; reruns refused | Stopped three idle marimo kernels first |
| 2026-11-02 | Gate 3: OSM layers | 11,172 polygons and 2,963 anchors published to new tables; core files unchanged; reruns refused | Added a labelled nearest-county fallback for 15 pier ferry terminals |
| 2026-11-02 | Close out | Docs updated and backup deleted | Committed on branch `ny-statewide-data`. `docs/STATUS.md` and `question_bank.md` stay with the folder restructure |
| 2026-11-02 | Notebook testing, headless | With workarounds kept outside the repo, Part 2 ran on Rochester, Corning and NYC, and the Explorer on the statewide core run. POI coverage matched the marts | Neither notebook runs as committed, for any market. The bugs predate this work and are listed under Deferred |
