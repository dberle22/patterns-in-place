# Intelligence Framework Engine

Purpose:

- provide reusable identity-layer outputs for `Position` analyses
- document the current Intelligence Framework query surfaces
- define the narrow downstream contract before we build consumer notebooks

## What The Framework Is

The Intelligence Framework is the national metro classification and comparison
system that sits underneath `Act 1` identity work and parts of `Act 3` and
`Act 4`.

It produces a repeatable set of outputs across three frames:

- `Character`
- `Livability`
- `Opportunity`

And one combined layer:

- `Cross-Frame`

Those outputs answer four recurring questions:

- what kind of place is this metro?
- how does it rank inside each frame?
- what other metros are most similar to it?
- where do the three frame stories agree versus conflict?

The long-form methodological reference still lives in
`exploration/intelligence_framework/docs/intelligence_framework_overview.md`.
This folder translates that work into the smaller downstream contract the
Metro Deep Dive program should actually read.

## What Is Already Materialized

The current promoted framework marts live in DuckDB schema
`mart_intelligence`.

CBSA-grain tables:

- `intelligence_character`
- `intelligence_livability`
- `intelligence_opportunity`
- `intelligence_cross_frame`

Spatial tables:

- `intelligence_zones`
- `intelligence_zones_zcta`

Current live state reviewed through `2026-09-08`:

- each CBSA-grain table has `396` rows for `396` distinct CBSAs
- the current promoted peer surface is top `10` peers per table
- cross-frame divergence fields are promoted into DuckDB
- Phase 7 tract and ZCTA outputs are promoted into DuckDB
- the separate Time-Series engine now owns four versioned trajectory tables in
  `mart_intelligence`; legacy Phase 6 files remain comparison evidence only

## What Downstream Analyses Should Read

For the first MDD consumers, use the framework this way:

- `Profile` reads `intelligence_character`, `intelligence_livability`,
  `intelligence_opportunity`, and `intelligence_cross_frame`
- `Peers` reads the frame tables plus `intelligence_cross_frame`
- `Trajectory` reads the four canonical `intelligence_trajectory_*` tables
  governed by the Time-Series engine
- `Candidate Scan` combines current cross-frame fields with those Time-Series
  outputs; its ranking stays analysis-local
- `Internal Structure` reads `intelligence_zones` and
  `intelligence_zones_zcta`

## First-Class Query Surfaces

We do not want to document all `150` to `190` columns per table as equally
important. The first downstream contract is a curated subset:

- `labels`: frame cluster labels, combined cluster, frame leaders and laggards
- `percentiles`: frame percentile ranks and cross-frame percentile rank
- `fingerprint topics and subjects`: selected topic and subject scores for
  Act 1 profile work
- `peers`: top-10 peer names, codes, and cosine similarities
- `divergence context`: overlap and disagreement fields from Phase 5
- `zones`: Phase 7 tract and ZCTA outputs for Internal Structure

## What Is Not In The Contract Yet

- a locked `fingerprint` mart does not exist yet; current fingerprint queries
  are curated joins across the frame tables
- the Phase 7 consumer contract should document the current model build and
  input/boundary vintages before Internal Structure is locked; new table
  fields are needed only if the existing build evidence cannot supply them
- the legacy Phase 6 candidate list is intentionally not promoted; Candidate
  Scan uses it only as a port-comparison baseline
- the cross-frame table still mixes clean aliases with many source-prefixed
  fields like `character__...`, `livability__...`, and `opportunity__...`

## Starter Queries

Use the SQL files in `queries/` as the first notebook-ready access layer:

- `profile_labels.sql`
- `profile_core_kpis.sql`
- `profile_peers.sql`
- `profile_cross_frame_divergence.sql`
- `zones_cbsa_summary.sql`
