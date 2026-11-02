# Issue Visuals: Build Rules

**Status:** Active
**Updated:** 2026-11-02

How to go from an approved outline to the evidence and print visuals for a Metro Deep Dive issue. It is written so it can become a Claude Code skill or agent: each phase has inputs, steps, a gate and an output, and every rule says why it exists.

**The product is the article, not the charts.** Answer the outline's questions first, with several tables and quick views per question. Write down what the evidence says. Only then choose the one visual that carries each claim.

Learned from two builds: [What NY Is](ny_state/primer/series_intro/WHAT_NY_IS_VISUALS_BUILD_PLAN.md) (2026-10-17 to 10-19) and [Albany Lens 1](ny_state/metro_deep_dives/albany/part_1/ALBANY_LENS1_VISUALS_BUILD_PLAN.md) (v1 2026-10-22). Add a rule when a review catches something a rule would have prevented.

---

## When to use

- **Use** when an issue outline lists sections, questions and planned exhibits, and those exhibits need to become print visuals.
- **Don't use** for exploration in `analyses/` notebooks, or for Carto and reactive maps, which stay exploration only (E10).

## Inputs

| Input | Where |
|---|---|
| Outline: argument, sections, questions, planned exhibits | `issues/<series>/<piece>/<PIECE>_OUTLINE.md` (Dan owns it) |
| Question Bank, Exhibit Bank, print rules, D/E decisions | The series repo context, e.g. `issues/ny_state/upstate_downstate_repo_context.md` |
| Routed analyses and their queries | The notebooks the outline's "Explore with" lines name |
| Style | `foundations/visual_library/chart_engine_py/chart_engine/pip_theme.yml` through `Theme`; the visual style guide |
| Reference notebook | [WHAT_NY_IS_VISUALS.py](ny_state/primer/series_intro/WHAT_NY_IS_VISUALS.py) |

## Outputs

```
issues/<series>/<piece>/
  <PIECE>_OUTLINE.md              input
  <PIECE>_VISUALS_BUILD_PLAN.md   Phase 1
  <PIECE>_EXPLORATION.py          Phase 2: tables, quick views, reads (not for print)
  <PIECE>_VISUALS.py              Phase 3: the print exhibits
  sql/                            new queries only
  reference/                      hand-curated inputs (landmarks, POI anchors) + a sources file
  data/                           pulled external files + a manifest with URL, date, checksum
  output/drafts/                  PNGs, rewritten on every run
  output/                         finals (PNG + SVG), after sign-off
```

A metro with several articles gets one folder per article, `issues/<series>/<metro>/part_<N>/`, using the layout above. Files that more than one article uses sit at the metro root: `<metro>_common.py`, shared `sql/`, `data/` and `reference/`. In the New York series the folder paths follow [its layout](ny_state/README.md) (`issues/ny_state/metro_deep_dives/<metro>/`) and the article text lives in the vault, with working copies in `drafts/` deleted when the work is done. Example: [Albany](ny_state/metro_deep_dives/albany/README.md).

---

## Workflow

Six phases. **Stop at every gate** and wait for Dan.

### Phase 0: Orient

1. Read the outline, `docs/STATUS.md`, the repo context's print rules, and the analyses the outline routes to.
2. Probe the warehouse for **every number and claim in the outline** (R7). Note what holds, what is off, and what data exists that the outline doesn't know about.
3. List the print gates that apply (R15).

Output: notes for the plan. No code in the issue folder yet.

### Phase 1: Plan

Write `<PIECE>_VISUALS_BUILD_PLAN.md` from the template below. Organize it by **question set**: each of the outline's questions gets the candidate views that could answer it (tables, maps, charts, from more than one angle) and the data behind each. Exhibits are chosen later. Corrections to the outline and new findings go in a Findings section.

**Gate:** Dan approves the question sets and candidate views, and answers the open decisions or marks them as decide-later.

### Phases 2–4 run one question set at a time

Take one question through Explore, its gate, Build and Review before starting the next. The exploration notebook answers questions; the visuals notebook holds only promoted exhibits and the confirmed results behind them, organized by question in article order. A plan's Workflow section spells out the loop and a status per question (example: the [Albany Lens 1 plan](ny_state/metro_deep_dives/albany/part_1/ALBANY_LENS1_VISUALS_BUILD_PLAN.md)).

