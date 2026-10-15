# Glossary

**Status:** Active
**Updated:** 2026-09-29

Shared vocabulary across the repo. When a term appears in any doc or code comment, it means what it means here. Where a longer definition exists, the entry links to it.

---

## Geography

| Term | Meaning |
|---|---|
| **Place** (platform sense) | Any geographic unit with aggregate facts, from the whole US down to a tract. The Places layer is the main warehouse. |
| **Census Place** | The Census geography for a city, town or CDP (`geo_level = place`). Not the same as the platform sense above. |
| **CBSA** | Core-Based Statistical Area: a metropolitan or micropolitan area built from counties. The main unit for cross-market comparison. |
| **Metro / micro** | The two kinds of CBSA. Metropolitan areas have an urban core of at least 50,000 people; micropolitan areas, 10,000–50,000. |
| **ZCTA** | ZIP Code Tabulation Area: the Census approximation of a ZIP code. Used for reader-friendly presentation. |
| **Tract** | Census tract, the smallest geography in regular use here. The grain of the zone model. |
| **NTA** | Neighborhood Tabulation Area: NYC's neighborhood geography, used by Stoop. |
| **Point** | A location with a latitude and longitude: a POI, a transit stop, a listing. |
| **Parcel** | The legal land unit from tax or assessor records. |
| **Polygon** | A named zone made of points or parcels that maps up toward Places: a zoning district, a flood zone, an NTA. |
| **Crosswalk** | A table mapping one geography to another, named `xwalk_<from>_<to>`. |
| **Universe** | The set of geographies a model covers. Differs by surface (396, 401 or 925 CBSAs); see [ARCHITECTURE.md](ARCHITECTURE.md#open-items). |

## Warehouse

| Term | Meaning |
|---|---|
| **Staging** | Source-shaped landed tables, kept faithful to the source. |
| **Silver** | Standardized tables with consistent geo and time keys. ACS tables come as `_base` / `_kpi` pairs. |
| **Gold** | Wide, cross-topic tables at the standard grain; the main query target. |
| **Mart** | A purpose-built schema (`mart_*`) shaped for one use: intelligence scores, app serving, an engine's outputs. Gold holds stable derived metrics; marts hold use-case-specific combinations. |
| **Standard grain** | `(geo_level, geo_id, geo_name, year)`. Tables at the same grain join implicitly. |
| **Promotion** | Moving a table or method from an analysis or engine into `foundations/` once it has a stable interface and more than one consumer. |

## Meaning and analysis

| Term | Meaning |
|---|---|
| **Theme** | A broad lens on a place: Character, Livability or Opportunity. |
| **Topic** | A subject area that groups metrics: housing, labor, age, industry. A topic can serve more than one theme. |
| **Metric** | One measured quantity, defined in `metric_catalog.yml`. |
| **KPI** | A metric chosen as an input to an Intelligence frame. |
| **Polarity** | Whether a higher KPI value is better, worse or neither within its frame. |
| **Model role** | How a KPI is used in a frame: `core` (drives clustering and scoring), `sensitivity` (in clustering only, as a robustness check), `descriptive` (for interpretation only), `dropped` (kept in the catalog as a recorded decision). |
| **Question hierarchy** | High-, medium- and low-level questions, modified by a user profile. See [OVERVIEW.md](OVERVIEW.md#how-we-think-about-a-question). |
| **Output framework** | A recurring shape an answer takes: benchmark, ranking, trend, cluster, score, deep dive. |
| **Benchmark** | One place compared against a reference group (national, division, state, peer set). |
| **Semantic layer** | The YAML catalogs in `foundations/semantic_layer/` that define tables, metrics, joins, themes, questions and chart rules. |

## Intelligence Framework

Full method: [methodology/intelligence_framework/](methodology/intelligence_framework/README.md).

| Term | Meaning |
|---|---|
| **Frame** | One of three CBSA-level models, each producing a cluster label, a composite score and a peer set. |
| **Character** | Who lives in a place and what makes it structurally distinct. Descriptive, not normative. |
| **Livability** | Whether day-to-day conditions support quality of life: affordability, health, access, environment. |
| **Opportunity** | Economic prospects for residents, investors and businesses. |
| **Cross-Frame** | The combined view of all three frames. Finds metros that are internally coherent or "diverging from themselves". |
| **Cluster label** | The type a metro is assigned within a frame: *what kind of place is this?* |
| **Composite score** | A metro's percentile position within a frame: *how does it rank?* |
| **Peers / similarity** | The metros most like a given metro, by cosine similarity on the same KPI vectors: *what else is like it?* |
| **Trajectory** | Direction and speed of change over time: diverging or converging, improving or declining. |
| **Turn signal** | A metro whose short-run direction contradicts its medium-term trend. |
| **Zone** | One of seven national tract types (e.g. Knowledge Corridor, Working Neighborhoods). The same label means the same thing in every market. |
| **Corridor / district** | A within-market grouping of related tracts, built by the Corridor Intelligence engine. |

## Metro Deep Dive

Full structure: [metro_deep_dive_program.md](../metro-deep-dive-program/metro_deep_dive_program.md).

| Term | Meaning |
|---|---|
| **Engine** | Reusable computation (POI, geography, benchmarking, time series, infrastructure). Built only when an analysis needs it. |
| **Analysis** | A reusable notebook investigating one question, nationally or for one market. Exploratory; final outputs don't live here. |
| **Issue** | One published market piece. Selects from analyses, renders to publisher spec, and owns every lock-once decision. |
| **Analysis families** | **Position** (where the framework places a market; CBSA grain, same for every market), **Explanation** (why it sits there; sub-CBSA, routed per market), **Thematic** (national claims that transpose to any market). |
| **Routing** | Using the Intelligence Framework to decide which analyses a given market gets. |
| **Act 1–4** | Output lenses for an issue: Act 1 who this market is, Act 2 how it works, Act 3 how it's changing, Act 4 where inside it the structure and opportunity are. Lenses, not containers. |
| **Fixed spine** | Sections that appear identically in every issue so markets stay comparable: market verdict, fingerprint radar, LQ quadrant and exposure scorecard, zone composition, corridor stat blocks. |
| **Flex** | Sections that change per market, around the fixed spine. |
| **Lock-once decision** | A presentation or method choice fixed once for the series, such as radar axis order. |
| **LQ** | Location quotient: an industry's local employment share against its national share. Above 1.25 counts as a specialization. |

## Publishing formats

| Term | Meaning |
|---|---|
| **Metro Deep Dive** (format) | A long-form, full narrative on one market. |
| **Opportunity List** | An 800–1,200 word ranked or filtered list of places, with 1–3 visuals. |
| **Data Take** | A 500–900 word piece built on one finding and one visual. |
| **Chart a day** | Publisher's pipeline for turning one low-level question into one chart and post. |

## Repo status labels

| Term | Meaning |
|---|---|
| **Active** | In development. |
| **Paused** | Not in development; intended to resume. |
| **Legacy** | Kept only until its live parts move elsewhere. Don't build new work here. |
