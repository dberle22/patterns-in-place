# Asset Inventory
## What's Already Built, What State It's In, What to Do Next

This doc is the running ledger of every asset that exists for Patterns in Place — the data infrastructure, the interactive tools, and the analysis series. Each asset gets a status flag, a description of what it can do today, and the next move that gets it from its current state to publishable.

The publication's launch speed depends on this inventory being accurate. If something is listed as "Ready to Deploy" but actually has six bugs, the launch sequence breaks. Update this doc whenever an asset advances a stage.

---

## Status Definitions

Every asset is in one of four states:

| Status | What it means | What to do |
|---|---|---|
| **Shareable** | The asset works, is documented, and is ready to be referenced publicly. | Use it in launches as-is. |
| **Ready to Deploy** | The asset works locally or in a staging environment but isn't live yet. | Schedule the deployment. |
| **Needs Packaging** | The asset works but isn't presentable — it needs documentation, narrative wrapping, or a published reference. | Block 1–3 days to package. |
| **In Development** | The asset is actively being built; not yet usable. | Track progress; don't reference publicly. |

Update the status flag in this doc when an asset advances. The launch sequence in `publication_playbook.md` assumes the status is current.

---

## Layer A — Infrastructure

Foundational systems that every analysis depends on. These are not publishable artifacts on their own but are the engine.

### Bronze / Silver / Gold Data Pipeline

**Status:** Shareable
**Owner:** Internal
**Last updated:** Pre-launch (April 2026)

**What it does:** Unified ingestion and normalization of ACS, BEA, BLS, HUD, Zillow, and TIGER data across CBSA, county, zip code, and tract geographies. Bronze is raw ingested data; Silver is cleaned and aligned; Gold is analysis-ready feature tables. The pipeline is queryable for both broad cross-metro comparisons and narrow neighborhood-level questions.

**Why it matters:** The pipeline is the publication's structural advantage. It is the thing that lets a Comparison piece or an Opportunity Finder list be produced consistently rather than recomputed from scratch every time. It is the asset that makes Patterns in Place a publication and not a series of one-offs.

**Current state:** Semi-automated with some manual steps (re-runs, validation checks). Documented but not yet narrated for a general audience.

**Next moves:**
1. Write the public origin story — Move 5 in the launch checklist (`publication_playbook.md`)
2. Stand up the public `data-pipeline` GitHub repo with a README that points readers to the origin story
3. Document any manual steps so a future contributor (or future you) can re-run cleanly

**Where it appears in launches:** The pipeline origin story is the foundational piece that every other Medium piece references. Subsequent analyses link back to it as the methodology citation.

---

### Visual Library / Design System

**Status:** Shareable
**Owner:** Internal
**Last updated:** Pre-launch (April 2026)

**What it does:** Defines the consistent look and feel for all analytical outputs. Color palette, typography, chart templates, map style defaults, the Patterns in Place wordmark. Ensures every chart, map, and dashboard produced under Patterns in Place carries a unified visual identity.

**Why it matters:** Visual consistency is one of the most under-rated credibility signals in data publishing. Readers recognize a Patterns in Place chart in a forwarded screenshot. A piece with default Matplotlib styling under the Patterns in Place masthead damages the brand more than no piece at all.

**Current state:** Drafted. Not yet documented as a public reference.

**Next moves:**
1. Stand up the public `visual-library` GitHub repo
2. Write the visual library piece — Move 7 in the launch checklist
3. Apply the system to every chart and map in the launch sequence (Moves 5, 6, 7, 8)

**Where it appears in launches:** Every visual asset in every launch. The visual library piece (Move 7) is also the explicit "we take craft seriously" signal to hiring managers.

---

## Layer B — Tools

Interactive products that readers can use directly. These are the differentiator layer — the artifacts that distinguish Patterns in Place from a data blog.

### NYC Neighborhood Explorer

**Status:** Ready to Deploy
**Owner:** Internal
**Last updated:** Pre-launch (April 2026)

**What it does:** Interactive mapping tool for exploring NYC neighborhoods by census tract. Integrates demographic data with points of interest. Visual, immediately engaging, and broadly accessible to a general audience.

**Why it matters:** This is the publication's first public tool launch and the first artifact most readers will encounter. NYC is recognizable enough that a curious general reader will click; the tract-level granularity is novel enough that a civic tech practitioner will share it.

**Current state:** Built. Tested locally. Not yet deployed to Streamlit Community Cloud.

