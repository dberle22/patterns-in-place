## What This Is

The reusable visuals for the NY series. An exhibit is one chart, one data binding, built once as a Marimo cell and reused by changing its parameters.

An exhibit is not a question and not an insight. The question is what we want to know, the exhibit is the machinery that shows it, and the insight is what a specific run of it says about a specific place. Only the machinery is reusable. What Syracuse's income distribution means is written once, in Syracuse's article.

Each exhibit names its visual library type, its parameters, and its source. An exhibit with no parameters is not reusable and should be rewritten until it has some.

**Build discipline:** an exhibit earns a spec the second time we reach for it, not the first. This bank is a catalog of what we expect to reuse, not a build queue. Write the first section article, notice which cells got copied, and promote those.

**Library note:** the visual library has 15 implemented types in R and ggplot2, all static PNG. Two exhibits below need a type the library does not have yet; they are marked **NEW TYPE**. Carto and reactive maps stay exploration only (E10).

> [!note] Library engine (settled 2026-10-15)
> Both the R/ggplot2 library and its native Python port (Altair, matplotlib/geopandas) are in use. Engine choice per exhibit is handled in Claude Code sessions; the exhibit specs here stay engine neutral.

---

## Geography and Orientation

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

## People

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

## Economy

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

## Infrastructure and Structure

| ID | Exhibit | Type | Parameters | Source |
|---|---|---|---|---|
| X.19 | Network map. Roads, rail, transit, ports, or canal, drawn over a base geography. | Highlight context map | `layers`, `geo_extent`, `year` | Infrastructure engine (B1) |
| X.20 | Network with population. The same network overlaid with population, so gaps are visible. | Highlight context map + proportional symbol | `layers`, `geo_extent`, `pop_year` | Infrastructure + ACS |
| X.21 | Downtown crop. A zoomed map of one CBD with its anchors marked. | Highlight context map | `geo_id`, `anchor_types`, `zoom` | Internal Structure, POI |
| X.22 | Zone composition. Share of each zone type within a metro, benchmarked. | Bar, benchmarked | `cbsa_code`, `zone_model`, `year` | Intelligence Framework Phase 7 |

X.19 and X.20 both wait on B1. X.21 is the CBD cell that will get reused on every metro spotlight, which makes it one of the highest-value exhibits in the bank. Internal Structure now runs per market from a Python script (2026-11-02), so run it for the metro first.

---

## Change and Comparison

| ID | Exhibit | Type | Parameters | Source |
|---|---|---|---|---|
| X.23 | Growth map. Change in a metric over a window. | Choropleth, diverging | `geo_level`, `metric_id`, `year_range` | ACS, warehouse |
| X.24 | Rank shift. How a set of geographies moved in rank between two years. | Bump chart | `geo_level`, `geo_filter`, `metric_id`, `year_a`, `year_b` | Warehouse |
| X.25 | Two-metric scatter. Any two metrics across a geography set, with quadrants. | Scatter | `geo_level`, `geo_filter`, `metric_x`, `metric_y`, `year` | Warehouse |
| X.26 | Before and after. One metric across two points in time for a set of geographies. | Slopegraph | `geo_level`, `geo_filter`, `metric_id`, `year_a`, `year_b` | Warehouse |
| X.27 | Within-metro spread. Distribution of a tract-level metric inside each metro. | Boxplot | `cbsa_filter`, `metric_id`, `year` | ACS tract |
| X.28 | Ranked bar with contributions. A ranking with the components that produced it visible. | Bar, segmented | `geo_filter`, `score_id`, `top_n` | Intelligence Framework |

X.25 and X.26 are the workhorses. Almost every ranking question and most thematic analyses land in one of these two shapes, which is why they are worth parameterizing carefully rather than rebuilding per article.

X.28 builds its composite inside the analysis that uses it; composite scores are an approach, not a production layer (2026-11-02).

---

## Risk and Health

