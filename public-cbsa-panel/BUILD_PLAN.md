# Metro & Micro Panel Build Plan

**Release:** v2026.1  
**Status:** v2026.1 published on Zenodo September 28, 2026; GitHub release hygiene and outreach remain  
**Project:** Patterns in Place: Metro & Micro Panel (`pip-metro-micro-panel`)
**Published:** September 28, 2026

## Outcome

Publish a citable, versioned public release containing a static current-vintage county-to-CBSA crosswalk and two documented CBSA-year panels. The canonical v1 release is archived on Zenodo with a DOI. Source Cooperative may become an additional query-oriented mirror if beta-publisher access is approved.

This plan follows the locked v1 scope in [v2026.1_scope.md](spec/v2026.1_scope.md). “Dan” tasks require account ownership, editorial judgment, or an external post. “Code” tasks are implementation and verification work in this monorepo.

> Assumption: “posting our models” means publishing the release artifacts and launch materials, not exposing private warehouse models. The public release contains only the three approved tables and their documentation.

## Delivery gates

| Gate | Must be true before advancing |
| --- | --- |
| Public contract | Every release field has approved lineage; Zillow and held-back sources are absent. |
| Release candidate | Export, validation, coverage report, and generated docs all pass from one command. |
| Publish-ready | Public repo, Zenodo record, licenses, citation, and release assets are ready. |
| Launch-ready | Downloadable DuckDB quickstart and DOI work from a clean environment; the analysis and outreach materials are approved. |

## Post-publication handoff

The v2026.1 data-release milestone is complete: Zenodo is the immutable canonical copy,
with the version DOI and concept DOI recorded in `RELEASES.md`. The remaining work below is
deliberately separated into (1) a companion GitHub code release, (2) optional distribution,
(3) outreach, and (4) investigations that should inform v2. A new agent should treat the
published Zenodo files as read-only and create a *new Zenodo version* for any correction or
refresh.

## Foundation prerequisite — County-first CBSA data refresh

**Goal:** refresh and validate the shared county inputs and aggregation logic that the public
panel will consume. This is a Foundations-owned epic, assigned to a dedicated agent before the
exporter begins.

The complete task list and acceptance criteria are in
[`foundations/archive/2026-09_county_first_cbsa_refresh/EPIC_COUNTY_FIRST_CBSA_REFRESH.md`](../foundations/archive/2026-09_county_first_cbsa_refresh/EPIC_COUNTY_FIRST_CBSA_REFRESH.md) (done; archived).
It covers BEA county GDP through 2024, historical county HUD FMR, and BEA-correct real-GDP
aggregation. It establishes the county-first contract; it does not publish the public release.

- [x] Create and link the dedicated Foundations epic for the county-first refresh.

## Epic 1 — Establish the public data contract

**Goal:** turn the conceptual scope into an auditable, column-level release contract before any public build code exists.

### Code tasks

- [x] Create `audit/public_column_lineage.csv` with one row per candidate public field: public table/column, private source table/column, agency, source dataset, upstream variable, transformation, units, source vintage, coverage window, null behavior, and Zillow review result.
- [x] Trace the selected ACS, BEA, HUD FMR, and Census/OMB geography fields through the private Gold and Silver builds.
- [x] Verify `affordability_wide.value_to_income` uses ACS `B25077` median home value for the public calculation; no public-only replacement is needed.
- [x] Confirm the 2023 CBSA delineation source/vintage, 935-CBSA universe, county membership, central/core-versus-outlying designation, and established primary-state rule.
- [x] Record lineage gaps, sparse coverage, and source references in `audit/lineage.md` and `audit/source_references.md`.
- [x] Create draft `config/tables.yml` with ordered fields, types, required/null thresholds, and coverage expectations.
- [x] Review the draft allowlist with Dan, remove non-county RPP fields and redundant CBSA flags, retain annualized rent, and freeze the approved configuration pending Foundations validation.

### Dan tasks

- [x] Review and approve proposed field removals and the annualized-rent public field before the contract was frozen.
- [x] Confirm the desired citation name: Dan Berle as author and Patterns in Place as the project brand.

