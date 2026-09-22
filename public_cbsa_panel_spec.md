# Patterns in Place: Public CBSA Panel Release Spec

**Status:** Draft · **Last updated:** 2026-09-20 · **Owner:** Dan

## Purpose

Publish a small, well documented, citable slice of the Patterns in Place Gold layer as an open CBSA panel, so that the harmonization work is visible and reusable by other people.

The product is not the underlying data. ACS, BEA and HUD are all publicly available. The product is the harmonization: 401 CBSAs on a single grain of `(geo_level, geo_id, geo_name, year)`, with the crosswalk decisions, CBSA vintage rebasing and derived metric formulas written down. Framed for an outside reader: this is the join you do not want to do.

### Goals

1. A citable research artifact with a DOI, usable as a portfolio and application credential.
2. A zero friction access path: one DuckDB query, no signup, no download required.
3. Documentation good enough that a stranger can trace any column back to its upstream source variable without asking.
4. A repeatable release process, so v2 costs a day instead of a month.

### Non-goals

- Revenue, licensing or any commercial path.
- Completeness. This is three tables, not the warehouse.
- A hosted API, query UI or dashboard. Those are separate products.
- Real time or high frequency data. Sources are annual or quarterly.

### Success criteria

| Criterion | Target |
| --- | --- |
| Release published with DOI | v2026.1 live on Source Cooperative and Zenodo |
| Quickstart query works from a clean machine | Verified, no local install beyond DuckDB |
| Accompanying analysis published | One post using the released tables, same window |
| External pickup | At least one of: Data Is Plural, NICAR-L reply, third party use |
| Rebuild cost | Full release rebuildable by one command |

## Release contents (v2026.1)

Three tables. One is the spine, one is differentiated, one is the download driver.

| Table | Role | Source Gold table | Upstream | Why it ships |
| --- | --- | --- | --- | --- |
| `geo_dim` | Spine | `silver.xwalk_*` + CBSA membership | Census TIGER, county to CBSA 2023 | Lets anyone join their own county data up to the CBSA panel. Puts the crosswalk work on display. |
| `economics_industry_wide` | Differentiated | `gold.economics_industry_wide` | BEA | Sector shares and HHI at CBSA grain, consistently built across 401 metros. Nobody publishes this clean. Substrate for the first analysis. |
| `affordability_wide` | Download driver | `gold.affordability_wide` | ACS, HUD FMR | Rent to income, value to income, FMR gap. Cross domain and derived. The table journalists will actually use. |

### Zillow removal

Zillow is out of the public release entirely. Before build, audit `gold.affordability_wide` for any ZHVI or ZORI derived columns. If `value_to_income_ratio` is built on ZHVI, rebuild it on ACS median home value (`B25077`) for the public table. Keep the Zillow version internal and unreleased. The public build should have no Zillow dependency in its lineage at all, not just no Zillow columns in the output.

### Held back from v1

| Table | Reason |
| --- | --- |
| `economics_labor_wide` | LAUS unemployment is easy to get from BLS directly. Documentation burden without scarcity. |
| `economics_gdp_wide` | Headline metro GDP is a straightforward BEA pull. Superseded by the industry table for our purposes. |
| `housing_core_wide` | Zillow entanglement plus high column count. Candidate for v2 after the Zillow audit. |
| `population_demographics` | Widely mirrored elsewhere. Adds bulk, not value. |
| `migration_wide`, `transport_built_form_wide` | Thin relative to the ACS originals. Revisit when IRS flows land. |
| Composite and intelligence scores | Not production ready. Publishing unvalidated scores would undercut the credibility the rest of the release is buying. |
| `tx_isd_metrics` | Off the CBSA grain. Different release entirely. |

### Coverage

To confirm during build and state explicitly in the README: year range per table, CBSA count per year, and whether the panel is balanced. CBSA definitions change between vintages, so the panel is almost certainly unbalanced at the edges. That is fine, but it has to be documented, not discovered.

## Repo scaffolding

A new standalone public repo, separate from `metro_deep_dive`. The platform repo stays private. This repo contains the export build, the docs, and nothing else.

Working name: `pip-cbsa-panel`.

