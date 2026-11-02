# What New York Is: Visuals Build Plan

**Status:** Active
**Updated:** 2026-10-19

Plan and build record for the four visuals in the opening sections of [series_intro.md](series_intro.md): the Population Map in "Two New Yorks", plus Map 1 (Regions and CBSAs), Map 2 (Core Infrastructure) and the "How New York Stacks Up" benchmark in "What New York Is". Everything is built in one marimo notebook, [what_ny_is/WHAT_NY_IS_VISUALS.py](what_ny_is/WHAT_NY_IS_VISUALS.py).

| Visual | Intro section | Exhibit | Questions | Status (2026-10-19) |
|---|---|---|---|---|
| Population rank over time | Center of the Story | X.3 | S2.5 | Built 2026-10-19, two versions (rank, share of US); awaiting review |
| Population Map | Two New Yorks | X.2 (variant: tract density base) | S2.5 | Reviewed; v2 built beside v1 |
| Map 1: Regions and CBSAs | What New York Is | X.1 | S2.1, S2.2 | Reviewed; v2 built beside v1 |
| Map 2: Core Infrastructure | What New York Is | X.19 | S3.1 | Reviewed; v2 (infrastructure-led, short landmark cut) built beside v1 |
| How New York Stacks Up | What New York Is | X.4 | S2.4, S2.5 | Reviewed; table chosen; v2 with "as if a state" ranks built beside v1 |

IDs are from the Question Bank and Exhibit Bank in [ny_state_of_mind_repo_context.md](ny_state_of_mind_repo_context.md).

---

## Handoff: where things stand

**Next task:** Dan reviews the two population history charts (rank and share) and picks one or both. The v2s of the other four were approved on 2026-10-19 ("looking great"); v1 cells stay until Dan says to cut them. Exports remain off. The 2026-10-19 review below is the spec for the v2s. The [ingestion review](MAP2_INGESTION_REVIEW.md) records the earlier Map 2 data handoff.

**Read first:** this plan, [AGENTS.md](../../../AGENTS.md), [NY_REGIONS_SPEC.md](NY_REGIONS_SPEC.md), and for Map 2 the [Infrastructure Engine README](../../engines/infrastructure/README.md) and [CONTRACT](../../engines/infrastructure/CONTRACT.md).

**How to work in this folder**
- **One notebook.** All code is in `what_ny_is/WHAT_NY_IS_VISUALS.py`: a setup cell (imports, paths, projection, theme), one section per visual with its settings cell first, and a **Map helpers** section at the end with every drawing function as an `@app.function`. Layer queries are `.sql` files in `what_ny_is/sql/`. Don't add a separate `.py` module: the kernel caches imported modules, and edits then need a restart (this happened on 2026-10-18).
- **Marimo rules.** Every variable shared between cells must be unique across the notebook (prefix per section, e.g. `map2_fig`); use `_`-prefixed names for cell-local values. Run `.venv-marimo/bin/marimo check` after every edit. From the repo root, execute the notebook with `MPLBACKEND=Agg .venv-marimo/bin/python metro-deep-dive-program/issues/ny_state/what_ny_is/WHAT_NY_IS_VISUALS.py`; Agg avoids the macOS GUI backend during a headless script check.
- **Dan often has the notebook open** in the VS Code marimo extension. Editing cells that already exist is fine. **Adding or removing cells while it's open causes `ValueError: Cell '<id>' already exists`.** Before structural edits, ask Dan to close it; after, tell him to run "Developer: Reload Window" and reopen.
- **Nothing saves yet.** Every `save(...)` call is commented out (`# off until we export`) and `output/drafts/` is empty on purpose. To look at a draft yourself, run the notebook as a script and `savefig` to your own scratch directory, not to `output/`.
- **No commits** until Dan approves. Use repo-relative paths only in committed files.
- **Environment.** `.venv-marimo` (DuckDB 1.5.5) now has the spatial extension installed. Inter is installed system-wide, and both matplotlib and R find it. The DuckDB path comes from `DB_PATH` in `.Renviron` through `_shared/act_1/duckdb_helpers.py`.

**Built so far (2026-10-18)**
- Shared setup, the regions seed and the definitions spec (below)
- Review maps for regions, CBSAs and Downstate definitions, plus the label and color settings
- Population Map drafts, the benchmark and Map 1 (sections below)
- `foundations/ROADMAP.md` ticket for 14 Suffolk tracts missing from the ACS tract pull

---

## Locked decisions

