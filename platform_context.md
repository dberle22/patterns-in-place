# Platform Context
## What's Built, What's Live, and What the Publication Can Claim

**Purpose:** Publication-facing context for the Patterns in Place ecosystem. Covers what exists across the three underlying repos, the status of each product, and what data coverage we can credibly claim in editorial copy. This is not a technical reference — it is an editorial reference. Last updated: 2026-05-10.

---

## The Three Underlying Repos

Patterns in Place draws on work across three interconnected repos. Each one is a potential source of published analysis, tools, or methodology pieces.

| Repo | Role | Stack |
|---|---|---|
| `metro_deep_dive` | Upstream demographic data pipeline. Ingests ACS, BEA, BLS, HUD, Zillow, and TIGER data. Produces a multi-layer DuckDB for any US metro. | R, DuckDB |
| `rental_area_search` (Stoop NYC) | NYC neighborhood discovery platform. Consumes Metro Deep Dive outputs. Two apps: Stoop Explore (day-trip and neighborhood intelligence) and Stoop Search (move-in evaluation, in progress). | Python, DuckDB, Streamlit, GeoPandas |
| `metro_deep_dive_chatbot` | Conversational analytics interface to the Metro Deep Dive Gold layer. NL questions → SQL → chart → written answer. Portfolio demo for non-technical analysts. | Python, R, Streamlit |

A fourth repo — `retail_opportunity_finder` — is a separate Southeast US retail investment tool that also draws from Metro Deep Dive. It is a secondary track.

---

## Data Coverage

These are the data sources behind the pipeline. These inform what the publication can claim in methodology sections.

| Source | What It Covers |
|---|---|
| ACS (Census Bureau) | Age, race, education, income, labor, housing, migration, transportation — 5-year rolling estimates |
| BEA Regional API | GDP by metro, personal income, Regional Price Parity |
| BLS LAUS | Labor force and unemployment by metro |
| BPS (Census Bureau) | Building permits by metro |
| HUD | Fair Market Rent, rent burden (CHAS) |
| Zillow | Home value index (ZHVI), observed rent index (ZORI) |
| TIGER/Line + Census | Geometry and geography crosswalk tables |
| IRS migration | County-to-county flows — planned, not yet in production |

**Supported geographies:** US, Region, Division, State, CBSA, County, Census Place, Census Tract, ZCTA

---

## What the Pipeline Produces (Gold Layer)

These are the analysis-ready tables that power tools and analyses. All are complete as of April 2026 unless noted.

| Domain | Key Inputs | Status |
|---|---|---|
| Population, age, race, education | ACS | Complete |
| Income, earnings, Regional Price Parity | ACS, BEA | Complete |
| GDP by metro | BEA | Complete |
| Labor force, unemployment | ACS, BLS | Complete |
| Industry sector shares and concentration | BEA | Complete |
| Housing: vacancy, tenure, rent, home value, permits, burden | ACS, HUD, BPS | Complete |
| Rent-to-income, value-to-income, FMR gap | Gold housing + income | Complete |
| ACS mobility and nativity | ACS | Complete |
| Commute, transit, WFH, vehicle access | ACS | Complete |
| Texas school district metrics | ACS + ISD | Complete (secondary track) |

**Composite scores** (affordability, overheating, economic strength, investment): Design is complete; none are in production. They depend on base mart stability and weight approvals.

**Normalization supplements** (z-scores, percentiles): Planned; not started.

---

## Visual Library

15 chart types are structurally implemented in R + ggplot2. All outputs are PNG. The shared layer (prep and render functions) is mature; some individual implementations are still partial.

**Implemented types:** bar, line, scatter, choropleth, slopegraph, bump chart, heatmap table, age pyramid, hexbin, highlight context map, proportional symbol map, bivariate choropleth, correlation heatmap, strength strip, boxplot

---

## Product Status

### Metro Deep Dive Pipeline

**What it is:** The Bronze → Silver → Gold ingestion pipeline. The structural advantage of the publication. Produces consistent, query-ready tables across US metros from public sources.

**Publication status:** Shareable as methodology reference. Not yet narrated for a general audience. A "How It's Built" piece or methodology doc would make the pipeline directly publishable.

---

### Retail Opportunity Finder (ROF)

**What it is:** An interactive Streamlit tool for exploring retail investment opportunities across Southeast US markets. Combines census tract demographics, cluster-based investment zones, and parcel-level data to identify and rank retail sites.

**Publication status:** Working MVP. Sections 01–03 are most portable. A deployed version scoped to Jacksonville exists (committed to git for Streamlit Community Cloud). Needs narrative packaging before public launch.

