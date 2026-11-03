## What This Is

The questions we want to answer in the NY series. A question is what we want to know. It is not a chart and not an article. Questions get answered by analyses, analyses get shown through exhibits (see Exhibit Bank), and articles are assembled from the answers.

Every question has a home, a source, and a readiness. Readiness is the honest state of the data today:

- **Ready** means the data is in the warehouse and the question can be answered now
- **Gated** means something specific is blocking it, named in the row
- **Build** means it needs new ingest work

Questions here that map to the Metro Deep Dive program keep the program's own IDs (Q1 to Q6, A1 to A10) so we are not maintaining two vocabularies.

### Declared Builds

Build work named in the readiness column. Each build unblocks a set of questions and exhibits.

| ID | Build | Unblocks | Status |
|---|---|---|---|
| B1 | NY infrastructure ingest: highways, Amtrak and major rail, MTA lines and stations, ports, bus depots, Erie Canal | S3.1, S3.2, R.3, X.19, X.20 | Mostly built 2026-11-02: statewide roads, rail, subway lines and canals (local Parquet), plus stations, ferry terminals, bus facilities and airports in the warehouse. Ports not built. See [the build plan](NY_STATEWIDE_DATA_BUILD_PLAN.md). **OPEN:** confirm layer list and whether the Erie Canal and Thruway for the Series Intro map come from B1 or are hand assembled |
| B2 | State footprint source assembly: SUNY, DOCCS prisons (open and closed), OMH psychiatric centers, state parks, the Adirondack Park and DEC lands, plus state government jobs by county | S5.3, S5.4, R.10, X.16, X.17 | Not started. Source plan below |

