# NY State of Mind: Repo Context

**Status:** Active
**Updated:** 2026-10-21

Everything a Claude Code session needs to build analyses and exhibits for the NY State of Mind series: the questions, the exhibits, the data and print rules, and the program vocabulary. Combined from the series docs on 2026-10-17.

## How to Use This Doc

**This is the source of truth for build status.** Readiness in Part 2 and build status in Part 3 change when code ships, so they are maintained here, in the repo. The Obsidian copies of the Question Bank and Exhibit Bank are planning snapshots. When a build lands, update the readiness and build status here in the same change.

**Contents**
1. Working rules for analysis sessions
2. Question Bank: what we want to know, with IDs and readiness
3. Exhibit Bank: reusable chart cells with parameters
4. Approach: tools plus data (D) and editorial (E) decisions
5. Program Glossary: Metro Deep Dive terms the banks use

**Not included:** writing and planning docs (Series Overview, Primer Overview, Series Intro). They live in Obsidian. The series context in brief: NY State of Mind is a Patterns in Place writing series on New York State, published on Substack. The primer is one article (the Series Intro). Next is the Albany spotlight, one installment per lens starting with Lens 1, with statewide lens articles, rankings and regional pieces in between; see the [Article Slate](ARTICLE_SLATE.md). NYC is the finale. AI Inversion is a separate AI impacts ranking, outside the series.

**Current task:** The four opening visuals were reviewed on 2026-10-19 and v2s built beside each v1 in the notebook (Map 2 v2 is infrastructure first, with six landmarks and four ports; the benchmark is a table with "as if a state" ranks). Dan approved the v2s. The population history chart (X.3) is built in two versions (rank and share of US) from `what_ny_is/reference/state_population_history.csv`; review pending, then cut v1s and export. See [the visuals build plan](WHAT_NY_IS_VISUALS_BUILD_PLAN.md), "Review, 2026-10-19". The broader B1 and statewide Overture POI work remain deferred. A later B2 starting point is state government share of employment by county from QCEW (see Part 2, B2 Source Plan).

# Part 1: Working Rules for Analysis Sessions

- **Start from a question ID, not a chart idea.** Articles are assembled from questions, analyses, and exhibits (E5).
- **Check readiness first.** Ready means the data is in the warehouse. Gated and Build items name their blocker. Don't plan around gated data without saying so.
- **Reuse before building.** Check the Exhibit Bank for an existing exhibit. An exhibit earns a spec the second time it is used, not the first: build the cell, notice when it gets copied, then promote it using the spec format in Part 3.
- **Data rules:** REDC regions first, vernacular second (D1). Show metros and micros, lead with metros (D2). The state overview uses NY only data; metro pieces may cross state lines (D3). 2023 vintage and 2023 CBSA delineations (D4). Population growth window is 2012 to 2024, from ACS 5-year (settled 2026-10-18); mark the 2021 consistency break.
- **Print rules:** cluster labels and peer lists are cleared for print. Frame composite scores are held back from print. Carto and reactive maps are exploration only (E10).
- **Chart engines:** both the R/ggplot2 Visual Library and its Python port are in use. Pick per exhibit; specs stay engine neutral.
- **Glossary caveat:** definitions marked (inferred) in Part 5 have not been confirmed. Ask before relying on one.
- **Tools:** Marimo notebooks, the Patterns in Place DuckDB warehouse, the Visual Library.
- **Explore with the analysis notebooks.** Metro questions name the `analyses/` notebook to open for each; see Part 2, Metro Deep Dive Questions, "Using the Analysis Notebooks".

# Part 2: Question Bank

### What This Is

The questions we want to answer in the NY series. A question is what we want to know. It is not a chart and not an article. Questions get answered by analyses, analyses get shown through exhibits (see Exhibit Bank), and articles are assembled from the answers.

Every question has a home, a source, and a readiness. Readiness is the honest state of the data today:

- **Ready** means the data is in the warehouse and the question can be answered now
- **Gated** means something specific is blocking it, named in the row
- **Build** means it needs new ingest work

Questions here that map to the Metro Deep Dive program keep the program's own IDs (Q1 to Q6, A1 to A10) so we are not maintaining two vocabularies.

#### Declared Builds

Build work named in the readiness column. Each build unblocks a set of questions and exhibits.

| ID | Build | Unblocks | Status |
|---|---|---|---|
| B1 | NY infrastructure ingest: highways, Amtrak and major rail, MTA lines and stations, ports, bus depots, Erie Canal | S3.1, S3.2, R.3, X.19, X.20 | Partial, 2026-10-18: Map 2's bounded inputs are ingested and validated (179,751 Infrastructure serving features), plus the Canal Corporation centerline and seven curated port candidates. Map 2's working notebook draft is built; its independently checked drawing query selects 2,366 named Thruway, 5,803 other interstate and 6,855 tagged main-line rail features. Road names/refs supply the Thruway highlight without operator tags. Visual review and exports remain pending. See [WHAT_NY_IS_VISUALS_BUILD_PLAN.md](WHAT_NY_IS_VISUALS_BUILD_PLAN.md). These remain local engine/reference artifacts, not new warehouse tables. **OPEN:** full layer list (MTA lines and stations, bus depots) for later pieces; deferred |
| B2 | State footprint source assembly: SUNY, DOCCS prisons (open and closed), OMH psychiatric centers, state parks, the Adirondack Park and DEC lands, plus state government jobs by county | S5.3, S5.4, R.10, X.16, X.17 | Partial source assembly: official Adirondack and Catskill Park boundaries downloaded and validated for Map 2 on 2026-10-18. The remaining B2 assembly is not started. Source plan below |

##### B2 Source Plan

Researched 2026-10-17. Field lists not yet confirmed for the data.ny.gov datasets; check the column schema before ingest.

