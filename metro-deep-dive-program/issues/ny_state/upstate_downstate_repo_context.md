# Upstate, Downstate: Repo Context

**Status:** Active
**Updated:** 2026-11-02

The entry doc for Claude Code sessions on the New York series. Upstate, Downstate is a Patterns in Place writing series on New York State, published on Substack. This file says where things are and which rules apply. It holds no questions, exhibits or article plans of its own.

## Current first task

**The growth ranking data pass.** The plan is in the vault at `rankings/growth/Growth Ranking.md` (K.2, K.6, S6.1). Build it in [`rankings_and_analyses/growth/`](README.md#adding-a-piece).

What comes after it is in the Article Sequence and the Next up callout in the Series Overview.

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
