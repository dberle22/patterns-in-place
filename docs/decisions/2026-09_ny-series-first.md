# First Metro Deep Dive work: the New York series

**Date:** 2026-09 (about 2026-09-22)
**Supersedes:** [First Metro Deep Dive market: Richmond](2026-07_first-market-richmond.md)
**Source:** Dan's in-progress series overview, "NY State of Mind (Series)" (not yet in the repo)

## Decision

The first published Metro Deep Dive work is a series on New York State, working title *NY State of Mind*. Its work lives in `metro-deep-dive-program/issues/new_york/`. The scope is still being defined; the current outline has four parts:

| Part | Planned pieces |
|---|---|
| **State primer** | Overview, then one piece per section: what New York is (its regions), infrastructure, who lives here, the economy, where it's headed |
| **Regional deep dives** | Hudson Valley, Southern Tier, North Country |
| **Metro deep dives** | Syracuse, Albany, Utica, Ithaca, Binghamton; New York City as the finale |
| **Rankings** | Ranked comparisons of New York CBSAs, e.g. job centers, population growth, economic indicators, human capital, underrated metros, downtowns |

Richmond is paused and moves later. Its work proved the program's engines and analyses, but it isn't being written up yet.

## Why

New York is Dan's home: the place Dan grew up, studied, lives and travels. The series explores the whole state, not just the city, through data. The goal is to learn something new about the place rather than to be exhaustive.

## What it means

- **Same machinery, new market set.** Metro and regional pieces follow the program's Position and Explanation analyses (profile, trajectory, internal structure, peers, growth, housing, job centers, metro construction, daily amenities, regional role). Primer sections pull in Thematic analyses: A2 building lowers prices, A7 who is squeezed and A4 remote work in infrastructure and housing; A6 specialization and A10 polarization in the economy; A3 moving toward harm and A8 life expectancy in where it's headed.
- **Data decisions for the series:**
    1. Start from New York's 10 official regional economic development council regions; discuss colloquial definitions (upstate and downstate) alongside.
    2. Show all metro and micro CBSAs, but focus on metros.
    3. Use cross-state data for a CBSA that crosses the state line, so the NYC metro isn't cut off.
    4. Use the 2023 vintage as the standard.
- **Format:** still long-form Substack (see [the format decision](2026-06_deep-dive-format.md)), but as a multi-part series rather than one market serialized act by act.
- **Tools:** marimo notebooks, the Patterns in Place DuckDB, the visual library, and interactive Carto maps.
- **Citations:** pieces cite the public CBSA panel where its data is used.
