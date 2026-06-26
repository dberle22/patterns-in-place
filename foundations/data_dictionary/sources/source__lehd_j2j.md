# Source Spec: LEHD J2J

## 1. Overview

- Source: U.S. Census Bureau
- Program: Longitudinal Employer-Household Dynamics (LEHD) Job-to-Job Flows (J2J)
- Access pattern in current first-pass scope: public bulk `csv.gz` release files plus `version_*.txt`, manifest files, and a J2JOD-only availability metadata file; no API key required
- Current verified live release as of `June 22, 2026`: `R2026Q1`
- Current verified live metadata schema version in release files: `V4.14.0`
- Current verified public schema documentation page: `j2j_latest`, titled `V4.13.0`, last updated `February 13, 2025`
- Native public geographies in the bulk release: national, state, and complete metropolitan / micropolitan areas
- Scope in Foundations: first-pass shared ingest should keep `J2J` counts only, defer `J2JR` to validation use, defer `J2JOD` to Deep Dive-specific work, and annualize a narrow rolling window across both state and metro files before staging
- Documentation goal: define what the three public J2J products are, confirm the live file shapes and coverage windows, and narrow the first-pass ingest surface before writing staging code

J2J is the LEHD product that measures worker reallocation across jobs rather than workforce composition at a point in time. It is the closest shared-data source in Foundations for labor-market fluidity, job laddering, and industry-switching behavior.

This is a topic-level child spec for the LEHD family. QWI and LODES should remain separate child specs because their file shapes, geography coverage, and downstream modeling rules differ materially.

---

## 2. Coverage Matrix

| Topic group | Staging family contracts | Silver outputs | Gold outputs |
| --- | --- | --- | --- |
| LEHD J2J counts | `staging__lehd_j2j.md` | `silver.lehd_j2j` | `gold.labor_j2j_wide` |
| LEHD J2JR published rates | deferred from shared first-pass ingest; optional validation companion only | deferred | deferred |
| LEHD J2JOD origin-destination flows | deferred from shared first-pass ingest; Deep Dive-specific follow-on | deferred | likely separate Deep Dive flow output if kept at pair grain |

---

## 3. Source Contract

- Provider: U.S. Census Bureau
- LEHD data landing page: `https://lehd.ces.census.gov/data/`
- J2J landing page: `https://lehd.ces.census.gov/data/#j2j`
- Current J2J bulk root: `https://lehd.ces.census.gov/data/j2j/`
- Current latest release root: `https://lehd.ces.census.gov/data/j2j/latest_release/`
- Current J2J schema page: `https://lehd.ces.census.gov/data/schema/j2j_latest/lehd_public_use_schema.html`
- Current J2J naming spec: `https://lehd.ces.census.gov/data/schema/j2j_latest/lehd_csv_naming.html`
- J2J data notices: `https://lehd.ces.census.gov/doc/J2J_data_notices.pdf`
- J2J Explorer: `https://j2jexplorer.ces.census.gov/`
- Authentication: none

**What we verified**

- The live `latest_release` index currently publishes `50` states plus `DC`, plus separate `metro/` and `us/` directories.
- The live public bulk release does not currently expose county directories the way QWI does.
- State directories are broken into three real public products:
  - `j2j/`: counts
  - `j2jr/`: rates
  - `j2jod/`: origin-destination flows
- Delaware `version_j2j.txt`, `version_j2jr.txt`, and `version_j2jod.txt` all currently report `2000:2-2025:1`, `V4.14.0`, `R2026Q1`.
- The schema / naming docs still point to `j2j_latest` pages titled `V4.13.0`, even though the live release metadata files report `V4.14.0`.

**Important terminology correction**

The public product name for the rates tables is `J2JR`, not `J2R`. If a planning note or discussion says `J2R`, the live release directories, filenames, manifests, and metadata all use `j2jr`.

**Local wrapper validation**

The installed `lehdr` package in this repo environment is version `1.1.4`. Local inspection on `June 22, 2026` did not find exported or internal helpers for J2J retrieval. That means Track `23.3` should treat direct Census bulk-file ingestion as the reliable baseline rather than assuming a `lehdr` J2J wrapper exists.

---

## 4. What The Three Public Products Are

J2J is published as three related but distinct public-use table families:

| Product | File prefix | What it is | Best use in Foundations |
| --- | --- | --- | --- |
| J2J counts | `j2j_` | Count tables for hires, separations, transitions between jobs, transitions to or from nonemployment, and selected average-earnings measures tied to those transitions | Canonical mobility counts, numerator fields, and earnings-change building blocks |
| J2J rates | `j2jr_` | Rate tables for the main hire / separation / persistence concepts in J2J | Canonical mobility rates when we want published rates rather than re-derived rates |
| J2J origin-destination flows | `j2jod_` | Paired origin and destination job-flow tables with origin geography and origin firm dimensions attached to destination-side rows | Industry-switching pairs, geographic labor import/export analysis, and origin vs destination earnings comparisons |

