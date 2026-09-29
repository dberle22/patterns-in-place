# Patterns in Place — Tech Landscape Map

*A mental map of the data tooling space, organized by your stack's concepts. Each section: how to categorize it, the leaders, the smaller players where contribution is realistic, and where to show up. "Contributable" means open source with an active community small enough that a good PR, extension, or writeup gets noticed.*

---

## 1. Languages — SQL, R, Python

Languages aren't a "space" with companies, but each has a tooling ecosystem and specific projects where your work naturally plugs in.

**SQL**
- **Leaders/standards:** ANSI SQL is fragmenting into dialects; DuckDB's dialect is becoming a reference point for analytics SQL (friendly syntax extensions like `GROUP BY ALL`, `EXCLUDE`)
- **Tools you touch:** SQLGlot (parsing/transpiling — already in your stack), sqlfluff (linting), Jinja2 templating
- **Interesting frontier:** Malloy (Google-incubated semantic query language — a rethink of SQL itself), PRQL (pipeline-style SQL alternative)
- **Contributable:** SQLGlot takes community PRs and dialect fixes constantly; a DuckDB-dialect edge case you hit in your validator is a legitimate contribution

**R**
- **Center of gravity:** Posit (tidyverse, Quarto, Shiny). Community: #rstats on Bluesky, R-bloggers, posit::conf
- **Your niche projects:** tidycensus (Kyle Walker), duckdb R package, duckplyr (dplyr backend on DuckDB — young and actively seeking real-world usage reports), ggplot2 extension ecosystem
- **Contributable:** tidycensus (issues/docs from heavy use at 401-CBSA scale), duckplyr (bug reports from your pipeline are genuinely wanted), a ggplot2 extension package if you ever open-source parts of your visual library

**Python**
- **Too big to be a community** — the entry points are project-specific: GeoPandas, Streamlit, Pydantic (you use all three)
- **Rising in your orbit:** Ibis (dataframe API over DuckDB/anything — the Python analog to duckplyr), marimo (reactive notebooks, fast-growing Streamlit alternative), Polars
- **Contributable:** Streamlit community (gallery, forum), GeoPandas docs/examples

---

## 2. Visual Library — What Category Is This?

**It's not headless BI.** Headless BI = a semantic layer served over API with no UI (Cube is the canonical example) — that's closer to your `semantic_layer/` YAML catalogs. Your visual library is a different thing, sitting at the intersection of two categories:

