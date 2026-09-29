# Ideas
*Open questions, analytical angles, and writing seeds — organized by theme. Add to this freely. When a prompt becomes a piece, give it a folder under `publisher/content/` using a template from `templates/`.*

---

## How to use this file

A prompt is not a piece. It's a question worth sitting with. When a prompt is sharp enough — you can state the finding, name the audience, and pick a format — it becomes a piece. The test is the five questions in `docs/strategy/PUBLISHING.md`.

Three signals that a prompt is ready to become a piece:
1. You can write the thesis in one sentence
2. You know which Gold table or Intelligence output answers it
3. You have a visual in mind

Until all three are true, it stays here.

---

## Housing & Vacancy

- Is the national vacancy "tightening" story real, or is it an average masking two structurally different kinds of markets?
- High vacancy isn't one thing — what are the distinct types (weak demand vs. seasonal/vacation vs. structural oversupply) and how do you tell them apart in the data?
- Which metros have the highest rent burden, and does that correlate with vacancy tightness or diverge from it?
- Where are builders actually adding supply, and does permit activity match where vacancy is tightest?
- Income growth vs. rent growth: which metros are getting more affordable and which are quietly getting worse?
- The affordability paradox: are there metros where vacancy is loose *and* rent burden is high? What does that mean?

---

## Intelligence Framework Findings

- The L/O scatter: which metros rank high on Livability but low on Opportunity — and what does that gap look like on the ground?
- The divergence list: metros that rank top-20 on one frame and bottom-100 on another. What's the mechanism in each case?
- The Southern health deficit: why do Southern metros cluster differently on Livability, and what's driving it?
- Hidden winners: metros that score in the bottom half nationally but are trending strongly positive on trajectory. Who are they and why?
- Opportunity for whom? Metros where Resident Opportunity and Investor Opportunity point in opposite directions — the extraction story vs. the underrated quality-of-life play.
- What do the Character clusters actually reveal that a single demographic profile misses? What surprised you when the k=7 solution resolved?
- GMM soft memberships: which metros are genuinely ambiguous between clusters, and is that ambiguity analytically interesting or just noise?
- Cross-frame peers: metros that are cosine-similar on one frame but diverge sharply on another. These are the most analytically interesting comparisons.

---

## Metro Character & Place Stories

- What does "Sun Belt Growth" actually mean as a metro type? What do the seven Character clusters reveal that the label hides?
- The Immigrant Gateway cluster: which metros define it, and what does that character type predict about economic trajectory?
- Salt Lake City: the Sun Belt metro nobody calls a Sun Belt metro
- Which metros are genuinely hard to classify — the ones that don't fit cleanly into any Character cluster?
- Peer surprises: every major metro has a statistical twin that would shock most people. What are the most counterintuitive cosine-similarity pairs?
- Is there a metro that looks like Austin in the data but costs half as much? (Opportunity List format)

---

## Contrarian Takes

- Population growth is a worse investment signal than you think — what actually predicts market resilience?
- The most underbuilt cities aren't the ones in the headlines. Who are they?
- The Sun Belt boom is already slowing in specific markets. Where, and what's the leading indicator?
- Vacancy rate as a market signal: what does it actually tell you, and what does it not tell you that people assume it does?
- Why the metros "winning" on Livability aren't always the ones gaining population
- Rent burden and income growth are both moving — but not always in the same direction. Which frame matters more for where a market is heading?

---

## Technical — How We Built This

- Why I built a semantic layer before building any dashboards — and what it forced me to see
- DuckDB as a local analytical data warehouse: what works and what doesn't at 20+ table scale
- How I designed a three-frame scoring model from scratch with no labeled training data
- Soft cluster membership (GMM) vs. hard labels: when ambiguity is the honest answer
- The within/national IQR ratio: a simple diagnostic for whether a KPI adds zone-level signal
- Handling missingness at 396-CBSA, 400-metric scale: why median imputation was the right call
- Building a catalog-driven Streamlit app: the `metric_catalog.yml` pattern
- Why I separated Gold tables from Intelligence marts — and when to break that rule
- ETL in R for ACS data: a pattern that actually scales across 14 source tracks

---

## Deep Dive Seeds

*These are place-first questions — too big for a Data Take, pointing toward a Metro Deep Dive.*

- Jacksonville: how a mid-size metro quietly became a logistics capital — and what the Intelligence frame scores say about where it's going
- Richmond VA: high Livability scores but a Character cluster that doesn't fit the narrative. What's the actual story?
- What happened to Dayton — and what other Rust Belt cities can learn from it
- Cleveland vs. Pittsburgh: a tale of two recoveries, told through the Livability and Opportunity frames
- A Sun Belt metro that surprises: high Character score, low Opportunity score, growing fast. Which one and why?

---

## Thinking Prompts
*Not article ideas — questions to sit with before writing. Use these to find the thesis.*

- Which finding from the Intelligence Framework genuinely surprised you when the clusters first resolved? That surprise is probably a story.
- What does the cross-frame overlap flag surface that you didn't expect? Are there metros where all three frames diverge from each other?
- When you look at the Phase 6 candidate list, what's the most analytically interesting metro that isn't Jacksonville or Richmond?
- Which questions from the vacancy series couldn't fit in 700 words? Those overflow questions are the next track.
- Which metros kept coming up across multiple pieces? Repetition is a signal.
- What does the data say that a typical urban commentator would push back on? Start there for Contrarian Takes.
- Which findings need the interactive tool to be understood vs. which can be conveyed in a static chart? The static ones are publishable now.
- After finishing the vacancy series: what do you now know about your own writing rhythm that you didn't know before?