```markdown
pip-cbsa-panel/
├── README.md                  # what it is, grain, coverage, quickstart, license, citation
├── METHODOLOGY.md             # crosswalks, CBSA vintage rebasing, ACS interpretation, formulas
├── CHANGELOG.md               # one section per release
├── RELEASES.md                # per source vintage status and next upstream release date
├── LICENSE                    # CC-BY-4.0
├── CITATION.cff               # GitHub citation widget + Zenodo pickup
├── docs/
│   ├── geo_dim.md
│   ├── economics_industry_wide.md
│   └── affordability_wide.md
├── build/
│   ├── export.py              # Gold DuckDB -> public Parquet + bundled .duckdb
│   ├── tables.yml             # table + column allowlist, renames, descriptions
│   ├── validate.py            # contract checks, fails the build
│   └── coverage_report.py     # generates validation/coverage_report.md
├── validation/
│   └── coverage_report.md     # generated, committed, diffable per release
├── examples/
│   ├── quickstart.sql
│   ├── quickstart.py
│   └── quickstart.R
├── .github/workflows/
│   └── release.yml            # tag -> build, validate, upload, Zenodo
└── data/v2026.1/              # gitignored locally, published to Source Cooperative
    ├── geo_dim.parquet
    ├── economics_industry_wide.parquet
    ├── affordability_wide.parquet
    ├── pip_cbsa_panel.duckdb
    └── manifest.json          # file hashes, row counts, build timestamp, source vintages
```

### Conventions

- Table and column names in the public release are snake_case and frozen. A rename is a breaking change and gets a major version.
- `tables.yml` is the single source of truth for what is public. The exporter never reads a table not listed there. This is the guard that keeps internal columns, including anything Zillow derived, out of the release by construction.
- Every table carries `geo_level`, `geo_id`, `geo_name`, `year` as the leading columns, in that order.
- Every table carries a `source_vintage` column or, where a single value applies to the whole table, a documented table level vintage in `manifest.json`.
- Parquet files use ZSTD compression and are written as a single file per table, not partitioned. At this row count partitioning adds friction for readers and buys nothing.
- `manifest.json` is machine readable and is what a downstream user or a future refresh job checks against.

## Documentation spec

The data dictionary already exists in `schemas/data_dictionary/layers/gold/`. Most of this is a rendering job, not a writing job. Generate `docs/*.md` from the dictionary YAML where possible so the docs cannot drift from the schema.

### README.md

Order matters. A reader decides in fifteen seconds whether to keep going.

1. One sentence: what this is and what grain it is on.
2. The quickstart query, above the fold, copy and paste ready.
3. Table inventory: three rows, name, what it covers, years, row count.
4. Coverage and caveats in three bullets.
5. License, citation block, DOI badge.
6. Links to `METHODOLOGY.md`, `docs/`, `RELEASES.md`.

Quickstart, verbatim in the README:

```sql
INSTALL httpfs; LOAD httpfs;
SELECT * FROM read_parquet('https://data.source.coop/<org>/pip-cbsa-panel/v2026.1/affordability_wide.parquet') LIMIT 10;
```

### METHODOLOGY.md

This is the document that carries the credibility. Sections:

- **CBSA definition and vintage.** Which delineation vintage, why 2023 county membership, how earlier years are rebased onto it, and what that does to comparability across the panel.
- **Crosswalk construction.** How county to CBSA mapping is built, how splits and merges are handled, what happens to counties with no CBSA.
- **ACS interpretation.** Five year rolling estimates, what `year` means (end year of the window), why overlapping windows mean year over year deltas are not independent observations.
- **Suppression and missingness.** How suppressed or unreliable estimates are represented, and whether margins of error are carried.
- **Derived metric formulas.** Every computed column written out as a formula, not prose.
- **Known issues.** An honest list. This section buys more trust than any other.

### Per table doc template

Identical structure for all three files in `docs/`:

1. **Header.** Table name, one line description, grain, primary key.
2. **Coverage.** Years, geo levels, row count, distinct CBSA count, balanced or unbalanced.
3. **Column table.** The core of the document:

| Column | Type | Definition | Units | Upstream source | Upstream variable | Null behavior |
| --- | --- | --- | --- | --- | --- | --- |

The `Upstream variable` column is the one that separates this from every other scraped panel. A reader should be able to trace `rent_to_income_ratio` back to specific ACS table numbers without asking.

