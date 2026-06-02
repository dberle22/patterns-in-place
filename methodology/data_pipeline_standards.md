# Data Pipeline Standards

## Purpose

This document defines how data is ingested, normalized, and served across Patterns in Place. The Bronze/Silver/Gold architecture is the publication's structural advantage — it is what allows a Comparison piece to use the same definitions as a Metro Deep Dive, and what allows a Data Take written six months from now to plug cleanly into the same scoring models as today's piece.

If a piece needs data that doesn't yet flow through this pipeline, the answer is almost always to extend the pipeline rather than write a one-off script.

---

## Why This Standard Exists

US demographic, economic, and housing data is fragmented across at least a dozen federal agencies and several private sources. Each publishes on different schedules, at different geographies, with inconsistent variable names and definitions. A solo operator who treats each piece as a standalone data pull will spend 80% of their time reconciling sources and 20% writing.

The Bronze/Silver/Gold pipeline solves that. Once a source is ingested into Bronze, normalized into Silver, and joined into a Gold feature table, every future piece that uses that source pays a fraction of the original cost.

The cost of bypassing the pipeline is real. A Data Take written from a one-off script can't be reproduced six months later, can't be cited, and can't be plugged into the next Comparison piece. Bypassing the pipeline once is a tax. Bypassing it five times is institutional debt.

---

## The Three Layers

### Bronze — Raw ingested data

**Purpose:** A faithful, append-only copy of source data. Minimal transformation; the goal is provenance, not usability.

**Rules:**
- One Bronze table per source dataset (e.g., `bronze.acs_5yr_county`, `bronze.zillow_zhvi_zip`, `bronze.bls_qcew_county`)
- Source URL, ingest timestamp, and source vintage stored as columns on every row (or as table-level metadata)
- No renaming, no joining, no derived columns
- Versioned by ingestion date; old versions retained for at least 24 months

**What goes in Bronze:**
- ACS (American Community Survey) — 1-year and 5-year estimates
- BEA (Bureau of Economic Analysis) — regional GDP, personal income
- BLS (Bureau of Labor Statistics) — QCEW employment and wages, CPI, LAUS unemployment
- HUD — fair market rents, area median income limits
- Zillow — ZHVI, ZORI, listing inventory
- TIGER — Census geographic boundary files
- Future sources: Department of City Planning (NYC), Florida parcel data, IRS migration data

### Silver — Normalized and aligned

**Purpose:** Cleaned, type-coerced, geographically aligned data with consistent variable names and definitions.

**Rules:**
- Every Silver table has a clear primary key (typically `geoid` + `year` for annual data; `geoid` + `year_month` for monthly)
- Variable names follow the publication's naming conventions (see below)
- Geographic identifiers are normalized to standard FIPS codes
- Unit conversions and definitional reconciliation handled here (e.g., reconciling Zillow's "metro" definition to OMB's CBSA definition)
- One Silver table per logical concept, not per source (e.g., `silver.county_population`, `silver.cbsa_housing_prices`, not `silver.acs_county_pop_estimates_2023_v1`)

**What goes in Silver:**
- Population by geography and year
- Housing prices by geography and time
- Employment by sector, geography, and time
- Income distributions by geography
- Migration flows
- Geographic crosswalks (county-to-CBSA, zip-to-tract)

### Gold — Analysis-ready feature tables

**Purpose:** Pre-joined, pre-aggregated, derived feature tables that analyses pull from directly.

**Rules:**
- One Gold table per analysis use case
- All derived metrics (price-to-income ratios, year-over-year changes, peer rankings) computed here
- Documented schema (every column has a definition in the data dictionary — see future `data_sources_reference.md`)
- Versioned when the underlying definitions change

**What goes in Gold:**
- `gold.cbsa_market_snapshot` — the standard set of indicators for every CBSA, current quarter
- `gold.metro_peer_groups` — peer assignments for every CBSA, used by Comparison pieces
- `gold.overheating_index_inputs` — the cleaned, joined inputs to the Overheating Index
- `gold.investment_score_inputs` — same for Investment Score
- `gold.tract_demographics` — tract-level demographic features for the NYC explorer and county-level analyses
- `gold.parcel_features_florida` — parcel-level features for the Florida tool

---

## Naming Conventions

Consistency at the column-name level pays compounding dividends. Every analysis that pulls from Silver or Gold should be able to use the same variable names.

### Geography identifiers

| Concept | Column name | Format |
|---|---|---|
| State | `state_fips` | 2-character FIPS code (e.g., "12") |
| County | `county_fips` | 5-character FIPS code (e.g., "12031") |
| CBSA | `cbsa_code` | 5-character CBSA code (e.g., "27260") |
| Census tract | `tract_fips` | 11-character GEOID |
| Zip code | `zip5` | 5-character zip |

Always include a human-readable label alongside the code (`county_name`, `cbsa_name`).

### Time

| Concept | Column name | Format |
|---|---|---|
| Year (annual data) | `year` | Integer (e.g., 2024) |
| Year-month (monthly data) | `year_month` | String "YYYY-MM" |
| Quarter | `year_quarter` | String "YYYY-Q1" |
| Date (point-in-time) | `as_of_date` | ISO date |

### Common metrics

| Concept | Column name | Notes |
|---|---|---|
| Population | `population` | Integer |
| Median household income | `median_hh_income` | Integer USD |
| Median home value | `median_home_value` | Integer USD |
| Median rent | `median_rent` | Integer USD/month |
| Year-over-year change | `<metric>_yoy` | Float (e.g., 0.05 = 5%) |
| Five-year change | `<metric>_5yr` | Float |

### Source attribution

