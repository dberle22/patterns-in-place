# Position Peers Analysis

This analysis turns the promoted top-10 peer surfaces into notebook-friendly
peer queries and simple validation visuals for any target metro.

It is the second downstream consumer of the Intelligence Framework engine after
`profile/`.

## What It Reads

- `mart_intelligence.intelligence_character`
- `mart_intelligence.intelligence_livability`
- `mart_intelligence.intelligence_opportunity`
- `mart_intelligence.intelligence_cross_frame`

## What It Produces

Planned primary exploration surface:

- `POSITION_PEERS_NOTEBOOK.py`
  Marimo notebook for interactive cross-frame and frame-specific peer review,
  overlap, and head-to-head comparison.

Reusable query surfaces:

- `queries/peer_list.sql`
- `queries/peer_benchmark_top5.sql`

Validation visuals:

- `figures/<cbsa_code>/peer_similarity_bars.html`
- `figures/<cbsa_code>/peer_compare_heatmap.html`

These HTML files remain the responsibility of the separate `peers.py`
headless QA runner. The Marimo notebook renders in place and is not required to
export files.

## Why This Exists

The promoted framework marts store peers in a wide top-10 format. That is fine
for the mart contract, but awkward for actual notebook work.

This analysis converts the current peer contract into reusable query surfaces
without asking the engine layer to change first.

See [POSITION_PEERS_SPEC.md](POSITION_PEERS_SPEC.md) for the agreed SQL plan,
notebook flow, visuals, guardrails, and build checklist.
