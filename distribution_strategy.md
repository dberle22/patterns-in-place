# Distribution Strategy
## Where Patterns in Place Shows Up, To Whom, and How Often

This is the distribution layer. The editorial strategy defines what gets published; this doc defines where each piece goes, what role each platform plays, and how the cross-platform rhythm actually works in practice.

A publication is only as good as its distribution. Brilliant analysis with no readers is a private journal. Patterns in Place reaches its four audiences through four platforms, each with a different role.

---

## The Frame

```
                    PATTERNS IN PLACE
                          │
   ┌──────────┬───────────┼───────────┬──────────┐
   │          │           │           │          │
 GitHub    Medium     LinkedIn    Streamlit   Newsletter
   │          │           │           │       (later)
Credibility  Depth   Distribution   Tools     Owned audience
```

Four platforms, one publication. Different jobs, different audiences, different cadences. Same voice.

---

## Platform Architecture

| Platform | Role | Primary Audience | Cadence |
|---|---|---|---|
| GitHub (PatternsInPlace org) | Technical home base. All repos, notebooks, methodology. The credibility layer. | Hiring managers, technical peers, civic tech | Ongoing commits; one polished repo per major project |
| Medium | Primary long-form publishing home. Narrative adaptations of all analyses. Organic discoverability. | General public, investors, planners, analysts | 1 piece per project; 2–4 per month sustained |
| LinkedIn | Distribution and visibility engine. Visual outputs and short takeaways drive traffic to longer pieces. | Hiring managers, professional network, investors | 2–3 posts per project; 8–12 per month sustained |
| Streamlit / Shinyapps | Interactive tool deployment. The differentiator layer. Tools are the publication's most defensible asset. | Practitioners, investors, general public | 1 deployed tool per major analysis; 2–4 live by end of month 2 |
| Newsletter (later) | Owned audience. The only channel you control. Activated at month 3+. | All four audiences, segmented when scale justifies | 1–2 per month |

---

## Platform 1 — GitHub (the credibility layer)

GitHub is the credibility surface. Hiring managers and technical peers look here first. Civic tech practitioners assess your work here before they decide whether to share it. The publication's structural advantage — the Bronze/Silver/Gold pipeline — only counts if it's visible.

### What lives on GitHub

- **`publication-index`** — the org-level README and a single page that links to every published analysis, tool, and repo. Updated with every release.
- **`data-pipeline`** — the Bronze/Silver/Gold ingestion code, normalized schemas, and methodology docs. The thing that makes the rest possible.
- **`visual-library`** — design system, chart templates, color tokens. Linked from every analysis repo.
- **`nyc-neighborhood-explorer`** — Streamlit app source, tract-level data, README pointing to the live deployment.
- **`market-scoring-models`** — Overheating Index and Investment Score, with reproducible Quarto notebooks.
- **`florida-parcel-analysis`** — parcel-level analysis tool source and methodology.
- **(Future) `metro-deep-dives`** — one Quarto notebook per Metro Deep Dive published. The reproducibility companion to the Medium piece.

### Repo discipline

Every repo gets:

- A **README** that explains what the repo is, who it's for, and how to use it (this is non-negotiable)
- A **LICENSE** (MIT for code, CC-BY-SA for analyses by default — decided per repo)
- A **link back** to the relevant Medium piece if one exists
- A **link to the visual identity repo** so reproducers get the look right
- A **CHANGELOG** for repos that update over time

### What not to do on GitHub

- Don't publish unfinished work. Half-done repos hurt more than no repos.
- Don't include API keys, even private ones, even if the repo is private.
- Don't write for technical peers exclusively. The README is also read by hiring managers — write for both.

### Cadence

GitHub is "always on." Commits land continuously, but polished updates (new repo, new release, README revision) come in coordinated waves with Medium and LinkedIn launches.

---

## Platform 2 — Medium (the depth layer)

Medium is the long-form home and the discovery engine. Its surface is where general readers, investors, and journalists encounter the publication for the first time.

### Why Medium

- Built-in audience for data-rich, well-written pieces
- Organic discovery via tags, recommendations, and the Medium homepage
- Publication structure (header, masthead, masthead description, tags) maps cleanly to "Patterns in Place" branding
- Lower friction than maintaining a self-hosted blog in year one — re-evaluate at month 6

### What goes on Medium

Every Metro Deep Dive, every Opportunity List, and every Data Take. Not every Medium piece needs a GitHub companion, but every GitHub release should have a Medium companion piece.