**Next moves:**
1. Deploy to Streamlit Community Cloud — Move 4 in the launch checklist
2. Apply Patterns in Place visual identity (header, wordmark, About panel)
3. Mobile-test before launch (most LinkedIn traffic comes from mobile)
4. Write the launch piece — Move 6
5. Coordinated three-platform launch — Move 6

**Where it appears in launches:** Move 4 (deploy) and Move 6 (public launch). The tool is the URL referenced from the launch piece, the LinkedIn post, and the GitHub repo.

---

### Florida Target Parcel Analysis

**Status:** Ready to Deploy
**Owner:** Internal
**Last updated:** Pre-launch (April 2026)

**What it does:** Market-level parcel analysis tool scoped to Florida with full data coverage. Built for real estate investors and developers who need to evaluate specific parcels against market context. Narrow but high-intent audience.

**Why it matters:** This is the publication's first test of reaching a practitioner audience beyond the data and tech community. If it lands, it validates that Patterns in Place can serve real estate investors directly — which is one of the four target audiences.

**Current state:** Built. Tested. Not yet deployed.

**Next moves:**
1. Deploy to Streamlit Community Cloud — Move 10
2. Identify 5–10 Florida real estate investor forums, subreddits, and newsletters for targeted distribution
3. Write the launch piece — Move 10
4. Targeted outreach to top 3 communities

**Where it appears in launches:** Move 10. This is the last move in the six-week launch sequence and the first practitioner-audience test.

---

### LLM Chatbot Foundation

**Status:** In Development
**Owner:** Internal
**Last updated:** Pre-launch (April 2026)

**What it does:** Early-stage question-and-answer interface trained on urban data questions. Eventually becomes a public-facing chatbot grounded in the Bronze/Silver/Gold pipeline. The Q&A training set is itself a content asset (each question is a Data Take in waiting).

**Why it matters:** Two things at once. The training set is a content gold mine for the Data Take format (see `editorial_strategy.md`). The chatbot itself, once public, becomes the most interactive entry point to the publication and a legitimate AI-applied-to-data demonstration.

**Current state:** Foundation built. Not yet ready for public deployment. Q&A training set is partially curated.

**Next moves (short-term, weeks 1–6):**
1. Mine the Q&A training set for the most surprising or counterintuitive question
2. Ship the first Data Take built from that question — Move 9 in the launch checklist
3. Continue mining the set; build a backlog of 8–12 Data Takes ready to publish

**Next moves (medium-term, months 2–4):**
1. Move chatbot from development to public beta — see `growth_roadmap.md`
2. Train on the full curated Q&A set
3. Ground responses in the Bronze/Silver/Gold layer rather than free-form generation

**Where it appears in launches:** The Q&A training set drives Move 9 (first Data Take). The chatbot itself is part of the months-2–4 vision in `growth_roadmap.md`, not the first six weeks.

---

## Layer C — Analysis Series

Recurring analytical products. Each series has a methodology piece that runs once and a stream of application pieces that run regularly.

### Overheating Index

**Status:** Needs Packaging
**Owner:** Internal
**Last updated:** Pre-launch (April 2026)

**What it does:** Composite scoring model flagging overheated or at-risk housing markets based on affordability and price-trend indicators. The foundation for a recurring market analysis series.

**Why it matters:** A scoring model that is published, methodology-transparent, and applied consistently across markets is one of the most reusable content engines a data publication can build. Every quarter you can publish "the most overheated markets right now"; every month you can publish a Data Take using the score on a single market.

**Current state:** Model built and validated. Not yet narrated for a general audience. No published methodology piece exists.

**Next moves:**
1. Write the methodology piece — Move 8, Part 1
2. Write the first application piece — "The Most Overheated Housing Markets Right Now" — Move 8, Part 2
3. Set up the `market-scoring-models` GitHub repo with reproducible Quarto notebook
4. Establish quarterly application rhythm

**Where it appears in launches:** Move 8 (the two-part series). After launch, every future application piece links back to Part 1 as the canonical methodology reference.

**Series cadence going forward:**
- Methodology piece: published once, occasionally updated
- Quarterly "current state" piece: every three months
- Monthly Data Takes applying the score: weekly when relevant

---

### Investment Score

**Status:** Needs Packaging
**Owner:** Internal
**Last updated:** Pre-launch (April 2026)

**What it does:** Composite scoring of market investment attractiveness using economic, housing, and demographic signals. Pairs with the Overheating Index for a complete market intelligence picture (high investment attractiveness + low overheating risk = the headline finding).

