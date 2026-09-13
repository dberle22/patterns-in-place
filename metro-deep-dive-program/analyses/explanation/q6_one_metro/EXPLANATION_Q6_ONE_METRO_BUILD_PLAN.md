# Explanation Q6 — One Metro? Build Plan

**Status:** Epic 1 not started

**Depends on Q2 (E3)** for the access method and on Regional Role (E4) for
regional context. The integration half additionally depends on a LODES OD source
that does not appear to exist yet.

## How this plan works

**Epic 1 is an audit, and it comes first.** Epics 2–5 are written from
expectation rather than evidence and should be rewritten once the audit reports.

## Epic 1 — Audit Flow Data and Center Inputs

- [ ] **Confirm plainly whether any LODES OD or equivalent flow matrix exists.**
  This determines whether half the analysis is buildable at all.
- [ ] If OD does not exist, scope what ingesting it would require and record that
  as a separate decision, not a silent blocker.
- [ ] Confirm LODES WAC/RAC grain and vintage for the structural half.
- [ ] Confirm CBSA-to-county relationships and whether central/outlying status is
  already flagged.
- [ ] Determine what candidate anchor cities or downtowns can be derived from,
  and whether a Place-grain source is needed.
- [ ] Read Q2's access definition and record what Q6 adopts and what it varies.
- [ ] Review what Regional Role produced and what Q6 can reuse.
- [ ] State plainly which half of this question is buildable now.

**Done when:** the buildable half is clearly separated from the blocked half,
with the OD gap recorded as a named dependency. The spec is rewritten against
those findings.

Record the audit in `EXPLANATION_Q6_AUDIT.md`.

## Epic 2 — Build the Structural Read

*Provisional. Rewrite after Epic 1.*

- [ ] Build the county role table from WAC/RAC and industry mix.
- [ ] Build the employment-center distribution.
- [ ] Build the industry similarity comparison.
- [ ] Build the core/outlying comparison.
- [ ] Label all of it as structural evidence, not integration.

**Done when:** the structural evidence stands on its own without implying
commuting claims.

## Epic 3 — Build the Anchor-City Read

*Provisional. Rewrite after Epic 1.*

- [ ] Derive candidate anchor cities and downtowns.
- [ ] Apply Q2's access method with those as the center input.
- [ ] Build the candidate anchor-city inventory with access surfaces.
- [ ] Read job corridors and amenity clusters at metro scale.
- [ ] Assess whether the metro resolves into one center or several.

**Done when:** the polycentricity question has an answer grounded in the shared
access method, and any friction with that method is documented.

## Epic 4 — Add Integration When OD Exists

*Provisional. Blocked until OD is available.*

- [ ] Build the county integration matrix from OD shares.
- [ ] Define the integration rule and its thresholds.
- [ ] Add the sensitivity table.
- [ ] Produce the explicit integration result.

**Done when:** integration claims rest on flows. Until then this epic stays
unstarted and the analysis returns `insufficient flow data`.

## Epic 5 — Review

*Provisional. Rewrite after Epic 1.*

- [ ] Test on a metro known to be polycentric and one known to be monocentric.
- [ ] Report findings about the shared access method back to Q2.
- [ ] Record what the A5 "How many downtowns?" theme can reuse.

**Done when:** the method distinguishes real cases and its reusable parts are
documented.

## What not to do

- do not claim integration without OD
- do not blend the structural and anchor-city halves into one weaker score
- do not substitute a proxy for flows and call it integration
- do not grow a second 15-minute definition
