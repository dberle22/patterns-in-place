# Source Spec: LEHD LODES

## 1. Overview

- Source: U.S. Census Bureau
- Program: Longitudinal Employer-Household Dynamics (LEHD) Origin-Destination Employment Statistics (LODES)
- Access pattern in current first-pass scope: public state-based `csv.gz` bulk files plus per-state `version.txt`, checksum, and geography crosswalk files; no API key required
- Current verified public format as of `June 22, 2026`: `LODES 8.4`, with state-based files under `https://lehd.ces.census.gov/data/lodes/LODES8/`
- Current verified year coverage in the live Census docs: `2002-2023` for most states
- Native geography in the public files: census block, with provider-supplied crosswalks to tract, county, CBSA, ZIP, and other higher geographies
- Scope in Foundations: first-pass managed staging should cover WAC and RAC only, aggregated to tract immediately after download; OD is researched here but deferred from the initial ingest
- Documentation goal: confirm the real LODES file families, current coverage window, and the narrowest viable first-pass ingest scope before writing staging code

LODES is the LEHD product that gives Foundations an employment-side geography layer below county. WAC tells us what jobs are located in a block, RAC tells us where workers live, and OD links the two. That makes LODES the labor-market companion to tract-scale ACS neighborhood profiling.

This is a topic-level child spec for the LEHD family. QWI and J2J should remain separate child specs because their access patterns, dimensional structure, and downstream uses differ materially.

---

## 2. Coverage Matrix

| Topic group | Staging family contracts | Silver outputs | Gold outputs |
| --- | --- | --- | --- |
| LEHD LODES workplace area characteristics | `staging__lehd_lodes_wac.md` | `silver.lehd_lodes_wac` | joined into `gold.economics_lodes_wide` |
| LEHD LODES residence area characteristics | `staging__lehd_lodes_rac.md` | `silver.lehd_lodes_rac` | joined into `gold.economics_lodes_wide` |
| LEHD LODES origin-destination flows | deferred | deferred | deferred Deep Dive flow table |

---

## 3. Source Contract

- Provider: U.S. Census Bureau
- LEHD data landing page: `https://lehd.ces.census.gov/data/`
- LODES landing page: `https://lehd.ces.census.gov/data/#lodes`
- Live LODES root index: `https://lehd.ces.census.gov/data/lodes/`
- Current LODES 8 bulk root: `https://lehd.ces.census.gov/data/lodes/LODES8/`
- Current technical document: `https://lehd.ces.census.gov/doc/help/onthemap/LODESTechDoc.pdf`
- OnTheMap application: `https://onthemap.ces.census.gov/`
- Authentication: none

**What we verified**

- The live Census data page now states that LODES data are available for `2002-2023`, not just through `2022`.
- The current public technical document is `LODES 8.4`, revised `2025-12-03`.
- The live `/data/lodes/` index shows `LODES8/` as the active current directory.
- State directories are organized around three file families: `od/`, `rac/`, and `wac/`.
- Each state directory also includes a `version.txt`, a SHA checksum file, and a block-level geography crosswalk file such as `[st]_xwalk.csv.gz`.

**Important planning correction**

The existing Track `23.2.1` checklist text still references `LODES 8.3` and `2022` as the most recent available year. Current Census documentation has moved past that assumption. As of `June 22, 2026`, the live public documentation shows:

- format version `8.4`
- data years through `2023`

That means the source spec for `23.2.1` should document the live current shape rather than preserve the older planning assumption.

**Local wrapper validation**

The installed `lehdr` package in this repo environment is version `1.1.4`, and it does expose a working `grab_lodes()` helper with this effective interface:

- `state`
- `year`
- `version = c("LODES8", "LODES7", "LODES5")`
- `lodes_type = c("od", "rac", "wac")`
- `job_type = c("JT00", "JT01", "JT02", "JT03", "JT04", "JT05")`
- `segment = c("S000", "SA01", "SA02", "SA03", "SE01", "SE02", "SE03", "SI01", "SI02", "SI03")`
- `agg_geo = c("block", "bg", "tract", "county", "state")`
- `state_part = c("", "main", "aux")`
- `download_dir`
- `use_cache`

The local function body confirms that `grab_lodes()` downloads the block-grain bulk file from the Census directory and only then aggregates it if `agg_geo != "block"`. In other words, `agg_geo = "tract"` is a convenience wrapper over the same block-file download, not a separate tract-level upstream artifact.

---

## 4. Staging Shape

LODES does not publish one normalized long table like QWI. Instead, it publishes many wide CSV files keyed by block IDs, file family, workforce segment, and job type.

**Directory and file organization**

At the root of `LODES8`, each state has a lowercase two-letter folder such as `ca/` or `de/`. Inside each state folder:

- `od/` holds origin-destination flow files
- `rac/` holds residence area characteristic files
- `wac/` holds workplace area characteristic files
- `[st]_xwalk.csv.gz` maps `tabblk2020` to tract, county, CBSA, ZIP, and other higher geographies
- `version.txt` records the state vintage and format version
- `lodes_[st].sha256sum` supports file integrity checks