| Piece | Source | Shape | Notes |
|---|---|---|---|
| State government jobs by county | QCEW, state government ownership code | County table | Already ingested, so this is a filter, not new ingest. Expect suppression in the smallest counties, which are the ones S5.3 is about |
| SUNY campuses | [SUNY Campus Locations with Enrollment](https://data.ny.gov/d/3cij-nwhw) (data.ny.gov `3cij-nwhw`) | Points | Includes enrollment, also useful for M.16 |
| Prisons, open | DOCCS [facility location search](https://doccs.ny.gov/locationsearch/11) | Points, geocoded from addresses | No downloadable facility table found. The monthly [DOCCS fact sheet](https://doccs.ny.gov/system/files/documents/2026/03/doccs-fact-sheet-march-2026.pdf) names the 42 open facilities but has no county or capacity |
| Prisons, closed | [Wikipedia: List of New York state prisons](https://en.wikipedia.org/wiki/List_of_New_York_state_prisons) | Table | Not a state source, but the only list found with county, security level, opened and closed year together. Cross-check against DOCCS closure announcements: DOCCS says 26 closures since 2011, the Wikipedia table shows 27 |
| OMH psychiatric centers | OMH [Directory of Facilities](https://www.omh.ny.gov/omhweb/aboutomh/omh_facility.html) | Points, geocoded from addresses | About 25 facilities, including children's and forensic centers |
| State park facilities | OPRHP [State Park Facility Points](https://data.ny.gov/d/9uuk-x7vh) (data.ny.gov `9uuk-x7vh`) | Points | Updated April 2026 |
| State park boundaries | OPRHP boundary layer, found only on a [DOT dev server](https://gisportaldev.dot.ny.gov/server/rest/services/CulturalResources/Cultural_Resources/MapServer/16) | Polygons | Find the production copy before relying on it |
| Adirondack Park | APA [Blue Line polygon](https://services2.arcgis.com/8krRUWgifzA4cgL3/ArcGIS/rest/services/BluelinePolygon/FeatureServer/0), also on [APA GIS downloads](https://apa.ny.gov/planning/gis/downloads.html) | Polygon | Official 2018 boundary |
| Other state land | DEC [DEC Lands layer](https://gisservices.dec.ny.gov/arcgis/rest/services/reference/MapServer/2) | Polygons | Forest Preserve, State Forests, Wildlife Management Areas, with acres and county. Supports R.10 |
| State agency offices | None found | | No statewide inventory of state owned buildings with locations. The QCEW filter covers this better, since most of it is Albany |

**Build order:**
1. QCEW state government share by county. No new ingest, and it tests whether the "small counties lean on the state" story holds before building anything else
2. One points table: SUNY, prisons (open and closed), OMH, park facilities, with `institution_type`, `status`, `closed_year`
3. Land polygons: Blue Line and DEC Lands, kept separate from the points since they show land, not jobs

**Watch:** prisons and OMH centers need geocoding (about 80 addresses), and the closed prison list leans on Wikipedia until checked against DOCCS.

> [!todo] Check Overture and OSM before hand geocoding
> Overture POIs and OSM are already in the stack. Check whether they can supply some of the points layer instead of geocoding by hand:
> - **Overture places:** look for categories covering prisons, colleges and universities, psychiatric hospitals and parks. Overture has no ownership field, so state run sites would need to be matched by name against the lists above
> - **OSM:** candidate tags to check are `amenity=prison`, `amenity=university` / `amenity=college`, hospitals tagged for psychiatry, and `boundary=protected_area` or `leisure=park` for park and state land polygons. The `operator` tag may identify state ownership (DOCCS, SUNY, OMH, OPRHP, DEC); check how consistently it is filled in
> - **Expect gaps:** neither source will reliably have closed prisons or closure years, so the closed list still comes from DOCCS and Wikipedia. Use Overture or OSM to fill coordinates, and the state lists as the source of truth for what counts

Other gates that are not builds, listed here so they are tracked in one place:
- **No NY POI run** gates S3.4, R.5, M.11, M.12, K.9, K.10, X.21
- **Internal Structure Part 2 not built for NY** (needs the NY POI run; Part 1 runs on national Phase 7 zones) gates S3.3, M.12, K.9, K.10, X.21, X.22
- **LODES OD not ingested** gates M.14
- **Composite scores not in production** gate K.5, K.7, K.8, X.28

---

### Primer Questions

#### What NY Actually Is

| ID | Question | Source | Readiness |
|---|---|---|---|
| S2.1 | How do the 10 official REDC regions compare to the colloquial ones, and where do they disagree? | Geography engine, CBSA delineations | Ready |
| S2.2 | Which CBSAs sit in which region under each definition, and which ones move? | Geography engine | Ready |
| S2.3 | For counties in no CBSA at all, are they functionally independent or orbiting a neighboring metro? | LODES WAC/RAC, county grain | Ready |
| S2.4 | How does NY compare to the rest of the country on the basic benchmarks? | Benchmarking engine | Ready |
| S2.5 | How much of the state is downstate, and how has that share moved over time? | ACS, decennial | Ready |

S2.3 is Q6 pointed the other way. Q6 asks whether an outlying county inside a CBSA really belongs. This asks whether a county outside every CBSA is orbiting one anyway. Same commuting evidence, opposite direction. The primer version stays simple: where do this county's workers go, and is there a dominant destination.

#### The Lines People Move Along

| ID | Question | Source | Readiness |
|---|---|---|---|
| S3.1 | What is the physical network that moves the state? | Infrastructure engine | **Build** (B1) |
| S3.2 | Which population centers are far from major infrastructure? | Infrastructure + ACS population | **Build** (B1) |
| S3.3 | Where are the core downtowns and central business districts? | Internal Structure, A5 | Gated (Internal Structure not built; hand assemble for the primer) |
| S3.4 | What anchors each downtown: transit, a university, an office core, a hospital, government? | Internal Structure, POI | Gated (no NY POI run) |
| A4 | Did remote work rewire where work happens? | ACS WFH series, LODES | Ready |

#### Who Lives Here

| ID | Question | Source | Readiness |
|---|---|---|---|
| S4.1 | What does the state's age structure look like, and how does it vary geographically? | ACS | Ready |
| S4.2 | Where are people from, and how does that change from CBSA to county to tract? | ACS | Ready at CBSA and county; confirm tract grain |
| S4.3 | Which places have the most external migration, and what did it do to them? | ACS nativity, IRS flows | Ready |
| S4.4 | Which states do New Yorkers move to, and which states do they come from? | IRS flows 2012 to 2022 | Ready |
| S4.5 | Where do people move within the state? | IRS county flows | Ready |
| A2 | Does building more housing lower prices? | Permits, HPI, stock composition | Ready |
| A7 | Who is squeezed: which people in which places carry the worst cost burden? | ACS burden, income | Ready |

Housing lives here rather than in Infrastructure because A2 and A7 are about who can afford to live where, which is a question about people.

#### What People Do Here

| ID | Question | Source | Readiness |
|---|---|---|---|
| S5.1 | What are the top industries and sectors by region, and how different are the regions really? | BEA sector shares | Ready |
| S5.2 | Where are the core job centers? | LODES WAC | Ready |
| S5.3 | Where is the state's own footprint, and which small counties does it sit on? | SUNY, DOCCS, OMH, state agencies, parks | **Build** (source assembly) |
| S5.4 | How concentrated is each place, by sector and by employer? | QCEW 2010 to 2024, BEA | Ready, with small county suppression |
| A6 | Does industry specialization predict growth? | LQ lagged panel | Ready |
| A10 | Is the wage distribution polarizing, and where? | Sector wage distribution, OEWS | Ready |

S5.4 measured two ways tells different stories. One large sector is not the same as one large employer. A county can look diversified by sector and still have a single state institution as its largest employer. That is the finding worth writing about, and it feeds the rankings later.

#### Where It's Headed

| ID | Question | Source | Readiness |
|---|---|---|---|
| S6.1 | Which areas are growing and which are shrinking? | ACS, decennial | Ready |
| S6.2 | Which areas carry the highest environmental risk? | FEMA risk score, AQI | Ready |
| S6.3 | What do health outcomes look like by region and CBSA? | health_wide | Ready |
| S6.4 | What major investments and policies are coming, and where do they land? | Editorial research | N/A, not a data question |
| A3 | Are people moving toward harm? | Hazard vs growth | Ready |
| A8 | What is the geography of life expectancy in the state? | health_wide | Ready |

---

### Regional Deep Dive Questions

These run per region. The first four are the same question asked of every region; the rest are specific arguments we already know we want to make.

| ID | Question | Source | Readiness |
|---|---|---|---|
| R.1 | How do the cities inside this region fit together? | Peers, LODES, industry mix | Ready |
| R.2 | Does this region make sense on its own, or does it belong with another? | Commuting, industry, migration | Ready |
| R.3 | Is this region underserved by infrastructure? | Infrastructure + population | **Build** (B1) |
| R.4 | Where is housing being built in this region, and what is the existing stock? | Permits, ACS stock | Ready |
| R.5 | Are there real amenity clusters here? | POI | Gated (no NY POI run) |
| R.6 | Western NY and the Finger Lakes: one region or two? | R.2 applied | Ready |
| R.7 | What is "Upstate"? | R.2 applied, plus the vernacular evidence | Ready |
| R.8 | How is the Southern Tier defined, and by whom? | R.2 applied | Ready |
| R.9 | Are NYC and Long Island really two regions? | Commuting, CBSA delineation | Ready |
| R.10 | Why the Adirondacks will never be developed, and why that is fine | Park boundary, land use, forever wild | Ready |

---

### Metro Deep Dive Questions

The metro spotlight template, organized by lens (settled 2026-10-21). Each metro gets up to five installments, one per lens. A lens can be a full article or a short note. Larger metros (Albany, Buffalo, Rochester, NYC) get all five; smaller metros get a spotlight plus one or two lenses. The metro lineup and order live in the [Article Slate](ARTICLE_SLATE.md).

Every installment has:
- A history opening (E4)
- A human story as the bridge into the data (E2)
- 4 to 6 exhibits, as a guideline: build what the piece needs, then cut what doesn't earn its place
- A close that points to the next installment

The template is a guide. It sets which questions an installment covers, not their order, and an installment can lead with its own hook.

Questions keep their M IDs from the earlier template-section layout. M.20 and up are new to the lens layout; most are a statewide question applied at the metro grain, noted in the Program column. The **Explore with** column names the analysis notebook to open (see [Using the Analysis Notebooks](#using-the-analysis-notebooks) below). "Direct" means no notebook fits yet: query the warehouse from the issue notebook.

#### Lens 1: What [Metro] Actually Is
*Overview and Metro Construction*

| ID | Question | Program | Explore with | Readiness |
|---|---|---|---|---|
| M.1 | What kind of market is this? | Position: Profile | Profile, Act 1 Position | Ready for exploration; frame scores held from print |
| M.3 | Who are its peers? | Position: Peers | Peers | Ready (cluster label and peer list cleared for print) |
| M.2 | How is the metro assembled: counties, cities, neighborhoods? | Position: Internal Structure | Internal Structure Part 1 | Part 1 ready (national Phase 7 zones); Part 2 gated (no NY POI run) |
| M.9 | Is there one main downtown or several? | A5, Q6 places, Q2 job centers | Q6 One Metro, Q2 Job Center Outcomes | Partial: Q6 place and anchor marts exist; A5 banked |
| M.10 | Which counties are core, outlying, exurban, and do they really belong? | Q6 | Q6 One Metro | Data present; integration threshold must be stated for print |

#### Lens 2: The Lines People Move Along
*Regional Role and Daily Amenities*

| ID | Question | Program | Explore with | Readiness |
|---|---|---|---|---|
| M.20 | What physical network runs through it: highways, rail, canal, ports? | S3.1 at metro grain | Infrastructure exploration | **Build** (B1 beyond Map 2's bounded layers) |
| M.13 | What role does it play in the broader region? | Regional Role | Regional Role | Partial (WAC/RAC only) |
| M.14 | Where do people commute from? | Regional Role | Regional Role | Gated (LODES OD not ingested) |
| M.11 | What are the core amenities, and how good is access to them? | Q4 | Q4 Daily Needs | Gated (no NY POI run; basket not defined) |
| M.12 | Are there amenity clusters, and how do they line up with downtowns, jobs and housing? | Q4 + Internal Structure | Q4 Daily Needs, Internal Structure Part 2 | Gated (no NY POI run) |

#### Lens 3: Who Lives Here
*Housing stock, plus demographics*

| ID | Question | Program | Explore with | Readiness |
|---|---|---|---|---|
| M.21 | What does the age structure look like? | S4.1 at metro grain | Direct (ACS age) | Ready |
| M.22 | Where are people from: nativity, race, language? | S4.2 at metro grain | Direct (ACS) | Ready |
| M.23 | Who is moving in and out, and from where? | S4.3 to S4.5 at metro grain | Direct (IRS flows) | Ready |
| M.5 | What does the existing housing stock look like? Is cheap housing a sign of too much supply or too little demand? | Q1 | Q1 Market, Q1 National | Ready |
| M.24 | Who carries the worst cost burden? | A7 at metro grain | Direct (ACS burden, HUD CHAS); A7 spec | Ready (data); A7 notebook not built |

#### Lens 4: What People Do Here
*Jobs*

| ID | Question | Program | Explore with | Readiness |
|---|---|---|---|---|
| M.8 | What are the core industries and anchor employers? | Industry surfaces, QCEW | Direct (BEA, QCEW) | Ready |
| M.25 | How concentrated is the economy, by sector and by single employer? | S5.4 at metro grain | Q2 Job Concentration; direct QCEW | Ready, with small county suppression |
| M.6 | Where are the main job centers? | Q2 job centers | Q2 Job Center Outcomes | Ready |
| M.7 | Do people live near them, and can they afford to? | Q5, Q2 | Q2 Job Center Outcomes, Q2 Proximity Method | Q5 ready (OEWS present); Q2 straight line only |
| M.15 | How does its economy compare to the rest of the region? | Benchmarking, industry mix | Regional Role, Q2 Job Concentration (comparison market) | Ready |

M.15 moved here from Regional Role: it's a jobs question, which leaves Lens 2 about movement and connection.

#### Lens 5: Where It's Headed
*Trajectory and growth*

| ID | Question | Program | Explore with | Readiness |
|---|---|---|---|---|
| M.1 | Where is the market's position moving? | Position: Trajectory | Trajectory | Ready for exploration; frame scores held from print |
| M.4 | Where is growth landing: greenfield, infill, or nowhere? | Q3 | Q3 Where Growth Lands | Data present (`mart_explanation_q3`); tract vintage handling to verify |
| M.19 | What major investments are coming, and what are they changing? | S6.4 at metro grain | Direct (permits, jobs, growth); editorial research | Partial: data ready; the investment itself is editorial |
| M.26 | What are the risks: environmental hazard, health? | S6.2, S6.3, A3 at metro grain | Direct (FEMA NRI, AQI, health_wide); A3 spec | Ready (data); A3 notebook not built |

M.1 appears twice on purpose: Profile is where the market is now (Lens 1), Trajectory is where it's going (Lens 5).

#### Spotlights
Deeper analyses that don't fit the core template. A spotlight goes inside the lens it informs, or stands alone when it's big enough (Utica).

| ID | Spotlight | Question | Applies to | Explore with | Readiness |
|---|---|---|---|---|---|
| M.16 | Education | How much of this economy is the university, and what does the student population do to the numbers? | Ithaca, Binghamton, Syracuse, Albany | Direct (ACS group quarters, QCEW/BEA education); Profile for context | Ready |
| M.17 | Anchor legacy | What did the anchor employer leave behind after it shrank? | Schenectady (in Albany Lens 4), Rochester, Binghamton | Q2 Job Concentration; direct QCEW, OEWS | Ready |
| M.18 | Resettlement and immigration | What did resettlement do to a city built for more people? | Utica | Q1 Market; direct ACS nativity, language, occupancy | Ready |
| M.19 | Live investment | How is a major new investment changing this place, while it happens? | Syracuse (Micron) | Trajectory, Q3; direct permits and jobs | Partial: data ready; the investment itself is editorial (S6.4) |
| | History | Not a data question. Feeds history openings (E4) | Every metro | | N/A |

#### Using the Analysis Notebooks

The `metro-deep-dive-program/analyses/` notebooks are the exploration surface for metro pieces. Most take a CBSA from a dropdown filled from the warehouse and default to Richmond (40060).

1. **Explore in the analysis notebooks as they are.** Open with `marimo edit <notebook>` and switch the dropdown to the metro (Albany is 10580). Don't change the Richmond defaults; they're part of each analysis's QA setup. The Q2 notebooks also read `Q2_CBSA_CODE` and Regional Role reads `REGIONAL_ROLE_CBSA_CODE`, so setting either opens them on the chosen metro.
2. **Write findings into the article outline** (for example `albany/ALBANY_LENS1_OUTLINE.md`) next to the question ID they answer, not into the analysis folder.
3. **Build print visuals in an issue notebook** for the metro, such as `albany/ALBANY_VISUALS.py`, following [`what_ny_is/WHAT_NY_IS_VISUALS.py`](what_ny_is/WHAT_NY_IS_VISUALS.py). Reuse the analyses' `queries/*.sql` rather than copying their logic. Final story assembly lives in `issues/`, not `analyses/`.
4. **"Direct" questions** have no notebook yet. Query the warehouse from the issue notebook and note which queries get copied between metros: that's the signal to promote them.

**Notebook readiness for NY.** This table is the source of truth; update it when a notebook gains NY coverage.

| Notebook | Lens questions | Status for NY |
|---|---|---|
| [Act 1 Position](../_shared/act_1/ACT_1_POSITION_NOTEBOOK.py) | M.1, M.3 together | Ready; good first look at any metro |
| [Profile](../../analyses/position/profile/POSITION_PROFILE_NOTEBOOK.py) | M.1 (Lens 1) | Ready; frame scores for exploration only |
| [Peers](../../analyses/position/peers/POSITION_PEERS_NOTEBOOK.py) | M.3, K.6 | Ready; peer lists cleared for print |
| [Trajectory](../../analyses/position/trajectory/POSITION_TRAJECTORY_NOTEBOOK.py) | M.1 (Lens 5), M.19 | Ready |
| [Candidate Scan](../../analyses/position/candidate_scan/POSITION_CANDIDATE_SCAN_NOTEBOOK.py) and [Discovery](../../analyses/position/candidate_scan/POSITION_CANDIDATE_DISCOVERY_NOTEBOOK.py) | Rankings (K.2, K.6) | Ready; all markets, filter to NY |
| [Internal Structure Part 1](../../analyses/position/internal_structure/POSITION_INTERNAL_STRUCTURE_NOTEBOOK.py) | M.2 | Ready (national Phase 7 zones) |
| [Internal Structure Part 2](../../analyses/position/internal_structure/POSITION_INTERNAL_STRUCTURE_PART2_NOTEBOOK.py) | M.2, M.12 | Blocked: needs a NY POI run |
| [Q1 Market](../../analyses/explanation/q1_supply_or_demand/EXPLANATION_Q1_MARKET_NOTEBOOK.py) and [National](../../analyses/explanation/q1_supply_or_demand/EXPLANATION_Q1_NATIONAL_NOTEBOOK.py) | M.5, M.18 | Ready |
| [Q2 Job Center Outcomes](../../analyses/explanation/q2_job_proximity/EXPLANATION_Q2_JOB_CENTER_OUTCOMES_NOTEBOOK.py) | M.6, M.7, M.9 | Ready (straight line distance only) |
| [Q2 Job Concentration](../../analyses/explanation/q2_job_proximity/EXPLANATION_Q2_JOB_CONCENTRATION_NOTEBOOK.py) | M.15, M.17, M.25 | Ready; set a comparison market |
| [Q2 Proximity Method](../../analyses/explanation/q2_job_proximity/EXPLANATION_Q2_PROXIMITY_METHOD_NOTEBOOK.py) | M.7 | Ready (method review) |
| [Q3 Where Growth Lands](../../analyses/explanation/q3_where_growth_lands/EXPLANATION_Q3_NOTEBOOK.py) | M.4, M.19 | Data present; tract vintage gate to verify |
| [Q4 Daily Needs](../../analyses/explanation/q4_daily_needs/EXPLANATION_Q4_NOTEBOOK.py) | M.11, M.12 | Blocked: Richmond and Jacksonville only; needs a NY POI run |
| [Q6 One Metro](../../analyses/explanation/q6_one_metro/EXPLANATION_Q6_NOTEBOOK.py) | M.9, M.10 | Ready; integration threshold must be stated for print |
| [Regional Role](../../analyses/explanation/regional_role/EXPLANATION_REGIONAL_ROLE_NOTEBOOK.py) | M.13, M.14, M.15 | Partial: LODES WAC/RAC only, no commute flows |
| [Infrastructure exploration](../../engines/infrastructure/INFRASTRUCTURE_EXPLORATION_NOTEBOOK.py) | M.20 | Engine notebook; NY coverage is Map 2's bounded layers |
| Thematic A1 to A10 | M.24 (A7), M.26 (A3) | Specs and build plans only, no notebooks. Query directly, or build after the entry's Epic 1 audit |
| Catchment | None | Not used; built around a single Jacksonville property |

---

### Rankings Questions

Rankings emerge from the writing (E8). These are the axes we have named so far, not a commitment to write all of them.

| ID | Question | Readiness |
|---|---|---|
| K.1 | Which metros have the strongest job centers? | Ready (raw KPIs) |
| K.2 | Which are growing fastest and slowest? | Ready |
| K.3 | Which have the strongest economic indicators? | Ready (raw KPIs) |
| K.4 | Which have the most human capital? | Ready |
| K.5 | Which metros are underrated, and what does underrated mean? | Gated (composite scores not in production) |
| K.6 | Which cities are growing faster or slower than their national peer group? | Ready (cluster labels cleared for print) |
| K.7 | Which have a strong economy now, and which have the ingredients for one? | Gated (composite scores) |
| K.8 | Which areas need investment most? | Gated (composite scores) |
| K.9 | Which are the top downtowns? | Gated (Internal Structure, POI) |
| K.10 | Which are the most walkable districts? | Gated (Internal Structure, POI) |
| A1 | How exposed is each metro's job mix to AI? | Active |

Composite scores (affordability, overheating, economic strength, investment) are designed but not in production, and frame composite scores are held back from print until the Intelligence Framework review answers Section B and A1. That is what gates K.5, K.7, and K.8.

---

### Reader Framings

Not questions and not analyses. These are article shapes that pull from questions already banked. Each could become its own piece.

| ID | Framing | Pulls from |
|---|---|---|
| F.1 | If I am a young person looking for work, where do I go? | S6.1, M.6, K.1, K.2, R.4 |
| F.2 | If I am older, where can I best afford to retire? | S4.1, R.4, A7, S6.3 |

---

### Not Questions

Things raised in planning that belong elsewhere, kept here so they do not get re-raised as questions.

| Item | Where it belongs |
|---|---|
| NY's population rank falling from first to fourth | Editorial, with one exhibit (X.3) |
| Sunnyside Yards and other named investments | Editorial, S6.4 |
| Ellis Island, the Erie Canal, Rockefeller, Moses | Section intros (E4) |
| Comparative state history: is NY really the only state central in every era? | Open. A possible piece, not a primer question |
| "How has the state changed over time" | Not a question. Time is a dimension on every question (E6) |

---

### Appendix: Mapping From the First Module List

The original 27 numbered items were mostly questions, not modules. Mapping for anyone reading the older planning doc.

| Old # | Now |
|---|---|
| 1 | S2.1, S2.2 |
| 2 | S3.1, S3.2 |
| 3 | M.16 |
| 4 | S5.1 |
| 5 | S4.1 |
| 6 | S4.2 |
| 7 | S3.3, S3.4 |
| 8 | S6.1 |
| 9 | S4.3 |
| 10 | S4.4 |
| 11 | S4.5 |
| 12 | S6.2 |
| 13 | S6.3 |
| 14 | R.4 |
| 15 | K.5 |
| 16 | R.5 |
| 17 | S5.2 |
| 18 | K.6 |
| 19 | F.1 |
| 20 | F.2 |
| 21 | Retired, see E6 |
| 22 | K.7 |
| 23 | K.8 |
| 24 | S2.3 |
| 25 | Retired, same as 21 |
| 26 | S5.3 |
| 27 | S5.4 |

# Part 3: Exhibit Bank

### What This Is

The reusable visuals for the NY series. An exhibit is one chart, one data binding, built once as a Marimo cell and reused by changing its parameters.

An exhibit is not a question and not an insight. The question is what we want to know, the exhibit is the machinery that shows it, and the insight is what a specific run of it says about a specific place. Only the machinery is reusable. What Syracuse's income distribution means is written once, in Syracuse's article.

Each exhibit names its visual library type, its parameters, and its source. An exhibit with no parameters is not reusable and should be rewritten until it has some.

**Build discipline:** an exhibit earns a spec the second time we reach for it, not the first. This bank is a catalog of what we expect to reuse, not a build queue. Write the first section article, notice which cells got copied, and promote those.

**Library note:** the visual library has 15 implemented types in R and ggplot2, all static PNG. Two exhibits below need a type the library does not have yet; they are marked **NEW TYPE**. Carto and reactive maps stay exploration only (E10).

> [!note] Library engine (settled 2026-10-15)
> Both the R/ggplot2 library and its native Python port (Altair, matplotlib/geopandas) are in use. Engine choice per exhibit is handled in Claude Code sessions; the exhibit specs here stay engine neutral.

---

### Geography and Orientation

| ID | Exhibit | Type | Parameters | Source |
|---|---|---|---|---|
| X.1 | Region assignment map. Counties or CBSAs colored by which region they fall in under a chosen definition. | Choropleth | `definition` (REDC, vernacular, upstate/downstate), `geo_level` | Geography engine |
| X.2 | CBSA locator map. Metro and micro areas sized by population. | Proportional symbol map | `year`, `cbsa_type` | Geography, ACS |
| X.3 | Rank over time. One geography's national rank on one metric, traced across years. | Line | `geo_id`, `metric_id`, `year_range`, `n_comparators` | ACS, decennial |
| X.4 | Benchmark bar. One geography against US, region, state, or peer set on one metric. | Bar with reference line | `geo_id`, `metric_id`, `benchmark_type` | Benchmarking engine |
| X.5 | Dominant destination map. Each county colored by where its workers commute to, shaded by how dominant that destination is. | **NEW TYPE** (categorical choropleth with intensity) | `geo_level`, `year`, `min_share` | LODES WAC/RAC |

X.3 is the exhibit behind the population rank arc: first from 1810 to 1960, then passed by California, then Texas, then Florida. It reuses cleanly for any rank claim.

X.5 does the work for S2.3 and also for R.2 and M.13. Worth building properly because three questions need it.

---

### People

| ID | Exhibit | Type | Parameters | Source |
|---|---|---|---|---|
| X.6 | Age pyramid. | Age pyramid | `geo_level`, `geo_id`, `year` | ACS |
| X.7 | Median age map. | Choropleth | `geo_level`, `year`, `geo_filter` | ACS |
| X.8 | Top group by area. Each small area colored by its largest race or ethnicity group. | **NEW TYPE** (categorical choropleth) | `geo_level`, `year`, `category_set` | ACS |
| X.9 | Composition bars. Group shares across a set of geographies, ordered. | Stacked bar | `geo_level`, `geo_filter`, `category_set`, `year` | ACS |
| X.10 | Net migration map. | Choropleth, diverging | `geo_level`, `year_range`, `flow_type` (domestic, international, total) | IRS flows, ACS |
| X.11 | Top flows. Largest inbound and outbound origin-destination pairs for one geography. | Bar, paired | `geo_id`, `direction`, `year`, `top_n` | IRS flows |
| X.12 | Flow map. Origin-destination lines weighted by volume. | **Exploration only** | `geo_id`, `year`, `min_flow` | IRS flows |

X.8 is the NYT-style top-ethnicity-by-tract map. The library has no categorical choropleth, so this is a real build. It will also serve any other "which category dominates here" question, so it is worth doing once and doing well.

X.12 is listed so nobody builds it for print. Flow maps read badly as static PNG.

---

### Economy

| ID | Exhibit | Type | Parameters | Source |
|---|---|---|---|---|
| X.13 | Industry mix bars. Sector shares for a set of geographies, side by side. | Stacked bar | `geo_level`, `geo_filter`, `naics_level`, `year` | BEA |
| X.14 | Specialization grid. Location quotient by geography and sector. | Heatmap table | `geo_level`, `geo_filter`, `naics_level`, `year` | BEA, QCEW |
| X.15 | Job center map. Employment density with centers marked. | Proportional symbol map | `cbsa_code`, `year`, `threshold` | LODES WAC |
| X.16 | Concentration strip. How concentrated each geography is, by sector and separately by employer. | Strength strip | `geo_level`, `geo_filter`, `measure` (sector, employer), `year` | QCEW, BEA |
| X.17 | State footprint map. State-run institutions plotted against county population. | Proportional symbol over choropleth | `institution_types`, `geo_level` | SUNY, DOCCS, OMH, agencies |
| X.18 | Wage distribution. Spread of wages across occupations or across geographies. | Boxplot | `geo_level`, `geo_filter`, `year` | OEWS |

X.16 is the exhibit that carries S5.4, and the two-measure parameter is the whole point: one large sector and one large employer look different and mean different things.

X.17 depends on assembling the state institution list, which is the smaller of the two declared builds.

---

### Infrastructure and Structure

| ID | Exhibit | Type | Parameters | Source |
|---|---|---|---|---|
| X.19 | Network map. Roads, rail, transit, ports, or canal, drawn over a base geography. | Highlight context map | `layers`, `geo_extent`, `year` | Infrastructure engine (B1) |
| X.20 | Network with population. The same network overlaid with population, so gaps are visible. | Highlight context map + proportional symbol | `layers`, `geo_extent`, `pop_year` | Infrastructure + ACS |
| X.21 | Downtown crop. A zoomed map of one CBD with its anchors marked. | Highlight context map | `geo_id`, `anchor_types`, `zoom` | Internal Structure, POI |
| X.22 | Zone composition. Share of each zone type within a metro, benchmarked. | Bar, benchmarked | `cbsa_code`, `zone_model`, `year` | Intelligence Framework Phase 7 |

Map 2's bounded X.19 working draft is built and awaits visual review; X.20 remains unbuilt. Additional B1 layers remain deferred. X.21 is the CBD cell that will get reused on every metro spotlight, which makes it one of the highest-value exhibits in the bank once Internal Structure exists.

---

### Change and Comparison

| ID | Exhibit | Type | Parameters | Source |
|---|---|---|---|---|
| X.23 | Growth map. Change in a metric over a window. | Choropleth, diverging | `geo_level`, `metric_id`, `year_range` | ACS, warehouse |
| X.24 | Rank shift. How a set of geographies moved in rank between two years. | Bump chart | `geo_level`, `geo_filter`, `metric_id`, `year_a`, `year_b` | Warehouse |
| X.25 | Two-metric scatter. Any two metrics across a geography set, with quadrants. | Scatter | `geo_level`, `geo_filter`, `metric_x`, `metric_y`, `year` | Warehouse |
| X.26 | Before and after. One metric across two points in time for a set of geographies. | Slopegraph | `geo_level`, `geo_filter`, `metric_id`, `year_a`, `year_b` | Warehouse |
| X.27 | Within-metro spread. Distribution of a tract-level metric inside each metro. | Boxplot | `cbsa_filter`, `metric_id`, `year` | ACS tract |
| X.28 | Ranked bar with contributions. A ranking with the components that produced it visible. | Bar, segmented | `geo_filter`, `score_id`, `top_n` | Intelligence Framework |

X.25 and X.26 are the workhorses. Almost every ranking question and most thematic analyses land in one of these two shapes, which is why they are worth parameterizing carefully rather than rebuilding per article.

X.28 waits on composite scores going to production.

---

### Risk and Health

| ID | Exhibit | Type | Parameters | Source |
|---|---|---|---|---|
| X.29 | Risk map. | Choropleth | `geo_level`, `risk_metric`, `year` | FEMA, AQI |
| X.30 | Risk against growth. Hazard exposure on one axis, population change on the other. | Bivariate choropleth | `geo_level`, `risk_metric`, `year_range` | FEMA + ACS |
| X.31 | Outcome spread. A health outcome across regions or metros. | Boxplot or strength strip | `geo_level`, `geo_filter`, `outcome_metric`, `year` | health_wide |

X.30 is A3 Moving Toward Harm in a single chart, and the bivariate choropleth already exists in the library.

---

### Build Status Summary

**Ready now, library type exists:** X.1, X.2, X.3, X.4, X.6, X.7, X.9, X.10, X.11, X.13, X.14, X.15, X.16, X.18, X.23, X.24, X.25, X.26, X.27, X.29, X.30, X.31

**New visual type needed:** X.5, X.8

**Bounded working draft built; visual review pending:** X.19 (Map 2)

**Bounded inputs available, exhibit not built; remaining B1 layers deferred:** X.20

**Waiting on source assembly:** X.17

**Waiting on Internal Structure or POI:** X.21, X.22

**Waiting on composite scores:** X.28

**Exploration only, never print:** X.12

---

### Exhibit Spec Format

When an exhibit gets promoted, it gets a short spec. Not a schema, just enough that the next person who reaches for it knows what it takes.

```
### X.n Name
Type: <visual library type>
Question(s): <IDs from the Question Bank>
Takes: <parameter list with types>
Returns: <what the cell outputs>
Source: <tables or engine>
Notes: <suppression, vintage, coverage caveats>
```

# Part 4: Approach

Here we outline some of the common approaches we take. Decisions are numbered so other docs can cite them: **D** for data decisions, **E** for editorial decisions. The Question Bank and Exhibit Bank cite these IDs, so keep the numbers stable and add new rules at the end.

## Tools
- We will use Marimo notebooks for arranging and organizing our data for the articles
- Patterns in Place DuckDB for data storage
- Substack for posting
- Visual Library for standardizing visuals (final visuals, see E9)
- Carto and reactive maps for exploration only, never print (E10)

> [!note] Visual Library engine (settled 2026-10-15)
> Both the original R/ggplot2 library and its native Python port (Altair, matplotlib/geopandas) are in use. Which engine renders a given exhibit is an implementation detail for Claude Code sessions, not a series decision.

## Modules
We will use a modular approach to building out sections. This will enable us to reuse and rearrange our articles as needed while maintaining data standards.

## Data Decisions
- **D1.** Use official regional definitions (the 10 REDC regions) to start, but then we will compare with different regional definitions.
- **D2.** We will show all Metro and Micro CBSAs, but our focus will be on Metros.
- **D3.** We will use cross state data when looking at specific CBSAs, so we don't cut off the NYC area. The state level overview uses NY only data.
- **D4.** We will use the 2023 vintage as our standard (2023 CBSA delineations).

## Editorial Decisions
- **E1.** Voice: Writing as research, don't claim to know everything, the point is in finding out cool new things.
- **E2.** Frame: human stories are bridges to hard data, this is what keeps it from being another data dump and lets me learn about areas as more than just numbers.
- **E3.** Thesis: New York is always at the center.
- **E4.** History as section intros, not as their own section. We want to tie history directly into our writing as much as possible, instead of just making it a brain dump.
- **E5.** Articles are assembled from questions, analyses, and exhibits. Questions are standardized, analyses are the unique insights generated, and exhibits follow common best practices.
- **E6.** Time is a dimension, not a section.
- **E7.** The Primer is a writing exercise, it sets the foundation for our whole series.
- **E8.** Rankings should emerge from our writings. Let's see what's interesting to write about first, before we commit to a ranking article.
- **E9.** We should reuse our Visual Library for final visuals as much as possible.
- **E10.** Carto and reactive maps stay exploration only. Print visuals are static and come from the Visual Library.

# Part 5: Program Glossary

Metro Deep Dive program terms that the Question Bank and Exhibit Bank use without defining. Definitions marked **(inferred)** were reconstructed from how the banks use the term; confirm or correct them.

## Program Structure
- **Metro Deep Dive (MDD):** the flagship publishing program. Three layers: `engines/` (reusable computation, promoted to `foundations/` on second use), `analyses/` (parameterized Marimo notebooks), `issues/` (publication folders with lock once decisions)
- **Analysis families:**
  - **Position:** where a market stands. Includes Profile, Peers, Trajectory, Internal Structure, and the Candidate Scan
  - **Explanation:** why it stands there. The Q analyses below
  - **Thematic:** cross market themes. The A analyses below. Spec'd and outlined, not all built
- **Frames:** Character, Livability, Opportunity. The three lenses every market is scored on; a cross frame score combines them
- **Frame composite scores:** held back from print until the Intelligence Framework review answers Section B and A1
- **Composite scores** (affordability, overheating, economic strength, investment): designed, not in production

## Position Analyses
- **Profile:** frame and topic scores for one market against the nation
- **Peers:** most similar markets by frame and cross frame; cluster labels and peer lists are cleared for print
- **Trajectory:** how a market's position moved over time, with turn signals
- **Internal Structure:** how a metro is assembled internally (zones, downtowns, places). Part 1 runs for NY on national Phase 7 zones; Part 2 needs a NY POI run
- **Regional Role** (inferred): what a metro does for its wider region, via commuting and economic comparison. Partial today (LODES WAC/RAC only)

## Explanation Analyses (Q)
- **Q1** Housing supply and demand: is cheap housing a sign of supply or of absent demand
- **Q2** Job proximity: do people live near job centers (straight line distance only today)
- **Q3** (inferred) Where growth lands: greenfield, infill, or nowhere. Gated on tract vintage handling
- **Q4** (inferred) Amenity access: core amenities and access per tract. Gated on a NY POI run and an amenity basket
- **Q5** (inferred) Can people afford to live near the jobs (uses OEWS)
- **Q6** (inferred) County integration: does an outlying county really belong in its CBSA, based on commuting. Gated on stating an integration threshold

## Thematic Analyses (A)
- **A1** AI Inversion: are the metros that won the knowledge economy transition the most exposed to AI task displacement (Felten AIOE scores joined to OEWS)
- **A2** Building Lowers Prices: does building more housing lower prices
- **A3** Moving Toward Harm: are people moving toward hazard exposure
- **A4** Remote Work Rewired: did remote work rewire where work happens
- **A5** (inferred) Downtowns: is there one main downtown or several. Banked
- **A6** Specialization: does industry specialization predict growth
- **A7** Who Is Squeezed: which people in which places carry the worst cost burden
- **A8** Geography of Life Expectancy
- **A9** **OPEN:** not referenced anywhere in the NY series docs. Add the definition
- **A10** Job Polarization: is the wage distribution polarizing, and where

## NY Series IDs
- **S** primer questions (S2 to S6 match Lenses 1 to 5), **R** regional, **M** metro spotlight, **K** rankings, **F** reader framings: all in the Question Bank
- **X** exhibits: Exhibit Bank
- **B** declared builds: Question Bank
- **D** and **E** rules: Approach

## Geography
- **REDC regions:** the 10 official Regional Economic Development Council regions; the series' base regional definition (D1)
- **Vernacular regions:** colloquial regions (Upstate, Downstate, Western NY, Southern Tier, North Country). Where they disagree with REDC is a theme in itself (for example, Rochester is usually called Western NY but the REDC puts it in the Finger Lakes)
- **CBSA:** Core Based Statistical Area, metro or micro, 2023 delineations (D4)
