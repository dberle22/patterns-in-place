# Albany Lens 1: Visuals Build Plan

**Status:** Active
**Updated:** 2026-10-26

Outline: [ALBANY_LENS1_OUTLINE.md](ALBANY_LENS1_OUTLINE.md). Rules: [VISUALS_BUILD_RULES.md](../../VISUALS_BUILD_RULES.md). Notebooks: [exploration](ALBANY_LENS1_EXPLORATION.py) and [visuals](ALBANY_LENS1_VISUALS.py); exploration helpers in [albany_explore.py](albany_explore.py); the commuting work banked for Lens 2 in [ALBANY_LENS2_EXPLORATION.py](ALBANY_LENS2_EXPLORATION.py).

Geography: the 5-county Albany-Schenectady-Troy CBSA (10580), 2023 delineation (D4).

## Handoff: start of the next session

**Update (2026-10-24):** the article structure changed (see Article structure below). Q4 was explored first, as the grounding for the new At a glance opening, and the exploration notebook is now interactive: pickers with one large chart, and zoomable Carto maps with toggleable overlays (Review 6). Later the same day (Review 7): the At a glance set is chosen and prototyped (Q4e), the key-places draft is ready for Dan's data review (Q4f, R14), Q1 is banked for Lens 2 apart from a high-level line, and every exploration map is now interactive. Next: Dan's data review of the key places and the Q4 reads, then the Q3 re-run on the new clusters.

**Where things stand (2026-10-23):**
- **Q1 (commuting) is fully explored,** with eight views and draft reads. Dan is reviewing it.
- **Q2 is partly explored** (job centers on all jobs, public share).
- **Q3 is explored on the promoted zones** (re-run 2026-10-27), with Q3e combining the zones and the POIs (Review 13). A corridor view is still to do.
- **Q4 has v1 exhibits and three small checks.**

The visuals notebook still holds v1, organized by outline section. It gets reorganized by question as each question is promoted (Workflow, step 5).

**First steps for the next session:**
1. Take Dan's Q1 review: confirm or edit the reads, and pick the views to print (Q1 Gate A).
2. Promote Q1 into the visuals notebook (Workflow, Promote). This also starts the notebook's reorganization by question.
3. Explore Q2 (Workflow, Explore).

## Workflow: one question at a time

Each question set goes through the same loop, start to finish, before the next one starts. Two notebooks, two jobs:

| Notebook | Job | Organized by | Style |
|---|---|---|---|
| [ALBANY_LENS1_EXPLORATION.py](ALBANY_LENS1_EXPLORATION.py) | Answer the question: several tables and quick views, then the reads | Article section (since 2026-10-26, Review 12), keeping the question IDs (Q1a, Q4g, …) | Quick: house colors, no print polish |
| [ALBANY_LENS1_VISUALS.py](ALBANY_LENS1_VISUALS.py) | Print exhibits and the confirmed results that back them | Question set, in article order | Print: `new_map`, `add_text`, `save`; settings cells; check tables |

**The loop, per question:**

1. **Explore** (exploration notebook). Build the candidate views listed under the question: tables first, then maps or charts, from more than one angle (R30). End the section with dated **Reads**: draft article sentences with numbers (R31).
2. **Gate A: Dan reviews the reads.** He confirms or edits each read, asks for more angles if needed, and **picks the views that become print exhibits**. Record it as a dated review below; locked choices go in Locked decisions.
3. **Promote** (visuals notebook), one exhibit at a time:
   - Give the question its own section: a markdown cell with the claim and the confirmed reads, then a data cell, a check table, a settings cell, a draw cell and `save(...)`.
   - **Move, don't copy.** A prep function or query that a print exhibit uses moves into the visuals notebook (helpers) and `sql/`; the exploration notebook imports it back. Exploration-only helpers live in `albany_explore.py`, which every lens's exploration notebook imports.
   - The check table asserts the confirmed reads' numbers (R10), so a data refresh that changes a printed claim fails loudly.
   - The drawing is rebuilt in print style. Exploration figures are never exported.
   - Mark the exploration sub-section "Promoted → E#".
4. **Gate B: Dan reviews each draft exhibit.** Revisions go beside the original (R24) and are recorded in a dated review.
5. **Close the question.** Its status in the table below goes to "Promoted", and the outline section is updated (Dan edits the outline). Then the next question starts.

The first time a question is promoted, its section replaces the matching v1 section in the visuals notebook. Any v1 cells not yet promoted move to a "v1 (2026-10-22), superseded" block at the end until Dan cuts them.

**Status values:** Planned → Exploring → Reads ready (waiting on Gate A) → Promoting → Drafts ready (waiting on Gate B) → Promoted.

## Question sets

| # | Question | Outline section | Bank | Status | Exhibits |
|---|---|---|---|---|---|
| Q1 | Who belongs to the metro, and how far does Albany's labor market reach? | How it's assembled (high level only) | M.10 | **Banked for Lens 2** (M.13, M.14), apart from "does every county belong" and one line on reach (Dan, 2026-10-24) | E1; shed maps go to Lens 2 |
| Q2 | Is there a center, or four cities? Where do people live, where are the jobs? | 2 | M.9, M.2 | Exploring | TBD at Gate A |
| Q3 | How is the metro assembled inside? | 3 | M.2 | Explored on the promoted zones, with Q3e (2026-10-27); corridor view to do | TBD at Gate A |
| Q4 | What kind of market is this, and who are its peers? | At a glance + What kind of place (new order) | M.1, M.3 | Exploring (interactive views built 2026-10-24; reads next) | E7, E8 (v1); At a glance TBD |

Order: Q1 → Q2 → Q3 → Q4. Q3 comes after Q2 so the anchors and roads layers built for Q2 can serve its corridor view.

### Q1. Who belongs, and how far does Albany reach?

**Explore** (exploration notebook, Q1a–Q1h):
- [x] Q1a: where each member county's residents work (table)
- [x] Q1b: commuting in, by outside county and distance band, with the public/private split (R33); regional map
- [x] Q1c: commuting out, where metro residents work outside it; regional map
- [x] Q1d: statewide, the largest outside metro for every NY county, with and without NYC
- [x] Q1e: reach, how many outside NY counties send 5/10/25%+ to each NY metro
- [x] Q1f: county-to-county matrix inside the metro
- [x] Q1g: the four cities, place-level OD both ways
- [x] Q1h: tract-level sheds for the four largest all-jobs centers. Data: `commute_sheds` run for 10580 on 2026-10-22, `either_endpoint`, JT00 + JT02, 49 states' aux files (AK and MI unpublished), all reconciled.
- [ ] Optional: OMB's own input (ACS 2016–20 county commuting) to check Schoharie. Needs a small ingest (Open decisions).