#### B2 Source Plan

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
- ~~**No NY POI run**~~ Lifted 2026-11-02: the NY POI run exists with categories (S3.4, R.5, M.11, M.12, K.9, K.10, X.21). The M.11 basket is a pick of POI categories, made at analysis time
- **Internal Structure notebooks crash as committed** (S3.3, S3.4, M.2, M.12, K.9, K.10, X.21, X.22). The analysis exists as two per-market notebooks, and there is no separate script. The queries and marts work; see [Notebook fixes](NY_STATEWIDE_DATA_BUILD_PLAN.md#notebook-fixes)
- **LODES OD not ingested** gates M.14. Albany Part 2 uses county commuting shares instead
- ~~**Composite scores not in production**~~ Lifted 2026-11-02: composite scores (affordability, overheating, economic strength, investment) are built within each analysis as needed (an approach, not a production layer). K.5, K.7, K.8 and X.28 build theirs in the analysis. Frame composite scores were updated 2026-11-02; print clearance is open decision 15

### Build Work by Piece

Carried over from the retired Article Slate and refreshed 2026-11-02. Article order is in the Series Overview.

| Work | Kind | Unblocks | Needed by |
|---|---|---|---|
| QCEW state government share by county (B2 step 1) | Query, no ingest | S5.3, S5.4, X.16 | Albany Part 2, The State as Employer |
| POI filter review ([candidate and evidence](NY_STATEWIDE_DATA_BUILD_PLAN.md)). Raw POI counts overstate some markets until done | Review | M.11, M.12, S3.4, R.5, K.9, K.10, X.21 and any cross-market POI count | Top Downtowns, Most Walkable Districts |
| Categorical choropleth types (X.5, X.8) | Visual Library | S2.3, R.2, M.13, top group maps | What Is Upstate |
| ~~POI runs beyond Albany~~ Done 2026-11-02: all 27 NY CBSAs and the non-CBSA counties (`SYNTH-NY`). Filter by confidence before comparing markets; see the [build plan](NY_STATEWIDE_DATA_BUILD_PLAN.md) | Engine run | Internal Structure Part 2, M.11, M.12, S3.4, R.5, K.9, K.10, X.21 outside Albany. Q4 still needs its markets wired | Top Downtowns, Most Walkable Districts |
| LODES OD ingest ([scope](../../analyses/explanation/q6_one_metro/LODES_OD_INGEST_AGENT_SCOPE.md)) | New ingest | M.14, commute flows in Regional Role and Q6 | Stronger version of What Is Upstate, Capital District |
| B1 remaining layer: ports. MTA lines and stations, bus depots and rail were built 2026-11-02 | Engine extension | S3.1, S3.2, R.3, X.20 | The Canal Corridor 200 Years On |
| ~~Geography: analytical CBSA boundary~~ Not a gate for NY: the statewide infrastructure runs clip to analytical state geometry and are cleared for consumers | Engine slice | Infrastructure layers becoming authoritative | The Canal Corridor 200 Years On |
| B2 steps 2 and 3: state institution points; Blue Line and DEC Lands polygons | Source assembly | S5.3 map, X.17, R.10 | The State as Employer (full version), The Adirondacks |
| Thematic notebooks: A3, A4, A8 (Epic 1 audit first) | Analysis build | Statewide analyses that use them | Growing Toward Harm?, The Canal Corridor 200 Years On, the life expectancy piece |

**Readiness to verify before planning around these:**
- **M.4 (Q3):** `mart_explanation_q3.tract_growth_status` and `place_growth_horizons` have Albany rows. Is the tract vintage issue actually handled?
- **M.10 (Q6):** the place, anchor and county context marts were recorded as existing for Albany, but on 2026-11-02 the stored `place_poi_context` held only Richmond and Jacksonville and `place_infrastructure_context` only Richmond. The Q6 notebook's POI queries read `mart_poi` live. Albany Part 1 used OMB's 25% commuting test as a working threshold; adopting it would settle open decision 3

---

## Primer Questions

### What NY Actually Is

| ID | Question | Source | Readiness |
|---|---|---|---|
| S2.1 | How do the 10 official REDC regions compare to the colloquial ones, and where do they disagree? | Geography engine, CBSA delineations | Ready |
| S2.2 | Which CBSAs sit in which region under each definition, and which ones move? | Geography engine | Ready |
| S2.3 | For counties in no CBSA at all, are they functionally independent or orbiting a neighboring metro? | LODES WAC/RAC, county grain | Ready |
| S2.4 | How does NY compare to the rest of the country on the basic benchmarks? | Benchmarking engine | Ready |
| S2.5 | How much of the state is downstate, and how has that share moved over time? | ACS, decennial | Ready |

S2.3 is Q6 pointed the other way. Q6 asks whether an outlying county inside a CBSA really belongs. This asks whether a county outside every CBSA is orbiting one anyway. Same commuting evidence, opposite direction. The primer version stays simple: where do this county's workers go, and is there a dominant destination.

### The Lines People Move Along

| ID | Question | Source | Readiness |
|---|---|---|---|
| S3.1 | What is the physical network that moves the state? | Infrastructure engine | **Build** (B1) |
| S3.2 | Which population centers are far from major infrastructure? | Infrastructure + ACS population | **Build** (B1) |
| S3.3 | Where are the core downtowns and central business districts? | Internal Structure, A5 | Data ready; the Internal Structure notebooks need [fixes](NY_STATEWIDE_DATA_BUILD_PLAN.md#notebook-fixes) |
| S3.4 | What anchors each downtown: transit, a university, an office core, a hospital, government? | Internal Structure, POI | Data ready; the Internal Structure notebooks need [fixes](NY_STATEWIDE_DATA_BUILD_PLAN.md#notebook-fixes). POI filter review before comparing markets |
| A4 | Did remote work rewire where work happens? | ACS WFH series, LODES | Ready |

### Who Lives Here

| ID | Question | Source | Readiness |
|---|---|---|---|
| S4.1 | What does the state's age structure look like, and how does it vary geographically? | ACS | Ready |
| S4.2 | Where are people from, and how does that change from CBSA to county to tract? | ACS | Ready at CBSA and county; confirm tract grain |
| S4.3 | Which places have the most external migration, and what did it do to them? | ACS nativity, IRS flows | Ready; use IRS county totals for net migration ([N11](../NATIONAL_FOLLOWUPS.md)) |
| S4.4 | Which states do New Yorkers move to, and which states do they come from? | IRS flows 2012 to 2022 | Ready; flows leave out suppressed small pairs, mostly out of state ([N11](../NATIONAL_FOLLOWUPS.md)) |
| S4.5 | Where do people move within the state? | IRS county flows | Ready; flows leave out suppressed small pairs ([N11](../NATIONAL_FOLLOWUPS.md)) |
| A2 | Does building more housing lower prices? | Permits, HPI, stock composition | Ready |
| A7 | Who is squeezed: which people in which places carry the worst cost burden? | ACS burden, income | Ready |

Housing lives here rather than in Infrastructure because A2 and A7 are about who can afford to live where, which is a question about people.

### What People Do Here

| ID | Question | Source | Readiness |
|---|---|---|---|
| S5.1 | What are the top industries and sectors by region, and how different are the regions really? | BEA sector shares | Ready |
| S5.2 | Where are the core job centers? | LODES WAC | Ready |
| S5.3 | Where is the state's own footprint, and which small counties does it sit on? | SUNY, DOCCS, OMH, state agencies, parks | **Build** (source assembly) |
| S5.4 | How concentrated is each place, by sector and by employer? | QCEW 2010 to 2024, BEA | Ready, with small county suppression |
| A6 | Does industry specialization predict growth? | LQ lagged panel | Ready |
| A10 | Is the wage distribution polarizing, and where? | Sector wage distribution, OEWS | Ready |

S5.4 measured two ways tells different stories. One large sector is not the same as one large employer. A county can look diversified by sector and still have a single state institution as its largest employer. That is the finding worth writing about, and it feeds the rankings later.

### Where It's Headed

| ID | Question | Source | Readiness |
|---|---|---|---|
| S6.1 | Which areas are growing and which are shrinking? | ACS, decennial | Ready |
| S6.2 | Which areas carry the highest environmental risk? | FEMA risk score, AQI | Ready |
| S6.3 | What do health outcomes look like by region and CBSA? | health_wide | Ready |
| S6.4 | What major investments and policies are coming, and where do they land? | Editorial research | N/A, not a data question |
| A3 | Are people moving toward harm? | Hazard vs growth | Ready |
| A8 | What is the geography of life expectancy in the state? | health_wide | Ready |

---

## Regional Deep Dive Questions

These run per region. The first four are the same question asked of every region; the rest are specific arguments we already know we want to make.

| ID | Question | Source | Readiness |
|---|---|---|---|
| R.1 | How do the cities inside this region fit together? | Peers, LODES, industry mix | Ready |
| R.2 | Does this region make sense on its own, or does it belong with another? | Commuting, industry, migration | Ready |
| R.3 | Is this region underserved by infrastructure? | Infrastructure + population | **Build** (B1) |
| R.4 | Where is housing being built in this region, and what is the existing stock? | Permits, ACS stock | Ready |
| R.5 | Are there real amenity clusters here? | POI | Ready for one market. POI filter review before comparing markets |
| R.6 | Western NY and the Finger Lakes: one region or two? | R.2 applied | Ready |
| R.7 | What is "Upstate"? | R.2 applied, plus the vernacular evidence | Ready |
| R.8 | How is the Southern Tier defined, and by whom? | R.2 applied | Ready |
| R.9 | Are NYC and Long Island really two regions? | Commuting, CBSA delineation | Ready |
| R.10 | Why the Adirondacks will never be developed, and why that is fine | Park boundary, land use, forever wild | Ready |

---

## Metro Deep Dive Questions

The spotlight template, with each section's questions mapped to the program analysis that answers it. Nothing here is new; this is the program applied to NY metros.

### Overview
| ID | Question | Program | Readiness |
|---|---|---|---|
| M.1 | What kind of market is this, and where is it going? | Position: Profile, Trajectory | Ready. Frame composite scores updated 2026-11-02; print clearance is open decision 15 |
| M.2 | How is the metro assembled internally? | Position: Internal Structure | Data ready; the Internal Structure notebooks need [fixes](NY_STATEWIDE_DATA_BUILD_PLAN.md#notebook-fixes). Seven national tract types cleared for print, used in Albany Part 1 |
| M.3 | Who are its peers? | Position: Peers | Ready (cluster label and peer list cleared for print) |

### Housing and Growth
| ID | Question | Program | Readiness |
|---|---|---|---|
| M.4 | Where is growth landing: greenfield, infill, or nowhere? | Q3 | Gated (tract vintage handling) |
| M.5 | What does the existing housing stock look like, and is cheap housing supply or absent demand? | Q1 | Ready |

### Jobs
| ID | Question | Program | Readiness |
|---|---|---|---|
| M.6 | What are the main job centers? | Job centers (built) | Ready |
| M.7 | Do people live near them, and can they afford to? | Q5, Q2 | Q5 ready (OEWS present); Q2 straight line only |
| M.8 | What are the core industries and anchor employers? | Industry surfaces, QCEW | Ready |

### Metro Construction
| ID | Question | Program | Readiness |
|---|---|---|---|
| M.9 | Is there one main downtown or several? | A5 | Banked |
| M.10 | Which counties are core, outlying, exurban, and do they really belong? | Q6 | Gated (integration threshold must be stated). Albany Part 1 uses OMB's 25% commuting test as a working threshold |

### Daily Amenities
| ID | Question | Program | Readiness |
|---|---|---|---|
| M.11 | What are the core amenities, and how good is access per tract? | Q4 | Ready. Pick the basket from POI categories at analysis time. Starting point: grocery, pharmacy, primary care, school, park, library, cafe or restaurant |
| M.12 | Are there specific clusters, and how do they line up against downtowns, jobs, and housing? | Q4 + Internal Structure | Data ready (with the M.11 basket); the Internal Structure notebooks need [fixes](NY_STATEWIDE_DATA_BUILD_PLAN.md#notebook-fixes) |

### Regional Role
| ID | Question | Program | Readiness |
|---|---|---|---|
| M.13 | What role does this city play in its broader region? | Regional Role | Partial (WAC/RAC only) |
| M.14 | Where do people commute from? | Regional Role | Gated (LODES OD not ingested) |
| M.15 | How does its economy compare to the rest of the region? | Benchmarking, industry mix | Ready |

### Spotlights
Per-metro questions that sit outside the template.

| ID | Question | Applies to | Readiness |
|---|---|---|---|
| M.16 | How much of this economy is the university, and what does the student population do to the numbers? | Ithaca, Binghamton, Syracuse, Albany | Ready |
| M.17 | What did the anchor employer leave behind after it shrank? | Schenectady, Rochester, Binghamton | Ready |
| M.18 | What did resettlement do to a city built for more people? | Utica | Ready |

For Albany, M.16 (SUNY Albany, RPI, Union, Skidmore) is planned for Part 2. The Empire State Plaza and Rockefeller story is a history lead (E4), not M.16.

### Coverage by Article

Which questions each drafted article draws on, so later pieces don't repeat them and gates show up before drafting.

| Article | Questions used | Notes |
|---|---|---|
| Albany Part 1: What Albany Actually Is (published 2026-11-01) | M.1, M.2, M.3, M.6, M.9, M.10, M.13 (county commuting shares), M.15, S4.5 | M.10 uses OMB's 25% threshold. The Second City argument seeds K.3 |
| Albany Part 2: is Albany more than a government town? (next) | M.8, M.13, M.15, M.16 | County commuting shares in place of M.14. Don't repeat M.6 job centers |

### Using the Analysis Notebooks

The `metro-deep-dive-program/analyses/` notebooks are the exploration surface for metro pieces. Most take a CBSA from a dropdown filled from the warehouse and default to Richmond (40060).

1. **Explore in the analysis notebooks as they are.** Open with `marimo edit <notebook>` and switch the dropdown to the metro (Albany is 10580). Don't change the Richmond defaults; they're part of each analysis's QA setup. The Q2 notebooks also read `Q2_CBSA_CODE` and Regional Role reads `REGIONAL_ROLE_CBSA_CODE`, so setting either opens them on the chosen metro.
2. **Put findings in the piece's outline,** next to the question ID they answer, not in the analysis folder.
3. **Build print visuals in the piece's own folder,** following the [visuals build rules](../VISUALS_BUILD_RULES.md) and [`WHAT_NY_IS_VISUALS.py`](primer/series_intro/WHAT_NY_IS_VISUALS.py). Reuse the analyses' `queries/*.sql` rather than copying their logic. Final story assembly lives in `issues/`, not `analyses/`.
4. **For a question with no notebook,** query the warehouse from the piece's notebook and note which queries get copied between metros: that's the signal to promote them.

**Notebook readiness for NY.** This table is the source of truth; update it when a notebook gains NY coverage.

| Notebook | Questions | Status for NY |
|---|---|---|
| [Act 1 Position](../_shared/act_1/ACT_1_POSITION_NOTEBOOK.py) | M.1, M.3 | Ready; good first look at any metro |
| [Profile](../../analyses/position/profile/POSITION_PROFILE_NOTEBOOK.py) | M.1 | Ready; frame score print clearance is open decision 15 |
| [Peers](../../analyses/position/peers/POSITION_PEERS_NOTEBOOK.py) | M.3, K.6 | Ready; peer lists cleared for print |
| [Trajectory](../../analyses/position/trajectory/POSITION_TRAJECTORY_NOTEBOOK.py) | M.1 | Ready |
| [Candidate Scan](../../analyses/position/candidate_scan/POSITION_CANDIDATE_SCAN_NOTEBOOK.py) and [Discovery](../../analyses/position/candidate_scan/POSITION_CANDIDATE_DISCOVERY_NOTEBOOK.py) | K.2, K.6 | Ready; all markets, filter to NY |
| [Internal Structure Part 1](../../analyses/position/internal_structure/POSITION_INTERNAL_STRUCTURE_NOTEBOOK.py) | M.2 | Crashes as committed; small [fix](NY_STATEWIDE_DATA_BUILD_PLAN.md#notebook-fixes) (national Phase 7 zones) |
| [Internal Structure Part 2](../../analyses/position/internal_structure/POSITION_INTERNAL_STRUCTURE_PART2_NOTEBOOK.py) | M.2, M.12 | Crashes as committed; see [fixes](NY_STATEWIDE_DATA_BUILD_PLAN.md#notebook-fixes). Selector covers every CBSA and POI marts cover every NY CBSA, but NY markets show no infrastructure |
| [Q1 Market](../../analyses/explanation/q1_supply_or_demand/EXPLANATION_Q1_MARKET_NOTEBOOK.py) and [National](../../analyses/explanation/q1_supply_or_demand/EXPLANATION_Q1_NATIONAL_NOTEBOOK.py) | M.5, M.18 | Ready |
| [Q2 Job Center Outcomes](../../analyses/explanation/q2_job_proximity/EXPLANATION_Q2_JOB_CENTER_OUTCOMES_NOTEBOOK.py) | M.6, M.7, M.9 | Ready (straight line distance only) |
| [Q2 Job Concentration](../../analyses/explanation/q2_job_proximity/EXPLANATION_Q2_JOB_CONCENTRATION_NOTEBOOK.py) | M.15, M.17 | Ready; set a comparison market |
| [Q2 Proximity Method](../../analyses/explanation/q2_job_proximity/EXPLANATION_Q2_PROXIMITY_METHOD_NOTEBOOK.py) | M.7 | Ready (method review) |
| [Q3 Where Growth Lands](../../analyses/explanation/q3_where_growth_lands/EXPLANATION_Q3_NOTEBOOK.py) | M.4 | Data present; tract vintage gate to verify |
| [Q4 Daily Needs](../../analyses/explanation/q4_daily_needs/EXPLANATION_Q4_NOTEBOOK.py) | M.11, M.12 | Not open for NY: its market dropdown lists only Richmond and Jacksonville. Albany Part 1 read the POI run directly from its own `sql/` |
| [Q6 One Metro](../../analyses/explanation/q6_one_metro/EXPLANATION_Q6_NOTEBOOK.py) | M.9, M.10 | Ready; state the integration threshold for print (Albany Part 1 used OMB's 25%) |
| [Regional Role](../../analyses/explanation/regional_role/EXPLANATION_REGIONAL_ROLE_NOTEBOOK.py) | M.13, M.14, M.15 | Partial: LODES WAC/RAC only, no commute flows |
| [Infrastructure exploration](../../engines/infrastructure/INFRASTRUCTURE_EXPLORATION_NOTEBOOK.py) | S3.1 | Engine notebook; statewide NY core and context runs exist. The notebook has not been checked against them |
| Thematic A1 to A10 | A3, A7 and others | Specs and build plans only, no notebooks. Query directly, or build after the entry's Epic 1 audit |
| Catchment | None | Not used; built around a single Jacksonville property |

---

## Rankings Questions

Rankings emerge from the writing (E8). These are the axes we have named so far, not a commitment to write all of them.

| ID | Question | Readiness |
|---|---|---|
| K.1 | Which metros have the strongest job centers? | Ready (raw KPIs) |
| K.2 | Which are growing fastest and slowest? | Ready. ACS 5 year, 2010 to 2014 vs 2020 to 2024 pooled. First ranking piece (2026-11-02) |
| K.3 | Which have the strongest economic indicators? | Ready (raw KPIs) |
| K.4 | Which have the most human capital? | Ready |
| K.5 | Which metros are underrated, and what does underrated mean? | Ready (composite built in the analysis) |
| K.6 | Which cities are growing faster or slower than their national peer group? | Ready (cluster labels cleared for print). Peers use `irs_net_agi`; the [N11](../NATIONAL_FOLLOWUPS.md) effect on them is unchecked |
| K.7 | Which have a strong economy now, and which have the ingredients for one? | Ready (composite built in the analysis) |
| K.8 | Which areas need investment most? | Ready (composite built in the analysis) |
| K.9 | Which are the top downtowns? | Gated: POI filter review, and the Internal Structure notebooks need [fixes](NY_STATEWIDE_DATA_BUILD_PLAN.md#notebook-fixes) |
| K.10 | Which are the most walkable districts? | Gated: POI filter review, and the Internal Structure notebooks need [fixes](NY_STATEWIDE_DATA_BUILD_PLAN.md#notebook-fixes) |
| A1 | How exposed is each metro's job mix to AI? | Active |

Composite scores (affordability, overheating, economic strength, investment) are built within each analysis as needed (an approach, not a production layer), so K.5, K.7 and K.8 are buildable now. Defining "underrated" (K.5) is still the editorial work. Frame composite scores were updated 2026-11-02; whether they print is open decision 15.

---

## Reader Framings

Not questions and not analyses. These are article shapes that pull from questions already banked. Each could become its own piece.

| ID | Framing | Pulls from |
|---|---|---|
| F.1 | If I am a young person looking for work, where do I go? | S6.1, M.6, K.1, K.2, R.4 |
| F.2 | If I am older, where can I best afford to retire? | S4.1, R.4, A7, S6.3 |

---

## Not Questions

Things raised in planning that belong elsewhere, kept here so they do not get re-raised as questions.

| Item | Where it belongs |
|---|---|
| NY's population rank falling from first to fourth | Editorial, with one exhibit (X.3) |
| Sunnyside Yards and other named investments | Editorial, S6.4 |
| Ellis Island, the Erie Canal, Rockefeller, Moses | Section intros (E4). Empire State Plaza opens the jobs section of Albany Part 1 |
| Comparative state history: is NY really the only state central in every era? | Open. A possible piece, not a primer question |
| "How has the state changed over time" | Not a question. Time is a dimension on every question (E6) |

---

## Appendix: Mapping From the First Module List

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