**File naming conventions**

| Family | Template | Notes |
| --- | --- | --- |
| `od` | `[st]_od_[part]_[type]_[year].csv.gz` | `part` is `main` or `aux` |
| `rac` | `[st]_rac_[seg]_[type]_[year]_1.csv.gz` | segment-specific residence files |
| `wac` | `[st]_wac_[seg]_[type]_[year].csv.gz` | segment-specific workplace files |
| `xwalk` | `[st]_xwalk.csv.gz` | block geography crosswalk |

The live RAC naming did not always match the older `_1` suffix example in our Delaware spot-check. For future OD work, the safer implementation rule is:

- prefer `lehdr::grab_lodes()` or a provider index-driven resolver over hardcoding one RAC suffix pattern
- keep the OD contract documented at the same state-based file-family level even though WAC/RAC are the only first-pass ingest targets

**Meaning of the main naming pieces**

| Piece | Values used in current docs | Meaning |
| --- | --- | --- |
| `part` | `main`, `aux` | OD only; `main` is in-state home/work pairs, `aux` is jobs working in-state with residence outside the state |
| `type` | `JT00`, `JT01`, `JT02`, `JT03`, `JT04`, `JT05` | all jobs, primary jobs, all private jobs, private primary jobs, all federal jobs, federal primary jobs |
| `seg` | `S000`, `SA01-03`, `SE01-03`, `SI01-03` | total jobs, worker age, worker earnings, or broad industry segment slices |

**Observed row shapes by file family**

| File family | Key geography columns | Main payload columns | Notes |
| --- | --- | --- | --- |
| `OD` | `w_geocode`, `h_geocode` | `S000`, `SA01-03`, `SE01-03`, `SI01-03`, `createdate` | flow between workplace and residence blocks |
| `RAC` | `h_geocode` | `C000`, `CA01-03`, `CE01-03`, `CNS01-20`, `CR01-05`, `CR07`, `CT01-02`, `CD01-04`, `CS01-02`, `createdate` | residence-block profile; no firm age or firm size payload |
| `WAC` | `w_geocode` | `C000`, `CA01-03`, `CE01-03`, `CNS01-20`, `CR01-05`, `CR07`, `CT01-02`, `CD01-04`, `CS01-02`, `CFA01-05`, `CFS01-05`, `createdate` | workplace-block profile; firm age and firm size only appear here |

**Crosswalk shape**

The provider crosswalk file uses `tabblk2020` as the block key and includes at minimum the higher geographies we care about for Foundations:

- `st`
- `cty`
- `trct`
- `bgrp`
- `cbsa`
- `zcta`
- `blklatdd`
- `blklondd`
- `createdate`

That means we do not need to reconstruct tract IDs by string truncation alone if we choose to carry the published crosswalk into staging QA, although dropping the last four digits from a 15-digit block code will still recover the 11-digit tract GEOID directly.

---

## 5. Staging To Silver

Recommended first-pass handoff:

1. Read WAC and RAC block files only.
2. Validate the published block IDs and `createdate`.
3. Derive tract IDs from the block code prefix or validate against the published state crosswalk.
4. Aggregate to tract before writing the managed staging tables.
5. Preserve provenance fields that let us trace the tract rows back to the source state-year file.
6. Join `silver.xwalk_tract_county` to validate tract coverage and to support later county / CBSA rollups.
7. Publish separate tract-grain staging and Silver outputs:
   - `staging.lehd_lodes_wac`
   - `staging.lehd_lodes_rac`
   - `silver.lehd_lodes_wac`
   - `silver.lehd_lodes_rac`

Recommended first-pass analytical payload to carry from staging into Silver:

- total jobs / workers
- age bands
- earnings bands
- broad NAICS sector buckets
- education bands

Recommended first-pass payload to defer from modeled Silver outputs unless immediately needed:

- race / ethnicity
- sex
- WAC-only firm age and firm size
- OD block-to-block flows

**Deferred OD ingest note**

OD is still part of the confirmed source contract for this family even though it is deferred from the current staging script. When we ingest it later, the expected first pass should:

- pull state-based `od` files with explicit `state_part` handling
- preserve both `w_geocode` and `h_geocode`
- decide the managed storage grain before landing the table, rather than defaulting to raw block-to-block persistence
- document Alaska and Michigan year gaps separately from the WAC/RAC path because OD availability is not identical by state-year

Those columns can still remain available in the tract staging tables, but narrowing the first modeled surface keeps `23.2.4` aligned to the roadmap language and avoids over-expanding the initial contract.

---

## 6. Transformation Notes