| Decision | Choice | Source |
|---|---|---|
| Output format | Static PNG/SVG in the Substack article; interactive Carto versions of Maps 1 and 2 linked out | Dan, 2026-10-15 |
| Regions | 10 official REDC regions | [Series decision](../../../docs/decisions/2026-09_ny-series-first.md) |
| CBSAs | 2023 vintage; show all metros and micros, lead with metros | Series decision |
| Downstate definitions | All three stored as boolean columns in the REDC county seed; everything starts with `downstate_core` (10 counties) | Dan, 2026-10-17 |
| Map data sources | Existing OSM Infrastructure and Overture POI engines, not new NYS GIS or BTS pipelines. Fall back to those sources only for a real gap | Dan, 2026-10-17 |
| Benchmark data shape | One `.sql` file returns a tidy table; visual forms are drawn on top of it | Dan, 2026-10-17 |
| Population | ACS 5-year, full 2012–2024 series. Growth is measured 2012 → 2024. Mark the 2021 jump as a consistency break | Dan, 2026-10-17; window confirmed 2026-10-18 |
| Population Map design | Tract population density on a **log scale** as the base, with CBSAs and REDC regions overlaid. NYC filling the top classes is expected. Palettes under review: green → red, yellow → red, viridis | Dan, 2026-10-18 |
| Map rendering | One-off geopandas/matplotlib maps using the visual library theme, in the notebook's Map helpers. The library can't draw them yet (see Shared setup). Promote to library types on second use | 2026-10-18 |
| Engine | Python first. If a visual doesn't look right in Python, try the R/ggplot2 library for it. Both are fine for final output | Dan, 2026-10-18 |
| Labels | CBSA labels are the full CBSA name (no state suffix), wrapped after hyphens. Labels can be hand-placed by longitude and latitude | Dan, 2026-10-18 |
| Saving | Drafts are not written to disk until Dan asks for exports | Dan, 2026-10-18 |
| Draft exports on | The six article visuals save PNGs to `output/drafts/` on every run, under stable names with no "v2" (`population_rank_history`, `population_share_history`, `population_density`, `map1_regions_cbsas`, `map2_core_infrastructure`, `benchmark_table`), so Obsidian embeds survive the v1 cut. v1 and review saves stay off. Finals (`draft=False`, adds SVG) after sign-off | Dan, 2026-10-19 |
| Revisions | Keep each v1 cell; build v2 in new cells beside it so before and after can be compared. Cut later | Dan, 2026-10-19 |
| One job per visual | Population Map = Two New Yorks; Map 1 = reference (regions, metros); Map 2 = the canal and Thruway corridor; benchmark = Downstate vs Rest of State | 2026-10-19 review |
| Map 2 emphasis | Infrastructure first. Keep only landmarks the article text mentions (about 6) plus one NYC callout | Dan, 2026-10-19 |
| Benchmark form | Table, not the dot strip, with "as if it were a state" ranks for Downstate and Rest of State | Dan, 2026-10-19 |
| Population rank chart | Add X.3 to the intro, from a seed of decennial counts 1810–2020 for NY, CA, TX, FL and the US. Build both a rank version and a share-of-US version | Dan, 2026-10-19 |
| Population Map palette | Yellow → red stays. Dan asked whether green → red is more standard; kept sequential because density runs one way (diverging palettes imply a meaningful midpoint), green/red reads as good/bad, and red–green is the most common color-vision deficiency. If green is wanted, a sequential green (e.g. `YlGn`) is the alternative | Dan, 2026-10-19 |

---

## Review, 2026-10-19

All four drafts were rendered and inspected at full size and phone width. Dan agreed to every fix below. The v2 cells implement them; v1 cells are unchanged.

**Numbers for captions** (checked against the warehouse, `downstate_core`)
- Downstate holds **64.7% of New Yorkers on 4.9% of the land** (2,331 of 47,123 sq mi of land, tract land areas).
- **38 of 52 Rest of State counties lost population, 2012 → 2024** (ACS 5-year; 2021 consistency break applies). Only 1 of the 10 Downstate counties did.
- Rest of State is flat overall (+0.05%). The intro's "much of Upstate has been losing population" should read "flat overall, with most counties shrinking". **Article text edit pending, Dan's call.**