**Why it matters:** The pair is more valuable than either model alone. The Overheating Index identifies risk; the Investment Score identifies opportunity. Together they make Patterns in Place a genuine market intelligence source rather than just a commentary outlet.

**Current state:** Model built and validated. Not yet narrated. No published methodology piece exists.

**Next moves (medium-term, months 2–3):**
1. Write the methodology piece — mirrors the Overheating Index methodology piece structure
2. Write the first application piece — see `growth_roadmap.md`
3. Add to the `market-scoring-models` GitHub repo

**Where it appears in launches:** Months 2–3, after the Overheating Index series has established the format. Mirrors the Overheating Index series structure exactly.

---

### Chatbot Q&A Training Set

**Status:** Shareable (as content source)
**Owner:** Internal
**Last updated:** Pre-launch (April 2026)

**What it does:** A series of urban data questions developed to train the chatbot. Each question is a ready-made Data Take piece — already framed, already targeted at a specific finding, requiring only data pull and short-form write-up.

**Why it matters:** This is the lowest-cost content engine in the publication. Every question in the set is a Data Take draft. Once the format is established, weekly cadence becomes routine.

**Current state:** Partially curated. Several dozen questions exist; not all have been validated as having interesting data answers.

**Next moves:**
1. Pick the single most interesting question for Move 9 (the first Data Take)
2. Mine the rest of the set; tag each question with status (Ready / Needs Data / Drop)
3. Build a backlog of 8–12 Ready questions before week 5

**Where it appears in launches:** Move 9 and onward. The set powers the weekly Data Take cadence indefinitely.

---

## Asset Snapshot

A single-table view of where everything stands. Update this section every time an asset advances.

| Asset | Layer | Status | First public moment |
|---|---|---|---|
| Data Pipeline | A | Shareable | Move 5 (week 2) |
| Visual Library | A | Shareable | Move 7 (week 3) |
| NYC Neighborhood Explorer | B | Ready to Deploy | Move 4–6 (weeks 1–3) |
| Florida Parcel Analysis | B | Ready to Deploy | Move 10 (week 6) |
| LLM Chatbot Foundation | B | In Development | Months 3–4 (public beta) |
| Overheating Index | C | Needs Packaging | Move 8 (week 4) |
| Investment Score | C | Needs Packaging | Months 2–3 |
| Chatbot Q&A Training Set | C | Shareable | Move 9 (week 5) |

---

## What This Inventory Does Not Yet Include

Assets to track once they exist:

- **Metro Deep Dives** — each Metro Deep Dive published becomes a referenceable asset for future Comparisons. Track them here once the first one (Jacksonville, per `growth_roadmap.md`) ships.
- **County and tract-level analyses** — see months 3–4 in `growth_roadmap.md`. Add them here once they ship.
- **Newsletter** — once activated (~month 3), track it here as a distribution asset with subscriber count.
- **Standalone site** — see month 6+ in `growth_roadmap.md`. Add when launched.

---

## Asset Hygiene Rules

To keep this inventory useful rather than performative:

1. **Update the status flag the day an asset advances.** Stale flags break the launch sequence.
2. **Don't list assets that don't exist yet.** Future plans live in `growth_roadmap.md`. This doc is the present-tense ledger.
3. **Be honest about "Ready to Deploy" vs. "In Development."** The cost of overstating readiness is a missed launch; the cost of understating is nothing.
4. **Every Shareable asset must have a public reference within 30 days of being marked Shareable.** Otherwise downgrade to Needs Packaging.
5. **Layer C assets only count as Shareable when they have a published methodology piece.** A model with no methodology page is Needs Packaging at best.

---

## How This Doc Sits Alongside the Others

- `publication_playbook.md` — the operational launch sequence that depends on this inventory
- `editorial_strategy.md` — defines the pillars and formats; this doc lists the assets that feed them
- `distribution_strategy.md` — defines where each asset shows up
- `asset_inventory.md` — *this doc.* The current-state ledger.
- `growth_roadmap.md` — what's coming next; the source for new assets that get added to this inventory over time
- `methodology/` — the standards each Layer C asset references

---

## Next Up

After confirming the inventory is current:

1. Cross-reference each asset against `publication_playbook.md` to confirm the launch sequence is consistent.
2. Update `methodology/data_pipeline_standards.md` to match the actual pipeline state.
3. Begin moves 1–3 of the launch checklist while continuing to maintain this inventory.

The single most leveraged thing this inventory does is force honesty about the gap between "I have built it" and "the public can use it." Most projects die in that gap. The status flags make the gap visible.