### Phase 2: Explore

Build `<PIECE>_EXPLORATION.py`, one section per question set:

1. Build the candidate views: tables first, then quick maps or charts. Use house colors but skip print polish.
2. Try more than one angle (R30). For example, tract clusters next to the raw metrics behind them, or both directions of a flow.
3. End each section with **Reads**: two to five dated draft sentences on what the evidence says, written for the article (R31).
4. Add each finding that changes the outline to the plan's Findings.

**Gate:** Dan reviews the reads and picks, for each claim, the view that becomes the print exhibit. The plan's exhibit table is filled in only now.

### Phase 3: Build, one exhibit at a time

For each exhibit, in the plan's build order:

1. Promote from the exploration notebook. **Move, don't copy:** a query or prep function a print exhibit uses moves to `sql/` and the visuals notebook's helpers, and the exploration notebook imports it back. Write any new queries, then a data cell with a check table that asserts the confirmed reads (R10).
2. Add a settings cell for everything the reader sees (R18), then the drawing cell.
3. Run `marimo check`, then run the whole notebook headless (`python <notebook>.py`).
4. **Look at the PNG** (R21). Fix collisions and clipping before showing it.
5. Tick the plan's task list.

**Gate:** Dan reviews each draft before the next exhibit starts, unless he asks for a batch.

New external data (a downloaded file, a hand-curated list) gets its own gate: **stop for data review** before drawing with it (R14).

### Phase 4: Review rounds

- Record each review as a dated `## Review, YYYY-MM-DD` section in the plan: Dan's notes, then the agreed changes.
- Build revisions as v2 cells **beside** v1 (R24). Dan cuts v1.
- Move settled choices into the plan's Locked decisions table so they aren't re-argued.

### Phase 5: Finalize

1. `save(..., draft=False)` for approved exhibits only (R26).
2. Give Dan an article edits checklist: places where the text and the numbers disagree (R27).
3. When every task is done, set the plan's status to Done and archive it under `<area>/archive/YYYY-MM_<name>/` (docs/CONVENTIONS.md §4).

---

## Rules

Rule numbers are stable IDs that plans and reviews cite. A new rule takes the next number and goes in the section it belongs to.

### Planning

- **R1. Plan before building.** The outline says which exhibits to make; the plan decides whether each one can carry its claim. *Why:* Albany v1 went from outline straight to seven exhibits, and three failed review (a bar chart for a "where" claim, a section with no visual, a map built on uncleared labels). All three would have shown up in a plan.
- **R2. One claim per exhibit, written as its draft title.** If you can't write the claim, the exhibit isn't ready. *Why:* the title test catches exhibits that only show data without making a point.
- **R3. Pick the form from the claim.**

  | Claim is about | Form |
  |---|---|
  | Where something is, or how it spreads | Map |
  | A few things on one measure | Bars or a table |
  | Change over time | Line |
  | Rank among many | Rank line or table |
  | Many metrics for a few geographies | Table |

  *Why:* "four cities, no center" is a claim about geography. Albany v1 drew it as a bar chart of places, and it didn't land.
- **R4. Compare like with like.** The numerator and denominator must describe the same population: jobs against resident **workers**, not residents. Say what's being counted: tracts or people, jobs or workers. *Why:* jobs vs residents mixes in children and retirees and overstates job centers.
- **R5. One job per visual.** A bearings map (where things are) and an argument map (what the data shows) are usually two maps. *Why:* What NY Is had to split Map 1 (reference) from Map 2 (infrastructure) and the Population Map (two New Yorks).
- **R6. Fold thin sections into existing exhibits.** If a section's answer is one number per geography, put it on a map or chart that already exists rather than adding a table. *Why:* Albany's "Does everyone belong?" read as a table with no visual; the commute shares belong on the metro map.
- **R30. Explore before choosing.** Each question gets several views before one becomes an exhibit: a table, plus at least one alternative angle (another metric, another geography level, the reverse direction of a flow, the raw inputs behind a model output). *Why:* Albany v1 printed the first view of each question. Dan's review asked for POI clusters and demographics beside the tract clusters, and for commuting in both directions.
- **R31. Exploration ends in sentences, not charts.** Each question set's Reads are draft article sentences with numbers, dated, and marked for Dan to confirm. A view that produced no read is cut. *Why:* the goal is strong articles, not a stack of graphs.

