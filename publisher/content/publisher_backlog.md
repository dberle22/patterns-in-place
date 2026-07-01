# Publisher Content Backlog
**Last updated:** 2026-06-30

---

## Strategy

Two independent content tracks. They serve different communities and can run in parallel — a reader can come from either direction and encounter the other.

**Track 1 — Technical writing:** How this platform was built. DuckDB, DWH design, ETL patterns, semantic layers, R-based data viz, multi-frame scoring models. Audience: data engineers, analysts, developers. Entry point: professional communities (dbt Slack, DuckDB Discord, r/datascience, LinkedIn, Substack tech writers). Goal: professional credibility and portfolio.

**Track 2 — Data analysis writing:** What the platform finds. Metro patterns, neighborhood economics, the Intelligence frame findings. Audience: urban policy, housing, real estate, economic geography communities. Entry point: Substack, X, City Observatory, Strong Towns, Reddit urban planning communities. Goal: participate in conversations that are already happening with something novel to add.

The most powerful single post sits at the intersection: here's a surprising finding about a city, and here's the data infrastructure that made it possible to see. Write a few of each track first, then find the crossover angle.

See `reference_landscape.md` for the publications, writers, and communities to engage with.

---

## Workflow (per post)

```
1. QUESTION   — pick the question; state what you're trying to show and for whom
2. VISUAL     — decide the chart type and what dimensions the reader needs to see
3. SQL/R      — write the query by hand against DuckDB; render in R
4. EXECUTE    — run; save result as result.csv and chart.png
5. WRITE      — data-first interpretation; what's surprising, what it means
6. PUBLISH    — Substack post + X thread (280-char hook + chart)
7. NOTES      — what worked, what didn't, how long it actually took
```

Each post lives in `publisher/output/{post_id}/` and produces:
```
publisher/output/{post_id}/
    question.md       ← the question, intent, and visual rationale
    query.sql         ← hand-written SQL
    result.csv        ← output dataframe
    chart.png         ← R chart output
    post_draft.md     ← Substack post + X thread
    notes.md          ← what worked, what didn't, how long it took
```

---

## Post Tracker

| ID | Track | Topic | Status | Notes |
|----|-------|-------|--------|-------|
| p001 | — | — | — | First post — pick from backlog below |

---

## Track 1 — Technical Writing Backlog

These are process and build posts. The audience is people who build data systems or want to.

**The platform build series (most natural starting point):**
- Why I built a semantic layer before building any dashboards — and what it forced me to see
- DuckDB as a local analytical data warehouse: what works and what doesn't at 20+ table scale
- How I designed a three-frame scoring model from scratch with no labeled training data
- Building a catalog-driven Streamlit app: the `metric_catalog.yml` pattern
- ETL in R for ACS data: a pattern that actually scales across 14 source tracks
- Why I separated Gold tables from Intelligence marts — and when to break that rule
- Soft cluster membership (GMM) vs. hard labels: when ambiguity is the honest answer

**Data engineering specifics:**
- Handling missingness at 396-CBSA, 400-metric scale: why median imputation was the right call
- The within/national IQR ratio: a simple diagnostic for whether a KPI adds zone-level signal
- How I built a crosswalk-based spatial join pipeline for tract, ZCTA, county, and CBSA grains

---

## Track 2 — Data Analysis Writing Backlog

These are findings posts. The audience is people who care about cities and neighborhoods.

**Intelligence frame findings (calibrated, ready to write):**
- The L/O scatter: which metros have high livability but low opportunity — and what that gap looks like on the ground
- The Southern health deficit: why Southern metros cluster differently on livability and what's driving it
- Social capital and economic mobility: what the Opportunity Insights data shows when you put it next to our frame scores
- Hidden winners: metros that score in the bottom half nationally but are trending strongly positive on trajectory
- The divergence list: metros that rank top-20 on one frame and bottom-100 on another — what that means

**Metro character archetypes (from Phase 2 clusters):**
- What "Sun Belt Growth" actually means as a metro type: the seven character clusters explained
- The Immigrant Gateway cluster: which metros define it and why it's analytically distinct

**Housing and economics (Gold table data, no Intelligence framing needed):**
- Rent burden by metro: the tightest and most affordable markets in 2023
- Vacancy rate as a market signal: how to read it beyond the headline number
- Permits per housing unit: who is actually building and who is talking about it
- Income growth vs. rent growth scatter: which metros are getting more and less affordable

**Neighborhood economics (Phase 7 preview — write after zone work is done):**
- What a Knowledge Corridor actually looks like in the data: the tract-level profile
- The distressed/thriving split inside a single metro: why CBSA-level analysis misses the story

---

## Learnings Log

Captured after each post. Feeds pipeline integration decisions later.

*(empty — fill after first post)*

---

## Pipeline Integration (deferred)

After 3–5 manual posts, revisit:
- Which steps were mechanical and repeatable? → candidates for automation
- Which steps required judgment? → keep manual
- What does the existing chatbot pipeline get right vs. wrong for this workflow?