4. **Derived formulas.** For any computed column, the formula in a latex block.
5. **Caveats.** Table specific gotchas.
6. **Example queries.** Two or three, showing the table doing something real.

### Coverage report

`validation/coverage_report.md` is generated by `build/coverage_report.py` and committed with each release. Contents: row count by table by year, distinct CBSA count by year, null rate by column by year, and min/max/median for numeric columns.

This is a small build with outsized payoff. Null rates by year make suppression and coverage gaps visible up front instead of something a user finds three hours in. It is also diffable between releases, which is how you catch an upstream schema change.

### CITATION.cff

Standard CFF, with `type: dataset`, author, title, version, DOI and release date. GitHub renders a citation widget from it and Zenodo reads it on release.

## Hosting, versioning, licensing

Three hosts, three jobs. No single vendor sits between a reader and the data.

| Host | Holds | Why |
| --- | --- | --- |
| [Source Cooperative](https://source.coop) | Canonical Parquet + bundled `.duckdb` | Free for public data, nonprofit (Radiant Earth), HTTP range readable so DuckDB queries remotely with no download. Audience skews research and civic data. |
| GitHub | Docs, build code, release tags, coverage reports | Where the methodology lives and where issues get filed. Docs render via Pages. |
| [Zenodo](https://zenodo.org) | Versioned archive + DOI | Turns a repo into a citable artifact. Hooks to GitHub releases, mints a DOI per version plus a concept DOI for the dataset as a whole. |

MotherDuck is deliberately not in v1. A MotherDuck share requires the consumer to hold a MotherDuck account in the same cloud region and attach the share to their workspace. That is fine as a convenience path for people already on the platform, and wrong as the front door. Revisit as a secondary surface after v1 ships.

### Formats

Publish both, always:

- **Parquet, one file per table.** Powers the zero friction quickstart. This is the format the release is actually judged on.
- **A single bundled `.duckdb` file.** The "just give me the whole thing" path. Includes all three tables plus a `_manifest` table.

### Versioning

- Scheme: `vYYYY.N`, so `v2026.1` is the first release of 2026.
- Releases are immutable. A published version is never overwritten, never patched in place. A mistake gets `v2026.2`, and `CHANGELOG.md` says what was wrong.
- No `latest` alias in the data paths. Readers must cite a version. A moving target is uncitable.
- Schema changes: an added column is a minor release. A removed or renamed column, or a changed definition for an existing column, is a new year band or a documented breaking change called out at the top of the changelog.
- The git tag, the Source Cooperative path, the Zenodo version and `manifest.json` all carry the same version string. The release workflow should fail if they disagree.

### Licensing

- Derived tables: **CC-BY-4.0**. Attribution is the point, given the goals.
- Upstream is entirely federal (ACS, BEA, HUD, Census TIGER), so there is no redistribution constraint to manage once Zillow is out.
- `README.md` carries an explicit upstream attribution block naming each source agency and dataset, separate from the license.
- Build code: MIT, so the pipeline itself is reusable.

## Refresh automation

Refresh is an internal pipeline concern, not a release cadence promise. The public release is versioned and occasional. The automation exists so that producing a version is cheap and so that upstream releases do not sit unnoticed for months.

### Per source cadence

| Source | Upstream cadence | Typical release window | Triggers a new panel version |
| --- | --- | --- | --- |
| ACS 5 year | Annual | December | Yes, this is the main driver |
| BEA regional (GDP by industry) | Annual, with revisions | Late year, revisions ongoing | Yes |
| HUD FMR | Annual | Late summer, FY effective October | Yes |
| Census TIGER / CBSA delineations | Irregular, OMB bulletins | Irregular | Only on a delineation change, which is a breaking change |

Realistically that is one panel release per year plus a revision release. `RELEASES.md` states this plainly and lists the next expected upstream date per source. A status table that says "ACS vintage 2023, next upstream December 2026" reads as rigor. Implying a refresh cadence the sources cannot support does the opposite.

### Pipeline shape

```mermaid
flowchart TD
  A[Upstream check job] --> B{New vintage?}
  B -- no --> C[Update RELEASES.md checked date]
  B -- yes --> D[Run ingest to Gold]
  D --> E[Run export.py against tables.yml]
  E --> F[Run validate.py]
  F -- fail --> G[Open issue, stop]
  F -- pass --> H[Generate coverage report]
  H --> I[Human review of diff]
  I --> J[Tag release, publish]
```

### What to automate now

Build one path properly rather than half automating four.

1. **Upstream vintage check.** A scheduled job that checks each source for a newer vintage than `manifest.json` records, and opens a GitHub issue when it finds one. Cheap, high value, and it removes the need to remember.
2. **The export and validate path.** `export.py` plus `validate.py` plus `coverage_report.py` runnable as one command against a Gold DuckDB. This is what makes v2 cost a day.
3. **The release workflow.** Tag triggers build, validate, upload to Source Cooperative, push to Zenodo.

Leave the ingest itself manual for now. It already exists, it runs rarely, and automating a once a year job that touches four different agency APIs is the wrong place to spend effort.

### Validation contract

`validate.py` fails the build on any of these:

- Primary key not unique on `(geo_level, geo_id, year)`.
- A column present in the output that is not declared in `tables.yml`.
- Any lineage reference to a Zillow source table.
- Null rate on a required column above a per column threshold declared in `tables.yml`.
- CBSA count for any year outside an expected band.
- A column type change versus the previous release manifest.
- Row count change versus previous release beyond a declared tolerance, unless a new year is being added.

## Distribution and post strategy

The core rule: a dataset alone is a link nobody clicks. A dataset attached to a claim someone wants to check is a reason to open it. The analysis and the release ship in the same window, with the analysis in front.

### Sequence

| Week | Action | Notes |
| --- | --- | --- |
| 0 | Ship quietly | Publish to Source Cooperative, cut the GitHub tag, get the Zenodo DOI. Verify the quickstart from a clean machine with nothing but DuckDB installed. No announcement. |
| 1 | Publish the analysis | The industry concentration piece, using `economics_industry_wide`. Dataset is a link inside it, not the headline. |
| 2 | Submit to Data Is Plural, post to NICAR-L | Both want exactly this format. NICAR replies are the best documentation QA available. |
| 3 | Bluesky thread, then CNG | Lead with the finding, not the dataset. Cloud-Native Geospatial Forum for the crosswalk architecture writeup, which is its own piece. |
| 4+ | LinkedIn methodology post | Hold until there is a usage story to tell. |

### Channels

| Channel | What to send | Why |
| --- | --- | --- |
| [Data Is Plural](https://www.data-is-plural.com) | Short submission, one paragraph, the link | Highest ROI single action. The dataset matches the newsletter format exactly, and readership is journalists and researchers who will use it. |
| NICAR-L (IRE data journalism listserv) | Plain text post, quickstart query inline | Data reporters hunt for clean metro panels constantly. Fast, blunt feedback on documentation. |
| Bluesky urban econ cluster | Finding first, chart, dataset link last | Urban Institute, Brookings Metro, Furman staff plus the independent writers. A dataset post from an unknown gets ignored. A finding gets reshared. |
| Cloud-Native Geospatial Forum | Crosswalk and Parquet architecture writeup | Separate, genuinely publishable piece. Reaches the practitioners most likely to reuse the spine. |
| Hacker News | Only if the hook is the one liner | "401 metros, one DuckDB query, no signup" is the framing. Skip if it feels forced. |
| LinkedIn | Methodology post, later | Professional audience, wrong first audience for a dataset drop. |

### Post assets to produce

These are build deliverables, not afterthoughts:

- [ ] One chart from `economics_industry_wide` that carries the analysis on its own
- [ ] The quickstart query as a copy and paste block, tested
- [ ] A 100 word dataset description reusable across Data Is Plural, NICAR and the repo
- [ ] A screenshot or code snippet showing the query returning rows, for social

### What not to do

- Do not announce before the quickstart is verified from a clean machine. A broken first impression is unrecoverable with this audience.
- Do not post the dataset to more than one channel on the same day. Stagger, so feedback from the first improves the second.
- Do not lead any post with the pipeline architecture. That is the second piece, for a different audience.

## Build phases

Six phases. Each has an acceptance criterion the Code session can verify without asking.

### Phase 0: Zillow audit

Blocking. Nothing else starts until this is clean.

- Trace lineage for every column in `gold.affordability_wide` and `gold.economics_industry_wide` back to source.
- Flag any column derived from ZHVI or ZORI.
- Rebuild `value_to_income_ratio` on ACS `B25077` median home value if it currently uses ZHVI.
- Produce a written lineage table: public column, upstream source, upstream variable.

**Acceptance:** a lineage report listing every public column with its upstream source, and zero Zillow references.

### Phase 1: Scaffolding

- Create `pip-cbsa-panel` repo with the directory structure above.
- Write `tables.yml` with the full column allowlist, renames, descriptions and null thresholds for all three tables.
- Stub all markdown files with headings.

**Acceptance:** repo structure exists, `tables.yml` declares every column intended for release.

### Phase 2: Export and validate

- `export.py`: reads the Gold DuckDB, applies `tables.yml`, writes Parquet plus the bundled `.duckdb` plus `manifest.json`.
- `validate.py`: implements the validation contract in full.
- `coverage_report.py`: generates the markdown coverage report.
- Single command runs all three.

**Acceptance:** one command produces a complete `data/v2026.1/` directory, validation passes, and the exporter refuses to emit any column absent from `tables.yml`.

### Phase 3: Documentation

- Generate `docs/*.md` from the data dictionary YAML plus `tables.yml`, following the per table template.
- Write `METHODOLOGY.md` by hand. This one is not generated.
- Write `README.md`, `RELEASES.md`, `CHANGELOG.md`, `CITATION.cff`, `LICENSE`.
- Write the three quickstart examples in `examples/`.

**Acceptance:** every column in every published table appears in a docs table with a populated upstream variable cell. No `TBD` anywhere.

### Phase 4: Publish

- Register the Source Cooperative account and repository.
- Upload `v2026.1`.
- Cut the GitHub tag, connect Zenodo, mint the DOI.
- Verify the quickstart from a clean environment.

**Acceptance:** the quickstart query runs on a machine that has never seen this project, returns rows, and the DOI resolves.

### Phase 5: Automation

- `release.yml`: tag triggers build, validate, upload, Zenodo push, with a version consistency check.
- Upstream vintage check job, scheduled, opens an issue when a newer vintage appears.

**Acceptance:** a dry run tag produces a complete release without manual steps, and the vintage check job runs green.

### Sequencing note

Phases 0 through 4 are the release. Phase 5 can land after publication. Do not let automation block shipping.

## Open decisions

These need an answer before or during build. Most are cheap to settle.

| # | Decision | Default if undecided |
| --- | --- | --- |
| 1 | Publishing identity: personal name, or a Patterns in Place org | Patterns in Place as publisher, personal name as author in `CITATION.cff`. Keeps the byline credential while giving the project its own surface. |
| 2 | Repo name | `pip-cbsa-panel` |
| 3 | Geo levels in the release: CBSA only, or CBSA plus county and state | CBSA only for v1. County multiplies row count and documentation surface for a marginal audience gain. |
| 4 | Does `geo_dim` include geometry, or identifiers only | Identifiers only. Geometry means a separate GeoParquet decision and a much larger file. Link to TIGER instead. |
| 5 | Are ACS margins of error carried | No for v1, documented as a known limitation. Carrying MOEs roughly doubles the column count. |
| 6 | Year range | Whatever is fully covered across all three tables with no partial years at the edges. Confirm during Phase 0. |
| 7 | Which analysis ships in week 1 | Industry concentration from `economics_industry_wide`, since it uses the differentiated table and the finding is already partly formed. |
| 8 | Does the chatbot get pointed at the public tables | No. Keep the chatbot on the internal warehouse. Coupling them creates a release constraint neither product needs. |

### Risks

- **Documentation is the long pole.** Phase 3 is where this stalls. The generation step from the existing dictionary YAML is what keeps it from becoming a writing project.
- **The upstream variable column may not be fully populated in the existing dictionary.** If it is not, Phase 0 gets longer. Worth checking early, because a docs table with empty source cells undercuts the entire premise.
- **Quiet launch risk.** A release with no accompanying analysis gets no pickup and is hard to relaunch. If the analysis is not ready, hold the announcement, not the release.

### Handoff to Code

Start at Phase 0. The lineage audit determines whether `affordability_wide` needs a rebuild, and that answer changes the shape of Phases 1 through 3. Do not scaffold the repo before the audit is done.