**Acceptance:** `config/tables.yml` is complete; every included column has auditable lineage; no included lineage references Zillow, BFS, CBP, QCEW, CHAS, permits, vacancy, or occupancy.

**Completed:** The v1 allowlist is approved pending Foundations validation. It retains annualized
median rent, removes redundant CBSA boolean flags and non-county RPP fields, and makes public
BEA and HUD field names source-explicit.

## Epic 2 — Build the release exporter

**Goal:** deterministically create the three allowed public tables from the private Gold DuckDB.

### Code tasks

- [x] Define a single release command and its required input: private Gold DuckDB path, release version, and output directory.
- [x] Build the crosswalk extraction for `cbsa_county_crosswalk`, using only the approved current-vintage geography fields.
- [x] Build fact-table extraction for `economics_industry_wide` and `affordability_wide`, filtering to `geo_level = 'cbsa'` and the approved field allowlists.
- [x] Apply all public names, column order, types, and public-only derived calculations from `config/tables.yml`.
- [x] Write one ZSTD-compressed Parquet file per table and a bundled DuckDB file containing the three tables plus `_manifest`.
- [x] Write `manifest.json` with release version, hashes, row counts, schema, source/table/column vintages, and build metadata.
- [x] Keep generated files under gitignored `output/`; do not place private data or absolute local paths in committed files.

### Dan tasks

- [x] Set the intended v2026.1 release date: September 25, 2026, subject to release-candidate readiness.

**Acceptance:** one command produces Parquet, bundled DuckDB, and manifest from the Gold DuckDB without manual table editing.

**Completed:** `scripts/build_release.py` reads the approved contract, produces the three ZSTD
Parquet files and bundled DuckDB, and omits local private paths from the manifest. The final
production run waits for the Foundations handoff.

## Epic 3 — Validate the data and release contract

**Goal:** fail closed when an export is incomplete, out of scope, or structurally inconsistent.

### Code tasks

- [x] Validate fact-table uniqueness on `(geo_level, geo_id, year)` and crosswalk uniqueness on its declared county-to-CBSA membership key.
- [x] Validate that output columns exactly match `config/tables.yml` and ordered key fields are first.
- [x] Validate CBSA-only fact-table geography and the expected 935-CBSA crosswalk universe.
- [x] Validate required-field null thresholds, data types, valid years, and non-null identifiers.
- [x] Scan configured lineage and build inputs for Zillow and other held-back source dependencies.
- [x] Compare schema, row counts, and coverage with the preceding release when one exists; require an explicit override for approved differences.
- [x] Generate `coverage_report.md`: table-level totals, fact-table annual coverage, crosswalk coverage, null rates, and numeric summaries.
- [x] Add focused automated tests for successful and intentionally failing validations.

### Dan tasks

- [x] Review the first coverage report, approve the release treatment for sparse BEA industry fields, and log the remaining coverage investigation for v2.

**Acceptance:** validation passes for a release candidate; each intentionally invalid fixture fails with a useful message; the coverage report contains no unexplained major anomaly.

**Completed:** the release builder validates the contract before writing; focused fixtures cover
valid output, duplicate keys, non-CBSA fact rows, bundled DuckDB contents, and an unapproved
prior-release coverage change.

## Epic 4 — Produce public documentation and examples

**Goal:** give an unfamiliar researcher enough information to use and cite each field without contacting us.

### Code tasks

