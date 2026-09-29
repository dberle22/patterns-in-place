# Position Candidate Scan Spec

**Status:** Planned

**Primary surfaces:** `POSITION_CANDIDATE_SCAN_NOTEBOOK.py` and
`POSITION_CANDIDATE_DISCOVERY_NOTEBOOK.py`

**Historical baseline:** `metro-deep-dive/RESEARCH_TOOL_ROADMAP.md` and
`metro-deep-dive/research-tool/components/candidate_tab.py`

**Dependencies:** Existing Intelligence Framework CBSA marts, the current
Time-Series trajectory marts, and governed CBSA identity/filter fields. No
Candidate Scan engine or new Foundations asset is required for the first build.

## Goal

Build one internal Marimo notebook that helps an analyst decide which metros
deserve review next and understand why each one surfaced.

This is a port and update of the legacy Research Tool Candidate List. It keeps
the original purpose—market-selection support based on cross-frame divergence
and trajectory interest—while replacing stale file-backed assumptions with the
current Position and Time-Series contracts.

The scan is not a ranking of the best metros and does not choose the editorial
calendar automatically.

## Product Boundary

Candidate Scan is the one Position analysis whose primary view is all markets
rather than one selected CBSA. It remains in Position because it combines the
same repeatable Profile and Trajectory evidence used to route later analyses.

The first build is deliberately notebook-only:

- two complementary Marimo notebooks: a light Discovery surface for choosing
  markets to discuss and a detailed Candidate Scan for transparent ranking,
  explanation, sensitivity, and QA
- read-only DuckDB inputs
- no separate headless runner
- no required SQL files or saved QA bundle
- no new mart or engine-owned candidate score

The notebook may calculate a transparent, versioned ranking for exploration.
That ranking stays analysis-local until another consumer demonstrates that the
same method needs promotion.

## Inputs

| Input | Role |
|---|---|
| Cross-frame Profile fields | Current frame positions, divergence, alignment, signature, and identity context |
| Time-Series frame outputs | Current position, movement, salience, signal tier, and coverage by frame |
| Time-Series turn signals | Current short-versus-medium-run turn evidence |
| Governed CBSA attributes | CBSA name plus the geographic and population fields required for filtering |
| Legacy Phase 6 candidate work | Behavioral and scoring baseline to audit, not a canonical notebook input |

The current top-10 Peers surface is not required to rank candidates. Peer
context can remain a downstream drill-through after a market is selected.

## Candidate Method

The update should preserve the old method's question, not copy its historical
formula blindly.

The notebook should:

1. Reconstruct the legacy candidate result as a comparison baseline.
2. Map its cross-frame and trajectory concepts to fields that exist in the
   current engine contracts.
3. Define a small, explicit candidate-method version using only those current
   fields.
4. Show each component beside the final rank so the analyst can see why a
   market moved up or down.
5. Keep weights and thresholds visible and include a compact sensitivity view
   before treating the ordering as useful.

If an old pattern cannot be reproduced without rebuilding deprecated engine
logic, the notebook should omit it or replace it with a clearly named current
signal. It must not silently recreate Time-Series scoring or labels.

## Notebook Surfaces

| Surface | Purpose |
|---|---|
| Discovery guide | Provide a plain-language first-look workflow for identifying markets worth an analyst conversation |
| Discovery lenses | Show balanced leads, strong recent movement, unusual profiles, or Opportunity turns without introducing a second ranking method |
| Purpose and method note | Explain what the scan ranks and what it does not claim |
| Coverage summary | Show eligible metros, missing inputs, method version, and source vintages |
| Filters | Narrow by geography, population range, divergence context, trajectory signal, and turn status |
| Ranked candidate table | Show rank, market identity, score components, current Position signals, and coverage |
| Why this market surfaced | Explain one selected row through its visible contributing signals |
| Shortlist comparison | Compare a small analyst-selected set without turning the notebook into a full Profile or Peers surface |
| Sensitivity and QA | Show rank movement under a small number of reasonable alternatives plus duplicate/null checks |

## Outputs

The required outputs are two interactive Marimo notebooks: the light Discovery
surface for first-look discussion and the detailed Candidate Scan for method
inspection. Neither writes a candidate mart, CSV, HTML bundle, or publication
chart.

An issue or planning workflow may record a chosen market separately, but the
notebook does not own that decision.

## Interpretation Guardrails

- Candidate rank means review priority under one declared method, not quality,
  opportunity, or importance.
- Cross-frame divergence and trajectory salience are different signals and
  remain visible separately.
- Missing or ineligible trajectory evidence cannot be treated as zero signal.
- Current engine labels and thresholds must be read from the engine outputs,
  not reimplemented in notebook cells.
- Ordinary markets are valid results; the scan should not manufacture a story
  for every CBSA.
- Publication claims still inherit the Intelligence Framework and Time-Series
  review gates.

## Out of Scope

- a public landing page
- automated issue scheduling
- a durable candidate-score mart
- peer-network or beyond-top-10 similarity work
- final narrative recommendations
- publication-ready charts

## Success Check

Candidate Scan is ready when an analyst can filter the current CBSA universe,
inspect a transparent ranking, understand why any selected market surfaced,
compare a short list, and distinguish current canonical evidence from the
legacy Phase 6 baseline—all without writing outside the notebook.