**Category A — Grammar of graphics / chart specification systems**
Systems where charts are declarative specs + data contracts, not hand-coded artifacts:
- **ggplot2** (your foundation — the original)
- **Vega / Vega-Lite** (UW Interactive Data Lab — the JSON-spec equivalent; powers lots of downstream tools)
- **Observable Plot** (Mike Bostock's post-D3 grammar, JS)
- Your `prep_*.R → data contract → render_*.R` pattern is a chart specification system with a semantic layer bolted on — genuinely uncommon and writable-about

**Category B — BI-as-code / code-first publishing**
Tools where dashboards and reports are version-controlled code, not GUI artifacts:
- **Evidence.dev** (you spiked it — SQL + markdown → published site)
- **Rill** (BI-as-code on DuckDB; metrics defined in YAML — philosophically your closest commercial cousin)
- **Observable Framework** (static-site data apps, Bostock again)
- **Quarto** (your publishing layer — Posit's entry in this category)
- **Streamlit / marimo** (app-flavored end of the spectrum)

**The most interesting project in this space for you: Mosaic** (UW IDL — the Vega people). Interactive visualization framework where every chart is backed by DuckDB (including WASM in-browser). It is *exactly* the "charts as specs over DuckDB" idea. Small academic-adjacent community, very contributable, and a writeup of your visual library architecture would land with that crowd.

**Who's doing interesting work:** UW Interactive Data Lab (Vega, Mosaic), Observable, Evidence, Rill, Posit (Quarto dashboards). The "chart rules from a semantic layer" idea (your `chart_rules.yml`) is something Rill and Evidence are both circling — you built it independently, which is a story.

---

## 3. Databases

**Leaders (know them, don't orbit them):**
- Snowflake, Databricks, BigQuery — the cloud warehouse triopoly
- ClickHouse — real-time analytics; huge open-source community but crowded

**Your ecosystem (small, contributable, and where your credibility compounds):**
- **DuckDB** — the core. Contribution surface is unusually broad: the **community extensions ecosystem** (launched 2024) lets anyone publish an extension; docs and blog examples are community-driven; DuckDB Labs amplifies good user stories. A "43M-row QCEW on a laptop" post is exactly what they retweet.
- **MotherDuck** — Slack community, community showcases, actively courts exactly your profile (covered in outreach tracker)
- **duckdb-spatial** — the extension you'd lean on for geo work; young, issues welcome
- **chDB / DataFusion / Arrow** — adjacent embedded-analytics projects; know they exist, no need to engage
- **Malloy** — sits between database and semantic layer; small passionate community

**Where to show up:** DuckDB Discord, MotherDuck Slack, DuckCon (DuckDB's community conference — talks from practitioners with real workloads are the whole program).

---

## 4. Semantic Layer

The most active conceptual debate in the modern data stack right now, and your hand-rolled YAML approach puts you inside it.

**Leaders:**
- **dbt (MetricFlow)** — the mindshare leader; you adopted the spec without the tool, which is itself a take worth publishing
- **Cube** — the headless BI category creator; open source core; semantic layer served over API to any frontend
- **Looker/LookML** — the legacy standard everyone is replacing
- **AtScale** — enterprise OLAP-flavored player

**Smaller / contributable:**
- **Lightdash** — open-source BI built on dbt semantic definitions; active community, welcomes contributors
- **Malloy** — semantic modeling as a language rather than YAML; small community, Google-backed, intellectually serious
- **Rill** — metrics-in-YAML on DuckDB (again — your closest cousin)
- **Boring Semantic Layer / lightweight OSS entrants** — a wave of minimal semantic-layer projects appeared in 2025; the space is fluid enough that hand-rolled implementations like yours get attention

**The current frontier — semantic layers as AI grounding:** The industry has converged on your chatbot's thesis: LLMs shouldn't write free SQL; they should query through a semantic layer. dbt, Cube, and Snowflake are all racing to be the "context layer for AI" — including MCP servers that expose semantic layers to LLMs. Your constrained NL-to-SQL design is independent evidence for the consensus position, built before it was consensus. That's your strongest single piece of technical content.

**Where to show up:** dbt Community Slack (#semantic-layer channels), Cube community, and the MCP ecosystem discussions (GitHub, Anthropic's MCP community) where semantic-layer servers are being built now.

---

## 5. Data Chatbots / NL-to-SQL

**Leaders (platform-embedded):**
- Databricks Genie, Snowflake Cortex Analyst — both semantic-model-grounded, validating your architecture
- ThoughtSpot — the search-driven-analytics pioneer, pre-LLM
- Hex Magic, Julius — notebook/analysis-flavored AI

**Smaller / contributable (open source — your best entry points):**
- **Vanna.AI** — open-source RAG-based NL-to-SQL framework; large GitHub community; your "templates over generation" critique/comparison would be a substantive contribution or post
- **WrenAI** — open-source NL-to-SQL with an explicit semantic modeling layer (MDL) — architecturally the closest OSS project to your chatbot; active and contributable
- **Dataherald** — earlier OSS entrant; check current activity before investing

**Your differentiated position:** Most NL-to-SQL projects chase openness (answer anything). Yours chases reliability (LLM writes a plan, templates write SQL, validator gates everything). Benchmarking your approach against Vanna/WrenAI on your own question library would be a genuinely novel post — nobody publishes constrained-vs-open comparisons with real QA data.

---

## 6. Spatial Analysis

**Leader:** Esri/ArcGIS — the incumbent; worth knowing the vocabulary, not worth orbiting as an indie.

**The open/cloud-native spatial world (your actual habitat):**
- **CARTO** — cloud-native spatial analytics; publishes heavily; runs the Spatial Data Science Conference (SDSC — worth attending, practitioner-friendly)
- **Overture Maps Foundation** — the open POI/places dataset (Meta/Microsoft/Amazon/TomTom); *already on your Track 17 roadmap*; young community where data-quality feedback and usage writeups are valued contributions
- **DuckDB spatial + GeoParquet** — the emerging "spatial modern data stack"; GeoParquet is a young standard with an open community process
- **Kepler.gl / deck.gl** (Uber → OpenJS) — you already use PyDeck; the underlying community is contributable
- **H3** — Uber's hexagonal indexing system; ubiquitous in spatial analytics, worth learning if you don't know it
- **QGIS / PostGIS / GeoPandas / Apache Sedona** — the OSS foundation layer
- **Felt** — collaborative web mapping startup; watches for interesting map work

**Communities:** FOSS4G (the open-source geo conference, global + regional editions), NACIS (cartography — indie-mapper-friendly, October conference), SDSC (CARTO's), Overture community calls, GeoParquet GitHub.

**Your angle:** "DuckDB-spatial + GeoParquet + Overture instead of ArcGIS" is an active migration story many orgs are considering. Stoop's pipeline is a working example.

---

## 7. Concepts You're Missing (or Have Hand-Rolled Without Naming)

**Orchestration** — you don't have it; you have manually-triggered scripts.
- Leaders: **Airflow** (incumbent), **Dagster** (asset-oriented — its "software-defined assets" model maps 1:1 to your medallion tables), **Prefect**
- Honest take: at your scale, a Makefile or simple runner is defensible. But Dagster's free tier + asset model is the one to evaluate when manual triggering starts hurting. Dagster's community is also content-hungry — "orchestrating a solo data platform" is their favorite genre.

**Data quality / testing** — you deferred Great Expectations; alternatives exist at your weight class:
- **pointblank** (R — fits your stack natively), **Pandera** (Python dataframe validation), **Soda Core** (OSS), dbt tests / **SQLMesh audits**
- Your QA framework for the chatbot is a hand-rolled version of "evals" — the AI-engineering community would recognize it as such, which is another content bridge.

**Transformation frameworks** — you write raw SQL scripts; the category:
- **dbt** (deferred, fine), **SQLMesh** (the rising challenger — virtual environments, column-level lineage; smaller community, very contributable, and "why I chose neither" is a post)

**Catalog / metadata / lineage** — your data dictionary is a hand-rolled data catalog:
- Leaders: **DataHub**, **OpenMetadata**, Atlan (commercial). At your scale the YAML+MD dictionary is the right call, but knowing the category vocabulary ("column-level lineage," "active metadata") lets you write about it credibly.

**Table/file formats** — Parquet (you use), **Apache Iceberg** (the format war winner for lakehouses — know the vocabulary), **GeoParquet** (contributable, per spatial section).

**AI infrastructure (MCP)** — the Model Context Protocol is where semantic layers, chatbots, and data tools are converging in 2025–26. An MCP server exposing your Gold layer + semantic catalogs would be a small build with outsized visibility — it's the current-moment version of what your chatbot already does.

---

## The Map, Compressed

| Your concept | Category name | Leader | Best small player for you | Your entry artifact |
|---|---|---|---|---|
| Visual library | Chart grammar / BI-as-code | Vega, Observable | **Mosaic**, Evidence, Rill | Visual library architecture post |
| Databases | Embedded analytics | Snowflake, Databricks | **DuckDB extensions**, MotherDuck | HIB-1 pipeline post |
| Semantic layer | Semantic layer / headless BI | dbt, Cube | **Lightdash**, Malloy, Rill | "MetricFlow spec without dbt" post |
| Chatbot | NL-to-SQL / AI analyst | Genie, Cortex Analyst | **WrenAI**, Vanna | Constrained-vs-open benchmark post |
| Spatial | Cloud-native geo | Esri, CARTO | **Overture**, duckdb-spatial, GeoParquet | Stoop spatial pipeline post |
| (missing) Orchestration | Data orchestration | Airflow | **Dagster** | "Solo platform orchestration" post |
| (missing) Quality | Data quality / evals | Great Expectations | **pointblank**, SQLMesh | Chatbot QA framework post |