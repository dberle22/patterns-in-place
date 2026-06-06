# Topic: Vacancy Rates
**Last updated:** 2026-05-13  
**Status:** In progress — data explored, insights planned, no posts built yet  
**Data source:** ACS via `gold.housing_core_wide` | geo levels: us, state, region, cbsa  
**Years available:** 2012–2024

---

## The Story

The US housing market is at its tightest point in over a decade. The national vacancy rate has fallen every year since 2019 — from 12.1% to 10.1% in 2024 — with no region spared. The West was already the tightest in 2019 and has compressed further. The South, historically the most vacant, has seen the steepest absolute drop. And at the state level, the split between land-constrained coastal markets and vacation/rural states is striking.

This is a 3–4 post series. Each insight stands alone but reinforces the same underlying thesis: **the US is running out of housing slack**.

---

## Planned Insights

| # | Folder | Angle | Chart | Platform | Status |
|---|--------|-------|-------|----------|--------|
| 1 | `national_trend/` | US vacancy has fallen every year since 2019 | Line chart | X + Substack | Not started |
| 2 | `state_map/` | Which states have the tightest (and loosest) markets — and who compressed the most | Choropleth: 2024 rate + change from 2019 | Substack | Not started |
| 3 | `metro_rankings/` | The 20 tightest major metros in 2024 (pop > 250k filter) | Horizontal bar chart | X + Substack | Not started |
| 4 | `regional_trends/` | All four regions declining — but the West has been tight for years | Multi-line trend chart | Substack | Not started |

**Suggested publish order:** 1 → 3 → 2 → 4  
Start with the national hook, follow with the concrete metro ranking (most shareable), then zoom out to the state map and regional breakdown for the deeper-read audience.

---

## Key Numbers

**National (US geo level)**
- 2019: 12.1% | 2024: 10.1% | Change: -2.0pp over 5 years
- Every year from 2019–2024 is lower than the year before

**Tightest states (2024)**
- Connecticut 7.0% | Washington 7.3% | New Jersey 7.5% | California 7.5% | Oregon 7.5%
- Pattern: land-constrained coastal states dominate

**Loosest states (2024)**
- Maine 20.6% | Vermont 19.4% | Alaska 17.6% | West Virginia 15.4% | Florida 14.7%
- Pattern: vacation/second-home markets + rural/declining states

**Biggest compression (2019 → 2024, pp change)**
- Wyoming -4.7pp | New Mexico -4.3pp | Maine -4.0pp | Arizona -3.8pp | Florida -3.5pp
- Sun Belt and Mountain West doing most of the tightening

**Regional (2024)**
- West: 8.5% | Midwest: 9.4% | Northeast: 9.6% | South: 11.7%
- All regions declined steadily 2019–2024; South compressed most in absolute terms (-2.3pp)

---

## Data Notes

- CBSA-level averages are unweighted and higher than the US-geo figure — use the `us` geo level for the national headline number
- Highest-vacancy CBSAs are vacation markets (Nantucket, Vineyard Haven, Breckenridge) — filter metro rankings to pop > 250k to exclude
- `vacancy_rate` is stored as a decimal (0.07 = 7%) — multiply by 100 for display
- 2024 data is available and is the most current — use as primary year throughout