### Data

- **R7. Probe before you plan.** Test every number in the outline against the warehouse, and search for data the outline assumes is missing. *Why:* Albany's outline deferred Section 4 to a future data ingest that had already landed, and misread Q6's "10 candidate places" (really 10 job-center components tied to 6 places).
- **R8. Reuse analysis SQL from its own folder.** Never copy it. New queries go in the article's `sql/`, moving to the metro's `sql/` when a second article needs them, with `__NAME__` placeholders, filled by `run_sql(con, path, name=value)`. *Why:* one owner per query; fixes in the analysis reach the issue.
- **R9. Read governed marts before re-deriving.** If a mart already holds the answer, read it.
- **R10. Every section gets a check table.** Each row is a claim from the outline, the computed value, and passed/failed. Assert on hard facts (counts, definitions); display soft ones (approximate numbers). *Why:* the checks are the first answers to the outline's questions, and they catch drift when the data refreshes.
- **R11. Draw with display geometry, compute with analysis geometry.** Shoreline-clipped display layers are for drawing only; measures come from analysis tables.
- **R12. Name the method when you rerun an official test.** If an official rule is rerun on different data (OMB's commuting rule on LODES instead of ACS), the text says so. A county failing the rerun is not proof the official rule got it wrong.
- **R13. Prefer tract-level values to place values allocated from tracts.** Place figures built from tracts by population weight are rough where tracts split between places. If a place figure prints, show its quality flag in the check table. *Why:* Albany v1's Roessleville job count rests on that allocation.
- **R32. Read model outputs on the raw scale before naming or interpreting them.** Cluster centroids and scores are often standardized and polarity-flipped (higher = better, so a negative poverty centroid means *high* poverty). Profile each cluster on raw inputs (medians of the actual rates) before trusting or printing its name. *Why:* Phase 7's naming review read flipped values as raw. "Mixed-Income Middle Neighborhoods" turned out to be the lowest-poverty type nationally (6.1%, $104k median income), and "Established Residential" is rural (147 people per sq mi).
- **R33. Know the source's quirks before claiming from it.** Write the caveat into the exploration notebook beside the data. For example, LODES OD links home to the employer's *reported* establishment, so flows past ~75 miles are mostly remote work and multi-site reporting, not commutes. Test the obvious explanation before printing it: Albany's long-distance flows were 74–90% private, so "state jobs reported at Albany" was wrong.
- **R34. Check the universe a measure counts before quoting it.** Know whether a count covers all jobs or private jobs only, all workers or primary jobs, households or people. Reconcile it against a second source when one exists. *Why:* the warehouse's LODES WAC/RAC `jobs_total` is **private jobs only** (JT02; `jobs_all_total` is all jobs), and Q2's job centers and Q6's place jobs use it. For Albany that drops state government, and Albany city's jobs read 72k instead of the 132k that place-level OD shows. A cross-check between two sources caught it, and neither analysis spec mentioned it.
- **R14. Hand-curated points need sources.** Landmarks and POI anchors go in `reference/<name>.csv` with a `keep` column and one source per row in a sources file. Stop for data review before drawing them. *Why:* each point is an editorial claim about a real place.

### Print gates

- **R15. Check gates in the notebook, not in prose.** A check cell for each gate that applies:

  | Gate | Rule today |
  |---|---|
  | Phase 7 zone type names | Not printable while `zone_type_name_status = 'draft_label_pending_review'` |
  | Frame composite scores | Held from print |
  | Peer lists and cluster names | Cleared for print |
  | Cluster *labels* (e.g. "Type 2: …") | Confirm before printing |
  | Thresholds behind a claim (e.g. Q6 integration) | Must be stated in the text |

  A draft that uses ungated content says so in its subtitle.
- **R16. Exploration-only forms never print.** Flow maps (X.12), Carto and reactive maps stay in exploration (E10).

### Drawing

- **R17. Use the house style.** Colors are theme tokens via `Theme.color`. Fonts: Inter, then Arial. Figures are 1456 px wide (2× Substack content width) at 200 dpi, and map height follows the geography's shape. Map projection: a state plane or Lambert fitted to the area.
- **R18. Settings cells own everything the reader sees.** Labels, colors, label positions (`(lon, lat)` for map anchors, points for offsets), cut lists, metric lists. Drawing functions take these as arguments. *Why:* review edits become one-line changes, and Dan can make them himself.
- **R19. Helpers live at the end as `@app.function`.** Copy-adapt from the reference notebook rather than importing across issues. Within a metro, a helper a second article uses moves to `<metro>_common.py`; no article imports from another article's notebook. Promote a helper to the Visual Library when a second piece reuses it unchanged.
- **R20. Title states the claim, subtitle what's shown, source line the data and its caveats.** Vintages go in the source line (ACS 2020–24, LODES 2023, OMB 2023).
- **R21. Look at every PNG before reporting.** Read the image and fix overlapping labels, clipped titles and lines crossing values. *Why:* Albany v1 had label collisions on two maps and a mathtext bug (two `$` in one string) that only showed in the image.
- **R22. Escape `$` in matplotlib text** (`\$`). Two dollar signs in one string start math mode.

### Review and export

- **R23. Drafts save on every run under stable names** without version suffixes, so embeds in the article draft survive revisions.
- **R24. Revisions go beside the original.** v2 cells sit next to v1 until Dan cuts v1.
- **R25. Dated reviews, locked decisions.** See Phase 3.
- **R26. Finals only after sign-off.** `save(fig, name, draft=False)` writes PNG and SVG to `output/`.
- **R27. The agent doesn't edit the article.** Text fixes go to Dan as a checklist with the line, the issue and a suggested wording.

### Notebook mechanics

- **R28. marimo hygiene.** Names are unique across cells, and cell-local names start with `_`. Run `marimo check` and a full headless run before reporting. Editing a notebook Dan has open causes "Cell already exists", so ask him to reopen it after edits.
- **R29. Environment.** `.venv-marimo`, with `DB_PATH` from `.Renviron` (`connect_duckdb()` resolves it). Read-only connections.

---

## Build plan template

```markdown
# <Piece>: Visuals Build Plan

**Status:** Active
**Updated:** YYYY-MM-DD

Outline: <link>. Rules: <link to this doc>. Notebook: <link>.

## Handoff: where things stand
<one paragraph: what exists, what's next, what's waiting on Dan>

## Question sets
One per outline question: the question, the candidate views (table / map / chart, with
data), status (planned, explored, read written), and the draft reads once explored.

## Exhibits
Filled in after the Phase 2 gate: the view chosen for each claim.
| # | Exhibit | Question set | Claim (draft title) | Form | Exhibit Bank | Status |

## Locked decisions
| Decision | Choice | Who, date |

## Open decisions
- [ ] <decision>: options, recommendation

## Findings
<what the Phase 0 probe found: confirmations, corrections to the outline, new data>

## Print gates
<each gate that applies and its current state>

## <Exhibit name>   (one section per exhibit)
Claim. Form. Data (reused queries, new queries). Gates. Settings.
- [ ] task list

## Build order

## Review, YYYY-MM-DD   (appended per round)
```

## Notebook skeleton

```
app.setup        imports, paths, area code, CRS, export size, Theme, fonts
Title            what the notebook builds, links to outline and plan
Shared setup     connection, load_<area>_layers()
Per section:
  md cell        the section's questions and caveats
  data cell      queries, check table (asserts on hard facts)
  settings cell  labels, colors, positions, cut lists
  draw cell      new_map/figure, draw_*, add_text, save
Helpers          @app.function: color, run_sql, to_geo, layer loaders,
                 new_map, draw_*, add_text, save
```

## Reporting back to Dan

After each build step, report:
1. What was built and where (file links).
2. Check results, and any outline number that didn't hold.
3. Findings the outline doesn't have yet.
4. Open decisions, each with a recommendation.
5. What wasn't done or verified.

Don't paste the numbers the notebook already shows unless they change the argument.
