# Explanation Corridor Opportunity Read Build Plan

**Status:** Not startable yet — depends on Q2, Q3, and Q4 output

This analysis synthesizes upstream results. Starting it before those results
exist would mean inventing the thing it is supposed to summarize.

## How this plan works

**Epic 1 is an audit, and it comes first** — but unlike the other analyses,
Epic 1 here cannot run until Q2, Q3, and Q4 have produced real output. Epics 2–4
are written from expectation and should be rewritten once the audit reports.

## Epic 0 — Wait for Upstream

- [ ] Q2 (E3) has produced access and gradient surfaces.
- [ ] Q4 (E5) has produced POI clusters for at least one market.
- [ ] Q3 (E6) has produced a growth-location classification.

**Done when:** there is something real to synthesize.

## Epic 1 — Audit What the Upstream Analyses Actually Produced

- [ ] Inventory what Q2, Q3, and Q4 actually output, at what grain, for which
  markets.
- [ ] Determine whether any of those outputs are genuinely corridor-shaped, or
  whether they are tract-grain surfaces that only look corridor-like on a map.
- [ ] Test candidate corridor-identification approaches against real output:
  contiguous access runs, POI cluster chains, growth corridors.
- [ ] Determine whether a reconciliation rule is needed when approaches disagree.
- [ ] Review the Jacksonville and Richmond Corridor Intelligence artifacts as
  method reference: what did the paused engine do well, and what should not be
  repeated.
- [ ] State plainly whether corridors can be identified from upstream output, or
  whether this analysis needs a different framing.

**Done when:** we know whether the premise holds — that corridors emerge
organically from the access work — and the spec is rewritten against real
evidence.

Record the audit in `EXPLANATION_CORRIDOR_OPPORTUNITY_AUDIT.md`.

**If the premise does not hold, say so.** It is a legitimate finding that the
access work does not produce corridors, and it should be reported rather than
forced.

## Epic 2 — Identify Corridors

*Provisional. Rewrite after Epic 1.*

- [ ] Implement the chosen corridor-identification approach.
- [ ] Produce a corridor inventory for one market.
- [ ] Show the evidence that produced each corridor.

**Done when:** corridors are identified reproducibly, with visible lineage back
to upstream evidence.

## Epic 3 — Build the Synthesis

*Provisional. Rewrite after Epic 1.*

- [ ] Build the comparison matrix across the three evidence families.
- [ ] Build the selected-corridor profile and map.
- [ ] Build the evidence-and-caveat table.
- [ ] Draft one-sentence thesis candidates.

**Done when:** an analyst can compare corridors and see why each one surfaced.

## Epic 4 — Review

*Provisional. Rewrite after Epic 1.*

- [ ] Confirm the no-opportunity result works and is not cosmetic.
- [ ] Confirm no universal score has crept in.
- [ ] Define the handoff to the issue layer.

**Done when:** the read is honest about weak cases and hands off cleanly.

## What not to do

- do not start before upstream output exists
- do not create canonical corridor boundaries
- do not revive Corridor Intelligence as a dependency
- do not build an Investment Score
- do not force corridors out of evidence that does not support them