### Medium publication setup

- Publication name: Patterns in Place
- Tagline: "Independent urban data — what's changing, where, and why"
- Sections: Place Stories, Comparisons, Opportunity Finder, Decision Guide, Data Takes (mapped to the five pillars)
- Tags to apply consistently: Data, Real Estate, Urban Planning, Demographics, Cities — plus city-specific tags for individual pieces

### Medium discipline

- **Headlines:** Specific, finding-first. "Five Sun Belt Metros That Aren't Phoenix" beats "An Analysis of Sun Belt Metros."
- **Subheads:** One subhead per ~300 words. Readers scan.
- **Hero image:** Always a chart or map from the piece, never a stock photo. Visual identity matters.
- **CTA at the end:** Link to GitHub repo (if one exists), link to the relevant tool, link to subscribe to the publication.
- **Tag with discipline.** Three to five tags per piece, consistent across the publication.

### Cadence

Two to four pieces per month. The default rhythm:
- Week 1: 1 Data Take + 1 Opportunity List
- Week 2: 1 Data Take + work on the Metro Deep Dive
- Week 3: 1 Data Take + 1 Opportunity List
- Week 4: 1 Data Take + the Metro Deep Dive ships

That's eight pieces per month at full cadence. Realistic month-one target: four pieces.

---

## Platform 3 — LinkedIn (the distribution engine)

LinkedIn is the visibility engine. Most of the publication's first-year reach will come from LinkedIn — both for inbound consulting/hiring conversations and for general readership growth.

### Why LinkedIn

- Hiring managers, B2B operators, investors, and journalists all live there
- Visual content (maps, charts, screenshots) performs unusually well in the algorithm
- Single-image posts and carousels are the best LinkedIn formats for data work
- LinkedIn's reach for non-monetized organic content is still meaningful (unlike most platforms in 2026)

### What goes on LinkedIn

- A teaser post for every Medium piece — visual + insight + link
- Standalone short-form posts about findings that don't merit a full Medium piece
- Behind-the-scenes process posts (rare, intentional) — "here's a chart that didn't make the cut and why"
- Tool launches (Streamlit deployments) with screen captures

### LinkedIn post anatomy

The format that works for data publications:

- **Hook (line 1):** A specific finding or counterintuitive number
- **Context (2–4 lines):** Why this finding matters
- **The visual:** One image — a chart, map, or screen capture
- **The takeaway (2–3 lines):** What to do with this
- **The link:** Medium piece, tool, or GitHub repo — always linked, never withheld

Aim for 150–300 words. Long enough to be substantive, short enough to read in a feed.

### LinkedIn cadence

- 2–3 posts per major project (one launch post, one follow-up insight, one piece-of-the-process or behind-the-scenes)
- 8–12 posts per month sustained
- Mid-week, mid-morning ET tends to perform best
- Never two posts on the same day; never go two weeks without posting

### What not to do on LinkedIn

- Don't reframe pieces for a tracking-plan or B2B SaaS audience. That's a different venture (see `multi_venture_strategy.md` in the consulting folder if relevant). Patterns in Place posts on LinkedIn are about cities and place.
- Don't use stock images. The publication's visual identity is the asset.
- Don't post without linking. The whole point is to drive traffic to GitHub, Medium, or a tool.
- Don't post on weekends in volume — investors and hiring managers are off.

---

## Platform 4 — Streamlit and Shinyapps (the differentiator layer)

Tools are what separate Patterns in Place from a data blog. A live, interactive map or scoring tool sticks in a reader's mind in a way an article doesn't.

### Why interactive tools matter

- They demonstrate technical capability immediately and concretely
- They give readers something to do — not just consume
- They are the most shareable artifact in the entire publication (a tool URL gets forwarded; an article gets read once)
- They become the link in every Medium piece, every LinkedIn post, and every conversation

### Tools roadmap (priority order)

1. **NYC Neighborhood Explorer** — already built, deploy in week 1–2
2. **Florida Parcel Analysis** — already built, deploy in week 6
3. **Overheating Index dashboard** — interactive version of the scoring model, month 2–3
4. **Investment Score dashboard** — pairs with Overheating Index, month 2–3
5. **Chatbot** — public beta at month 3–4

### Tool deployment discipline

