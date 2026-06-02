# Editorial Strategy
## What Patterns in Place Publishes, For Whom, and How Often

This is the editorial offer. It defines the questions the publication answers, the formats every piece fits into, and the audiences each piece is written for. Every editorial decision — what to publish, what to skip, what to invest a month in — should be defensible against this doc.

---

## The Frame

Patterns in Place is not a portfolio and not a blog. It is a publication with a point of view. A publication is defined by the consistency of three things:

1. **The questions it answers** (the editorial pillars)
2. **The formats it answers them in** (the content types)
3. **The audiences it serves** (the readers it shows up for)

When those three things are tight and consistent, readers come back. When any one drifts, the publication becomes a personal blog with a logo on it.

---

## The Audiences

Patterns in Place serves four audiences simultaneously. Each piece should be written with one primary audience in mind, even if others end up reading it.

### Audience 1 — Real estate investors and analysts

**Who:** Independent investors, multifamily syndicators, REITs, broker-analysts, market intelligence teams at proptech companies.

**What they want:** Reliable market intelligence they can act on. Methodology they can trust. Markets they hadn't considered.

**Where they live:** LinkedIn, niche real estate forums (BiggerPockets, real estate investor Slack groups), targeted newsletters (Calculated Risk, John Burns), industry events.

**What converts them into regular readers:** A scoring model that ranks markets, applied consistently across geographies, with transparent methodology. The Overheating Index and Investment Score series exist for them.

### Audience 2 — Civic tech and open data practitioners

**Who:** Urban planners, GIS analysts, transportation researchers, public-sector data scientists, journalists at outlets like CityLab, Bloomberg Businessweek, The Pudding.

**What they want:** Reproducible methodology, open data lineage, well-documented pipelines, citable analyses. They will check your work.

**Where they live:** Twitter/X, GitHub, civic-tech Slack groups, Mastodon, niche mailing lists.

**What converts them into regular readers:** The pipeline origin story, the visual library piece, anything that demonstrates rigor under the hood. They become a referral channel for serious analyses.

### Audience 3 — Data and analytics hiring managers

**Who:** VPs of Data, Heads of Analytics, Founding Data hires, technical recruiters at companies that build data products or work with geographic data.

**What they want:** Evidence of someone who can do all three of "analyze, build, publish" — they see hundreds of resumes, very few public bodies of work.

**Where they live:** LinkedIn primarily. They also Google your name when reviewing applications.

**What converts them into a job conversation:** A coherent body of work that demonstrates range without seeming scattered. Patterns in Place becomes a portfolio that exists whether you're job-searching or not.

### Audience 4 — A general curious public

**Who:** People interested in cities and place. People considering a move. People who saw a chart on social media and clicked through.

**What they want:** A clear story about a real place. A surprising finding they didn't know. Something they can share at a dinner party.

**Where they live:** Medium, Reddit (r/dataisbeautiful, r/MapPorn, city-specific subreddits), LinkedIn shares from the other audiences.

**What converts them into regular readers:** A Place Story that makes them feel they understand a city better than they did before reading.

---

## The Five Editorial Pillars

Every piece published under Patterns in Place maps to one of five core questions. These are the brand promise to readers and the editorial filter for deciding what is worth producing. If a piece doesn't fit a pillar, don't write it.

### Pillar 1 — The Place Story

**Question it answers:** *How is this place changing and why?*

Deep narrative analyses of specific metros, CBSAs, and neighborhoods. The flagship pillar. A Place Story is a portrait painted in data.

**Primary audience:** General curious public, planners, locals.
**Typical format:** Metro Deep Dive (2,000–3,000 words).
**Cadence:** ~1 per month once cadence is established.
**Examples:** "Jacksonville: How a Mid-Size Metro Quietly Became a Logistics Capital." "What Happened to Dayton."

### Pillar 2 — The Comparison

**Question it answers:** *How does this place compare to its peers?*

Cross-metro peer analysis using the unified Bronze/Silver/Gold pipeline. The pillar that demonstrates the publication's structural advantage — the ability to consistently compare across geographies because the data is normalized.

**Primary audience:** Investors, analysts, hiring managers.
**Typical format:** Metro Deep Dive comparison section, or a standalone Opportunity List.
**Cadence:** ~2 per month.
**Examples:** "Five Sun Belt Metros That Aren't Phoenix." "How Indianapolis Compares to Its True Peers."

### Pillar 3 — The Opportunity Finder

**Question it answers:** *Where are the underrated opportunities?*

Ranked or curated market lists filtered through specific lenses. The most shareable pillar. These pieces convert browsers into regulars.

**Primary audience:** Investors, movers, developers.
**Typical format:** Opportunity List (800–1,200 words).
**Cadence:** Bi-weekly.
**Examples:** "10 Metros Where Wages Are Rising Faster Than Rents." "Where Builders Are Quietly Adding Supply." "The Mid-Size Cities With the Healthiest Young-Professional Pipelines."