- LODES files are annual snapshots, not quarterly panels.
- The first-pass tract tables should be based on block aggregation, not on any published higher-geography files, because the source of truth is the block file plus the published geography crosswalk.
- `grab_lodes(..., agg_geo = "tract")` is acceptable for quick validation, but we should think of it as a convenience wrapper over block-native source files rather than as a separate upstream tract artifact.
- WAC and RAC are not perfectly symmetric:
  - both carry age, earnings, broad sector, race, ethnicity, education, and sex counts
  - only WAC carries firm age and firm size counts
  - only OD carries paired home/work block flows
- Educational attainment variables are only available for `2009+`.
- WAC firm age and firm size variables are only available for `2011+` and only for `JT02` all-private jobs.

**Recommended first-pass scope decision**

The narrowest viable scope for Track `23.2` is:

- `version = "LODES8"`
- latest available year
- `lodes_type = "wac"` and `lodes_type = "rac"`
- `job_type = "JT02"` all private jobs
- `segment = "S000"` if we want one full-payload file per state and family
- block-native download, then tract aggregation in staging
- OD deferred

Why `JT02` first:

- it gives one ownership definition shared by WAC and RAC
- it aligns with the private-sector emphasis already used elsewhere in Foundations
- it is the only WAC job type where firm age and firm size are populated in later years
- it avoids stitching together private and federal job-type branches on day one

Why `S000` first:

- the `S000` WAC and RAC files already contain the full wide payload for age, earnings, sector, race, ethnicity, education, and sex
- downloading only `S000` avoids multiplying state file counts by ten segment variants when the total-slice file already contains the fields we plan to model

**Managed staging decision**

We do not currently expect block-level analytical use in Foundations. The approved first-pass staging contract should therefore:

- download the source block files
- validate block IDs and crosswalk coverage during the run
- aggregate to tract immediately
- write tract-level `staging.lehd_lodes_wac` and `staging.lehd_lodes_rac`

That keeps staging materially smaller while preserving the tract-level neighborhood signals we actually plan to use now.

---

## 7. Data Quality Expectations

- LODES is a modeled administrative product, not a survey microdata extract, so no sampling error fields are provided.
- Census applies disclosure avoidance and warns that small-cell precision should not be treated as literal block truth.
- The public files may exist for a valid state-year combination even when a specific slice contains only headers because there are no jobs in that combination.
- Current Census documentation says:
  - demographic fields in RAC/WAC begin in `2009`
  - federal job types begin in `2010`
  - WAC firm age and firm size begin in `2011`
- Current Census documentation also states that some recent state-years are incomplete for `OD` and `WAC` even though `RAC` is still available.

For Foundations QA, the main expectations are:

- source block IDs should always be 15-character 2020 Census block codes
- staged tract IDs should resolve cleanly to 11-character prefixes
- state-level row counts will vary dramatically and should not be used as a fixed completeness heuristic
- Alaska and Michigan require special attention in the latest years because official coverage tables show missing `OD` and `WAC` data there for `2022-2023`

---

## 8. Operational Notes

- The official docs now describe `LODES 8.4` even though some older planning notes still refer to `8.3`.
- The live public root shows `LODES8/` rather than a nested `LODES8.4/` directory, so scripts should treat `LODES8` as the path and use `version.txt` / the tech doc for the format version label.
- The installed local `lehdr` wrapper is a reliable starting point for Track `23.2.2` in a way that the QWI wrapper was not for Track `23.1`.
- `grab_lodes()` defaults `state_part` to `main` for `od` if omitted; that behavior should be documented rather than relied on implicitly when OD is tackled later.
- Because `grab_lodes()` downloads one file per state-year-type combination, the implementation should process states sequentially and avoid parallel DuckDB writes.
- The staging script should preserve provenance columns such as `state`, `year`, `job_type`, `segment`, `createdate`, and `source_file` so we can audit mixed-vintage reruns after tract aggregation.

---

## 9. Known Gaps

- The current latest-year choice is no longer a trivial yes/no check. `2023` is the latest documented year, but official coverage tables show missing `OD` and `WAC` files for Alaska and Michigan in `2022-2023`. Before Track `23.2.2`, we should decide whether the first managed load prioritizes:
  - latest-year freshness with known geographic gaps, or
  - an older year such as `2021` for fuller national WAC coverage
- We have confirmed the source shape for OD, but we have not yet chosen the right deferred analytical grain for eventual OD modeling. County, tract-to-tract, and CBSA rollups each imply different storage and QA costs.
- Puerto Rico is not part of the current LODES coverage even though it is in the LED partnership.
- The source spec confirms the live file family structure, but we have not yet profiled representative large-state row counts locally. That volume check belongs in the staging implementation task.

## 10. Source References

- Census LEHD data page: `https://lehd.ces.census.gov/data/`
- Census LODES landing page: `https://lehd.ces.census.gov/data/#lodes`
- Census LODES root index: `https://lehd.ces.census.gov/data/lodes/`
- Census LODES technical document: `https://lehd.ces.census.gov/doc/help/onthemap/LODESTechDoc.pdf`
- Local runtime validation of `lehdr::grab_lodes()` via installed package version `1.1.4`
