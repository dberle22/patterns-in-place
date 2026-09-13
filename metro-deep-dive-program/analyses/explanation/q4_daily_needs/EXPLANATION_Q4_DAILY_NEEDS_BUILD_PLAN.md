# Explanation Q4 — Daily-Needs Access Build Plan

**Status:** Epic 1 not started

**Depends on Q2 (E3)** for the access method. The basket work in Epic 2 can
proceed in parallel with Q2.

## How this plan works

**Epic 1 is an audit, and it comes first.** Epics 2–5 are written from
expectation rather than evidence and should be rewritten once the audit reports.

## Epic 1 — Audit the POI Surface

- [ ] Confirm which markets have governed POI runs and whether both are
  complete.
- [ ] Confirm the POI geography assignment surface: grains, assignment method,
  status values, and how unassigned or ambiguous records behave.
- [ ] Quantify taxonomy coverage: what share of places carry a usable primary
  category, and what share are null or unmapped.
- [ ] Review actual category frequencies in both markets before choosing any
  basket member.
- [ ] Determine what the taxonomy hierarchy profile and its mapping status
  provide, and whether the analysis can rely on them.
- [ ] Confirm tract population denominators for normalization.
- [ ] Read Q2's access definition and record exactly which parts Q4 will adopt
  unchanged and which it must vary, with reasons.
- [ ] State plainly whether the POI data can support a defensible basket, or
  whether coverage forces a narrower question.

**Done when:** we know what the POI data can honestly support, and the basket is
chosen from observed coverage rather than from an idealized list. The spec is
rewritten against those findings.

Record the audit in `EXPLANATION_Q4_AUDIT.md`.

## Epic 2 — Define the Basket

*Provisional. Rewrite after Epic 1.*

- [ ] Choose a narrow, defensible set of daily-needs categories.
- [ ] Define the multi-category sufficiency rule.
- [ ] Define coverage rules and the `unavailable` threshold.
- [ ] Test the basket against both pilot markets for category presence.

**Done when:** the basket is narrow, justified by observed coverage, and
survives both markets.

## Epic 3 — Apply the Access Method

*Provisional. Rewrite after Epic 1.*

- [ ] Build POI clusters as the center input.
- [ ] Apply Q2's reach measure to those centers.
- [ ] Build tract access components.
- [ ] Build the selected-market access map and distribution.
- [ ] Record where the shared method fit poorly and why.

**Done when:** the access read exists for both pilot markets, and any friction
with the shared method is documented rather than silently patched.

## Epic 4 — Two-Market Review

*Provisional. Rewrite after Epic 1.*

- [ ] Compare results across Richmond and Jacksonville.
- [ ] Test urban-form sensitivity.
- [ ] Test sensitivity to basket and reach choices.
- [ ] Decide whether the method is sound enough to scale.
- [ ] Report any findings about the shared access definition back to Q2.

**Done when:** we have a defensible go/no-go on national scale-out, and Q2 knows
what Q4 learned about its method.

## Epic 5 — National Scale-Out

*Provisional. Rewrite after Epic 1. Gated on Epic 4 passing.*

- [ ] Acquire and process broader POI coverage.
- [ ] Re-run coverage and mapping QA at national scale.
- [ ] Build the national comparison.

**Done when:** national coverage is real and its gaps are reported.

## What not to do

- do not treat POI counts as access
- do not scale nationally before the two-market review passes
- do not rewrite POI classification locally
- do not silently diverge from Q2's access definition
