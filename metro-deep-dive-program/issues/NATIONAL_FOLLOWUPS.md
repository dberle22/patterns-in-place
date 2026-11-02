# National Follow-ups

**Status:** Active
**Updated:** 2026-10-26

Questions and methods that come up in one market's issue work but are national in scope. Each one should be answered once, for every metro, and then reused in later markets. Add a row when issue work raises one, and link back to where it came up. When a row is answered, link the result and move it to Done.

## Open

| # | Question | Method and data | Raised in | Status |
|---|---|---|---|---|
| N1 | **Cluster names.** Do the 7 cross-frame cluster names describe their members? "High-Amenity Knowledge Civics" has 78 members, from Albany and Buffalo to San Diego, Boulder and Hawaii. | Profile every cluster on raw values (R32), propose names, re-promote. A national review, not per CBSA. | Albany Lens 1, Q4 (2026-10-24) | Future. Until then, Lens articles describe peers without naming the cluster |
| N2 | **Are peers regional or state-bound?** | Share of each metro's top-10 peers in its own state and region. First pass (2026-10-23): FL 70%, CA 65%, TX 54%, NY 43%, PA 32%, IN 3% (chance is about 3%). Check whether state-level or state-shaped inputs drive it. | Albany Lens 1, Q4 | First pass done; input check to do |
| N3 | **Regional shadow and megaregions.** Is a metro's profile shaped by a larger neighbor (Worcester and Providence next to Boston, Milwaukee next to Chicago)? Which megaregion is it in? | Distance to, and size of, the nearest larger metro, against peer sets. Megaregion assignment (America 2050's 11 megaregions) needs an external data pull with a data review (R14). | Albany Lens 1, Q4 | Idea; low priority (Dan, 2026-10-26: keep it, wait and see whether it fits) |
| N4 | **How far does each metro's labor market reach?** | 2023 LODES county OD (all 50 states and DC): per metro, the share of its jobs held by residents of outside counties, and the number of outside counties sending 5%, 10% or 25%+ of their resident jobs (counties that would pass OMB's 25% rule on this data). Cap or flag flows past 75 miles (R33). | Albany Lens 1, Q1e | Idea; NY-only version in Albany Q1e |
| N5 | **Second city.** Which metro is each state's second city by population, by GDP, and per person? | Rank metros within each state on size and per-capita measures. For NY: Buffalo is second by population and GDP; Albany leads Upstate per person. | Albany Lens 1, Q4 | Series thread; raise in Albany, revisit in each market |
| N6 | **At a glance, standardized.** One opening profile for every metro piece. | A fixed metric set with US, state and region ranks, plus a region aggregate built from counties (`upstate_aggregate`). Set chosen 2026-10-24: population, 10-yr growth, median household income, per capita income, median home value, bachelor's share, median age, non-white share. Print form still open (cards or a percentile dot plot). | Albany Lens 1 | Set chosen; prototype in Albany Q4e |
| N7 | **Does a large public sector steady a metro's economy?** | Job and output change through 2008–09 and 2020 by metro, against the public share of jobs. | Albany Lens 1 (Lens 4 topic) | Idea |
| N8 | **Where does a metro's growth come from?** | IRS county-to-county migration (`silver.irs_migration_flows`): in-movers by origin (same state, other states), and natural increase where available. | Albany Lens 1, Q4 | Albany done (Q4i, 2026-10-26). Unblocked: IRS direction fixed 2026-10-26 (foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md) |
| N9 | **Who out-commutes?** Are out-commuters on the metro's periphery? | Tract OD (commute-sheds engine): each tract's share of resident jobs outside the metro, split at 75 miles, against distance to the nearest job center. | Albany Lens 1, Q1c | Idea; Albany is the first case (Lens 2) |
| N10 | **Shared interactive exploration helpers.** | `explore_map`, `explore_points`, `map_overlays`, the picker charts and the migration helpers, now in `issues/ny_state/albany/albany_explore.py` (imported by the Lens 1 and Lens 2 exploration notebooks). Promote to a shared module when a second piece reuses them unchanged (R19). | Albany Lens 1 | Built in Albany (2026-10-24); moved to an Albany module (2026-10-26) |
| N11 | **IRS migration undercounts suppressed flows.** `silver.irs_migration_flows` and `silver.irs_migration_summary` sum county *pairs*; IRS suppresses pairs under 20 returns, which are mostly moves to and from other states. Albany metro, 2018–22: net +1,478 a year on pairs vs −1,491 on the IRS county totals (in from other states 1,760 vs 10,640). Every metro's `irs_net_migration_rate` and `irs_net_agi` (Phase 5 peer input) carry this bias. | Stage the IRS "Total Migration-US / Same State / Different State" rows (`get_irs_migration.R` already parses them, unfinished) and build metro and county nets from them; rerun the frames that use the IRS metrics and check peers. Albany works around it with `issues/ny_state/albany/data/irs_county_totals_2018_2022.csv`. | Albany Lens 1, Q4i (2026-10-27) | Open: for Dan to schedule (foundations) |

## Done

None yet.