**Observed counts-table row shape**

Live Delaware `j2j` rows are keyed by:

- `periodicity`
- `seasonadj`
- `geo_level`
- `geography`
- `ind_level`
- `industry`
- `ownercode`
- `sex`
- `agegrp`
- `race`
- `ethnicity`
- `education`
- `firmage`
- `firmsize`
- `year`
- `quarter`
- `agg_level`

They then carry a wide measure payload including:

- macro hires / separations and job starts / ends: `MHire`, `MSep`, `MJobStart`, `MJobEnd`
- direct job-to-job and adjacent flow measures: `EEHire`, `EESep`, `AQHire`, `AQSep`, `J2JHire`, `J2JSep`
- nonemployment transition measures: `NEHire`, `ENSep`, `NEPersist`, `ENPersist`, `NEFullQ`, `ENFullQ`
- comparison counts and earnings: `MainB`, `MainE`, `EESepS`, `EEHireS`, `AQSepS`, `AQHireS`, `JobStayS`, `MainBS`, `MainES`, plus related earnings fields such as `EEHireSEarn_Dest`
- status flags for each major measure such as `sMHire`, `sEEHire`, `sAQHire`, `sJ2JHire`, and earnings-status fields

**Observed rates-table row shape**

Live Delaware `j2jr` rows use the same identifier columns as `j2j`, but the payload is the rate counterpart:

- `MHireR`, `MSepR`, `MJobStartR`, `MJobEndR`
- `EEHireR`, `EESepR`, `AQHireR`, `AQSepR`, `J2JHireR`, `J2JSepR`
- `NEHireR`, `ENSepR`, `NEPersistR`, `ENPersistR`, `NEFullQR`, `ENFullQR`
- status flags such as `sMHireR`, `sEEHireR`, `sAQHireR`, `sJ2JHireR`

**Observed origin-destination row shape**

Live Delaware `j2jod` rows use the same destination-side identifiers as `j2j`, then add explicit origin fields:

- `geo_level_orig`
- `geography_orig`
- `ind_level_orig`
- `industry_orig`
- `ownercode_orig`
- `firmage_orig`
- `firmsize_orig`

The J2JOD payload then includes:

- paired flow counts: `EE`, `AQHire`, `EES`, `AQHireS`
- paired earnings measures: `EESEarn_Orig`, `EESEarn_Dest`, `AQHireSEarn_Orig`, `AQHireSEarn_Dest`
- status flags for each measure

The schema notes that in J2JOD tables, the main firm characteristics should be interpreted as the destination firm, while the `_orig` columns describe the origin firm.

---

## 5. Native Release Shape

J2J is not one monolithic dataset. The live public bulk release is structured by geography scope first, then by product family.

**Directory layout**

- `latest_release/[state]/j2j/`
- `latest_release/[state]/j2jr/`
- `latest_release/[state]/j2jod/`
- `latest_release/metro/j2j/`
- `latest_release/metro/j2jr/`
- `latest_release/metro/j2jod/`
- `latest_release/us/j2j/`
- `latest_release/us/j2jr/`
- `latest_release/us/j2jod/`

**Observed state file pattern**

State directories currently publish the richer combination surface, including:

- demographic families `d`, `sa`, `rh`, `se`
- firm-detail families `f`, `fa`, `fs`
- industry detail `n` and `ns`
- ownership `oslp`
- unadjusted `u`

Examples from Delaware:

- `j2j_de_d_f_gs_ns_oslp_u.csv.gz`
- `j2jr_de_sa_f_gs_ns_oslp_u.csv.gz`
- `j2jod_de_se_f_gs_ns_oslp_u.csv.gz`

**Observed metro file pattern**

Metro bulk files are materially narrower than state files. The live metro directories currently publish one combined demographic family pattern per CBSA:

- `sarhe`
- `f`
- `gb`
- `ns`
- `oslp`
- `u`

Examples:

- `j2j_10180_sarhe_f_gb_ns_oslp_u.csv.gz`
- `j2jr_10180_sarhe_f_gb_ns_oslp_u.csv.gz`
- `j2jod_10180_sarhe_f_gb_ns_oslp_u.csv.gz`

That means metro bulk ingest does not currently offer the same menu of simplified demographic slices that state and national J2J do.

**Observed national file pattern**

National files currently use:

- `gn`
- both `u` and `s`
- `d`, `sa`, `rh`, `se`
- `f`, `fa`, `fs`
- `n` and `ns`