---

### Stoop NYC (rental_area_search)

**What it is:** A neighborhood intelligence platform for New York City. The name is the editorial identity; the underlying repo is `rental_area_search`.

**Two app surfaces:**
- **Stoop Explore** — "Where should I spend a day?" Five-borough NTA map, curated POI layer, neighborhood character intelligence ("Best neighborhoods for X", "What this neighborhood is known for"), hotel coverage, public POI overlays. Built and live on the active branch.
- **Stoop Search** — "Is this neighborhood somewhere I'd like to live?" Phase 1 needs crime, school quality, and livability scoring. Phase 2 needs property listings data. Not yet built as a standalone app.

**Five data products behind Stoop NYC:**

| Product | What It Is | Status |
|---|---|---|
| Curated Places | Personal and editorial place lists (Google Maps exports + article scrapes) | Active. Hotels live. Excel upload pending. |
| City Baseline | Open/official place data: transit, parks, everyday retail, civic | Complete. 57,346 rows, 28 categories. Crime + school quality pending. |
| Neighborhood Context | ACS tract and NTA metrics from Metro Deep Dive | Active. Five-borough geography live. Full metric coverage partial. |
| Property Listings | Listings enriched with geography, transit, POI context | Placeholder only (22-row sample). |
| Shortlists | User-authored neighborhood and property saves | Partial. |

**Current sprint (as of 2026-05-10):** Stoop Explore V1 surface is built. Final UX review, smoke test, and public announcement remain. Crime, school quality, and crowd upload are still open on the data side.

**Publication status:** Ready to deploy. The app surface is built; the launch announcement and narrative piece haven't shipped yet.

---

### Metro Deep Dive Chatbot

**What it is:** A constrained NL-to-SQL chatbot. Users ask questions about US demographic and economic data; the system parses intent, generates SQL against the Gold layer, selects a chart type, renders the chart via R, and returns a written answer + chart + data table + SQL.

**Design principle:** Reliability over openness. Answer a narrow set of questions well; reject or clarify everything outside scope.

**Build status:**

| Phase | Status |
|---|---|
| Semantic layer (YAML catalogs for tables, metrics, geography, chart rules) | Complete |
| SQL pipeline (deterministic generation, validation, execution) | Complete |
| LLM orchestration (NL → structured plan → SQL) | Complete |
| Chart rendering (R subprocess bridge) | Complete |
| QA tooling and batch runner | Complete |
| Reference dashboard (Streamlit data explorer for QA ground-truth) | Complete |
| Streamlit chat UI (Phase 5) | Pending |
| Cloud deployment (MotherDuck migration, Streamlit Cloud) | Pending |

**Publication status:** In Development (core pipeline complete; frontend and deployment remain). Not yet publishable as a live tool. Strong portfolio piece once the UI ships.

---

## What the Publication Can and Cannot Claim Right Now

| Claim | Verdict |
|---|---|
| "A Bronze/Silver/Gold pipeline spanning ACS, BEA, BLS, HUD, Zillow" | Yes — pipeline is complete and shareable |
| "Nine Gold-layer tables covering population, housing, income, labor, industry, affordability, migration, transport" | Yes |
| "An interactive retail site finder for Southeast US markets" | Yes — Jacksonville deployment is live |
| "A neighborhood intelligence app for NYC" | Yes — Stoop Explore is built; announcement pending |
| "A conversational chatbot for US demographic data" | Qualified — the pipeline is complete; the UI is not |
| "Housing market overheating scores" or "investment scores" | Not yet — design complete, production blocked |
| "NYC crime and safety data" | No — deferred; source not finalized |
| "Property listings data for NYC" | No — placeholder only |

---

## Open Items That Affect Publication Planning

| Item | Repo | Notes |
|---|---|---|
| Stoop Explore public launch | rental_area_search | App built; needs UX review, smoke test, and announcement post |
| Chatbot Streamlit UI | metro_deep_dive_chatbot | Phase 5; blockers: frontend build + MotherDuck migration |
| Composite score production | metro_deep_dive | Blocked on base mart stability and weight approvals |
| Normalization supplements (percentiles, z-scores) | metro_deep_dive | Not started |
| Crime and school quality data | rental_area_search | Source choice and product framing deferred |
| IRS county-to-county migration flows | metro_deep_dive | Planned for v1.1; ACS mobility shipped first |
| Narrative packaging of the pipeline | — | Needed before "How It's Built" piece can ship |
