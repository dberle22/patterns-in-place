# Publication Playbook
## Setting Up Patterns in Place as a Real Publication

This is the operational starting point. It assumes you are launching Patterns in Place as an independent urban data publication — not a side blog, not a portfolio, not a consultancy. The other docs in this folder define what to publish, where to distribute, what's already built, and how this grows over time. This doc covers the work that has to happen before anything goes public.

---

## How This Doc Fits With the Others

You are building one thing — a publication with a point of view — but the work has four operating layers that each get their own doc:

1. **Identity and operations** (this doc) — the GitHub org, the Medium publication, the visual identity, the legal/account plumbing, the launch checklist.
2. **Editorial strategy** (`editorial_strategy.md`) — the five pillars, the three formats, the audiences each piece is written for, and how often each format ships.
3. **Distribution strategy** (`distribution_strategy.md`) — the role of each platform (GitHub / Medium / LinkedIn / Streamlit), the cross-platform cadence, the post bank, the anti-patterns.
4. **Asset inventory** (`asset_inventory.md`) — the full picture of what's already built across infrastructure, tools, and analysis series, with status flags for each piece.
5. **Growth roadmap** (`growth_roadmap.md`) — the multi-month arc from launch through standalone site and newsletter.
6. **Methodology** (`methodology/`) — the editorial pillars, format specs, data pipeline standards, and visual design standards as living reference docs.

Read in order if you're starting from zero. If you only have an hour, read this doc and `editorial_strategy.md`.

---

## 1. The Three Sentences

Before claiming a name or building anything new, lock in three sentences. Everything that follows is downstream of these.

- **What this is:** An independent urban data publication covering housing markets, demographics, and economic geography across the United States.
- **Who reads it:** Real estate investors and analysts, civic tech and open data practitioners, hiring managers evaluating analytical capability, and a curious general public interested in how cities work.
- **Why it's different:** Most people in this space are analysts who write, developers who build tools, or researchers who publish. Patterns in Place does all three — from raw ingestion through interactive delivery, across every geographic scale.

If those three sentences feel right, every other choice in this doc gets easier.

### The positioning statement (use everywhere)

> "Patterns in Place is an independent urban data publication. We build open analyses and tools for housing markets, demographics, and economic geography across the United States — from raw census data through interactive maps."

Variations:
- LinkedIn headline: "Patterns in Place — open urban data analyses and tools"
- GitHub org tagline: "Open analyses and tools for US housing, demographics, and economic geography"
- Medium publication subtitle: "Independent urban data — what's changing, where, and why"

---

## 2. Naming and Identity

The name is locked: **Patterns in Place.** Treat it as a publication name, not a personal brand. Your name is the byline; the publication is the masthead.

### Identity claims to make in week one

These are cheap, fast, and irreversible — do them before anything is published.

- [x] **GitHub organization:** `PatternsInPlace` (or `patternsinplace` lowercase if the camelcase version is taken). We will use my existing dberle22 account for now.
- [x] **Medium publication:** create at medium.com/patterns-in-place
- [ ] **LinkedIn page:** create the company page (separate from your personal profile) - Deferred.
- [x] **Substack handle:** reserve `patternsinplace.substack.com` as a defensive move even if you don't use it yet
- [ ] **Domain:** buy `patternsinplace.com`, `.org`, and `.co` from Namecheap or Porkbun (~$36 total)
- [ ] **Twitter/X handle:** reserve `@patternsinplace`
- [ ] **Email:** set up `hello@patternsinplace.com` via Google Workspace ($7/month) once the domain resolves
- [ ] **Streamlit Community Cloud:** create the org or namespace under Patterns in Place

Total cost: under $50 one-time and ~$7/month recurring. Total time: two hours if everything is available.

### What to check before claiming

1. USPTO trademark search (TESS): https://tmsearch.uspto.gov/ — confirm no conflicts with existing publications or data services
2. Google search: `"Patterns in Place" data` and `"Patterns in Place" housing` — check whether anything visible already uses the name
3. Domain availability across `.com`, `.org`, `.co`, and `.io`
4. GitHub org name availability
5. Medium publication URL availability

If any one of these surfaces a conflict, decide before claiming the rest. The cost of changing the name two months in is real.

---

## 3. Visual and Editorial Identity

Visual identity is part of the credibility layer for a data publication. It signals to readers that you take the craft seriously.

### What "Patterns in Place visual identity" means in practice

- A **shared color palette** used across every chart, map, and dashboard (already drafted in the visual library — see `methodology/visual_design_standards.md`)
- A **shared typeface system** for charts and long-form (the brief uses Playfair Display + IBM Plex; pick whatever serves the publication, but pick once)
- A **consistent chart and map aesthetic** — same gridlines, same legend treatment, same map projection defaults
- A **publication mark** — wordmark or simple logotype that appears on every chart export, every Streamlit tool, and every Medium piece header
- An **editorial voice** — measured, opinionated, data-first, no jargon-as-drama