Examples:

- `j2j_us_sa_f_gn_ns_oslp_u.csv.gz`
- `j2j_us_se_f_gn_ns_oslp_s.csv.gz`

**J2JOD-only auxiliary metadata**

J2JOD publishes an additional file named `j2jod_[geohi]_avail.csv.gz`. This file records the possible time window for each origin-destination geography pairing:

- `geo_level`
- `geography`
- `geo_level_orig`
- `geography_orig`
- `start_year`
- `start_quarter`
- `end_year`
- `end_quarter`

Observed Delaware example rows show national-to-state and state-to-state pair windows such as:

- destination `N,00` with origin `S,10`: `2000Q2-2025Q1`
- destination `S,01` with origin `S,10`: `2001Q2-2025Q1`

This file is important because J2JOD suppression and data availability are pair-specific, not just geography-specific.

---

## 6. Historical Coverage And Suppression Behavior

**Verified live metadata**

- Delaware `J2J`: `2000:2-2025:1`
- Delaware `J2JR`: `2000:2-2025:1`
- Delaware `J2JOD`: `2000:2-2025:1`
- Many metro series also begin around `2000:2`, but the live metro `version_j2j.txt` shows that coverage varies materially by CBSA

Examples from the live metro metadata:

- `10180`: `2000:2-2025:1`
- `02999`: `2001:2-2016:1`
- `09999`: `2010:2-2024:2`

**Most recent available year**

The most recent source year in the current live public release is `2025`, but the verified Delaware `R2026Q1` files currently only contain `2025 Q1`. That means:

- the source is current through calendar year `2025`
- the most recent fully observed year is `2024`
- a rolling completed-year window should use `2020-2024` if we want the latest `5` full years

**Important availability rule**

The J2J data notices explicitly state that lower levels of geography may have shorter time series than the national data because of state input availability. The live metro metadata confirms that this is not a theoretical caveat; it is a real property of the public files.

**Suppression behavior that matters for Track 23**

- J2J uses publication-status flags on the tables themselves, just like other LEHD products.
- J2JOD has an additional geography-pair availability file because some region pairs are only observable for part of the release window.
- The J2J data notices document multiple rounds of subnational suppression and state-specific non-current production.
- The notices also state that Puerto Rico and the Virgin Islands are experimental and not publicly available in the current production stream.

**Planning implication**

For Foundations, metro-level geographic flow work should assume:

- shorter and uneven history across CBSAs
- more suppression than state-level tabulations
- a need to validate geography pairs against `*_avail.csv.gz` before treating missing rows as zeroes

---

## 7. Recommended First-Pass Scope

The simplest high-value first pass is narrower than the full public surface.

**Recommended analytical split**

1. Treat `j2j` as the canonical first-pass mobility table.
2. Treat `j2jr` as an optional validation companion rather than a managed first-pass table.
3. Defer `j2jod` until a specific Deep Dive needs O-D labor-flow detail.
4. Keep state and metro ingestion separate because their file menus differ.

**Why not ingest `J2JR` in the shared first pass**

The Delaware spot-check showed that `J2J` and `J2JR` have the same dimensional lattice:

- both files had `148,970` data rows in the live `all` extracts
- both covered the same `2000 Q2-2025 Q1` window
- both used the same geography, demographic, industry, and firm-slice keys

The difference is payload, not grain:

- Delaware `J2J`: `87` columns and `8.7 MB` compressed
- Delaware `J2JR`: `49` columns and `3.7 MB` compressed

That means persisting both would largely duplicate the same row space. For Foundations, the simpler contract is:

- store `J2J` counts and earnings payload
- derive annual rates from those staged counts in Silver
- use `J2JR` only if we later want a QA parity check against published Census rates

**Recommended first-pass counts slice**

- Start with `j2j` only
- Ingest both state and metro files
- Use `demo = sa` for worker age and keep only all-sex rows downstream
- Use `fas = f`
- Use `indcat = ns`
- Use `owncat = oslp`
- Use `sa = u`
- Retain only the latest rolling `5` completed years
- Annualize quarter rows to one row per geography / year / industry / demographic slice before writing staging

This gives a manageable first pass for worker age by industry mobility without immediately exploding the surface with firm-age, firm-size, race/ethnicity, education, seasonally adjusted variants, O-D pair detail, or duplicate published-rate storage.

**State and metro file note**

The current shared ingest should cover both:

- state files, which use the `sa` family directly
- metro files, which use the combined `sarhe` family

For metro files, the age-only first-pass slice should still be enforced downstream by keeping:

- `sex = 0`
- `race = A0`
- `ethnicity = A0`
- `education = E0`