### Pillar 4 — The Decision Guide

**Question it answers:** *Where should I live or invest?*

Practical, data-driven guidance for real decisions. The pillar that takes the publication beyond observation into application.

**Primary audience:** Individuals at a crossroads — career move, relocation, first investment.
**Typical format:** Opportunity List or hybrid Decision Guide (1,000–1,500 words).
**Cadence:** ~1 per month.
**Examples:** "Where a $200k Income Goes Furthest in 2026." "If You're Considering Florida, These Are the Three Markets to Look At First."

### Pillar 5 — The Contrarian Take

**Question it answers:** *What does the data say that conventional wisdom gets wrong?*

High-shareability pieces built around a single surprising finding. The pillar that drives reach.

**Primary audience:** Everyone.
**Typical format:** Data Take (500–900 words).
**Cadence:** Weekly.
**Examples:** "The Sun Belt Boom Is Already Slowing — Here's Where." "Why the Most Underbuilt Cities Aren't the Ones in the Headlines." "Population Growth Is a Worse Investment Signal Than You Think."

---

### Pillar coverage targets

A healthy publication ships across all five pillars over any given quarter. As a rough mix:

| Pillar | Share of pieces | Cadence |
|---|---|---|
| Place Story | 15% | Monthly |
| Comparison | 25% | 2/month |
| Opportunity Finder | 25% | Bi-weekly |
| Decision Guide | 10% | Monthly |
| Contrarian Take | 25% | Weekly |

If one pillar disappears for two months, that's a signal — either the data isn't supporting that pillar or the publication is drifting.

---

## The Three Content Formats

Every piece produced fits one of three formats. Each has a defined structure, a natural platform home, and a production path that fits the existing stack. Format discipline is what makes the publication feel like a publication.

### Format 1 — The Metro Deep Dive

The flagship format. Highest credibility, highest production cost, lowest frequency. A Metro Deep Dive is the format that establishes the publication as serious.

**Length:** 2,000–3,000 words.

**Structure:**
1. The thesis (one paragraph) — what this piece is going to claim
2. Population trends (with chart)
3. Economic structure (sectors, employment composition)
4. Housing dynamics (price, rent, supply, vacancy)
5. Affordability (income vs. cost ratios, with peer comparison)
6. Sub-metro opportunity (where within the metro is the action)
7. The takeaway (one paragraph) — what to do with this

**Platform path:** Quarto notebook on GitHub (methodology + reproducibility) → narrative adaptation on Medium (general reader) → key visual + insight on LinkedIn (distribution).

**Pillar coverage:** Place Story, Comparison.

**Cadence:** Monthly.

**Production budget:** 3–5 days of work spread over 1–2 weeks.

### Format 2 — The Opportunity List

The shareable workhorse. Shorter, more accessible, drives the most LinkedIn traffic and the most newsletter signups.

**Length:** 800–1,200 words.

**Structure:**
1. The premise (one paragraph) — what filter you applied and why
2. The methodology (one paragraph) — what data, what threshold, what scoring
3. The list (5–12 markets, neighborhoods, or places)
4. One to two sentences per item, plus one number that anchors the case
5. The takeaway

**Platform path:** Medium (primary) + LinkedIn carousel or single-image post (distribution).

**Pillar coverage:** Opportunity Finder, Decision Guide.

**Cadence:** Bi-weekly.

**Production budget:** 1–2 days once the underlying scoring or filter exists.

### Format 3 — The Data Take

The fast format. Focused, opinionated, built around a single finding or contrarian insight. One question, one dataset, one clear argument. The format that establishes weekly cadence.

**Length:** 500–900 words.

**Structure:**
1. The question (one sentence — usually as the headline)
2. The conventional wisdom (one paragraph)
3. The data (one chart or map)
4. What the data actually says (two to three paragraphs)
5. Why this matters (one paragraph)

**Platform path:** Medium + LinkedIn (primary distribution).

**Pillar coverage:** Contrarian Take primary, but any pillar can be served by a Data Take.

**Cadence:** Weekly.

**Production budget:** 4–6 hours once data is clean.

---

### Format mix and the publication rhythm

A typical month, once cadence is established:

| Week | Format(s) | Count |
|---|---|---|
| Week 1 | 1 Data Take + 1 Opportunity List | 2 pieces |
| Week 2 | 1 Data Take + 1 Metro Deep Dive (Part 1 — thesis and setup) | 2 pieces |
| Week 3 | 1 Data Take + 1 Opportunity List | 2 pieces |
| Week 4 | 1 Data Take + 1 Metro Deep Dive (Part 2 — full piece, or full release) | 2 pieces |

That is 8 pieces per month: 4 Data Takes, 2 Opportunity Lists, 1 Metro Deep Dive (released in two parts or as one). Three pieces per week is unsustainable solo; one Data Take + one larger piece per week is the right rhythm.

---

## The Three-Surface Rule

Every project — every analysis worth publishing — feeds all three audience types through three different entry points. This is the rule that separates a publication from a blog.