Every Silver row keeps a `source` column identifying the Bronze table it came from. Every Gold row keeps `as_of_date` and a list of source tables in the schema documentation.

---

## Pipeline Operating Rules

### Refresh cadence

Each source has a documented refresh cadence:

| Source | Cadence | Refresh trigger |
|---|---|---|
| ACS 5-year | Annual (December release) | New release published |
| BEA regional | Quarterly | New release published |
| BLS QCEW | Quarterly | New release published |
| BLS CPI | Monthly | New release published |
| BLS LAUS | Monthly | New release published |
| HUD fair market rent | Annual | New fiscal year released |
| Zillow ZHVI | Monthly | Around the 15th |
| Zillow ZORI | Monthly | Around the 15th |
| TIGER boundaries | Annual | When new vintage matters |

The pipeline doesn't have to refresh every source on every schedule. Refresh when a published piece needs the new vintage.

### Validation

Every refresh runs the same validation checks:

1. Row count is within ±10% of the prior version
2. Primary key uniqueness holds
3. No null values in required columns
4. Variable distributions are within expected ranges (no impossible values like negative populations)
5. Geographic coverage is at least 95% of the expected universe (for ACS county data, that's 3,143 counties; flag if substantially fewer)

A failed validation blocks promotion from Bronze to Silver until investigated.

### Versioning

When a Silver or Gold table's definition changes (a new variable added, a metric redefined), bump the version. Old versions stay accessible for at least 12 months so old analyses remain reproducible.

### Documentation

Every Silver and Gold table has:
- A description of what it contains
- The source(s) it's derived from
- The refresh cadence
- The primary key
- Per-column definitions
- Known limitations

This will eventually live in a public `data_sources_reference.md`. For now it lives as comments in the pipeline code.

---

## What the Pipeline Does Not Do (Yet)

By design, the v1 pipeline focuses on the analyses the publication ships in Stage 1 and Stage 2. Several adjacent capabilities will get added as the publication matures:

- **Block group-level data** — the pipeline currently goes down to tract; block group is heavier and only needed for very specific analyses
- **National parcel coverage** — only Florida is covered today; expand only when an analysis warrants it
- **Real-time or weekly data** — everything is at least monthly; weekly listings or real-time MLS data is out of scope
- **Non-US data** — the publication is US-focused; international data is out of scope
- **Demographic projections** — the pipeline ingests observed data only; projections are a separate analytical layer
- **Sentiment or text data** — out of scope

If a piece needs something the pipeline doesn't have, the decision is: extend the pipeline (1–3 days of work, becomes reusable) or defer the piece. Don't bypass the pipeline with one-off scripts.

---

## Pipeline Anti-Patterns

Six things that will degrade the pipeline over time:

1. **One-off scripts that bypass Silver/Gold.** Every one-off creates a piece that can't be reproduced or extended.
2. **Inconsistent geographic identifiers across tables.** A `county_fips` in one table and `county_id` in another guarantees future joins break.
3. **Recomputing the same derived metric in multiple analyses.** If two pieces compute "price-to-income ratio" differently, the publication contradicts itself.
4. **Updating Silver in place without versioning.** Future-you can't reproduce past analyses.
5. **Skipping validation because "it usually works."** It works until it doesn't, and then a piece ships with bad data.
6. **Adding a source to Bronze without ever promoting it to Silver.** Dead data clutter is real overhead.

---

## When a Piece Needs New Data

The decision tree:

1. **Is the data available in Bronze?** If yes, lift it into Silver (1 day). Then build whatever Gold table the analysis needs.
2. **Is the source ingestable but not yet in Bronze?** Add it (1–2 days). Then through Silver and Gold as above.
3. **Is the source not available publicly?** If the analysis is critical, scope a paid acquisition. If not, choose a different angle.
4. **Is the source available but the cost is too high to justify?** Defer the piece. Patterns in Place doesn't ship pieces grounded in shaky data.

The cost of "extend the pipeline" is real but compounds. The cost of "one-off script" is small once but breaks every future use.

---

## Pipeline Evolution

The pipeline gets meaningful additions every few months:

- **Month 2–3:** Migration data (IRS county-to-county flows). Unlocks "where are people moving" analyses.
- **Month 3–4:** Block group-level demographics for selected metros (NYC first, Jacksonville second). Unlocks the retail opportunity finder.
- **Month 4–6:** Non-Florida parcel data for selected high-interest markets. Cost is real; only justify if practitioner-audience traction holds.
- **Month 6+:** Multi-modal transit accessibility data (GTFS-derived). Unlocks Decision Guide pieces around walkability and commute realities.
- **Month 9+:** Permit data (county-level new construction). Unlocks supply-side analyses across Opportunity Finder pieces.

This roadmap is illustrative, not committed. The trigger for each addition is "an analysis I want to publish needs this." Don't pre-build.

---

## How This Doc Sits Alongside the Others

- `../publication_playbook.md` — operational setup; references the pipeline as Layer A infrastructure
- `../editorial_strategy.md` — defines what to publish; constrained by what the pipeline can support
- `../asset_inventory.md` — current state of the pipeline as a publishable asset
- `editorial_pillars.md` — the questions; the pipeline determines which questions can be answered consistently
- `format_standards.md` — the structures; the pipeline supplies the data
- `data_pipeline_standards.md` — *this doc.* The structural advantage.
- `visual_design_standards.md` — how the data shows up visually

When in doubt about how to source data for a piece, the order is: check Silver/Gold → if it's not there, check Bronze → if it's not there, decide whether to extend or defer.

The single most important discipline this doc enforces is *don't bypass the pipeline*. Every bypass is a future tax.