**Recommended annualization rule**

- If the active release still ends at `2025 Q1`, keep `2020-2024` as the rolling `5` full-year window.
- If a later release fills all four quarters of `2025`, the rolling window can advance to `2021-2025`.
- Sum annual flow counts such as `MHire`, `MSep`, `EEHire`, `EESep`, `AQHire`, `AQSep`, `J2JHire`, `J2JSep`, `NEHire`, and related counts.
- Average stock-like or average-earnings fields across the observed quarters after validating the quarter count.
- Preserve `quarters_observed` so incomplete years remain detectable during QA.

This mirrors the current QWI simplification pattern: reduce the quarterly panel to an annual staging table, keep only a recent rolling history window, and let Silver own the derived normalized outputs.

**Important scope correction for Track 23.3**

The live public bulk release is national / state / metro oriented, not county-native. If Foundations needs county-grain J2J later, that will require a different extraction path than the current public bulk directory structure. Track `23.3.2` should not assume county bulk files exist upstream, and the shared first pass should exclude `J2JOD`.

---

## 8. Preferred Staging Contract

Preferred first-pass staging tables:

- `staging.lehd_j2j`

Recommended shared provenance columns:

| Column | Type | Description |
| --- | --- | --- |
| `product_type` | VARCHAR | Expected `j2j` in the shared first-pass contract |
| `periodicity` | VARCHAR | Managed periodicity, expected `A` after annualization |
| `source_periodicity` | VARCHAR | Published source periodicity, expected `Q` |
| `seasonadj` | VARCHAR | `U` or `S` |
| `geo_level` | VARCHAR | Destination geography level |
| `geo_id` | VARCHAR | Destination geography code |
| `ind_level` | VARCHAR | Destination industry aggregation level |
| `industry_code` | VARCHAR | Destination industry code |
| `ownercode` | VARCHAR | Ownership code |
| `sex` | VARCHAR | Worker sex code |
| `agegrp` | VARCHAR | Worker age code |
| `race` | VARCHAR | Worker race code |
| `ethnicity` | VARCHAR | Worker ethnicity code |
| `education` | VARCHAR | Worker education code |
| `firmage` | VARCHAR | Destination firm age code |
| `firmsize` | VARCHAR | Destination firm size code |
| `year` | INTEGER | Source year |
| `agg_level` | INTEGER | LEHD aggregation index |
| `quarters_observed` | INTEGER | Number of source quarters rolled into the annual row |
| measure payload | DOUBLE | Counts, rates, or earnings fields depending on product |
| status payload | INTEGER | Census status / suppression flags |
| `source_file` | VARCHAR | Source filename |
| `release_id` | VARCHAR | Release stamp such as `R2026Q1` |
| `schema_version` | VARCHAR | Metadata schema version such as `V4.14.0` |
| `state_scope` | VARCHAR | State code, `metro`, or `us` |
| `source_scope_type` | VARCHAR | `state` or `metro` |
| `source_scope_id` | VARCHAR | State abbreviation for state files or metro code for metro files |
| `keep_start_year` | INTEGER | First retained year in the rolling 5-year completed window |
| `keep_end_year` | INTEGER | Last retained fully observed year in the retained window |

The shared first-pass staging contract should not carry J2JOD origin fields because O-D work is deferred.

---

## 9. Operational Notes

- The live public release metadata are current through `R2026Q1`, while the public schema documentation pages still advertise `V4.13.0`. Staging code should trust the live metadata files for release provenance and use the docs for structure unless we find a field mismatch.
- The J2J data notices were updated on `April 29, 2026` and should be treated as required context for state-specific caveats.
- Beginning with the June 2020 release notes, J2J added average-earnings measures for job-to-job transitions to the CSV tables; they are part of the current live core-table shape.
- The July 2021 notices state that subnational seasonally adjusted J2J series were suppressed in that release window. Even though current national files publish both `u` and `s`, the safest first pass is still `u`.
- The Delaware `all` extracts confirm that `J2J` and `J2JR` share the same row lattice, so keeping both in the shared first pass would mostly duplicate storage rather than expand coverage.
- A Delaware spot-check also confirmed that the current live release reaches source year `2025` but only includes `Q1` for that year. The simplest first-pass annualization rule is therefore to keep the latest `5` completed years, currently `2020-2024`.
- J2JOD metro files are extremely large relative to J2J and J2JR. Live examples in `R2026Q1` include hundreds of megabytes compressed for a single metro file, which is a strong signal to keep O-D work narrow and sequential when Deep Dive needs arise.
- Because the public bulk release is not county-native, any later county-grain design should be treated as a separate research decision rather than assumed from the QWI pattern.