**Draft reads** (2026-10-22; confirm at Gate A):
- **One labor market at the core.** Rensselaer and Schenectady residents hold more jobs in the other central counties (42%, 38%) than at home (28%, 33%).
- **Albany County is the hub.** Rensselaer residents hold more jobs in Albany County (39%) than at home (28%).
- **Saratoga is a bridge.** 39% of its residents' jobs are at home, 35% in the core. It also supplies most of the metro residents working in Warren and Washington (80% and 72%).
- **Schoharie is the loosest member.** 49% of its residents' jobs are outside the metro, and 16% are in the core: short of the 25% rule on this data.
- **A ring of six outside counties sends 20–30% of their residents' jobs in** (Montgomery, Washington, Warren, Fulton, Greene, Columbia). Five are central counties of their own micro or metro areas in the CSA. **Greene is in neither**, and 20% of Greene's jobs are held by metro residents.
- **Albany has the widest commute shed upstate.** Leaving out NYC, it is the largest outside metro for 10 NY counties, more than any other metro. Eleven outside counties send 5%+ of their resident jobs there, and four send 25%+. Only NYC reaches further (24 counties at 5%+), and much of that is the remote-work effect.
- **The long tail isn't commuting.** About 63k inbound jobs come from 75–150 miles away, and 14k metro residents hold jobs "in" Manhattan. These are mostly private-sector, so most likely remote work and companies reporting every job at one address.
- **Albany city is a commuter city.** Only 14% of its 132k jobs are held by city residents. Troy residents are as likely to work in Albany (19%) as in Troy (18%).
- **Saratoga Springs draws from its towns:** 51% of its jobs are held by people living outside any Census Place.
- **The uptown-Albany-to-Wolf-Road band is the shared center:** 96k jobs, median worker 11 miles away, 10–20% of resident jobs in nearly every inner-county tract. Schenectady and Saratoga Springs run their own sheds (47% and 59% from their own county).
- **Downtown Albany's 50k jobs include about 15k held by people 75+ miles away** (statewide employers reporting at downtown addresses, R33). The local downtown workforce is nearer 35k; caveat any "biggest center" claim.

**Gate A** (Dan, in progress): which reads hold, and which views print. Candidates:
- E1, the bearings map (county flags plus city outlines and highways)
- E2, commuting in and out (Q1b/Q1c, or the statewide pull in Q1d)
- The reach table (Q1e)
- The four center shed maps (Q1h)

**Promote:** after Gate A.
- [ ] Reorganize the visuals notebook: a Q1 section replaces v1 sections 1 and 4
- [ ] Shared print layers that Q1 needs: city outlines, roads (see Shared layers)
- [ ] One exhibit at a time, each with a check table on the confirmed reads

### Q2. Is there a center, or four cities?

**Use all jobs (R34).** All-jobs counts: Albany city 131.8k (72.1k private), Schenectady 28.0k, Saratoga Springs 24.9k, Troy 19.1k; metro 460k (351k private).

**Explore:**
- [x] Q2a: job centers on all jobs. Q2's `apply_method` is imported unchanged and run on JT00 for 10580 only (`sql/q2_tracts_all_jobs.sql`); Q2's national mart is untouched. Comparison table and map against the published private centers.
- [x] Q2b: public share of jobs by tract (all minus private). Sets up Lens 4.
- [ ] Tract population density with the four city outlines (same classes as the series intro's Population Map)
- [ ] Tract jobs per resident worker, all jobs (2023 LODES WAC/RAC all-jobs totals)
- [ ] Table: the four cities and the larger CDPs, with residents, resident workers, jobs and jobs per worker, summed from the tracts inside each (R13); plus the share of metro population living outside any of them
- [ ] The Q6 anchor table, corrected: 10 components, 6 places
- [ ] The job center map with roads, rail, city outlines and curated anchors (needs the shared layers and `reference/anchors.csv`)

**Draft reads, Q2a/b** (2026-10-22):
- **The metro's biggest job tract is downtown Albany** (36001001100): 50k jobs, 71% public. Counting private jobs only, it looked like 14.5k. (See Q1's caveat on 75+ mile workers.)
- **The largest center is one 13-tract, 96k-job band** from uptown Albany through Colonie and Wolf Road. It takes in two mostly public uptown tracts (87% and 66%), likely the state office campus and the university; confirm with anchors.
- **11 centers on all jobs vs 14 on private.** Six small private centers (Malta among them) drop below the 1% floor as the metro total rises (Open decisions).
- Rural tracts show 40–60% public shares on small totals (schools, county seats).

### Q3. How is the metro assembled?

**The clusters changed.** Phase 7 was rerun on the fixed unemployment rate and promoted on 2026-10-23 ([review](../../../../exploration/intelligence_framework/phase_7_zone_methodology/PHASE7_LABOR_FIX_RERUN_REVIEW.md)). The original seven names were carried forward to the matched clusters and stay `draft_label_pending_review`. Names are reviewed **CBSA by CBSA during issue work**: propose Albany renames here for Dan's decision, not a national sweep. A rename means editing `zone_name_map` in `phase7_config.R` and re-promoting.