- Deploy on Streamlit Community Cloud (free tier) in year one
- Migrate paid or higher-traffic tools to Streamlit Cloud paid tier or fly.io once usage justifies it
- Every deployed tool carries the Patterns in Place wordmark in the header
- Every tool has an "About" panel with a one-paragraph explanation
- Every tool links back to the relevant Medium piece and GitHub repo
- Every tool is mobile-tested before launch

### Cadence

One deployed tool per major analysis. Two to four live by end of month 2. Five or more by end of month 6.

---

## Platform 5 — Newsletter (activated at month 3+)

The newsletter is the long-term defensibility layer — the only channel you fully own. Don't activate it until there's something worth subscribing to.

### When to launch

After three Metro Deep Dives, six Opportunity Lists, and ten Data Takes are published. Roughly month 3.

### Where to host

Substack or Beehiiv. Substack for simplicity, Beehiiv for better growth tooling once volume justifies it.

### Cadence

One to two issues per month. Each issue: a roundup of recent pieces + one exclusive finding or chart that hasn't appeared elsewhere.

### Why this is the most important long-term move

- Owned audience — no algorithm change can take it away
- Email subscribers convert to readers at 5–10x the rate of social followers
- A 2,000-subscriber list of the right people is more valuable than 10,000 LinkedIn followers
- The newsletter becomes the asset that monetizes (sponsorships, paid tier, eventually book)

---

## Cross-Platform Rhythm

The discipline that makes the publication work is *coordinated multi-platform releases*. A piece doesn't ship to one platform; it ships across the stack.

### The launch sequence for a Metro Deep Dive

```
Day -3: Quarto notebook finalized, committed to GitHub repo
Day -2: Medium piece drafted; visual identity applied to charts
Day -1: GitHub repo README updated with link to forthcoming Medium piece
Day  0: Medium piece published; LinkedIn launch post goes live within an hour
Day +1: Second LinkedIn post — a different insight from the same analysis
Day +3: Third LinkedIn post — a chart that didn't make the Medium piece
Day +7: Newsletter issue (when newsletter is live) features the piece
Day +14: First reference back to this piece in a Data Take or Opportunity List
```

### The launch sequence for a Data Take

```
Day  0 (morning): Medium piece published
Day  0 (afternoon): LinkedIn post with the visual + insight + link
Day +3 (optional): A short follow-up LinkedIn post if engagement signals merit it
```

### The launch sequence for a tool

```
Day -7: Tool deployed to Streamlit Community Cloud, tested
Day -3: Medium piece drafted explaining what the tool does and a sample finding
Day -1: GitHub repo public with full README
Day  0: Medium piece + LinkedIn post + tool URL all live within the same hour
Day +2: Second LinkedIn post showing a specific use case
Day +7: Targeted distribution to relevant communities (only for tools, only when there's a clear community fit — e.g., Florida real estate forums for the Florida tool)
```

---

## The Post Bank

Twenty-five starter ideas pulled from the existing inventory and editorial pillars. Use this when stuck for what to publish.

### Place Stories (Pillar 1)
1. Jacksonville: How a Mid-Size Metro Quietly Became a Logistics Capital
2. What Happened to Dayton (and What Other Rust Belt Cities Can Learn)
3. Salt Lake City: The Sun Belt Metro Nobody Calls a Sun Belt Metro
4. Charlotte's Quiet Reinvention as a Banking-and-Tech Hybrid
5. Tampa Bay's Three Different Housing Markets

### Comparisons (Pillar 2)
6. Five Sun Belt Metros That Aren't Phoenix
7. How Indianapolis Compares to Its True Peers
8. Cleveland vs. Pittsburgh: A Tale of Two Recoveries
9. The Three Mid-Atlantic Metros Nobody Talks About
10. Why Boise and Bend Aren't As Similar As You Think

### Opportunity Finder (Pillar 3)
11. 10 Metros Where Wages Are Rising Faster Than Rents
12. Where Builders Are Quietly Adding Supply
13. The Mid-Size Cities With the Healthiest Young-Professional Pipelines
14. Five Counties Where Owner-Occupancy Is Climbing
15. The Neighborhoods With the Strongest Population Inflows