- [x] Generate table reference pages from the data dictionary and `config/tables.yml`, including every public field’s source dataset, upstream variable, units, formula, coverage, and null behavior.
- [x] Write `METHODOLOGY.md` covering the static delineation vintage, crosswalk construction, primary-state rule, ACS five-year interpretation, overlapping windows, source-specific vintages, suppression/missingness, and formulas.
- [x] Write the public-repository handoff README (`PUBLIC_REPOSITORY_README.md`): one-sentence purpose, configurable downloaded-DuckDB query, table inventory, coverage caveats, license, citation, DOI location, and links to the full methodology.
- [x] Write `RELEASES.md` and `CHANGELOG.md`; make v2026.1’s source vintages and known limitations explicit.
- [x] Add `examples/quickstart.sql`, `examples/quickstart.py`, and `examples/quickstart.R`; each accepts the eventual published Parquet directory rather than a machine-specific local path.
- [x] Prepare a data `CITATION.cff`, CC-BY-4.0 data license statement, MIT code license, and federal-source attribution statement.
- [x] Add `FUTURE_RELEASE_NOTES.md` for release follow-ups, beginning with the BEA industry-coverage review.
- [x] Scan public-bound files for private paths, credentials, internal table names not needed for provenance, and unsupported claims.

### Dan tasks

- [x] Review the methodology’s caveats and the final citation language for accuracy and tone.

**Acceptance:** no public field lacks an upstream-variable reference; no documentation has `TBD`; all examples work against the release candidate.

## Epic 5 — Establish the public home and publish v2026.1

**Goal:** make the immutable release available, citable, and independently queryable.

### Dan tasks

- [x] Use the personal GitHub identity `dberle22` to own `metro_micro_panel`.
- [x] Create a personal Source Cooperative account.
- [x] Submit the Source Cooperative beta-publisher application.
- [ ] Obtain Source Cooperative beta-publisher access, then create an optional public distribution mirror.
- [x] Create a Zenodo account using the `dberle22` GitHub identity.
- [x] Enable the public GitHub repository in Zenodo after the initial push.
- [x] Create `dberle22/metro_micro_panel` and transfer the public documentation, release metadata, examples, and public artifact verifier from this workspace. The private Foundations build remains private.
- [x] Review the final release candidate and explicitly authorize publication.
- [x] Publish v2026.1 Parquet, DuckDB, manifest, coverage report, and citation metadata to the canonical Zenodo dataset record.
- [ ] Create GitHub release tag `v2026.1` as a companion code release and link it to the published Zenodo dataset.
- [ ] In the GitHub release notes, state that Zenodo is canonical, link both Zenodo DOIs, and do not upload duplicate data artifacts to GitHub.
- [ ] When Source Cooperative responds, either create an optional mirror using the identical Zenodo filenames and checksums, or record that access was not granted and close this task without blocking a future release.

### Code tasks

- [ ] Add a release workflow that checks tag/path/manifest version agreement before a future upload.
- [x] Make the public repo reproducibly package the docs, code, coverage report, and release metadata without private inputs or credentials.
- [x] Verify Zenodo file hashes against the final candidate manifest.
- [x] From a clean downloaded release with DuckDB only, query both published Parquet and bundled DuckDB files.
- [ ] Verify the GitHub citation widget, license links, version DOI, and concept DOI resolve to the intended release.
- [ ] Record the date and outcome of the live GitHub and Zenodo metadata check in `RELEASES.md`.

**Acceptance:** the public URLs work; the clean-download query returns rows; the DOI resolves; checksums match; all public metadata identifies v2026.1. Source Cooperative access is not a v2026.1 completion dependency.

## Epic 6 — Publish the analysis and outreach materials

**Goal:** launch through a useful finding, not a bare dataset announcement.

### Code tasks

- [ ] Select a first analysis question whose inputs have suitable v2026.1 coverage. Do not use sparse BEA GDP-share fields or BEA GDP industry HHI as a headline until Epic 7 resolves their missingness.
- [ ] Produce the first analysis using only documented v2026.1 public fields; an ACS industry-concentration analysis is the initial candidate because its coverage is suitable for a broad CBSA comparison.
- [ ] Create one publication-ready chart with a reproducible query/script and source note.
- [ ] Draft a 100-word dataset description, downloadable-DuckDB query snippet, and screenshot/code-result asset. Do not promise a remote DuckDB endpoint until one is actually operated.
- [ ] Draft channel-specific copy for Data Is Plural, NICAR-L, Bluesky, Cloud-Native Geospatial Forum, and LinkedIn.
- [ ] Document the analysis query and caveats so its claims can be reproduced from v2026.1.