| Surface | Audience | Artifact |
|---|---|---|
| GitHub | Hiring managers, technical peers, civic tech practitioners | Quarto notebook with methodology, data, reproducibility |
| Medium | General public, investors, planners, analysts | Narrative adaptation with charts and the human story |
| LinkedIn | Hiring managers, professional network, distributed audience | One visual asset, one specific insight, one link |

Skipping any one surface means losing one of the audiences. The discipline of "three surfaces per project" is the editorial habit that keeps reach broad and depth credible at the same time.

See `distribution_strategy.md` for how each surface is operated.

---

## Editorial Decision Framework

When deciding whether to write a piece, run it through this filter:

1. **Pillar fit** — does it answer one of the five core questions? If no, don't write it.
2. **Format fit** — does it fit cleanly into one of the three formats? If it needs a new format, you're either writing for a different publication or you've found a real gap. Be skeptical of "new format" instincts in year one.
3. **Pipeline coverage** — can the existing Bronze/Silver/Gold layer answer the question, or does it need new ingestion? If it needs new ingestion, defer unless the analysis justifies the build.
4. **Visual** — is there at least one chart, map, or table that anchors the piece? If no, the piece is probably a tweet, not a Medium post.
5. **Audience** — who is this for, specifically? If you can't name one of the four audiences, don't write it.

A piece that passes all five is a piece worth shipping. A piece that fails one is a piece worth either reframing or dropping.

---

## What Patterns in Place Doesn't Publish

Discipline is what makes the publication coherent. The things below are explicit non-coverage areas.

- **National macro takes** — interest rate predictions, recession calls, GDP commentary. There are better outlets for that. Patterns in Place is about *place*.
- **Politics, except where the data inescapably points to a policy implication** — when you have to call out a zoning policy as the cause of a price pattern, do it. When you don't have to, don't.
- **Personal essays.** No "what I learned moving to Austin." Save those for a personal blog if you want them.
- **Hot takes without data.** Every piece must have an underlying dataset visible to the reader.
- **Coverage of metros where the data is weak.** ACS small-area estimates get shaky below ~20k population. Don't pretend otherwise.
- **Stock picks, REIT recommendations, or specific property recommendations.** Adjacent enough to look credible, far enough from your competence to create real liability.

---

## Editorial Voice

The voice rules in `publication_playbook.md` apply to every piece. Specific to editorial work:

- **Lead with the finding.** First sentence names the surprise.
- **Name the place.** "Jacksonville," not "a southern metro." Specificity is the asset.
- **Show the chart early.** Most readers won't make it past the first scroll. Put the visual in front of them.
- **Acknowledge limitations.** "ACS five-year estimates have a confidence interval of about X." Honest framing builds long-term trust.
- **No throat-clearing.** Skip the "in this piece I will examine" intro paragraphs.
- **Earn every adjective.** "Booming" needs a number. "Struggling" needs a number.
- **End on a takeaway, not a summary.** What should the reader do, think, or share?

---

## How Editorial Decisions Compound

A few small disciplines, repeated, become the publication's defensibility over time:

1. **Pillar adherence.** Five years in, "Patterns in Place answers these five questions" is stronger as a brand promise than any tagline.
2. **Format consistency.** Readers learn what to expect. A Data Take is always a Data Take. A Metro Deep Dive is always a Metro Deep Dive.
3. **Voice consistency.** The same person could read a 2026 piece and a 2030 piece and recognize them as belonging to the same publication.
4. **Cross-linking discipline.** Every Metro Deep Dive of Jacksonville links back to the previous one. Every Overheating Index application piece links to the methodology. The internal link graph compounds into an authority graph.
5. **Visual identity discipline.** Charts that look like Patterns in Place charts get recognized in Slack screenshots, in newsletter forwards, in conference slides. The visual library is an editorial asset, not a design asset.

---

## How This Doc Sits Alongside the Others

- `publication_playbook.md` — operational setup. What accounts to claim, how to launch.
- `editorial_strategy.md` — *this doc.* What to publish.
- `distribution_strategy.md` — where each piece goes and how often.
- `asset_inventory.md` — what's already built that pieces can draw from.
- `growth_roadmap.md` — how the editorial scope expands over months.
- `methodology/editorial_pillars.md` — the deeper operating manual for each pillar.
- `methodology/format_standards.md` — the structural specs for each format.

When in doubt about whether to write a piece, the order to consult is: this doc → `methodology/editorial_pillars.md` → `methodology/format_standards.md`.

---

## Next Up

Once the editorial strategy is locked, move on to:

1. `distribution_strategy.md` — how each piece reaches the right audience on the right platform.
2. `methodology/editorial_pillars.md` — the deep operating manual for each pillar.
3. `methodology/format_standards.md` — the production specs for each format.

The single most leveraged thing this strategy gives you is the right to *say no* to pieces that don't fit. That right, exercised consistently, is what makes Patterns in Place a publication.
