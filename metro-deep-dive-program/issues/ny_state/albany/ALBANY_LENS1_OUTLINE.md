# Albany, Lens 1: What Albany Actually Is

**Status:** Outline draft
**Updated:** 2026-10-21

The first Albany installment. Geography: the 5-county Albany-Schenectady-Troy CBSA (10580), 2023 delineation (D4). Target: 1,500 to 2,500 words. Seven exhibits planned, above the 4 to 6 guideline; build them all, then decide which earn their place. Numbers below are first pulls from the warehouse, to confirm during the build.

## The Argument

Albany isn't one city with suburbs. It's four old cities (Albany, Schenectady, Troy, Saratoga Springs) that the federal definition joins into one metro, none of them big enough to dominate. The fastest-growing part, Saratoga County, is officially *outlying*.

## Opening (E4, E2)

- History intro: Fort Orange (1624), state capital since 1797, the Erie Canal meeting the Hudson in 1825 (Cohoes and Waterford). Ties back to the Series Intro's canal thread.
- Personal bridge: Dan's college years in Albany. *{Dan to write}*

## Sections

Order differs from the template on purpose: the "four cities, no center" hook leads, and Profile and Peers close as context. In every notebook, set the CBSA dropdown to Albany-Schenectady-Troy (10580).

### 1. The Metro on the Map
- Five counties: Albany, Rensselaer and Schenectady are **central**; Saratoga and Schoharie are **outlying** (`mart_explanation_q6.cbsa_county_context`)
- Hook: the county most people think of as Albany's growth engine isn't part of its core under the federal definition
- **Questions:** M.10
- **Explore with:** [Q6 One Metro](../../../analyses/explanation/q6_one_metro/EXPLANATION_Q6_NOTEBOOK.py) (county flags)
- **Exhibit:** county locator map colored central vs outlying, principal cities marked (an X.1 variant with `definition = cbsa_county_flag`)

### 2. Four Cities, No Center
- Population (Q6 place profile): Albany city about 100k (11% of the metro), Schenectady about 69k, Troy about 51k, Saratoga Springs about 29k
- Jobs tell a different story: Albany city has about 72k workplace jobs; Saratoga Springs has nearly as many jobs (about 22k) as Schenectady; Roessleville (Colonie, the Wolf Road area) has more jobs than residents
- The Q6 anchor result is **mixed**: 10 candidate places, 9 of them highly material
- **Questions:** M.9, M.2
- **Explore with:** [Q6 One Metro](../../../analyses/explanation/q6_one_metro/EXPLANATION_Q6_NOTEBOOK.py) (place profile, anchors), [Q2 Job Center Outcomes](../../../analyses/explanation/q2_job_proximity/EXPLANATION_Q2_JOB_CENTER_OUTCOMES_NOTEBOOK.py) (job centers)
- **Exhibits:** paired bar of residents vs workplace jobs by place (new cell; reuse candidate for every spotlight); X.15 job center map from the Q2 clusters (14 for Albany)

### 3. How the Metro Is Assembled
- Phase 7 tract zones: knowledge districts sit mostly in Albany County (13 tracts) and Rensselaer (7); Saratoga is mostly middle-income and established residential; Schoharie is almost all established residential
- **Questions:** M.2 (Internal Structure Part 1)
- **Explore with:** [Internal Structure Part 1](../../../analyses/position/internal_structure/POSITION_INTERNAL_STRUCTURE_NOTEBOOK.py)
- **Exhibits:** tract zone map; X.22 zone composition against the national mix
- **Check:** are zone type names cleared for print? (`zone_type_name_status`)

### 4. Does Everyone Belong?
- Schoharie is the obvious test: does its commuting pull toward the metro? Saratoga is the opposite case: outlying on paper, but is it really?
- Keep it short. The full answer needs LODES OD (M.14, Lens 2)
- **Questions:** M.10
- **Explore with:** [Q6 One Metro](../../../analyses/explanation/q6_one_metro/EXPLANATION_Q6_NOTEBOOK.py), [Regional Role](../../../analyses/explanation/regional_role/EXPLANATION_REGIONAL_ROLE_NOTEBOOK.py) (WAC/RAC until LODES OD lands)
- **Gate:** the Q6 integration threshold has to be stated in the text

### 5. What Kind of Market Is This?
- Albany's national peers (cleared for print) and a few raw benchmarks against the US and upstate peers
- Frame composite scores stay out of print, so lean on peers plus X.4 benchmark bars
- **Questions:** M.1, M.3
- **Explore with:** [Act 1 Position](../../_shared/act_1/ACT_1_POSITION_NOTEBOOK.py) for a first look, then [Peers](../../../analyses/position/peers/POSITION_PEERS_NOTEBOOK.py) and [Profile](../../../analyses/position/profile/POSITION_PROFILE_NOTEBOOK.py)
- **Exhibits:** peer list table; X.4 benchmark bars (population, median household income, bachelor's share)

## Close
Point to the next installment: what people actually do here (Lens 4), which opens with Rockefeller and Empire State Plaza and the state as employer, and picks up Schenectady and GE.

Keep Schenectady to its place in the metro here (one of the four cities). Its GE story belongs to Lens 4.

## Before the Build
1. Confirm zone names and the Q6 threshold are OK for print
2. Pick 3 or 4 benchmark metrics for section 5
3. Decide whether section 4 stays in or waits for Lens 2
