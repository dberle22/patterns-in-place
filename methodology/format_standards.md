# Format Standards

## Purpose

This document defines the structural specifications for the three Patterns in Place content formats: the Metro Deep Dive, the Opportunity List, and the Data Take. Every published piece fits one of these three formats. Format discipline is what makes the publication feel like a publication.

If you're about to start a piece and unsure how to scope it, read this document first.

---

## Why This Standard Exists

Independent publications often start strong and slowly devolve into "long when I have time, short when I don't, and inconsistent when I'm tired." Reader expectations don't form. Production time balloons. The publication becomes a personal blog with a logo on it.

Three defined formats fixes this. Each format has a length range, a structural skeleton, a platform path, and a production budget. Once you've shipped two of each, you have muscle memory; the marginal cost of the next one is dramatically lower than the first.

This doc is the production manual for each format.

---

## The Three Formats

### Format 1 — The Metro Deep Dive

The flagship format. Highest credibility, highest production cost, lowest frequency. A Metro Deep Dive is what a reader sends to a friend with the message "you have to read this."

#### Length and scope

- **Word count:** 2,000–3,000 words
- **Visual count:** 4–8 charts and maps
- **Time investment:** 3–5 working days spread across 1–2 weeks
- **Cadence target:** 1 per month sustained

#### Structural skeleton

```
1. The thesis (one paragraph)
   - State what this piece is going to claim
   - Anchor in one specific number or surprising fact

2. Population trends
   - Multi-decade chart
   - One-paragraph narrative

3. Economic structure
   - Sectors, employment composition
   - Dot plot or stacked area chart of sector share over time
   - One-paragraph narrative

4. Housing dynamics
   - Price, rent, supply, vacancy
   - 2–3 charts
   - 2–3 paragraphs

5. Affordability
   - Income vs. cost ratios
   - Peer comparison (anchors the next section)
   - 1 chart, 2 paragraphs

6. Sub-metro opportunity
   - Where within the metro is the action
   - Map or small multiples
   - 2–3 paragraphs

7. The takeaway (one paragraph)
   - What to do with this analysis
   - What to watch next
```

#### What every Metro Deep Dive must do

- Open with the thesis in the first paragraph (no throat-clearing)
- Anchor every claim in a specific number from the data pipeline
- Include at least one peer comparison
- Include at least one map
- Cite every data source explicitly (with date) at the bottom
- End with a forward-looking observation, not a summary

#### What a Metro Deep Dive must not do

- Tell a generic narrative ("the rise of the Sun Belt") — name the place, name the mechanism
- Cover a metro where the data is too thin to support 2,500 words
- Skip the peer comparison
- Use stock images
- Recap the methodology — link to the methodology pieces (Overheating Index, Investment Score, pipeline origin) instead

#### Platform path

```
GitHub:    Quarto notebook with full reproducibility
Medium:    Narrative adaptation with charts
LinkedIn:  Hero visual + thesis + link (one launch post)
LinkedIn:  Second post 2–3 days later — a different angle from the same piece
Newsletter: Featured piece in the next issue
```

#### Pillar coverage

- Place Story (primary)
- Comparison (secondary, via the peer comparison section)

#### Production rhythm (typical 5-day budget)

| Day | Focus |
|---|---|
| 1 | Pull data, draft outline, identify the thesis |
| 2 | Build the visuals (with visual library applied) |
| 3 | Draft sections 1–4 |
| 4 | Draft sections 5–7, integrate visuals |
| 5 | Edit, fact-check, source citation, ship |

---

### Format 2 — The Opportunity List

The shareable workhorse. Drives the most LinkedIn traffic, the most newsletter signups, and the most "I had not considered this" responses.

#### Length and scope

- **Word count:** 800–1,200 words
- **Visual count:** 1–3 charts or maps + a structured list
- **Time investment:** 1–2 working days once the underlying scoring or filter exists
- **Cadence target:** Bi-weekly

#### Structural skeleton

```
1. The premise (one paragraph)
   - What filter you applied
   - Why that filter is interesting

2. The methodology (one paragraph)
   - What data, what threshold, what scoring
   - Cite the underlying methodology piece if one exists

3. The list (5–12 places)
   - For each place:
     - Place name and one anchoring number
     - One to two sentences explaining the fit
     - Optionally: one specific watch-item

4. The takeaway (one paragraph)
   - What this list reveals collectively
   - What to do with the list
```

#### What every Opportunity List must do

- State the filter and methodology in the first 200 words
- Show the methodology link or methodology paragraph — don't hide the math
- Include at least one anchoring number per item
- Use the same structural pattern for every item (consistency makes the list scannable)
- Acknowledge what a candidate would have to fail to disqualify it

#### What an Opportunity List must not do

- Give "investment advice" or "buy" recommendations
- List places without explanation
- Cover places where the data is too thin
- Vary the structure between items
- Bury the methodology

#### Platform path

```
Medium:    Primary publication
LinkedIn:  Carousel format if visual-heavy; single image post otherwise
LinkedIn:  Optional second post a few days later — pull out one item with deeper context
Newsletter: Highlighted in the monthly issue
```