Every output should be recognizable as "a Patterns in Place piece" within three seconds. The brief already names this; the playbook just makes sure it actually gets enforced before launch.

### Voice rules of thumb

- Lead with the finding, not the methodology
- Name the place — "Jacksonville," not "a southern metro"
- Show one number that anchors the piece, not seven
- Acknowledge limitations honestly; never overclaim
- Use plain English; no consulting-deck nouns

---

## 4. Legal and Operating Setup

Patterns in Place can run as an unincorporated publication in year one. Form an entity only if and when you start monetizing (newsletter sponsors, paid tools, licensed analyses, consulting under the publication's name).

### What to set up now

- A separate `hello@patternsinplace.com` email
- A separate Mercury or business savings account if you're already an LLC for other work — keeps publication-related expenses cleanly traceable
- A simple Google Drive folder for source materials, spreadsheets, and draft pieces
- A password manager entry (1Password, Bitwarden) for all the publication accounts so handoff is possible later

### What to defer

- Forming a separate LLC just for the publication (only worth it once revenue exists)
- Trademarking the name (defer until ~$5k+ has been earned under the brand)
- Hiring contractors (defer until at least the first 10 moves are complete)
- Insurance (only relevant once tools serve real customers or paid clients)

---

## 5. Tools Stack (Recommended Minimum)

A publication this scale runs on under $50/month if you're disciplined.

| Function | Tool | Cost/mo |
|---|---|---|
| Email | Google Workspace (`hello@patternsinplace.com`) | $7 |
| Domain | Namecheap or Porkbun | ~$1 |
| Code + repos | GitHub (free tier; consider Pro at $4) | $0–$4 |
| Notebook publishing | Quarto (open source) | $0 |
| Long-form publishing | Medium publication | $0 |
| Tool deployment | Streamlit Community Cloud / shinyapps.io free tier | $0 |
| Distribution | LinkedIn (organic) + later Substack/Beehiiv newsletter | $0 |
| Visual editing | Figma free tier + Datawrapper free tier | $0 |
| Analytics | Plausible or Fathom (when standalone site exists) | $9–$14 |
| Project tracking | Notion or Linear free tier | $0 |
| Scheduler | Buffer free / Hypefury for LinkedIn | $0–$15 |

Total: under $50/month for a complete operating stack. Add a paid newsletter platform (Substack is free, Beehiiv is $0–$39) only when you're ready to start collecting subscribers.

---

## 6. The Launch Checklist — The First 10 Moves

The brief lays out ten sequenced moves that take the publication from zero public presence to an established launch over six weeks. They are reproduced here as an actionable checklist with owner, dependencies, and definition-of-done.

The sequencing matters. Each move either unlocks the next or compounds the ones before it. Do not skip ahead.

### Move 1 — Claim the Name Everywhere (Day 1)

**Outcome:** Every account that needs to exist for the publication exists, even if empty.

- [ ] GitHub organization created
- [ ] Medium publication created
- [ ] LinkedIn page created
- [ ] Substack handle reserved
- [ ] Domain purchased
- [ ] Twitter/X handle claimed
- [ ] Email up and forwarding

**Definition of done:** A LinkedIn post saying "I just launched Patterns in Place" would have a real link to click.

**Time budget:** 2 hours.

---

### Move 2 — Write the Publication README (Days 2–3)

**Outcome:** A single source-of-truth document under 400 words that answers four questions: what is this, what questions does it answer, what data and tools does it use, who is it for.

- [ ] Draft on paper first (pen, not screen)
- [ ] Cut to under 400 words
- [ ] Put on GitHub at `PatternsInPlace/.github/profile/README.md` (org-level README)
- [ ] Mirror as the Medium publication "About" page
- [ ] Reserve as the foundation for the standalone About page later

**Definition of done:** A friend who knows nothing about urban data can read it and explain back what Patterns in Place is.

**Time budget:** Half a day, including ruthless editing.

---

### Move 3 — Structure the GitHub Organization (Days 3–5)

**Outcome:** Six repos exist and are pinned in priority order. The top three have READMEs that describe what they are and how to use them.

Pin order:

1. `publication-index` — links to every analysis, tool, and post in one place
2. `data-pipeline` — Bronze/Silver/Gold ingestion and normalization
3. `visual-library` — design system and chart templates
4. `nyc-neighborhood-explorer` — interactive mapping tool
5. `market-scoring-models` — Overheating Index + Investment Score
6. `florida-parcel-analysis` — parcel-level investor tool

- [ ] Six repos created (private if not ready, public when ready)
- [ ] Top three repos have READMEs
- [ ] Each repo has a one-line description visible in the org overview
- [ ] LICENSE files in place (MIT or CC-BY-SA, decided per repo)

**Definition of done:** Visiting `github.com/PatternsInPlace` shows six pinned repos, each visibly intentional.

**Time budget:** Two evenings.

---

### Move 4 — Deploy the NYC Neighborhood Explorer (Week 1–2)

**Outcome:** The tool is live on Streamlit Community Cloud at a stable URL, carrying the Patterns in Place name and visual identity. Version 1 just needs to work and look intentional.

- [ ] Streamlit app deployed at a memorable URL
- [ ] Patterns in Place wordmark visible in the app header
- [ ] One-paragraph "About this tool" panel
- [ ] Link back to GitHub repo
- [ ] Tested on mobile (most LinkedIn traffic comes from mobile)

**Definition of done:** Someone clicking the URL from a LinkedIn post in two weeks gets a working tool that loads in under five seconds.

**Time budget:** One weekend.

---

### Move 5 — Write the Pipeline Origin Story (Week 2)

**Outcome:** First piece on Medium. Frames the data pipeline as a problem worth solving rather than a tutorial.

- [ ] Draft 1,500–2,000 words
- [ ] Open with the problem: US demographic data is fragmented across a dozen agencies
- [ ] Walk through the Bronze/Silver/Gold architecture conceptually, not technically
- [ ] End with what the pipeline unlocks (a list of analyses now possible)
- [ ] Link to the GitHub `data-pipeline` repo
- [ ] Include 2–3 visuals that match the Patterns in Place visual identity

**Definition of done:** A non-technical reader finishes the piece and understands why the pipeline matters.

**Time budget:** One full writing day, plus a second day for visuals and editing.

---

### Move 6 — Launch the NYC Tool Publicly (Week 2–3)

**Outcome:** Coordinated launch across three platforms in a single 24-hour window.

- [ ] Medium piece (1,000 words): why NYC, what the tool shows, two or three specific findings from the data
- [ ] LinkedIn post: map visual or screen capture, one specific insight, link to the Medium piece
- [ ] GitHub repo `nyc-neighborhood-explorer` made public with full README
- [ ] Cross-link: Medium piece links to the live tool and the repo; the tool links back to the Medium piece

**Definition of done:** First moment that the publication reaches an audience beyond your immediate network.

**Time budget:** Two days for content + a coordinated launch hour.

---

### Move 7 — Publish the Visual Library Piece (Week 3)

**Outcome:** A 600–800 word piece explaining why consistent visual identity matters in data journalism, using Patterns in Place outputs as the examples.

- [ ] 600–800 words
- [ ] Three or four example visuals (good vs. bad pairs are powerful)
- [ ] Link to the `visual-library` repo
- [ ] Cross-post to LinkedIn with one of the visuals as the hero image

**Definition of done:** A hiring manager skimming the piece concludes that you take craft seriously.

**Time budget:** One writing day.

---

### Move 8 — Launch the Overheating Index Series (Week 4)

**Outcome:** Two pieces published one week apart. Part 1 is the methodology explainer; Part 2 is the first application.

**Part 1 — methodology piece**
- [ ] Plain language, not equations
- [ ] One chart showing score distribution across markets
- [ ] Honest about limitations
- [ ] 1,200 words

**Part 2 — application piece**
- [ ] "The Most Overheated Housing Markets Right Now"
- [ ] 8–12 markets ranked
- [ ] One map
- [ ] One to two paragraphs per market
- [ ] Clear single takeaway
- [ ] 1,500 words

- [ ] Both pieces link to the `market-scoring-models` repo
- [ ] Every future application piece links back to Part 1

**Definition of done:** A search for "Overheating Index" lands on Part 1 as the canonical methodology reference.

**Time budget:** Two writing weeks (one piece per week).

---

### Move 9 — Ship the First Chatbot Q&A Data Take (Week 5)

**Outcome:** A standalone 600-word piece built around the single most interesting question from the chatbot training set.

- [ ] Pick the question where the data answer is most surprising or counterintuitive
- [ ] One question, one data-driven answer, one strong visual
- [ ] 600 words exactly (this is the format spec — see `methodology/format_standards.md`)
- [ ] Establishes the Data Take format as the publication's lowest-cost recurring output

**Definition of done:** You have a template you can apply to 20 more questions in the training set.

**Time budget:** Half a day per piece once the format is locked in.

---

### Move 10 — Launch the Florida Parcel Tool with a Targeted Pitch (Week 6)

**Outcome:** The Florida tool is live, a focused Medium piece is published, and a deliberate distribution push reaches Florida real estate investor forums and LinkedIn groups.

- [ ] Streamlit deployment of the Florida parcel analysis tool
- [ ] Medium piece (1,000 words) covering what the tool does and a sample finding
- [ ] LinkedIn post for the general audience
- [ ] List of 5–10 Florida real estate investor forums, subreddits, and newsletters identified for targeted distribution
- [ ] Direct outreach to the top 3 of those communities (not spam — a contextual share)

**Definition of done:** First evidence (or first negative signal) about whether Patterns in Place can reach a practitioner audience beyond the data and tech community.

**Time budget:** Three days including outreach.

---

### Launch checklist summary

| Week | Move | Output |
|---|---|---|
| Day 1 | 1 — Claim names | All accounts created |
| Days 2–3 | 2 — Write README | Source-of-truth doc live |
| Days 3–5 | 3 — Structure GitHub | Six repos pinned |
| Week 1–2 | 4 — Deploy NYC tool | Streamlit URL live |
| Week 2 | 5 — Pipeline origin story | First Medium piece |
| Week 2–3 | 6 — Launch NYC tool | Coordinated three-platform launch |
| Week 3 | 7 — Visual library piece | Craft signal published |
| Week 4 | 8 — Overheating Index series | Two-part series live |
| Week 5 | 9 — First Data Take | Format established |
| Week 6 | 10 — Florida tool launch | Practitioner audience tested |

By end of week 6: one origin story, two scoring methodology pieces, one application piece, two tools live, one Data Take published, six repos pinned, three audiences tested. That is a real publication.

---

## 7. What to Defer (Don't Do These Yet)

- Standalone website beyond the GitHub org page and Medium publication (revisit at month 6)
- Newsletter platform (revisit once Medium subscriber count crosses 200)
- Chatbot public deployment (revisit at month 3)
- County and tract-level analyses below CBSA scale (revisit at month 3)
- Paid sponsorships or monetization of any kind (revisit at month 6+)
- Hiring or contracting help (revisit only if revenue exists)
- A second publication or product brand (don't)

---

## 8. Common Mistakes to Avoid

1. **Publishing before claiming.** If you publish on Medium before the GitHub org exists, the credibility chain breaks. Always claim first.
2. **Treating the tools as products instead of publication assets.** The NYC explorer and Florida parcel tool are credibility and distribution surfaces for the publication, not standalone products. Frame them that way.
3. **Drifting voice across pieces.** A single inconsistent piece undoes ten consistent ones. Use the methodology docs as a constant reference.
4. **Skipping the visual identity step.** A piece with default Matplotlib charts under the Patterns in Place masthead actively damages the brand.
5. **Publishing without cross-linking.** Every Medium piece links to GitHub. Every GitHub README links to the relevant Medium piece. Every Streamlit tool links to both.
6. **Going dark for two weeks.** Cadence is the only thing that compounds. A short Data Take is better than a delayed Metro Deep Dive.
7. **Confusing the audiences on the wrong channel.** Real estate investors don't live on the same channels as civic tech practitioners. See `distribution_strategy.md`.

---

## 9. The 6-Week Setup Summary

### Week 1
- [ ] Claim all names and accounts (Move 1)
- [ ] Draft and publish the publication README (Move 2)
- [ ] Pin the six GitHub repos (Move 3 — start)
- [ ] Lock visual identity (colors, type, wordmark)

### Week 2
- [ ] Deploy the NYC Neighborhood Explorer (Move 4)
- [ ] Publish the pipeline origin story (Move 5)
- [ ] Begin coordinated NYC tool launch (Move 6)

### Week 3
- [ ] Complete the NYC tool launch (Move 6)
- [ ] Publish the visual library piece (Move 7)
- [ ] Begin Overheating Index draft (Move 8 — start)

### Week 4
- [ ] Publish Overheating Index Part 1 (Move 8)
- [ ] Begin drafting Part 2

### Week 5
- [ ] Publish Overheating Index Part 2 (Move 8)
- [ ] Publish first Chatbot Q&A Data Take (Move 9)

### Week 6
- [ ] Deploy Florida parcel tool (Move 10)
- [ ] Targeted distribution push (Move 10)
- [ ] Retrospective: what worked, what to drop, what to repeat

---

## Next Up

Once the operational scaffolding is in place, move through the other docs:

1. `editorial_strategy.md` — what to publish (pillars, formats, audiences)
2. `distribution_strategy.md` — where to publish (platforms, cadence)
3. `asset_inventory.md` — what's already built and ready to ship
4. `growth_roadmap.md` — what comes after the first six weeks
5. `methodology/` — the standards docs that govern every piece

The single most leveraged thing you can do this week is Move 1. Claiming the names is the act that turns a project plan into a publication.