| ID | Exhibit | Type | Parameters | Source |
|---|---|---|---|---|
| X.29 | Risk map. | Choropleth | `geo_level`, `risk_metric`, `year` | FEMA, AQI |
| X.30 | Risk against growth. Hazard exposure on one axis, population change on the other. | Bivariate choropleth | `geo_level`, `risk_metric`, `year_range` | FEMA + ACS |
| X.31 | Outcome spread. A health outcome across regions or metros. | Boxplot or strength strip | `geo_level`, `geo_filter`, `outcome_metric`, `year` | health_wide |

X.30 is A3 Moving Toward Harm in a single chart, and the bivariate choropleth already exists in the library.

---

## Build Status Summary

**Ready now, library type exists:** X.1, X.2, X.3, X.4, X.6, X.7, X.9, X.10, X.11, X.13, X.14, X.15, X.16, X.18, X.23, X.24, X.25, X.26, X.27, X.29, X.30, X.31

**New visual type needed:** X.5, X.8

**Waiting on the NY infrastructure ingest (B1):** X.19, X.20

**Waiting on source assembly:** X.17

**Ready, run the Internal Structure script for the metro first:** X.21, X.22 (updated 2026-11-02)

**Ready, composite built in the analysis:** X.28 (updated 2026-11-02)

**Exploration only, never print:** X.12

---

## Exhibits That Repeat

Expected to carry three or more pieces, so build these with parameters the first time. Carried over from the retired Article Slate on 2026-11-02 and restated by piece name.

| Exhibit | Expected uses |
|---|---|
| X.4 Benchmark bar | Albany parts, statewide context in rankings |
| X.13, X.14 Industry mix and specialization | Albany Part 2, The State as Employer, Company Town Index |
| X.16 Concentration strip | Albany Part 2, The State as Employer, Company Town Index |
| X.23 Growth map | Growth ranking, Growing Toward Harm?, a later Albany part |
| X.25 Two-metric scatter | Growth ranking, How Much of This Place Is the College?, Growing Toward Harm? |
| X.26 Slopegraph | Growth ranking, later Albany parts |
| X.1 Region assignment map | What Is Upstate, Capital District, Western NY vs the Finger Lakes |

---

## Albany Part 1 Exhibits, Not Yet Promoted

Built for [[Albany - What Albany Actually Is]] with their own e numbering. The growth ranking and the short deep dives will reuse several of them, which is the second use that earns a spec. Mapping below is from the article text; confirm against the notebook cells.

| Albany file | What it shows | Closest X | Proposed |
|---|---|---|---|
| e0b_nutshell_dots | One metro's rank among NY metros on a set of metrics | None | New X.32, Nutshell rank dots. Reused by every deep dive. **Promote first** |
| e1_metro_map, e1c_core_map | Metro counties, central vs outlying, named cities; e1c is the core zoom | X.2 (statewide locator) | New X.33, Metro orientation map, with a `zoom` parameter covering both. **Promote first** |
| e2_albany_buffalo_gdp | Two metros on one metric over time | X.3 (rank over time) | New X.34, Head to head trend, or a parameter on X.3 |
| e3_migration_flows | Migration rates per 1,000 across metros | X.10, X.11 | Check whether X.11 covers it |
| e4_peer_table | Ten closest national peers by similarity | None | New X.35, Peer table (M.3). **Promote first** |
| e5_top_places | Largest places in the metro, ranked | X.9 | A ranked bar; check whether X.9 covers it |
| e6b_population_arrow | Tract population density | X.7 | Generalize X.7 to any tract metric |
| e8_job_centers | Job centers by tract | X.15 | Is X.15. Record it as built |
| e9_zone_map | Neighborhood types by tract | X.22 (bars) | New X.36, Zone map |
| e10_zone_table | Neighborhood types with their profiles | X.22 | X.22 in table form |

---

## Exhibit Spec Format

When an exhibit gets promoted, it gets a short spec. Not a schema, just enough that the next person who reaches for it knows what it takes.

```
## X.n Name
Type: <visual library type>
Question(s): <IDs from the Question Bank>
Takes: <parameter list with types>
Returns: <what the cell outputs>
Source: <tables or engine>
Notes: <suppression, vintage, coverage caveats>
```
