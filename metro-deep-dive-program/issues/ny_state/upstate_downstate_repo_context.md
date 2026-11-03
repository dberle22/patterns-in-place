# Upstate, Downstate: Repo Context

**Status:** Active
**Updated:** 2026-11-02

The entry doc for Claude Code sessions on the New York series. Upstate, Downstate is a Patterns in Place writing series on New York State, published on Substack. This file says where things are and which rules apply. It holds no questions, exhibits or article plans of its own.

## Current first task

**The growth ranking data pass.** The plan is in the vault at `rankings_and_analyses/growth/Growth Ranking.md` (K.2, K.6, S6.1). Build it in [`rankings_and_analyses/growth/`](README.md#adding-a-piece).

What comes after it is in the Article Sequence and the Next up callout in the Series Overview.

## Open issues

Check this list before planning a piece. Remove a row when its issue is fixed.

| Issue | What it affects | What to do | Details |
|---|---|---|---|
| **IRS migration undercount (N11)** | `irs_net_migration_rate`, `irs_net_agi` and anything summing IRS county pairs. Pairs under 20 returns are suppressed, so net migration can have the wrong sign: Albany's metro shows +1,478 a year on pairs and -1,491 on IRS county totals | Don't print net migration from the warehouse. Use [`irs_county_totals_2018_2022.csv`](metro_deep_dives/albany/data/irs_county_totals_2018_2022.csv), which covers every US county for 2018 to 2022. `irs_net_agi` is also a peer input, and the effect on peer lists (K.6) hasn't been checked. The warehouse fix is for Dan to schedule | [N11](../NATIONAL_FOLLOWUPS.md) |
| **POI filter not decided** | Any POI count compared across markets. Raw counts overstate some markets, most of all Rochester, Corning and the non-CBSA counties | Do the review before the first cross-market POI comparison. Tables keep every record, so filtering happens in the review's chosen place | [Candidate filter](NY_STATEWIDE_DATA_BUILD_PLAN.md) |
| **Notebooks that don't run** | Internal Structure Parts 1 and 2 and the Infrastructure Explorer crash as committed, for every market | Fix them when a piece first needs them. Until then, query the marts and Parquet outputs directly | [Notebook fixes](NY_STATEWIDE_DATA_BUILD_PLAN.md#notebook-fixes) |
| **Visuals notebooks not rerun since the restructure** | `ALBANY_LENS1_VISUALS.py` and `WHAT_NY_IS_VISUALS.py`. Their paths were checked but they weren't run, because they rewrite draft PNGs | Run each one the next time its piece is touched, and check the PNG changes | |
| **Engine work not done for NY** | Q4 market wiring, Corridor inputs, the Place overlap and Q6 fix, ports, and 6 unmapped POI categories | Pick up when a piece needs them | [Deferred](NY_STATEWIDE_DATA_BUILD_PLAN.md#deferred) |

## Who owns what

| Owner | Holds | How to treat it |
|---|---|---|
| **Vault** | Series Overview, Approach, Claude Working Guide, overview docs, outlines, drafts and published text | The source for writing and planning. Read it for context |
| **Repo** | Question Bank, Exhibit Bank, Program Glossary, notebooks, exhibit PNGs | The source for data work. When a build lands, update readiness and build status in the banks in the same change |
| **claude.ai Project** | A mirror | Refreshed on purpose, never edited directly |

## Where things are

**In the repo:**
- [Question Bank](question_bank.md): question IDs, readiness, and how to use the analysis notebooks
- [Exhibit Bank](exhibit_bank.md): exhibit IDs, build status and specs
- [Program Glossary](program_glossary.md): Metro Deep Dive terms
- [Folder structure](README.md): what goes where, naming, and how repo folders mirror the vault
- [Visuals build rules](../VISUALS_BUILD_RULES.md): how to go from an outline to print visuals
- [NY statewide data build](NY_STATEWIDE_DATA_BUILD_PLAN.md): what POI and OSM data exists for New York, how it was run, and what was deferred
- [National followups](../NATIONAL_FOLLOWUPS.md): data issues found during NY work that affect every market

**In the vault**, at the path in the gitignored `CLAUDE.local.md` or `AGENTS.local.md` (ask Dan if they're missing):
- `Approach.md`: the D and E rules, the source for everything cited below
- `Upstate, Downstate - Series Overview.md`: sequence, status, decisions, open decisions
- `Claude Working Guide.md`: how sessions run, including drafting and review

## Working rules

- **Start from a question ID, not a chart idea** (E5).
- **Check readiness first.** Don't plan around gated data without saying so.
- **Reuse before building.** Check the Exhibit Bank. An exhibit earns a spec the second time it is used, not the first.
- **Confirm glossary terms marked (inferred)** before relying on them.
- **Keep open decisions in the Series Overview,** not scattered across docs.
- **No em or en dashes** in any doc text or suggested text.
- **Snapshot a file before restructuring it,** into `_archive/<date>/` with the date in the file name.

Tools: Marimo notebooks (`.venv-marimo`), the Patterns in Place DuckDB warehouse, and the Visual Library. The root [README](../../../README.md) has the warehouse path.

## Data rules

Summaries only. `Approach.md` has the full text.

- **D1:** REDC regions first, vernacular second.
- **D2:** show metros and micros, lead with metros.
- **D3:** the state overview uses NY only data; metro pieces may cross state lines.
- **D4:** 2023 vintage and 2023 CBSA delineations.
- **D5:** population growth uses ACS 5 year, 2010 to 2014 pooled against 2020 to 2024 pooled. The Series Intro benchmark used 2008 to 2012 vs 2020 to 2024, so the growth piece explains the difference in its methods or aligns the windows.

## Print rules

- **Cleared for print:** cluster labels, peer lists and neighborhood types.
- **Composite scores** are built within each analysis, not read from a production layer.
- **Frame composite scores** were updated on 2026-11-02. Their print clearance is open decision 15, so ask before printing one.
- **Carto and reactive maps** are exploration only (E10).

## Editorial pointers

Both rules are in `Approach.md`:

- **E15:** settle structure on a one page outline before drafting, with one line edit pass after that.
- **E16:** size the piece to the material. Formats are guidance, not rules.