### Dan tasks

- [ ] Edit and publish the selected first analysis after the quiet release verification.
- [ ] Submit the dataset to Data Is Plural.
- [ ] Post the plain-text quickstart and release description to NICAR-L.
- [ ] Post the finding-led Bluesky thread, then the crosswalk/Parquet architecture write-up to Cloud-Native Geospatial Forum.
- [ ] Decide whether the Hacker News framing is strong enough to post; skip it if it is not.
- [ ] Publish a later LinkedIn methodology post after there is a concrete usage or feedback story.
- [ ] Monitor replies, issues, and reuse; log actionable documentation problems for the next release.

**Acceptance:** the analysis is live and links to v2026.1; outreach is staggered rather than simultaneous; every public claim is reproducible from the released data.

## Epic 7 — Operate the release and prepare v2

**Goal:** make future releases cheaper without delaying v2026.1 for automation.

### Code tasks

- [ ] Add a scheduled upstream-vintage check for ACS, BEA, HUD FMR, and delineation updates; open an issue when a newer source is detected.
- [ ] Add release-to-release schema and coverage comparisons using the prior manifest.
- [ ] Document the human review and approval step for every immutable version.
- [ ] Investigate BEA professional GDP-share coverage end-to-end: profile raw county CAGDP9 lines 60, 64, and 65 by year; trace suppression and null handling through county-to-CBSA aggregation; and test whether all-component completeness creates avoidable nulls.
- [ ] Investigate BEA education/health GDP-share coverage with the same method for CAGDP9 line 68, identifying the precise source or aggregation mechanism for each missingness pattern.
- [ ] Reassess BEA GDP industry HHI only after those two reviews: reproduce the 147-of-935 2024 result, determine whether it is source sparsity or calculation behavior, and recommend retain, recalculate, or defer.
- [ ] Write each investigation's evidence, decision, and any proposed contract change in `FUTURE_RELEASE_NOTES.md`; do not change a published v2026.1 artifact.
- [ ] Before any v2 upload, build a new candidate directory, regenerate the manifest and coverage report, run the public artifact verifier, compare it with v2026.1, and have Dan approve the changelog and coverage diff.
- [ ] Publish a v2 correction or refresh as a new Zenodo version under the existing concept DOI; never modify or replace files in the published v2026.1 record.
- [ ] Maintain a v2 candidate list for BEA GDP concentration HHI; BFS, CBP, QCEW, CHAS, permits, vacancy, and occupancy, with the documentation cost and coverage threshold for each addition.

### Dan tasks

- [ ] Review external feedback and decide whether any v2 candidates solve a demonstrated user need.
- [ ] Approve a refresh only after reviewing the coverage diff and changelog.

**Acceptance:** a future refresh can identify source changes, build a candidate, show its differences, and wait for human approval before publication.

## Execution order

1. The Foundation prerequisite and Epic 1 are blocking: no exporter or public repository before
   the county-first inputs are validated and the public contract is audited.
2. Epics 2 and 3 proceed together, then Epic 4 uses the validated release candidate.
3. Epic 5 publishes only after the Foundation prerequisite and Epics 1–4 pass their acceptance
   criteria.
4. The data portion of Epic 5 is complete. Its GitHub companion release and optional Source
   Cooperative mirror may proceed independently of the immutable Zenodo record.
5. Epic 6 can begin now; it must select an analysis supported by the documented coverage.
6. Epic 7 follows publication and must not delay v2026.1.

## Main release definition of done — met

v2026.1's main release is complete when the three approved tables are publicly accessible and
immutable; a clean download can be queried with DuckDB; a Zenodo DOI and citation metadata
resolve; and every published column has a documented upstream variable and vintage. These
conditions are met by the Zenodo record published September 28, 2026.

## Full program definition of done

The broader launch program is complete when the companion GitHub release is verified, the
first reproducible analysis and selected outreach are published, and v2 investigations have
documented evidence and decisions. Source Cooperative remains an optional distribution mirror,
not a completion gate.