### Decision Guide (Pillar 4)
16. Where a $200k Income Goes Furthest in 2026
17. If You're Considering Florida, These Are the Three Markets to Look At First
18. The Best Metros for First-Time Investors With $100k
19. Where Remote Workers Are Actually Moving (And Where They Aren't)
20. The Three Cities I'd Live in if I Wanted Walkability Without the Northeast Premium

### Contrarian Take / Data Take (Pillar 5)
21. The Sun Belt Boom Is Already Slowing — Here's Where
22. Why the Most Underbuilt Cities Aren't the Ones in the Headlines
23. Population Growth Is a Worse Investment Signal Than You Think
24. The Real Reason Coastal California Is Losing Households
25. Why Affordability Indexes Are Lying to You About Three Specific Cities

By the end of three months, half of these should be published or in production. The other half become the next quarter's pipeline.

---

## Anti-Patterns

Six things that will sink the distribution strategy:

1. **Posting to one platform and forgetting the others.** A Medium piece without a LinkedIn post leaves 80% of the reach on the table.
2. **Posting to LinkedIn without linking.** Engagement-bait posts that withhold the link don't compound. Link to the work.
3. **Treating LinkedIn as a feed for both ventures.** Investors and hiring managers don't want tracking-plan content mixed with urban data content. Keep the channels segmented.
4. **Going dark for three weeks.** Cadence is the asset. A short Data Take is better than a delayed Metro Deep Dive.
5. **Skipping the visual identity.** Default chart styles signal amateur. Use the visual library every time.
6. **Building tools without writing about them.** A Streamlit deployment with no Medium piece is a private experiment.

---

## Measurement

Track these monthly. Trends matter more than absolute numbers in year one.

| Metric | Target by month 3 | Target by month 6 |
|---|---|---|
| Medium followers (publication) | 200 | 1,000 |
| Average claps per piece | 25 | 100 |
| LinkedIn page followers | 200 | 1,000 |
| LinkedIn average post impressions | 1,500 | 5,000 |
| GitHub org stars (across repos) | 50 | 250 |
| Streamlit tool sessions/month | 200 | 2,000 |
| Newsletter subscribers (when active) | 100 | 500 |
| Inbound conversations (job, partnership, press) | 1/month | 1/week |

If by month 6 these aren't tracking, the diagnosis is almost always one of two things:
1. Cadence dropped below twice a week — fix: lower the bar, ship Data Takes faster
2. Pieces aren't pillar-aligned — fix: re-read `editorial_strategy.md` and tighten the editorial filter

---

## Audience-Specific Tactics

### Reaching Audience 1 (real estate investors and analysts)

- LinkedIn is the primary channel
- Targeted distribution to BiggerPockets, real estate Slack groups, niche newsletters when a piece is specifically actionable for them
- The Florida parcel tool is the wedge product — use it as the on-ramp

### Reaching Audience 2 (civic tech and open data practitioners)

- Twitter/X for organic reach (low-effort cross-posting from LinkedIn)
- Hacker News submissions for major launches ("Show HN: An interactive map of NYC neighborhoods by census tract")
- Civic tech Slack groups (Code for America, urban-informatics communities) for methodology pieces
- The pipeline origin story is the hook

### Reaching Audience 3 (hiring managers)

- LinkedIn page + your personal LinkedIn profile linking to it
- Pinned Medium pieces and pinned GitHub repos in your personal LinkedIn Featured section
- The visual library piece signals craft; the Metro Deep Dive signals depth

### Reaching Audience 4 (general public)

- Medium's organic discovery
- LinkedIn shares from the other audiences
- Reddit submissions (r/dataisbeautiful, r/MapPorn, city-specific subreddits) for the most visual pieces
- The Place Story format is what brings them back

---

## How This Doc Sits Alongside the Others

- `publication_playbook.md` — operational setup. What accounts to claim and when.
- `editorial_strategy.md` — what to publish. The pillars and formats.
- `distribution_strategy.md` — *this doc.* Where each piece goes.
- `asset_inventory.md` — what's already built and ready to launch on each platform.
- `growth_roadmap.md` — how distribution scope expands over months.
- `methodology/` — the deep operating manual.

When deciding "should I post this on LinkedIn?", the order to consult is: this doc → `editorial_strategy.md` (does it fit a pillar?) → just post it, the right answer is almost always yes.

---

## Next Up

Once distribution is locked in, move on to:

1. `asset_inventory.md` — exactly what's already built and what state it's in.
2. `growth_roadmap.md` — how the publication evolves past the first six weeks.
3. `methodology/format_standards.md` — the production specs that make every piece feel consistent.

The distribution muscle gets built by *doing it weekly*. Twelve months of weekly Data Takes plus monthly Metro Deep Dives plus the occasional tool launch will create a publication that no competitor can replicate by trying harder for three months.