**Population Map**
- Yellow → red (`YlOrRd`). Green → red is a diverging palette on one-directional data and reads as good/bad; viridis makes the empty Adirondacks the loudest thing and its top class fades on white.
- Draw the Downstate line, annotated with each side's share of people and land. The intro's argument is Downstate vs Upstate, and only Map 1 showed the line.
- Remove the CBSA outlines and labels (Map 1's job); label about ten cities instead. White REDC lines were invisible on yellow, so drop them too.
- Six named bands (under 50, 50–250, 250–1,000, 1,000–5,000, 5,000–25,000, 25,000+) instead of nine classes.
- "No data" grey matched the neighboring states. Give it a distinct fill.
- Title states the finding ("Two-thirds of New Yorkers live on one-twentieth of the land"); drop "draft palette" from the subtitle.

**Map 1**
- Region fills and grey capitals work; keep them.
- Label the Downstate line directly ("Upstate ↑ / ↓ Downstate") instead of relying on the legend; on its own it read as a stray red stub.
- Micro outlines were invisible on pastel fills. D2 says show micros, so make them visible (darker, dashed outline) and label them with their first city, in a lighter style than metros.
- Fix labels: NEW YORK CITY spilled into the water, CENTRAL NEW YORK sat on a metro outline, Albany crossed the region border.

**Map 2**
- The canal and Thruway running together from Buffalo to Albany, then down the Hudson, is the strongest image in the set. Everything else supports it.
- Cut landmarks to those the article mentions: Lockport and Waterford (canal ends), Empire State Plaza (Rockefeller), Niagara Power Project (Moses), Bear Mountain (New Deal), Attica (prisons). One NYC callout names Ellis Island, Wall Street, the UN and the 9/11 Memorial as text. Label directly; no numbered key, no inset.
- Ports: NY/NJ, Albany, Buffalo and Oswego. Coeymans sits on Albany; Rochester is mostly a marina. Legend "Port", not "Port candidate".
- Interstates, main-line rail and REDC borders were all thin light grey. Drop the REDC borders (Map 1 has them) and darken the rail.
- Draw the Hudson River in water blue: half the corridor story, and the intro closes where the canal meets it. Source: OSM `river` features named Hudson River in the same Infrastructure handoff (150 features).
- Subtitle states the claim: the canal set the line from Buffalo to Albany; the Thruway and railroads still follow it.

**Benchmark**
- Table, not the strip. The strip gives each row its own scale, so a 1.7-year age gap looks as large as a 4× gap in immigrant share, and NY Total always sits at the right end of the population row.
- Add ranks for Downstate and Rest of State **as if each were a state** (ranked against the other 49 states, of 50). Rest of State comes in below the US on every metric; that is the Two New Yorks point in one line.
- Rank wording: "1 = highest (oldest, richest, fastest growing)" in the footnote; population shares (64.7% / 35.3%) beside the population values.
- Reuse the Downstate blue and Rest of State ochre across the series.
- Deferred: a cost-of-living-adjusted income row. BEA regional price parities exist for states and metros only, so there's no clean Rest of State value. Cover it in the text.

**Placement in the intro**
1. Center of the Story, after "...most recently Florida": population rank over time (X.3, new).
2. Two New Yorks, under the heading: Population Map v2.
3. Mapping the State: Map 1, then Map 2. Add a sentence there that points back to the Erie Canal paragraph.
4. How New York Stacks Up: the benchmark table.

**Missing visuals**
- X.3 population rank over time: approved; hand-entered decennial table (about 22 decades × NY, CA, TX, FL from Census historical counts) after the other visuals.
- Candidate, not approved: NYC vs Rest of State population indexed over time, for the "NYC kept growing" sentence. A county growth map (X.23) is the alternative but would be a fourth statewide map.

### Article edits for series_intro.md (Dan writes them in)

Line numbers are as of 2026-10-19. Check them off as they land.

**Accuracy fixes**
- [ ] **L18, "from 1810 to 1960":** true only on today's borders. In 1810, Virginia (still including West Virginia) had 983,152 people to New York's 959,049. Use "from 1820 to 1960", or keep 1810 and add "by today's borders". The chart footnotes already say this.
- [ ] **L18, "New York City has continued to grow... much of Upstate has been losing population":** the numbers we computed are Downstate (10 counties, +3.6% 2012–2024) and Rest of State (+0.05%, flat), not the city itself. Suggested: "Downstate has kept growing, slowly, while the rest of the state is flat overall, with 38 of its 52 counties shrinking since 2012." Footnote the 2021 ACS consistency break. If the sentence stays about NYC specifically, that number hasn't been checked.
- [ ] **L33, "a rural, Rust Belt Upstate in decline":** defensible at the county level (most counties shrinking, older, lower income), but the region as a whole is flat, not shrinking. Consider "stagnating" or "standing still".

**Missing text the visuals rely on**
- [ ] **Define Downstate in the text** (Two New Yorks, before or after the Population Map): NYC, Long Island, Westchester, Rockland and Putnam, the NY part of the NYC metro. The map, Map 1 and the benchmark all use this line.
- [ ] **Upstate vs "Rest of State":** the text says Upstate; the charts say Rest of State. Either add one sentence ("everything else, which I'll call Upstate") or relabel the charts "Upstate". Relabeling is a one-word change in the notebook.
- [ ] **Vernacular regions** (Mapping the State, with Map 1, per the L42 note): a sentence or two on where the common names disagree with the REDC regions (e.g. Rochester as "Western NY" but REDC Finger Lakes) and the debate over where Upstate starts. The Downstate line on Map 1 is one answer.
- [ ] **Map 2 tie-back:** one sentence pointing back to the Erie Canal paragraph (L27). The closing line (L69, "where the Erie Canal meets the Hudson") now pays off on the map, which draws the Hudson.
- [ ] **Benchmark prose:** the "as if a state" finding (Downstate 1st in GDP per capita and immigrant share; Rest of State 35th and 28th, and 47th in growth); the cost-of-living caveat on income (BEA regional price parities cover states and metros only, so keep it in words); the 2021 consistency-break footnote for growth.

**Checked 2026-10-19**
- [x] **"Upstate" in the figures:** `benchmark_table.png` and `population_density.png` now print "Upstate" (display names only; the SQL and v1 cells keep "Rest of State"). Same 52 counties; matches Map 1 and the article.
- [x] **Income paragraph, "a lower median in the city itself":** confirmed, keep it. ACS 2020–24 median household income: NYC $80.9k (five boroughs, pooled the same way as the benchmark; the published city figure is $80.5k) vs Downstate $94.8k vs the five suburban counties $131.5k. County medians: Bronx $48.7k, Brooklyn $80.3k, Queens $86.1k, Staten Island $98.3k, Manhattan $103.9k; every suburban county is higher (Rockland $110.0k to Nassau $146.2k). Optional: the city's median is about the US median ($80.7k).

**Cleanup**
- [ ] Replace the placeholders at L21, L39–47 and L50–66 with the images (L21's description is out of date: v2 has no CBSA overlay).
- [ ] L18–19: add a blank line before "## Two New Yorks".
- [ ] L69 says "Capital District"; Map 1 labels it "Capital Region" (the REDC name). Either is fine; consider matching, or using both once.

**Where the visuals go**
1. **End of Center of the Story, after L18:** population history chart. The rank version matches the sentence ("passed by California, then Texas... Florida"). The share version's "one in seven Americans" is the stronger hook if the paragraph leads with scale instead. Pick one for the body.
2. **L21, under "## Two New Yorks":** Population Map v2. The title states the finding, so the Downstate/Upstate paragraphs that follow read as the explanation.
3. **L39, Mapping the State:** Map 1 v2, followed by the vernacular-regions sentences.
4. **L44:** Map 2 v2, followed by the canal tie-back sentence.
5. **L50, How New York Stacks Up:** benchmark v2 table, followed by the benchmark prose.

**v2 build record (2026-10-19).** Each v2 is a new subsection directly under its v1 in the notebook, with its own settings cell (`density_v2_`, `benchmark_v2_`, `map1v2_`, `map2v2_` prefixes). New SQL: `downstate_shares.sql`, `benchmark_state_values.sql`, `map2_v2_water.sql`. New helpers at the end of Map helpers: `offset_align`, `draw_city_labels`, `draw_share_notes`, `draw_micros`, `add_as_if_ranks`, `draw_benchmark_table_v2`, `load_map2v2_water`, `draw_infrastructure_map_v2`. The only change to an existing helper is an optional `missing_color` on `draw_density` (v1 default unchanged). `marimo check` passes; full headless run rendered and inspected at 1456 px and 728 px. Nothing saved to `output/`.
- Benchmark v2 asserts NY Total's as-if rank equals the SQL state rank on every metric, and that each metric has 50 state values.
- Benchmark title follows the data, not the draft claim: Downstate is 1st in GDP per capita and immigrant share but 11th in income and 36th in growth, so "Downstate leads the country" was too strong. Now: "Split in two, New York ranks 1st and 35th in GDP per person".
- Map 2 v2 draws the whole OSM Hudson, up to its Adirondack source. Accurate, but it draws the eye into the park; clip north of Fort Edward if Dan prefers.
- Map 2 v2 is 6.9 in tall at 1456 px wide (v1: 10.3 in).

---

## Shared setup (done)

- [x] **Folder layout** under `issues/ny_state/what_ny_is/`:
  - `WHAT_NY_IS_VISUALS.py`: the notebook (see Handoff)
  - `sql/`: `ny_counties.sql`, `ny_cbsas.sql`, `neighbor_states.sql`, `ny_tract_density.sql`, `benchmark_stack_up.sql`, `benchmark_median_bins.sql`, `map2_infrastructure.sql`, `ny_principal_cities.sql`; v2: `downstate_shares.sql`, `benchmark_state_values.sql`, `map2_v2_water.sql`
  - `reference/`: `landmarks.csv` and `landmark_sources.json` (Map 2 input review)
  - `data/`: local one-off canal/park downloads and their provenance manifest
  - `output/`: final PNG/SVG plus GeoJSON exports for Carto; `output/drafts/` for saved variants. Both empty for now
- [x] **NY regions seed:** `foundations/etl/reference/ny_county_regions.csv`, 62 rows: `county_geoid`, `county_name`, `redc_region`, `downstate_core` (10), `downstate_mta` (12), `downstate_redc` (14), `source_url`, `as_of`. REDC assignments checked against each region's ESD page. The checks (62 rows, each county once, matches `geo.counties`, 10 regions, 10/12/14 counties, `core ⊂ mta ⊂ redc`) run in the notebook's first section. The seed is gitignored; see Open questions.
- [x] **Definitions spec:** [NY_REGIONS_SPEC.md](NY_REGIONS_SPEC.md). `downstate_core` is exactly the NY part of the 2023 NYC metro, and `downstate_mta` adds exactly the Kiryas Joel-Poughkeepsie-Newburgh metro.
- [x] **Style.** `foundations/visual_library/chart_engine_py/chart_engine/pip_theme.yml` through the library's `Theme`, and the [visual style guide](../../../foundations/visual_library/docs/visual_style_guide_and_standards.md). Figures are 1456 px wide (2× Substack content width) at 200 dpi; map height follows the state's shape.
- [x] **Library gaps.** `choropleth` shades categories along one blue ramp, so it can't do 10 region fills (a categorical choropleth is a NEW TYPE in the Exhibit Bank, X.5 and X.8). `highlight_context_map` draws polygons only, with no line layers, point symbols or dashed lines. `strength_strip` normalizes metrics across a peer set and needs one geography level. So every visual here is drawn by the notebook's own helpers.
- [x] **Geometry: draw with display layers, compute with analysis layers.**
  - Drawing: `geo.cbsas`, `geo.counties`, `geo.tracts_all_us` (2024 Census cartographic, clipped to the shoreline). The analysis TIGER shapes run out into the water (the NYC CBSA is about 1,900 sq mi larger, Buffalo about 780 sq mi into Lake Erie).
  - Spatial operations, such as clipping OSM features: `geo.states_analysis` / `geo.cbsas_analysis`.
  - CBSAs are clipped to the NY outline for drawing only. Neighboring states are drawn in faint grey; Canada is blank (`geo.states` is US only).
- [x] **Shared layers** (`load_base_layers`): counties joined to the seed, the NY outline, the 10 regions, the three Downstate lines (inland edge only, not the coast), the 27 NY-touching CBSAs (13 metros, 14 micros) and the neighboring states, in a Lambert conformal projection fitted to NY (`NY_CRS`). Geometry is read from `geom_wkb` with shapely.
- [x] **Names and colors cell.** `region_labels`, `region_colors`, `region_label_positions`, `cbsa_label_overrides`, `cbsa_label_style` (`full` or `short`), `cbsa_wrap_at`, `cbsa_label_positions`. Positions are `(longitude, latitude)`. New York's label sits in Long Island Sound at the center of the metro's NY part; the Poughkeepsie metro's label is in Dutchess, clear of the Downstate line.
- [x] **Review maps.** One map each for regions, CBSAs (all 27 labeled, with a label table) and the three Downstate definitions.

---

## Population Rank Over Time (Center of the Story)

**Job:** show the intro's claim that New York was the largest state from 1810 to 1960, then was passed by California, Texas and Florida. Notebook section sits before the Population Map, matching the article order.

**Data: `what_ny_is/reference/state_population_history.csv`** (110 rows; whitelisted in the folder `.gitignore` like `landmarks.csv`)
- Columns: `year`, `geography` (New York, California, Texas, Florida, United States), `population`, `state_rank`, `states_ranked`, `is_state`, `note`, `source_url`, `as_of`.
- Counts are Census decennial figures transcribed from Wikipedia's [historical population tables](https://en.wikipedia.org/w/index.php?title=List_of_U.S._states_and_territories_by_historical_population&oldid=1369369888), pinned to revision 1369369888 and parsed by script, not typed. The raw API download is in `data/wikipedia_state_population_history.json` (gitignored).
- **Ranks** were computed from all 50 states in that table: present-day boundaries, ranked among areas that were states at each census (the table's territory shading), DC excluded. `states_ranked` gives the denominator (17 in 1810, 50 from 1960).
- **US totals** are each census's official total, which excludes Alaska and Hawaii before 1960. For 1960–2010 the 50 states plus DC sum exactly to the official total; 2020 differs by 2,354 (later count corrections).
- Checks (the notebook asserts them): 110 rows; NY 1st at every census 1810–1960; NY 4th in 2020; NY 2020 = 20,201,249; one source revision. Spot checks: CA passes NY in 1970, TX in 2000, FL in 2020.
- **Boundary caveat:** in 1810, Virginia as then constituted (including West Virginia) had 983,152 people against New York's 959,049. New York is 1st in 1810 only on present-day boundaries; on the boundaries of the day it was 1st from 1820. Both charts say so in the source line. **Article text pending:** "from 1810 to 1960" needs that qualifier, or should read "from 1820".

**Design (matplotlib, `history_figure` frame matching the other visuals)**
- **Rank version:** rank on an inverted log axis so ranks 1–4 spread out; New York bold blue, CA/TX/FL muted; shaded 1810–1960 band; "Passed by California / by Texas / by Florida" on New York's line; direct end labels. Title: "New York was the largest state for 150 years".
- **Share version:** share of the US population. New York peaked at 14.9% in 1830 ("about one in seven Americans") and is 6.1% in 2020, below California (11.9%), Texas (8.8%) and Florida (6.5%). Florida is plotted from 1830 as a territory.
- Not the library's Altair `bump_chart`: these need direct event annotations and the same export frame as the other exhibits. Promote if a later piece reuses them.

**Build steps**
- [x] Seed, checks and both versions (2026-10-19); `marimo check` passes, full headless render inspected
- [ ] Dan picks rank, share or both
- [ ] Final export

---

## Population Map (Two New Yorks)

**Job:** show where New Yorkers actually live before the reader meets the regions. The dense Downstate core against a mostly empty Upstate, broken by the canal-corridor cities, is the "Two New Yorks" argument in one image.

**Data**
- `sql/ny_tract_density.sql`: tract shapes from `geo.tracts_all_us` (NY), left-joined to `gold.population_demographics` tract `pop_total` for 2024, density = `pop_total / land_area_sqmi`. 5,393 tracts with land are drawn.
- Checks (2026-10-18): tract shapes are shoreline-clipped and cover the same 48,970 sq mi as the county shapes. The 17 population rows with no shape are zero-population water tracts.
- **Known gap:** 14 Suffolk County tracts have no 2023–24 population in the warehouse (77,579 people; the county total is complete). They draw grey as "no data" with a note in the source line. Fix ticketed in [foundations/ROADMAP.md](../../../foundations/ROADMAP.md) (Next table).

**Design as drafted**
- Nine log classes stepping ×5 then ×2: under 10, 10–50, 50–100, 100–500, … 50,000+ people per sq mi (`density_breaks`)
- Three palette drafts stacked in the notebook (`density_palettes`): green → red (`RdYlGn_r`), yellow → red (`YlOrRd`), viridis. Dan liked all three on first look; the choice is part of the review
- Tracts with land but no residents draw white; no-data tracts draw grey. Legend top left
- Overlays: REDC region lines in white, metro outlines dark with labels, micro outlines lighter without labels

**Build steps**
- [x] Tract density query plus the checks
- [x] First variant set (2026-10-18)
- [x] Review with Dan (2026-10-19): yellow → red, six named bands, Downstate line with shares, no CBSA overlay, no NYC inset
- [x] v2 cells built beside v1
- [ ] Dan compares v1 and v2; cut v1 drafts
- [ ] Final export

---

## How New York Stacks Up (benchmark)

**Job:** one compact visual comparing Downstate, Rest of State, NY Total and the US on six metrics grouped by lens, with NY's rank among the 50 states.

**Data**
- `sql/benchmark_stack_up.sql` returns the tidy table (`lens`, `metric_id`, `metric_label`, `geography`, `year`, `value`, `state_rank`, `rank_of`, `downstate_definition`, `method`, `metric_order`). Downstate and Rest of State come from counties; NY Total and US are published figures; ranks are computed over the state rows.
- `sql/benchmark_median_bins.sql` returns age and household income bin counts for Downstate, Rest of State and all 62 counties. The notebook's `pooled_median` interpolates linearly inside the median bin and adds those rows.
- Both queries take `__DOWNSTATE__` and `__SEED_PATH__`, filled by `run_benchmark_sql`. Change `benchmark_downstate` in the notebook to rerun with another definition.

**Results (Downstate = `downstate_core`)**

| Metric | Downstate | Rest of State | NY Total | NY rank | US |
|---|---|---|---|---|---|
| Population | 12.8M | 7.0M | 19.9M | 4th | 334.9M |
| Median age | 39.3 | 41.0 | 39.8 | 18th | 38.9 |
| Foreign-born share | 31.4% | 7.0% | 22.8% | 3rd | 14.1% |
| Median household income | $94.8k | $75.8k | $86.0k | 15th | $80.7k |
| GDP per capita (2023) | $130.7k | $70.0k | $109.3k | 1st | $82.9k |
| Population growth, 2012–2024 | +3.6% | +0.0% | +2.3% | 44th | +8.3% |

**Checks** (assert in the notebook): Downstate + Rest = NY population; the 62-county pooled medians are 39.8 (published 39.8) and $86,616 (published $85,974, +0.7%). Pooled medians were chosen over weighted county medians, which run 4.5% high for income.

**Method notes**
- **GDP is BEA 2023.** The warehouse has no 2024 county GDP yet, so all four columns use 2023 and the source line says so.
- **US GDP per capita is the sum of the 50 states and DC.** The gold US row has no GDP.
- **Ranks are 1 = highest for every metric;** median age 18th means 18th oldest. DC and Puerto Rico are excluded.
- The 2012 → 2024 growth spans the 2021 ACS consistency break (the 2017–21 release was the first controlled to 2020 Census-based estimates). Footnote it in the text.
- Rest of State growth is +0.05% over 12 years; it prints as +0.0%.
- Cost of living: BEA regional price parities (`silver.bea_regional_marpp_*`) can back up the NYC cost-of-living note in the text.

**Build steps**
- [x] Both queries, the pooled-median step and the checks
- [x] Table and dot-strip drafts (`draw_benchmark_table`, `draw_benchmark_strip`). The strip leaves the US off the population row and gives it as text
- [x] Review with Dan (2026-10-19): table form; rank direction in the footnote; add "as if a state" ranks
- [x] v2 table built beside v1 (`draw_benchmark_table_v2`)
- [ ] Dan compares v1 and v2; cut the strip and v1 table
- [ ] Final export

**"As if a state" ranks (v2, Downstate = `downstate_core`; of 50, 1 = highest)**

| Metric | Downstate | Rest of State | NY Total |
|---|---|---|---|
| Population | 5th | 16th | 4th |
| Median age (oldest) | 22nd | 8th | 18th |
| Foreign-born share | 1st | 28th | 3rd |
| Median household income | 11th | 29th | 15th |
| GDP per capita (2023) | 1st | 35th | 1st |
| Population growth, 2012–2024 | 36th | 47th | 44th |

---

## Map 1: Regions and CBSAs

**Job:** give the reader their bearings: the 10 regions, where the metros sit inside them, and where the benchmark's Downstate line falls.

**Design as drafted**
- REDC regions as muted fills (`region_colors`), county lines faint
- Metro outlines dark with full-name labels; micro outlines lighter, no labels
- Region names in small grey capitals, hand-placed (`region_label_positions`) so they don't collide with metro names
- Downstate line: dashed risk red over a white underlay, so it reads along the black NYC metro outline it follows. `map1_downstate` switches definitions
- Legend: metro, micro, Downstate line. Source line: ESD REDC regions; Census cartographic boundaries

**Build steps**
- [x] Draft the static map, with label collisions in the Hudson Valley cleared (2026-10-18)
- [x] Review with Dan (2026-10-19): both maps stay, with separate jobs; the Population Map v2 drops the CBSA overlay
- [x] v2 cells built beside v1: direct Upstate/Downstate labels, dashed micro outlines with first-city labels, label moves
- [ ] Dan compares v1 and v2; cut v1
- [ ] Final export
- [ ] Export GeoJSON (regions, CBSAs, all three Downstate lines) for Carto

---

## Map 2: Core Infrastructure

**Job:** show the corridors that made the state. The canal and Thruway line from Buffalo to Albany is the visual hook that ties back to the Erie Canal history thread.

**Design**
- Base: NY outline with REDC borders in light grey; principal cities of the metros as reference dots.
- Layer emphasis, strongest first: canal system (accent color) → Thruway (heavy) and other interstates (light) → main-line rail (thin dashed) → ports (symbols) → numbered landmarks with a key.
- NYC landmarks sit too close together to separate at state scale. Show one NYC marker with an inset or caption list.
- Reuse `new_map`, `draw_outline`, `draw_regions`, `label` and `add_text` from Map helpers. Add line and point helpers there.

**Landmarks: map all of them, then cut.** Plot the full list in a working draft, then pick the final set with Dan by how the map reads.

| History theme | Landmarks |
|---|---|
| Erie Canal | Lockport Flight of Five · Buffalo Canalside (western end) · Waterford Flight (eastern gateway) |
| Immigration | Ellis Island · Statue of Liberty |
| Capitalism, highs and lows | Wall Street / NYSE · Kodak Park, Rochester · Bethlehem Steel, Lackawanna · GE, Schenectady |
| Military | West Point · Saratoga Battlefield · Fort Ticonderoga |
| Global center | UN Headquarters · 9/11 Memorial |
| Public works | Empire State Plaza (Rockefeller) · Niagara Power Project (Moses) · Jones Beach (Moses) · Bear Mountain (New Deal) |
| Social movements | Seneca Falls · Harriet Tubman Home, Auburn · Stonewall Inn |
| Media and culture | Rockefeller Center (NBC) · Woodstock / Bethel · Cooperstown |
| Prison towns | Attica · Clinton Correctional, Dannemora |
| Landscape | Adirondack Park (area) · Catskill Park (area) · Niagara Falls · Finger Lakes (area label) |

### Task list

**Approved by Dan, 2026-10-18:** Map 2's bounded ingestion scope, the OSM download,
state support in the shared Infrastructure Engine, and the proposed five ports
plus any additional relevant port candidates. Full statewide Overture POI and
the remaining B1 layers wait until Map 2 works. **Stop for data review before
step 7, the notebook section.** No further permission is needed for steps 1–6.

**Notebook authorized by Dan, 2026-10-18:** proceed with Map 2's notebook
section. Dan confirmed the VS Code Marimo editor was closed before cells were
added. After the changes, reload the VS Code window and reopen the notebook.

1. [x] **Canal centerline (one-off download).**
   - URL: `https://services6.arcgis.com/DmQy2NS38tchd4fs/arcgis/rest/services/Canal_Centerline/FeatureServer/10/query?where=1%3D1&outFields=*&outSR=4326&f=geojson`
   - Saved as `what_ny_is/data/canal_centerline.geojson`; URL, pull timestamp, checksum and geometry QA are recorded in `what_ny_is/data/map2_reference_manifest.json`. Add the notebook source note after the data review. No pipeline.
   - Expect 20 line features (about 570 KB) coded by `ROUTE`: `ER` Erie, `CH` Champlain, `OS` Oswego, `CS*` Cayuga-Seneca, plus spurs (`ER-OL`, `CH-FE`, …). Check: `ER` is one continuous line of about 338 miles; all routes about 534 (official system: 524). Checked 2026-10-17.
   - Why not OSM: OSM tags the canalized river stretches (Mohawk, Seneca, Oswego, Clyde) as rivers.
   - Credit "NYS Canal Corporation" in the source line; the service has no license text.

2. [x] **Park boundaries (one-off downloads)**, from the B2 Source Plan in the repo context:
   - Adirondack Park: APA Blue Line polygon, `https://services2.arcgis.com/8krRUWgifzA4cgL3/ArcGIS/rest/services/BluelinePolygon/FeatureServer/0` (query as GeoJSON like the canal)
   - Catskill Park: look for a Catskill Park boundary layer on the DEC service (`https://gisservices.dec.ny.gov/arcgis/rest/services/reference/MapServer`); layer 2 is DEC Lands (Forest Preserve, State Forests, WMAs), which is state land, not the park boundary. If no park boundary layer exists, use OSM `boundary=protected_area` and note it.
   - Save to `what_ny_is/data/` with URLs and pull dates in the notebook. Draw as light shaded areas.
   - Downloaded and validated: `adirondack_park.geojson` (APA; about 5.824 million acres) and `catskill_park.geojson` (DEC; about 696,707 acres). DEC's current `dil_reference/MapServer/8` is the actual Catskill Park boundary, so no OSM fallback is required. Both are one valid polygon in EPSG:4326. Provenance lives in `data/map2_reference_manifest.json` until the notebook section is approved.

3. [x] **NY OSM extract.**
   - Existing markets (Richmond, Jacksonville) cache an openstreetmap.fr PBF plus a GeoPackage adapter built with R `osmextract` (see the engine's `NOTES.md`, lines ~115–118, and `metro-deep-dive/metro-area-explorer/.../ingest_*_osmextract.R`). Build the NY one the same way, so `source_tags.other_tags` has the same shape.
   - Candidate sources: openstreetmap.fr `north-america/us-northeast/new_york` or Geofabrik `north-america/us/new-york`. Confirm the URL and size before downloading. Cache it outside git, alongside the existing caches.
   - Used the dated Geofabrik `new-york-261017.osm.pbf`: 497,738,989 bytes, provider MD5 verified. Cached under `engines/infrastructure/outputs/new_york_state/raw/`; the approximately 4 GB GeoPackage was built with `sources/ingest_new_york_osmextract.R`. Integrity check passed; all three layers declare EPSG:4326. Lines: 2,174,756; polygons: 5,092,046; points: 4,180,281. These are source-cache counts, not published POI counts.

4. [x] **State-scoped market in the Infrastructure Engine** (shared code: follow its README and CONTRACT, and update the CONTRACT in the same change).
   - `sources/osm_infrastructure.yml`: add `new_york_state` with `market_id: "36"` and a new key such as `boundary_level: state`, plus the usual `source_release`, `provider`, `source_asset_uri`, `source_asset_path`, `source_adapter_path`.
   - `acquire_osm_infrastructure.py`: `resolve_market` already accepts a numeric id. `resolve_boundary` only queries `geo.cbsas_analysis` with `mart_geography.identity_current` at `geo_level = 'cbsa'`. Add a state branch that reads `geo.states_analysis` with `geo_level = 'state'` (51 states in `identity_current`; `states_analysis` is catalogued with `geometry_role = 'analysis'` in `mart_geography.geometry_catalog`).
   - `normalize_osm_infrastructure.py` hardcodes `'cbsa' AS market_boundary_geo_level` (around line 120); make it follow the market. Grep `validate_` and `publish_` for other CBSA assumptions.
   - Run acquire → normalize → validate → publish with `--market new_york_state`. `configure_spatial` only loads the extension, so use an environment that has spatial for its DuckDB version (`.venv312` or `.venv-marimo`). Don't run DuckDB writes in parallel.
   - The engine keeps roads down to `tertiary`. Filter to what the map needs in the notebook query; don't change the engine's core mapping for this map.
   - Completed acquire → normalize → validate → publish for `new_york_state`, state `36`, 2023 analytical boundary. Of 180,497 selected source features, 733 fall outside NY; 179,764 are acquired and mapped, and 179,751 pass the geometry gate. The 13 rejected clipped geometries remain available for QA (six points, seven geometry collections). Final serving groups: 152,269 road, 21,368 rail, 6,114 water-network features. [Handoff](what_ny_is/data/map2_infrastructure_handoff.json) and [independent QA](what_ny_is/data/map2_ingestion_qa.json).
   - Required unplanned fixes, verified complete: preserve GDAL polygon-way identity via `osm_way_id` (843 valid NY water polygons would otherwise be rejected); use the state's geometry vintage rather than its identity vintage; explicitly preserve longitude/latitude axis order for metric QA; cache acquisition stages in temporary tables to avoid repeated full-adapter scans. Seven regression tests pass, and existing CBSA normalization/handoff compatibility was checked. The README and CONTRACT were updated. No managed warehouse tables were written.

5. [x] **Landmarks and ports, `what_ny_is/reference/landmarks.csv`.** Columns: `name, theme, kind, lat, lon, overture_id, keep`, with `kind` = `point`, `area` or `port`.
   - There is no NY run in `mart_poi` (it's CBSA-scoped to earlier markets). Either query Overture Places directly for the ~30 names (DuckDB `httpfs` on the Overture release, filtered to the NY bounding box), or take coordinates from Wikipedia or OSM and leave `overture_id` empty. Note which in the notebook.
   - Ports: 5 hand-placed points. Which 5 is an open question. Candidates for Dan: Port of New York and New Jersey (NY side), Albany, Oswego, Buffalo, Ogdensburg.
   - Completed all 30 planned landmarks plus seven ports, all with `keep=true` for the first review. Added Coeymans and Rochester to the approved five. Rochester represents its current terminal/marina complex; inclusion does not imply comparable freight activity. NY/NJ is represented by Howland Hook on Staten Island; Buffalo by Gateway Metroport's published location map. Each coordinate's source and interpretation are in `reference/landmark_sources.json`. All 37 coordinates are inside Geography's NY analytical boundary. `overture_id` is empty because no Overture run was made.

6. [x] **Principal-city dots.** `silver.xwalk_cbsa_primary_city` (`cbsa_code`, `primary_city`, `state_fips`, `place_fips`) joined to `geo.places_display` on `place_geoid = state_fips || place_fips`; use a representative point. Metros only.
   - Independently executed `what_ny_is/sql/ny_principal_cities.sql`: 22 NY principal-city points across 13 metros, unique at CBSA × Place. The crosswalk can name several principal cities per metro; retain them for the later visual review. These are display-geometry points, not job centers or city halls.

7. [x] **Notebook section.** Added independently executed `what_ny_is/sql/map2_infrastructure.sql` over the verified consumer artifact, plus the existing principal-city query:
   - **Thruway:** operator tags are optional; the proposed operator filter returned zero rows. The query uses source-supported names for the mainline, Berkshire Connector, New England and Niagara sections, Cross Westchester Expressway and Garden State Parkway Connector, plus I-190's named Grand Island bridges and I-90's western AMVETS segment. Checked against [the Authority's section descriptions](https://www.thruway.ny.gov/business/real-property). The Northway, Major Deegan, Albany's free I-90 and northern Niagara Expressway are not highlighted. Unnamed source segments may remain in the lighter interstate layer; the legend says "named sections" rather than claiming a legal inventory. Selected 2,366 features.
   - **Other interstates:** `motorway` with exact interstate route tokens, including semicolon-separated concurrent routes, excluding already highlighted sections. This avoids treating `I 81 BUS` as an interstate. Selected 5,803 features.
   - **Main-line rail:** `railway=rail` with `usage=main`.
   - Main-line rail selection is 6,855 features. Another 6,334 rail features have missing usage and are not reclassified. The notebook sources/limits cell preserves this distinction.
   - Loaded references and published features read-only, then clipped lines and parks to the NY display outline for drawing. The analytical artifacts remain intact. Added line/point/numbered-marker helpers in the notebook's Map helpers; no imported rendering module.
   - Settings cell first (`map2_` prefix), inventory table, map and source notes. Layer visibility, colors, numbered-marker offsets, city-label offsets and inset extent are editable. Landmark numbers stay stable when `keep` is changed. All `save` calls remain commented out.
   - Verified `marimo check`, full notebook execution with the Agg backend, independent SQL selection checks and actual 1456 px / 728 px scratch renders. All 37 input candidates are retained; seven NYC landmarks are in the inset. Earlier visual cells and existing helper functions were checked against the pre-edit file and are unchanged. Fixed key/source spacing after inspecting the phone-width render. No final output files were written.

8. [ ] **Draft and review.**
   - [x] Working draft with every landmark and port, area labels, principal-city dots, NYC detail and a two-column numbered key; inspected at phone width.
   - [x] Review with Dan (2026-10-19): infrastructure first; six landmarks, four ports, NYC callout, Hudson River, no REDC borders.
   - [x] v2 cells built beside v1; the cut lives in `map2v2_landmarks` / `map2v2_ports`, and `landmarks.csv` is unchanged.
   - [ ] Dan compares v1 and v2; adjust labels until the approved map reads at phone width.
   - [ ] Export PNG/SVG and GeoJSON for Carto after approval.

---

## Build order

1. ~~Regions seed and definitions spec~~ (done)
2. ~~Benchmark SQL and numbers~~ (built; review pending)
3. ~~Population Map variants~~ (drafted; review pending)
4. ~~Map 1~~ (drafted; review pending)
5. ~~Map 2 working draft with all candidates~~ (built; review pending)
6. ~~Review of all four with Dan~~ (2026-10-19); ~~v2 cells~~ (built)
7. ~~Population rank over time (X.3)~~ (built, two versions; review pending)
8. Cut v1s when Dan says; final exports
9. Carto versions after the static maps are approved

## Open questions

- **Revisit later:** the regions seed is not in git. `foundations/.gitignore` ignores every `*.csv`, and unlike the QCEW map it has no build script, so a lost copy has to be rebuilt by hand from [NY_REGIONS_SPEC.md](NY_REGIONS_SPEC.md). Kept out of git for now (Dan, 2026-10-18). The fix is one line: `!etl/reference/ny_county_regions.csv` in `foundations/.gitignore`
- Map 2 v2: clip the Hudson north of Fort Edward, or keep it to its source?
- X.3: rank version, share version, or both?
- Intro wording: "from 1810 to 1960" needs "on today's boundaries", or should read "from 1820" (Virginia, with West Virginia, was larger in 1810)
- Intro wording: change "much of Upstate has been losing population" to "flat overall, with most counties shrinking" (Dan's edit)
