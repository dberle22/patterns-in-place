# Explanation Q2 — Job-Center Method Record

**Status:** Initial Richmond review recorded; national candidate baseline
published.

**Purpose:** Store the reviewed job-center decision outside notebook state so
the analytical outcomes notebook can consume a stable, inspectable method. The
three V0 candidate versions are published nationally in `mart_explanation_q2`.

## Recommended V0 construction for review

This is a recommended baseline, not an adopted national rule.

1. **Core seed tract** — satisfies all three gates:
   - at least 2,500 2023 workplace jobs;
   - at least 1.0% of CBSA workplace jobs; and
   - at least 1.5 jobs per resident worker.
2. **One-hop extension tract** — shares a nonzero-length boundary with a core
   seed, passes the 2,500-job and 1.5 jobs-to-workers gates, and may miss the
   market-job-share gate.
3. **Candidate district** — a shared-edge connected component of core seeds and
   one-hop extensions. Components are evidence for review, not automatic zones.

The strict core-only and no-market-share constructions remain required
sensitivities. Job density remains contextual and is not a V0 center gate.

## Reviewed decision — Richmond, VA (`40060`)

- **Center construction selected for the initial outcomes read:**
  `recommended_core_one_hop`. It is a practical primary version, not a claim
  that one national rule is final for every CBSA.
- **Core seed parameters:** at least 2,500 jobs, 1.0% CBSA job share, and 1.5
  jobs per resident worker.
- **One-hop extension treatment:** retain one direct shared-edge neighbor that
  clears the job-floor and jobs-to-workers gates; never extend recursively.
- **Center representation and tract origin:** individual candidate-center tract
  centroids; the tract surface records the nearest candidate-center centroid.
- **Multiple-center treatment:** nearest candidate-center tract by Haversine
  distance; no district-level weighted centroid is used in V0.
- **Sensitivity cases retained:** `strict_core` and `no_share_sensitivity`.
- **Visible omissions or fragmentation:** the strict 1.0% share screen can
  exclude plausible attached and outlying centers. One-hop provides the main
  adjoining-tract check; no-share tests larger-market overshadowing.
- **Reviewer and date:** initial working decision from the Q2 method review,
  2026-09-19. Re-review before treating a different market's version as primary.

## Guardrails

- The absolute-job floor is a ratio safeguard, not a correction for tract size.
- Market job share is a core-seed signal, not a universal definition of every
  smaller or outlying center.
- Haversine distance from tract centroids is physical proximity only; it is not
  travel time, commuting behavior, or a 15-minute access result.