#### Pillar coverage

- Opportunity Finder (primary)
- Decision Guide (secondary, when the filter maps to a relocation or investment context)

#### Production rhythm (typical 1.5-day budget)

| Day | Focus |
|---|---|
| 1 (morning) | Run the filter, pull the data, validate the list |
| 1 (afternoon) | Draft the premise + methodology paragraphs, draft list entries |
| 2 (morning) | Build visuals, edit, ship |

---

### Format 3 — The Data Take

The fast format. Focused, opinionated, built around a single finding. One question, one dataset, one clear argument. The format that establishes weekly cadence.

#### Length and scope

- **Word count:** 500–900 words
- **Visual count:** 1 chart or map (occasionally 2)
- **Time investment:** 4–6 hours once data is clean
- **Cadence target:** Weekly

#### Structural skeleton

```
1. The question (the headline + one-sentence framing)

2. The conventional wisdom (one paragraph)
   - What the reader probably believes coming in

3. The data (one chart or map)
   - The visual that anchors the piece

4. What the data actually says (2–3 paragraphs)
   - The finding
   - The mechanism — why the data tells this story

5. Why this matters (one paragraph)
   - What to update going forward
   - What this implies for related questions
```

#### What every Data Take must do

- Open with the question (often as the headline) and a one-sentence framing
- Surface a specific finding in the first 200 words
- Include exactly one anchoring visual
- Stay opinionated — no "it depends" hedging
- Close with a clear "update your model" takeaway

#### What a Data Take must not do

- Try to be comprehensive
- Include more than one chart unless absolutely necessary
- Hedge the finding into uselessness
- Read like an academic abstract
- Drift past 1,000 words (if it's drifting, it might want to be an Opportunity List instead)

#### Platform path

```
Medium:    Primary publication (often the same day)
LinkedIn:  Single-image post within hours of Medium publishing
LinkedIn:  Optional follow-up post 3 days later if engagement signals merit
```

#### Pillar coverage

- Contrarian Take (primary)
- Any pillar can be served by a Data Take when the finding is sharp enough

#### Production rhythm (typical half-day budget)

| Block | Focus |
|---|---|
| 90 min | Pull data, validate the finding, build the visual |
| 90 min | Draft the piece |
| 60 min | Edit, ship to Medium, post to LinkedIn |

---

## Format Selection — Decision Tree

When you have an idea, run it through this tree:

1. Is this about *one specific place* (a metro, county, neighborhood) and does it warrant 2,500 words of analysis? → **Metro Deep Dive**
2. Is this a list of 5–12 places filtered by a defined methodology? → **Opportunity List**
3. Is this one specific finding, one chart, one argument? → **Data Take**
4. Is this something else? → either reframe to fit one of the three, or don't write it

Resist the instinct to invent a fourth format. Three formats cover the full production envelope a solo operator can sustain. New formats add real ongoing cost.

---

## The Three-Surface Rule (every format)

Every piece, regardless of format, ships across three surfaces:

| Surface | Role |
|---|---|
| GitHub | Methodology, reproducibility (Quarto notebook for Deep Dives; analysis script reference for Lists and Takes when relevant) |
| Medium | The narrative adaptation that the general audience reads |
| LinkedIn | The visual + insight + link that drives reach |

A piece that ships only to one surface is leaving the other audiences uncovered. The three-surface rule is the most important production discipline in this doc.

---

## Format Anti-Patterns

Things that look like format choices but actually break the system:

- **Long Data Takes.** A Data Take that hits 1,200 words wants to be an Opportunity List. Reframe it.
- **Thin Metro Deep Dives.** A Metro Deep Dive at 1,500 words is a Data Take in a tuxedo. Either expand it properly or downsize the format.
- **Opportunity Lists with one entry that gets all the attention.** That entry wants to be a Data Take. Pull it out.
- **Multi-piece series that aren't really series.** If two Data Takes share a thesis, they're one Opportunity List in disguise.
- **"Special editions" that break the format.** Discipline now beats experimentation in year one.

---

## Format Evolution Rules

These specs are the v1 standards. They will evolve as the publication learns what works.

- **A format spec gets updated** when 8+ pieces in that format have shipped and a clear pattern of "this works better" has emerged
- **A new format gets added** only when at least three pieces have been written in a "format that doesn't fit" pattern AND the gap is consistent across pillars
- **A format gets retired** if it produces fewer than two pieces in six months and engagement on those pieces is below average

Update this doc when any of those conditions trigger.

---

## How This Doc Sits Alongside the Others

- `../editorial_strategy.md` — strategy-level format overview
- `../distribution_strategy.md` — how each format reaches each platform
- `editorial_pillars.md` — what each piece is *about*
- `format_standards.md` — *this doc.* What each piece is *shaped like*.
- `data_pipeline_standards.md` — what the underlying data can support
- `visual_design_standards.md` — how the charts and maps look

When in doubt about how to scope a piece, the order to consult is: this doc → editorial_pillars.md → just start writing.