**Explore:**
- [x] Q3a: what the labels describe, raw median profile per zone type, US vs Albany (`sql/zone_profile.sql`)
- [x] Q3b: without labels, six tract maps of the raw inputs at metro quintiles
- [x] Q3c: Albany working names with a stress test (tracts per name and where they are; the 25 worst fits)
- [x] Q3d: POIs, the category mix by working name, POI clusters (k-means, k = 5), and dot maps
- [x] **Re-run Q3a and Q3c on the new clusters** (done 2026-10-27; reads refreshed, stress-test finding holds): what moved for Albany's 251 tracts, and do the working names and the stress-test finding still hold? First sign (2026-10-24, Q3c zone map): Comfortable suburbs 143, Rural and exurban 39 (was 48), Lower-income urban 32, Affluent urban 22 (was 1), Students and young professionals 13, Working-class urban 2. The working-names table and reads below predate this.
- [x] Q3e: who lives here × what's there. Each tract keeps its zone and gets one of four activity classes (Residential, Local-serving, Destination, Employment and industrial) by plain rules on POIs per resident, jobs per resident (LODES all jobs) and destination and industrial POI shares against the metro mix (`tract_activity`, `sql/tract_activity_base.sql`; Review 13)
- [ ] Q3: a POI corridor view (after the roads layer)
- [ ] A simple two-metric typology (e.g. density × income, or bachelor's share × owner share) as a transparent alternative
- [ ] A corridor view of POIs, once the roads layer is in

**Working names** (draft, on the pre-rerun clusters; re-check):

| National type | Albany working name | Stress test |
|---|---|---|
| Mixed-Income Middle Neighborhoods | Comfortable suburbs | **Splits in two.** Affluent suburbs (Loudonville, Niskayuna: $180–200k, poverty <2%) and modest small-city neighborhoods (Mechanicville, Watervliet, inner Schenectady: $49–71k, poverty 16–19%). Rename broader ("Middle neighborhoods") or split for Albany. |
| Established Residential | Rural and exurban | Fits: 43 of 48 tracts are town areas |
| Entry-Market Neighborhoods | Lower-income urban | Fits: the four cities' cores |
| Emerging Knowledge Districts | Students and young professionals | Fits so far (Albany 10, Troy 6, Schenectady 5, Saratoga Springs 2); check against campuses once anchors are in |
| Knowledge Corridor | Professional mixed-use (was Affluent urban; renamed 2026-10-27, Review 15) | One tract; too few to test |
| Working Neighborhoods | Working-class urban | One tract (Troy); too few to test |

**Draft reads** (pre-rerun; re-check):
- High bachelor's share and density run up the Northway from Albany toward Saratoga Springs.
- Poverty concentrates in two places: the old city cores, and the rural edges (Schoharie, northern Saratoga). Older residents dominate the rural edges.
- POI clusters mostly sort by density, with one distinct functional cluster: a **healthcare-heavy** group (33% of POIs, 25 tracts), likely the medical districts. The zones don't capture it.

**Background, the national label problem** (raw national medians, pre-rerun):

| Current name | Poverty | BA+ | Median income | Owners | Density | Problem |
|---|---|---|---|---|---|---|
| Mixed-Income Middle | 6.1% (lowest) | 45% | $104k | 78% | 2,500 | Not mixed-income: comfortable, educated suburbs. 57% of Albany's tracts. |
| Established Residential | 10.5% | 24% | $73k | 82% | 147 | Rural/exurban; the name hides that |
| Entry-Market | 26.6% | 18% | $45k | 44% | 3,800 | A euphemism for lower-income urban |
| Working Neighborhoods | 16.5% | 18% | $66k | 52% | 6,400 | Close to Entry-Market; the difference needs saying |
| Emerging Knowledge Districts | 14.8% | 56% | $75k | 27% | 7,500 | Renter-heavy, high turnover; "Emerging" implies a trend the model doesn't measure |
| Knowledge Corridor | 6.8% | 53% | $123k | 65% | 6,800 | Affluent, dense, educated; "Corridor" implies a shape the model doesn't measure |
| Commercial Core / Jobs Center | — | — | — | — | 56 | 69 tracts nationally; none in Albany |

Root cause: the K6/K7 review read polarity-flipped centroids as raw values (R32).

### Q4. What kind of market is this?

**Explore:**
- [x] Peer table and benchmark bars (v1 E6, E7; in the visuals notebook)
- [x] Q4a: scorecard, 29 metrics with US rank (of 393 metros) and NY rank (of 13), against NY State, the US and the median metro (`sql/q4_metro_scorecard.sql`; 2026-10-23)
- [x] Q4b: strip plots, Albany in each metric's distribution of all metros, NY metros marked
- [x] Q4a+: Upstate rank (of 12) and an Upstate aggregate from its 52 counties (≈ where it's a population-weighted mean); `position` column in words (2026-10-24)
- [x] Q4b and Q4d rebuilt as one large chart with a metric picker (and a metro picker for Q4d) (2026-10-24)
- [x] Q4c: cross-frame peers with raw stats, the frame-specific peer lists side by side, the 13 NY metros' clusters
- [x] Q4d: quick benchmark bars, Albany vs Buffalo, Rochester, Syracuse and the peer median, on any metrics from Q4a
- [ ] Reads for Q4 (after Dan's first look)
- [x] Apply R32 to the CBSA cluster before printing its name: profile "High-Amenity Knowledge Civics" on raw values (table in Q4c; read it at Gate A)
- [x] Cluster name and label: not printed in Lens 1; describe what the peers share (Dan, 2026-10-24). National naming review is [N1](../../NATIONAL_FOLLOWUPS.md)
- [x] Benchmark metrics: the six defaults (income, bachelor's, home value, 10-yr growth, GDP per capita, public share) are fine (Dan, 2026-10-24)
- [x] At a glance metric set: population, 10-yr growth, median household income, per capita income, median home value, bachelor's share, median age, non-white share (Dan, 2026-10-24). Prototype in Q4e: number cards and a percentile dot plot
- [x] At a glance print form: keep both for now (Dan, 2026-10-25)
- **What Kind of Place follow-ups, in priority order (Dan, 2026-10-26):**
  - [x] Q4g. What the ten peers share, on raw values, against all US metros (2026-10-26)
  - [x] Q4h. Albany, Buffalo and Rochester head to head (the second-city thread) (2026-10-26)
  - [x] Q4i. In-migration from the rest of New York (IRS county-to-county flows, `silver.irs_migration_flows`; N8) (2026-10-26; found the direction bug)
  - [ ] Q4j. A short, reusable explainer of the peer method (cosine similarity across three frames)
  - [ ] Regional shadow: idea only, national in scope (N3); wait and see whether it fits
- [x] Key places draft: `reference/anchors.csv` (35 in seven themes) with `reference/anchor_sources.json`; Wikipedia pulls in `data/` with a manifest (Q4f, 2026-10-24)
- [ ] **Data review (R14):** Dan sets `keep` and flags wrong points

## Exhibits

Filled in at each question's Gate A.

| # | Exhibit | Q | Claim (draft title) | Form | Status |
|---|---|---|---|---|---|
| E0b | At a glance | Q4e | High on income and education, middle of the pack on growth and age | Percentile dot plot | Built (Dan picked the dots over E0a's cards, 2026-10-27) |
| E1, E1c | The metro on the map, core detail | Q1, Q4f | Five counties, four old cities, and the Capital in the middle | County map with places, lines, key places; numbered core detail | Built (was E1 v2) |
| E2 | Albany vs Buffalo, real GDP | Q4h | Albany is closing in on Buffalo | Two lines, gap shaded | Built 2026-10-27 |
| E3 | Migration in and out | Q4i | Albany gains from the rest of New York and loses to other states | Mirrored bars by region, in vs out, net at right | Rebuilt 2026-10-27 on the IRS county totals |
| E4 | Peers with core metrics | Q4g | Albany's closest matches are older Northeast metros | Table: similarity and eight metrics, peer and US medians | Built 2026-10-27 (replaces v1 E6) |
| E5 | Top places | Q4f | The second-largest municipality is a suburban town | Ranked bars with hamlets | Built (was E1b) |
| E6, E7 | Density and the arrow | Q2 | 54% of the metro lives in the triangle and up the Northway, on 9% of the land | Tract choropleth with the arrow (triangle + Northway arm); residents vs land bars | Built 2026-10-27; redrawn north the same day |
| E8 | Job centers on all jobs | Q2a | The largest job center is the band from uptown Albany to Wolf Road | Proportional circles, centers by public share | Built 2026-10-27 (replaces v1 E3) |
| E9, E10 | Zones, and what's there | Q3a–c, Q3e | Comfortable suburbs fill the middle | Zone map; zone table with a "What's there" bar (residents by activity class) | Built 2026-10-27; names not cleared |

Cut from v1 (2026-10-27, Dan: "revamp the notebook so it's aligned to the structure"): the v1 county map, the places residents-and-jobs bars, the Q6 anchor table, the zone composition bars and the benchmark bars. Their PNGs are in `output/drafts/_v1_2026-10-26/`. Cut later the same day (Review 15): E0a (cards), E3 (migration bars: a line of text instead), E11 (zones × activity table) and E12 (activity map), with the activity classes folded into E10; PNGs in `output/drafts/_cut_2026-10-27/`. Exhibit numbers keep their gaps so the draft's review notes still match; renumber before print.

## Locked decisions

| Decision | Choice | Who, date |
|---|---|---|
| Plan before build | This plan supersedes v1's outline-driven list | Dan, 2026-10-22 |
| Analytics first | Explore each question with several tables and views and write reads before choosing exhibits | Dan, 2026-10-22 |
| **One question at a time** | Explore in the exploration notebook, Gate A, promote the chosen views into the visuals notebook, Gate B, then the next question (Workflow) | Dan, 2026-10-23 |
| Integration threshold | OMB's 25%, stated in the text with the LODES-vs-ACS caveat | Dan, 2026-10-22 |
| E1 and E2 | Separate maps | Dan, 2026-10-22 |
| Commute shed scope | Show the smaller sheds too (classes from 1%), both directions | Dan, 2026-10-22 |
| Commuting depth | A series of commuting views (statewide, between metros, within the metro) is worth exploring in full | Dan, 2026-10-22 |
| Section 4 | No standalone section; its test lives in Q1 | Dan, 2026-10-22 |
| Zone labels | Keep the national clusters; Albany gets working names, stress-tested against its tracts; renames proposed per CBSA | Dan, 2026-10-22; 2026-10-23 |
| Albany POI run | Done on Overture 2026-10-21.0; published to `mart_poi` 2026-10-22 | Dan, 2026-10-22 |
| Tract-level commute sheds | `commute_sheds` run for 10580, `either_endpoint`, JT00 + JT02; done 2026-10-22 | Dan, 2026-10-22 |
| Jobs universe | Albany analyses use all jobs (JT00) unless a view is explicitly about private jobs (R34) | Rules, 2026-10-22 |
| Q2 centers for Albany | Q2's method on all jobs, as an Albany sensitivity in the exploration notebook | Dan, 2026-10-22 |
| LODES jobs universe | Explicit private/all column names and a reader audit, by a separate agent: [LODES_JOBS_UNIVERSE_SPEC.md](../../../../foundations/etl/LODES_JOBS_UNIVERSE_SPEC.md) | Dan, 2026-10-23 |
| Labor fix and Phase 7 rerun | Done by separate agents ([ACS fix](../../../../foundations/etl/ACS_LABOR_B23025_FIX_SPEC.md), [Phase 7 rerun](../../../../exploration/intelligence_framework/phase_7_zone_methodology/PHASE7_LABOR_FIX_RERUN_SPEC.md)); promoted 2026-10-23 with the original names | Dan, 2026-10-23 |
| Residents-vs-jobs bar | Replaced; Q2 compares jobs with resident workers | Dan, 2026-10-22 |
| Peers and benchmarks | Keep; peers open the clustering topic | Dan, 2026-10-22 |
| Upstate definition | Series default: every county but NYC, Long Island, Westchester, Putnam, Rockland (`downstate_core`). So every NY metro but NYC's is Upstate. A standalone "defining Upstate" article comes later | Dan, 2026-10-24 |
| Article lead | Lead with the metro profile (At a glance), standard across metro pieces and not all economic. "Four cities, no center" returns as a thread in later sections | Dan, 2026-10-24 |
| Cluster names | Not in Lens 1. Lean on the peers and describe what they share. National naming review is future work (N1) | Dan, 2026-10-24 |
| Exploration style | Pickers with one large chart, and zoomable Carto maps (Plotly) with toggleable overlays, not grids of small statics. Static versions only for print | Dan, 2026-10-24 |
| National-scope questions | Tracked in [NATIONAL_FOLLOWUPS.md](../../NATIONAL_FOLLOWUPS.md) and revisited with each market | Dan, 2026-10-24 |
| Commute shed | Banked for Lens 2; Lens 1 shows the high level only | Dan, 2026-10-24 |
| At a glance set | The eight metrics above, with non-white share for diversity | Dan, 2026-10-24 |
| Key places | A curated landmark set (not amenity analysis, which is Lens 2), with a data review | Dan, 2026-10-24 |

## Open decisions

- [ ] **Q2's national method:** whether all jobs should become Q2's default, or a published sensitivity, for every CBSA. This is Q2's call; Albany's result is the evidence (Q2a).
- [ ] **Floor interaction:** hold the 1% market-share floor at the private-jobs level when comparing the two runs (so Malta survives), or accept the drop and say so.
- [ ] **ACS commuting ingest** to check OMB's own Schoharie test. Recommend deferring unless the article leans on Schoharie.
- [ ] **E5 anchors**, including whether GE goes in before Lens 4

## Findings

- **Confirmed from the outline:**
  - Five counties: three central, two outlying.
  - Albany city 100k residents (11% of the metro); Schenectady 69k, Troy 51k, Saratoga Springs 29k.
  - 14 Q2 job-center components (private jobs); zone counts by county matched (pre-rerun).
- **Corrected from the outline:**
  - **Albany city's "about 72k jobs" is private jobs.** All jobs: 131.8k. Saratoga Springs vs Schenectady on all jobs: 24.9k vs 28.0k (still "nearly as many").
  - **Roessleville's jobs-over-residents** rests on population-weighted allocation (R13); re-check on all jobs at tract level in Q2.
  - **Q6's "10 candidate places" is 10 components tied to 6 places.** Albany city is the place for five of them.
- **Saratoga is the fastest-growing county,** up 8.4% from 2008–12 to 2020–24. Schoharie shrank 7.9%.
- **Saratoga Springs is not an OMB principal city.**
- **The CSA covers the commuting ring.** The Albany-Schenectady CSA (104) adds Amsterdam, Glens Falls (Warren, Washington), Gloversville and Hudson. Greene is in no CBSA or CSA.
- **The zone composition's national baseline** is metro *and micro* tracts.
- **Tract unemployment rate: fixed.** An ACS B23025 mapping bug in `get_acs_labor.R` was found 2026-10-22 and fixed by the labor-fix agent; Phase 7 was rerun and promoted 2026-10-23.
- **LODES `jobs_total` is private jobs only (JT02)**, by design. `jobs_all_total` is all jobs (JT00). Q2 and Q6 used `jobs_total` without saying so. Explicit renaming is underway in a separate spec.
  - Albany city: 131.8k jobs in all, 72.1k private, so 45% public.
  - Metro: 460k in all, 351k private.

## Print gates

| Gate | State | Affects |
|---|---|---|
| Zone type names | Not cleared; Albany renames proposed per CBSA (Q3) | Q3 |
| Integration threshold stated in text | Locked at 25%; text to write | Q1 |
| CBSA cluster name and label | Not printed in Lens 1 (Dan, 2026-10-24); N1 for the national review | Q4 |
| Downtown Albany jobs | Caveat the 75+ mile share (R33) on any "biggest center" claim | Q1, Q2 |
| Frame composite scores | Held; none used | — |

## Shared layers for print

Built when the first promoted exhibit needs them:
- [x] `sql/metro_place_outlines.sql`: place polygons from `geo.places_display`, with kind and principal-city flag (2026-10-24; used by the exploration maps)
- [ ] `sql/metro_roads.sql`: motorway and trunk lines from the Infrastructure handoff (Q1 E1, Q2)
- [ ] Main-line rail: reuse What NY Is's selection (`what_ny_is/sql/map2_infrastructure.sql`) (Q2)
- [ ] `reference/anchors.csv` + sources: draft built 2026-10-24 (Q4f); waiting on the data review (R14)

## Review, 2026-10-22 (1): v1 visuals

1. **Metro on the Map:** fine; add city outlines, POIs and transit. *Response:* city outlines and highways go on E1; the fuller infrastructure and anchor layer goes on the job center map.
2. **Four cities, no center:** the bar isn't clear and a map would show how population falls; residents vs jobs is misleading, so include workers. *Response:* Q2 views.
3. **Job center map:** the best of the set; add boundaries, infrastructure and transit. *Response:* Q2, print layers.
4. **Metro assembly:** good, but labels and meanings aren't established. *Response:* Q3.
5. **Does everyone belong:** no good visual; fold it into earlier sections, and check commuting from outside counties. *Response:* Q1.
6. **What kind of market:** great; the intro to clustering. *Response:* Q4.

## Review, 2026-10-22 (2): plan

1. 25% is fine. Show the smaller commute sheds too, and check which outside counties draw residents from Albany's counties. *Response:* Q1 inbound and outbound views; the long tail's caveat in R33.
2. E1 and E2 as separate maps. *Locked.*
3. E2 extent: superseded by 1. The whole region, classed from 1%; the long tail goes in a table and the text.
4. Walk through the zone labels, and see what else could work. *Response:* Q3.
5. **Overall:** analytics first; strong articles, not a stack of graphs. *Response:* rules Phase 2 (Explore), R30, R31; this plan organized by question set.

## Review, 2026-10-22 (3): Q1 reads and zone labels

1. Explore commuting statewide and within the CBSA. *Response:* Q1d–Q1g; tract-level sheds via the commute-sheds run.
2. Keep the national clusters, rename the labels for Albany, build understanding as we go. *Response:* working names plus a stress test (Q3).
3. Run the Albany POI engine. *Response:* done; release bump and schema fix recorded in `engines/poi/NOTES.md`.
4. Trace the unemployment rate. *Response:* B23025 mapping bug; the jobs cross-check also found the private-jobs universe issue (R34).

## Review, 2026-10-22 (4): follow-ups

1. Tract-level commute sheds, here or by a follow-up agent? *Response:* here, one engine command (Q1h).
2. Rerun Q2 centers on all jobs. *Response:* done (Q2a/b).
3. Specs for the unemployment fix and the cluster rerun. *Response:* both written, then run by separate agents.

## Review, 2026-10-23 (5): workflow

1. Use the exploration notebook per section, one question at a time, then move the final visuals and results into the visuals notebook. Codify the flow in this plan; work on it in a new session. *Response:* Workflow section with two gates, a status ladder per question, and "move, don't copy" for promoted helpers; handoff written for the next session.


## Article structure (2026-10-24)

Dan's order, replacing the outline's. Dan edits the outline itself (R27).

1. **At a glance.** The standard metro profile: headline numbers with US, NY and Upstate ranks. Not all economic (economics is other lenses' job).
2. **Opening.** History, then Dan's personal bridge.
3. **What kind of place is this?** Peers (without a cluster name), what they share, and the key places (anchors). Places in the market.
4. **How it's assembled.** Counties, the four cities, zones; a short "does every county belong" test.
5. **Close.**

## Review, 2026-10-24 (6): Q4 first look and notebook style

Dan's notes, then the responses.

1. **Answers.** Benchmark defaults are fine, and keep all 29 metrics for review. National and NY ranks are good; add Upstate. Varying source years are fine but get called out in the writing and exhibits. *Response:* Upstate rank and aggregate added to Q4a and Q4d.
2. **Notebook style.** One visual with a metric picker, not small multiples; reactive Carto maps with metric and border toggles, not many statics. *Response:* Q4b, Q4d, Q1b/c, Q1h, Q2b, Q3b and Q3d's dot maps rebuilt that way (`explore_map`, `explore_points`, `map_overlays`; city outlines from `sql/metro_place_outlines.sql`). Q1d, Q2a and Q3d's cluster map followed the same day (`explore_category_map`), plus a new zone map in Q3c. Maps are simplified to stay under marimo's 8 MB cell output default (the largest, all POIs, is 4.9 MB).
3. **Reading the unemployment rank.** Rank 1 = highest, so #283 of 393 means 282 metros have a higher rate: good news. *Response:* a `position` column says it in words.
4. **Notes on what the numbers show**, with the pushback from the session:
   - Albany is third Upstate on population (Buffalo, Rochester) and **second on GDP (Buffalo $90.7B, Albany $84.9B)**, but first Upstate per person: per capita income, price-adjusted income, labor force participation. "Second economy" holds only per person.
   - GDP per capita (#34) overstates Albany: it divides workplace output, a quarter of it produced by people living outside the metro, by residents. Use per capita income (#63) for "how well off."
   - Affordable by national standards, not just NY's: value to income 3.27 vs US 4.12; price level 97.6. Property taxes aren't in the data.
   - Growth is small but real: +3.5% over the decade, against **+0.0% for Upstate** (2nd of 12). Net domestic migration is about neutral; out-of-state in-movers are low. Where the growth comes from is open (N8; Dan's hypothesis: from within the state).
   - The public sector is large (23.7%), but Upstate as a whole runs high too (19.5% vs 13.9% for the median metro). The "stable floor" is a hypothesis to test (N7), mostly in Lens 4.
   - Peers: nine of ten share Albany's cluster. The regional-shadow idea (smaller metros near a dominant one) is ours, not the model's; test it with megaregions (N3). Same-state similarity is common everywhere, not special to NY (N2).
5. **Commute shed.** The series context puts "where do people commute from" (M.14) and regional role (M.13) in Lens 2. *Recommendation:* bank most of Q1 for Lens 2. Keep the short "does every county belong" test (M.10: Saratoga, Schoharie) in How it's assembled, with one line on Albany's reach.
6. **Key POIs.** Amenity analysis (M.11, M.12) is also Lens 2. *Recommendation:* in Lens 1, "key places" means a curated anchor set (Capitol and Empire State Plaza, universities, hospitals, GE Schenectady, Saratoga Race Course, etc.) via `reference/anchors.csv` with sources and a data review (R14).

## Review, 2026-10-24 (7): answers and next steps

1. **At a glance:** add non-white share for diversity. *Response:* added (`pct_nonwhite` = 1 − non-Hispanic white share); Q4e prototypes the eight-metric set as number cards (US and Upstate ranks) and as a percentile dot plot. Albany is 24.5% non-white, near Upstate (23.3%) and far below the US (42.6%).
2. **Commute shed:** bank most of it for Lens 2; show the high level only. *Response:* Q1 status changed; a scope note heads Q1 in the exploration notebook.
3. **Key places:** draft them. *Response:* 35 candidates in seven themes (state government; history and the canal; education and research; health; industry; transport; leisure and culture), at least one in each of the four cities and one in Schoharie. Coordinates from Wikipedia, or from the Overture run where Wikipedia has none or points elsewhere (GlobalFoundries' page points to its California HQ; KAPL's to its West Milton site). All inside the five counties; all `keep=true` pending review.
4. **Tracker location:** `issues/NATIONAL_FOLLOWUPS.md` confirmed.
5. **Notebook:** the last static maps are interactive now (Q1d with a view picker, Q2a, Q3d clusters), and Q3c gained a zone map. Every map is under 0.3 MB except the all-POI view (4.9 MB).

## Review, 2026-10-24 (8): Albany Today, zones and Metro on the Map

1. **Key places:** data review passed; all 35 kept (Dan). Leisure split into *Parks and nature* and *Culture and sports*, so eight themes; `anchors_sha256` refreshed.
2. **Albany Today: In a Nutshell** (Gate A): build both forms as static print drafts. *Response:* new visuals-notebook section with `e0a_nutshell_cards` and `e0b_nutshell_dots`, a check table asserting the confirmed numbers (R10), and the scorecard helpers moved from the exploration notebook (move, don't copy). Population has no Upstate or US marker on the dot plot (totals aren't metros). **Gate B:** Dan picks cards, dots or both.
3. **Dan's reads** (2026-10-24, for the article; confirm wording at Gate A):
   - **Zones:** Albany city is the main anchor; the lower-income urban tracts sit in the hearts of Albany, Troy and Schenectady; most of the metro is inner suburb, ringed by exurban and rural; Saratoga Springs is further out, suburban and more affluent. A large suburb fills the middle of the Albany–Troy–Schenectady triangle (Colonie: Latham, Loudonville, Roessleville, the Wolf Road jobs band), and Clifton Park continues it north along the Northway.
   - *Check on "downtown is where the most poverty is":* Albany city has 11% of residents and 21% of those in poverty, the largest share of any place. Poverty rates are higher in Troy (24%), Schenectady (23%) and Cohoes (25%) than in Albany (22%). The lower-income urban tracts hold 12% of residents and 35% of the poor. 27% of the poor live outside any Census place (towns and rural areas). Tract poverty rate × ACS 2020–24 tract population.
   - *Caveat:* these reads use the working names on the **new** clusters. "Affluent urban" is now 22 tracts with an 11% poverty rate, so the names need the Q3 re-run before print.
   - **Q4:** Albany is stronger economically than most Upstate metros. The article will name the metrics that get their own deep dives in later lenses.
4. **The Metro on the Map, v2** (static): `e1v2_metro_map` (five counties by OMB flag, the four cities filled, other places outlined, Thruway and interstates, main-line rail, the canal, the rivers, key places outside the core labeled) and `e1v2_core_map` (the Albany–Troy–Schenectady triangle, 28 key places numbered by theme with a key). A table lists all 65 Census places (8 cities, 29 villages, 28 CDPs) for Dan to choose labels (`map1v2_places`). **Towns aren't Census places in NY:** Colonie, Clifton Park, Bethlehem and Guilderland can't be outlined, and Delmar has no 2020 place. A towns (county subdivision) layer would fix that; it needs a TIGER pull (R14 for new data). Parks are points; park outlines would also need new data.
5. **Outline:** sections no longer match the article order; proposal in the session, for Dan to edit (R27).

## Review, 2026-10-25 (9): towns, parks, outline, draft

1. **At a glance:** keep both forms for now (Dan).
2. **Towns and parks pulled** (Dan: yes). Census cartographic county subdivisions (2023) and ACS 2020–24 town populations (Census API); 22 parks and preserves from OpenStreetMap (Overpass), curated in `reference/parks.csv` with `keep`; the Adirondack Park boundary reused from What NY Is. Provenance in `data/anchors_reference_manifest.json`; downloads ignored by git like What NY Is. Check: the 72 towns and cities sum to the metro's 906,052. Both E1v2 maps now draw town lines and italic town names (hand-placed in `map1v2_towns`, `map1v2_core_towns`), park fills and the Adirondack boundary. **Data review (R14) for the parks list is Dan's.**
   - *Finding:* the town of Colonie (86k) is the metro's second-largest municipality, larger than Schenectady (69k) and Troy (51k); Clifton Park (38k), Guilderland (37k) and Bethlehem (35k) are each larger than Saratoga Springs (29k).
3. **Outline reordered** (Dan: yes): At a glance, history, Metro on the Map, What Kind of Place, How It's Assembled, Close; new argument line. Dan edits from here.
4. **Draft review** (`lens1_albany.md`): notes given in the session as a checklist (R27); next section to explore is What Kind of Place Is This.

## Review, 2026-10-26 (10): draft notes, priorities, top places

1. **Draft notes** added inline to `lens1_albany.md` as `{Review note, 2026-10-25: ...}` lines under each paragraph; Dan's text unchanged (verified by diff).
2. **What Kind of Place priorities:** peers' shared traits, Albany–Buffalo–Rochester, in-migration, method explainer, then regional shadow as an idea only (Q4g–Q4j in Q4; N3 marked low priority). Outline updated to match.
3. **Top places** (Dan: show the top places, incl. that many of the largest are unincorporated suburbs). *Response:* `e1b_top_places`, the 15 largest cities and towns with each town's largest hamlets and villages named; check table asserts Colonie 2nd, larger than Schenectady and Troy, and Clifton Park, Guilderland and Bethlehem each larger than Saratoga Springs. The four cities hold 27% of residents, towns 68%. *Wording:* NY towns are incorporated municipalities; the unincorporated units are the hamlets inside them (Latham, Loudonville), so the text should say "the suburbs people name are unincorporated hamlets" rather than "the largest places are unincorporated." Bethlehem and Halfmoon show no hamlets because none are 2020 Census places (Delmar is not).

## Review, 2026-10-26 (11): Q4g–Q4i explored

1. **Q4g–Q4i built** in the exploration notebook with draft reads (peers' shared traits, Albany vs Buffalo/Rochester/Syracuse with trends since 2012, IRS migration by region of the other end, a net-migration map).
2. **Data bug: IRS migration directions are reversed in the warehouse.** Staging maps the IRS `y2_` (destination) columns to origin. As stored, New York gains 413k people from other states in 2022; Manhattan → Miami reads as Miami → Manhattan. Affects `silver.irs_migration_flows`, `silver.irs_migration_summary`, the IRS fields of `gold.migration_wide` (net sign flipped) and the Intelligence Framework inputs. Spec for a separate agent: [IRS_MIGRATION_DIRECTION_FIX_SPEC.md](../../../../foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md). Workaround: `q4_metro_migration.sql` swaps back and `q4_metro_scorecard.sql` negates the net rate; the `irs_flows_reversed` guard fails when the fix lands. **Dan to decide** when the fix runs. (Review 12: clusters and peers are expected to hold; scores move.) **Fixed 2026-10-26:** warehouse and Intelligence marts rebuilt; both workarounds removed and the guard now fails if the reversal returns. Q4i reads the same (Albany +1,478 people a year net, 2018–22); the Q4a scorecard is row-for-row identical. Albany's Intelligence clusters and peers are unchanged; its Opportunity percentile moved 74.4 → 72.2 and cross-frame 85.3 → 88.4.
3. **Headline results:** Albany gains ~1,500 people a year net (2018–22), the only big Upstate metro to gain; +2,500 from Downstate, +1,300 from the rest of Upstate, −2,400 to other states; the pandemic roughly tripled it. Buffalo's real GDP lead over Albany shrank from $8.2B (2012) to $1.6B (2024).
4. **Gold rate definition:** `irs_net_migration_rate` is net *households* (returns) per resident, a documented choice; quote people (exemptions) in print.

## Review, 2026-10-26 (12): notebook restructure and the IRS fix spec

1. **Restructure now, before How It's Assembled** (Dan). *Response:*
   - `ALBANY_LENS1_EXPLORATION.py` now follows the article: 1 Albany Today (Q4e, Q4a, Q4b), 2 History (no data work), 3 The Metro on the Map (Q1a, Q1f, the Q1b table, Q4f), 4 What Kind of Place (Q4c, Q4g, Q4h, Q4i, Q4d), 5 How It's Assembled (Q2, Q3, with a to-do list). Question IDs and reads are unchanged; the county-belonging reads moved to section 3, and section 5's Q2 reads gained a pointer to the Q1h shed findings.
   - The banked commuting work (Q1b–Q1e with the maps, Q1g, Q1h) and its reads moved unchanged to a new `ALBANY_LENS2_EXPLORATION.py`.
   - All 41 exploration helpers moved, copied exactly from the notebook, to a plain module, `albany_explore.py`, with three new loaders both notebooks share (`load_commute_flows`, `load_tract_profile`, `all_jobs_centers`).
   - Checks: `marimo check` and ruff pass; both notebooks run headless and give the same numbers as before (Albany +1,478 people a year net, 2018–22; the 13-tract uptown band; zone counts 143/39/32/22/13/2).
   - The visuals notebook is unchanged; reordering it and cutting v1 wait for Dan's sign-off.
2. **IRS fix spec** expanded into the full fix, the downstream impact and the reruns: [IRS_MIGRATION_DIRECTION_FIX_SPEC.md](../../../../foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md). It has three parts (fix Foundations; rerun Intelligence Phases 2, 4, 5 and 6 with a control; refresh marts and outputs, then remove the Albany workaround) and two stops for Dan. Expected effect:
   - The stored net values are an exact sign flip, so clusters and peers should not change (distances and cosine similarity are unchanged when one column is negated for every metro).
   - The Character, Opportunity and cross-frame scores, the topic scores and the trajectory signals will change, because both IRS inputs have positive polarity.
   - The rerun tests this instead of assuming it.

## Review, 2026-10-27 (13): zones and POIs in one view (Q3e), and the Q3 re-run

1. **Combine the national zones and the POI clusters into one analysis** (Dan; four activity classes chosen over two). *Response:* Q3e keeps the zone as the base type (nationally comparable, who lives there) and adds an activity class per tract (what's there), by plain rules instead of a joint clustering, which would break the national comparison and pull Overture's coverage into the hard metrics.
   - Rules, first match wins: more jobs than residents → Destination if destination POIs run 1.5× the metro share, else Employment and industrial; POIs per 1,000 residents under the metro median (36.8) → Residential; destination POIs 1.5× or industrial POIs 2× the metro share → that class; else Local-serving. Shares are pulled toward the metro mix by 20 pseudo-POIs. Agriculture is left out of the industrial bundle (it pulled farm tracts in).
   - Result: Residential 120 tracts, Local-serving 83, Employment and industrial 29, Destination 19. Zones and activity are close to independent (adjusted Rand 0.06). Employment and Destination tracts are 17% of residents and 58% of jobs. Comfortable suburbs split 76 / 45 / 14 / 8, with almost no income difference between the kinds.
   - The Q3d k-means clusters match neither layer (0.06 against activity, 0.08 against zones) except P4, which Q3e recovers as Destination (15 of 25). Suggest retiring the k-means for print.
   - Place names in the reads come from the POIs in each tract (Albany Med, the University at Albany, RPI and Samaritan, Union and Ellis, Skidmore and the race course, the airport and Wolf Road, Crossgates, the Harriman campus); confirm against the Q4f anchors.
2. **Re-run the rest of Q3** (Dan). *Response:* Q3a–c already read the promoted zones; the reads are refreshed. The stress-test split of Comfortable suburbs holds; Rural and exurban is now 36 of 39 town-area tracts (was 43 of 48); Niskayuna's worst-fit tract now sits in Affluent urban. Checks: `marimo check`, ruff, and headless runs of both exploration notebooks pass.

## Review, 2026-10-27 (14): Dan's full draft, structure review, and the visuals rebuilt

1. **Review the draft's structure and points, and check them against the exploration** (Dan). *Response:* inline notes in `lens1_albany_draft.md` (Dan's current text from `lens1_albany.md`, unchanged, with `{Review note, 2026-10-27}` notes; 2026-10-25 notes that still apply are folded in). Main points: state "four cities, no center" once and prove it in How It's Assembled; show density once (moved to E6); trim colonial history, add the modern economy and Troy; move the personal paragraph to the open or close; give migration its own paragraph; fix the peer method description. Fact fixes: median household income is 2nd of 12 Upstate (income per person is 1st); the largest job center is the uptown–Wolf Road band (96k), not downtown (50k); "center in both" was all-jobs vs private-jobs, not public; Hampton Manor is East Greenbush; Malta is a center on private jobs only; Affluent urban's suburban tracts come from the national type, not tract designation; add Providence, RI.
2. **Build all the visuals and align the notebook to the article** (Dan). *Response:* `ALBANY_LENS1_VISUALS.py` rebuilt in article order (sections 1–5), E0a–E12 as in the Exhibits table; each data cell asserts the numbers the text uses. v1 cut (backup of the old notebook in the session scratchpad). Helpers the exhibits need moved from `albany_explore.py` to the visuals notebook (move, don't copy) and are re-exported there: `load_tract_profile`, `all_jobs_centers`, `irs_flows_reversed`, `classify_migration`, `migration_summary`, `tract_activity`, the activity constants, plus `ZONE_NAMES`, `ACTIVITY_RULES` and `POI_RUN_DIR`, which the exploration notebook now reads from there. All three notebooks pass `marimo check` and ruff and run headless.
3. **The triangle** (Dan: draw it to start): Albany, Troy, Schenectady, Colonie, Guilderland, Niskayuna, Bethlehem, Watervliet, Cohoes, Green Island. 48% of residents, 8% of land; Northway towns 18% and 8%. Open: the draft places Bethlehem in the small southern towns.
4. **Open for Dan:** pick E0a or E0b; whether E3 runs; the Bethlehem question; zone working names before print (E9–E11); a density floor for the activity rule (rural tracts read as Local-serving because POIs per resident run high where few people live).

## Review, 2026-10-27 (15): Dan's calls on the open items

1. **E0a or E0b** (Dan: the dots). *Response:* E0a's cell and `draw_nutshell_cards` removed.
2. **E3** (Dan: a line of text, not a chart). *Response:* the chart and `draw_migration_bars` removed; the migration numbers cell and its checks stay for the text.
3. **The triangle** (Dan: move it north to cover more of Colonie and southern Saratoga, with a corridor up to Saratoga Springs so it reads as an arrow). Why the first draw sat south: it outlined whole towns, and Bethlehem and Guilderland are large, low-density towns that pulled it south and west. *Response:* `TRIANGLE_TOWNS` is now Albany, Troy, Schenectady, Rensselaer (missing before), Watervliet, Cohoes, Green Island, Colonie, Niskayuna, Waterford, Halfmoon, Clifton Park: 49% of residents on 7% of land. `NORTHWAY_ARM` (Malta, Saratoga Springs): 5% on 2%. Drawn as one outline: 54% on 9%. Bethlehem and Guilderland are out, which settles the Bethlehem conflict in the text. The checks assert all three pairs.
4. **"Affluent urban"** (Dan: how to rename, and why that name?). *Response:* the name was set from the national Knowledge Corridor profile ($123k, 6.8% poverty, 6,800 per sq mi) when Albany had one such tract; after the 2026-10-23 rerun it has 22, and Albany's version is neither affluent nor urban: median income $88k (below Comfortable suburbs' $102k), poverty 11%, owners 41%, density 2,562, BA+ 54%, 1.7 jobs per resident. Dan picked **"Professional mixed-use"** (2026-10-27: it speaks to the character instead of overindexing on education). Renamed in `ZONE_NAMES` and `ZONE_COLORS`; E9 and E10 re-rendered.
5. **The activity exhibits** (Dan: fold them into the zones as a small add-on). *Response:* E11 and E12 cut; E10 gets a "What's there" bar per zone (residents by activity class) and the national type moves under each working name to make room. The rural Local-serving caveat now shows in the Rural and exurban bar.

## Review, 2026-10-27 (16): draft v2, maps, and migration on the IRS totals

1. **Draft v2** (Dan: review my language, propose changes in italics, consolidate the colonial history, add the other cities to the modern history as a new paragraph, write the method summaries, the last zones paragraph and the closing). *Response:* `lens1_albany_draft_v2.md`: italics = new or changed, strikethrough = proposed cuts, {Proposed: ...} = new paragraphs. Reasons in the chat thread.
2. **E1 and E1c** (Dan: show a few core places on the big map; more detail on the core map). *Response:* E1 now marks six core places (State Capitol, UAlbany, airport, RPI, Union College, GE Vernova) with short labels. E1c draws OSM areas over the place fills: the airport outline, 10 hospital campuses, 16 college campus polygons and every park of 10+ acres (`data/build_osm_core_detail.py`, `data/osm_core_detail.json` from Overpass, 2026-10-27).
3. **Migration** (Dan: does Albany only gain from within the state? Show in and out by Downstate, Upstate, other states). *Response:* checking it found that the pair-based IRS data misses the suppressed small pairs, mostly out-of-state moves. On the IRS county totals Albany's net is **−1,491 a year** (−1.6 per 1,000), not +1,478: +2,542 Downstate, +1,090 rest of Upstate, −5,123 other states. Still the best of the big four Upstate metros (Buffalo −2.4, Rochester −3.5, Syracuse −4.2 per 1,000) and 4th of 12 Upstate. E3 rebuilt as in vs out by region (`e3_migration_flows`); E4's migration column switched to the totals (Albany −1.6; 8 of 10 peers lose people; peer median −2.9). New `data/build_irs_county_totals.py` and `data/irs_county_totals_2018_2022.csv`. Foundations fix logged as N11 (it also affects the national `irs_net_migration_rate` and the `irs_net_agi` peer input).

## Review, 2026-10-30 (17): a drawn arrow

1. **E6b** (Dan: draw an actual arrow over the density map; a reference shape, not tract-exact). *Response:* new `e6b_population_arrow`, the E6 density map with a schematic arrow (`draw_arrow_schematic`) in place of the town outline. The head is the Albany–Schenectady–Troy triangle grown 35% about its centroid, pointing south at Albany; the shaft runs from the middle of the Schenectady–Troy side to Saratoga Springs. The 54% share is still the E6 town share. E6 is unchanged, so either can go in the draft.
