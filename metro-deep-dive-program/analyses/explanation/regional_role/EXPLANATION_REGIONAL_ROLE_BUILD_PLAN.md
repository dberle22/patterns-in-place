# Explanation Regional Role Build Plan

**Status:** Epic 1 not started

## How this plan works

**Epic 1 is an audit, and it comes first.** Epics 2–5 are written from
expectation rather than evidence and should be rewritten once the audit reports.

## Epic 1 — Audit the Region Inputs

- [ ] Confirm the state/region/division crosswalk and what fields it carries.
- [ ] Confirm CBSA-to-state and CBSA-to-county relationships and their vintages.
- [ ] Determine whether any adjacency or distance relation exists between
  counties or CBSAs, or whether lens 3 must derive it from geometry.
- [ ] Confirm IRS migration flow grain, years, and disclosure suppression rules.
- [ ] Confirm LODES WAC/RAC grain and vintage.
- [ ] **Confirm plainly whether any LODES OD table exists.** If not, record it as
  a blocking gap for commute-shed content and label that content deferred.
- [ ] Determine what industry mix and specialization measures already exist and
  whether Position or Benchmarking already computes them.
- [ ] Determine what megaregion sourcing would require, and recommend whether it
  belongs in v0.
- [ ] Review Position Profile, Peers, and Trajectory outputs for what Regional
  Role can consume rather than rebuild.

**Done when:** each of the four lenses is either confirmed buildable with named
sources, or recorded as blocked with the reason. The spec is rewritten against
those findings.

Record the audit in `EXPLANATION_REGIONAL_ROLE_AUDIT.md`.

## Epic 2 — Build the Region Lenses

*Provisional. Rewrite after Epic 1.*

- [ ] Implement the census division lens.
- [ ] Implement the state lens.
- [ ] Implement the nearby counties/metros lens, including the border-distance
  construction rule.
- [ ] Decide megaregions in or out; if in, source and label the layer.
- [ ] Produce a lens comparison surface showing which geographies each lens
  selects for one market.

**Done when:** one market can be read through each lens, and the differences
between lenses are visible rather than theoretical.

## Epic 3 — Establish the Market's Role

*Provisional. Rewrite after Epic 1.*

- [ ] Build the industry role comparison against each lens.
- [ ] Build the jobs/workers balance.
- [ ] Build the IRS migration exchange summary.
- [ ] Assemble the evidence needed for a market-role hypothesis.

**Done when:** the analysis says something about what the market does within its
region, not only where it ranks.

## Epic 4 — Build the Comparison Surface

*Provisional. Rewrite after Epic 1.*

- [ ] Build the regional comparison table and map with selectable KPIs.
- [ ] Build the nearby metro comparison as an extension of the benchmarks.
- [ ] Add the infrastructure context map.
- [ ] Show how the industry-role read changes across lenses.

**Done when:** an analyst can see both the market's position and how that
position depends on the boundary chosen.

## Epic 5 — Review and Split the Notebooks

*Provisional. Rewrite after Epic 1.*

- [ ] Test on a second market with a different regional character.
- [ ] Decide whether the setup/run notebook split is warranted.
- [ ] Record what the geography engine should eventually own.
- [ ] Record what Q6 can reuse.

**Done when:** the workbench is reusable across markets and its long-term
geography ownership is written down.

## What not to do

- do not present WAC/RAC balance as commuting flows
- do not block the whole analysis on megaregions
- do not rebuild Position's identity or peer logic
- do not let the lens comparison crowd out the role and comparison work
