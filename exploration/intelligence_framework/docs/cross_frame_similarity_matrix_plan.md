# Cross-Frame Similarity Matrix Plan

Brief revisit note for a possible future promotion of the full Phase 5 CBSA similarity matrix into `mart_intelligence`.

## Why this might matter

- The current Cross-Frame promotion is optimized for simple lookup and profile use.
- `mart_intelligence.intelligence_cross_frame` carries one static row per CBSA plus the widened published top-10 peer bundle.
- That is enough for profile panels and direct "most similar metros" questions, but it is awkward for threshold queries, graph-style peer exploration, and broader peer-neighborhood analysis.
- A long-form similarity table could become more valuable once Metro Deep Dive needs flexible peer discovery rather than only a fixed top-10 list.

## Current state

- Phase 5 currently publishes `cross_frame_phase5_similarity_top10.csv`.
- The current modeled universe is `396` CBSAs.
- The promoted Cross-Frame mart keeps the widened top-10 peer fields on the one-row-per-CBSA table.
- Downstream Area Explorer work currently only relies on the top peer bundle for the v1 contract.

## Feasibility snapshot

- A full directed no-self matrix at the current universe would be `396 x 395 = 156,420` rows.
- That is small enough for DuckDB and does not raise a meaningful storage concern.
- A minimal long-form artifact with `cbsa_code`, `peer_cbsa_code`, and `cosine_similarity` is expected to stay compact enough for routine product queries.
- The real question is product value, not compute cost.

## Recommendation for now

- Do not treat the full matrix as required platform work yet.
- If a near-term product only needs queryable peer sets, first promote the existing top-10 CSV as a separate long mart table.
- Revisit the full matrix when Metro Deep Dive or another downstream surface needs:
  - similarity-threshold queries
  - peer-network or peer-neighborhood analysis
  - pairwise rank lookup beyond the published top 10
  - reusable peer logic across multiple products

## Option A: Promote the existing top-10 CSV as a long mart table

This is the lightest useful next step.

- Source artifact: `exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/cross_frame_phase5_similarity_top10.csv`
- Proposed table: `mart_intelligence.intelligence_cross_frame_peers`
- Proposed grain: one row per `cbsa_code, peer_rank`
- Candidate columns:
  - `cbsa_code`
  - `cbsa_name`
  - `peer_rank`
  - `peer_cbsa_code`
  - `peer_cbsa_name`
  - `cosine_similarity`

Why this path is attractive:

- No change to the Phase 5 model output is required.
- The canonical published artifact already exists.
- Products can query peers as rows instead of unpacking wide `top10_peer_*` columns.
- This likely captures most of the practical value for Area Explorer and early Metro Deep Dive work.

## Option B: Materialize and promote the full matrix

This is the more flexible but slightly heavier path.

- Add a new canonical Phase 5 artifact such as `cross_frame_phase5_similarity_full.parquet`.
- Store it in long form rather than as a wide matrix.
- Proposed table: `mart_intelligence.intelligence_cross_frame_similarity`
- Proposed grain: one row per `cbsa_code, peer_cbsa_code`
- Candidate columns:
  - `cbsa_code`
  - `peer_cbsa_code`
  - `cosine_similarity`
  - `peer_rank`
  - optional `cbsa_name`
  - optional `peer_cbsa_name`

Open design choice:

- Directed matrix: keep both `A -> B` and `B -> A` for easy downstream querying.
- Undirected pair table: smaller and more normalized, but less convenient for product lookups.

Default recommendation:

- Keep the directed no-self long table because it matches how products are likely to query peers.

## Full end-to-end work plan

1. Add the canonical full-matrix Phase 5 artifact.
   Verify: rerun Phase 5 and confirm the output lands in `phase_5_cross_frame_integration/outputs/` with `156,420` directed no-self rows for the current universe.

2. Define the mart contract for the long similarity table.
   Verify: confirm the grain, decide whether to include name fields, and lock the table name before loader work begins.

3. Add a new `mart_intelligence` loader for the long similarity artifact.
   Verify: materialize the table in DuckDB, confirm row count, confirm no self-pairs, and confirm uniqueness at the intended grain.

4. Keep the current wide Cross-Frame score mart stable.
   Verify: `mart_intelligence.intelligence_cross_frame` still loads as one row per CBSA and existing downstream queries do not regress.

5. Update semantic-layer and mart documentation.
   Verify: docs clearly distinguish the one-row score mart from the long similarity mart and point products to the correct query surface.

6. Add a few sanity-check queries for product use.
   Verify: the promoted table can answer:
   - top 10 peers for one CBSA
   - all peers above similarity threshold `x`
   - pairwise similarity lookup for two CBSAs
   - rank of a given peer within a CBSA's similarity neighborhood

7. Decide whether to wire downstream products immediately or leave the mart as a ready capability.
   Verify: if Area Explorer or Metro Deep Dive adopts it now, update the relevant contract and roadmap notes at the same time.

## Rough effort estimate

- Top-10 long mart only: roughly a small loader pass plus docs, likely a light half-day task.
- Full matrix artifact plus mart promotion: roughly `4-6` focused hours, or closer to a full day if we want careful docs and downstream examples.

## Revisit trigger

Move this from "nice to have" to active work when at least one downstream product needs peer querying that the current widened top-10 columns cannot support cleanly.
