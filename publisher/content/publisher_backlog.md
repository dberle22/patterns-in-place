# Daily Data Publisher — Backlog
**Last updated:** 2026-05-13  
**Spec:** [daily_data_publisher_spec.md](daily_data_publisher_spec.md)  
**Owner key:** 🤖 Agent &nbsp;|&nbsp; 👤 Me &nbsp;|&nbsp; 🤝 Both

---

## Approach

Build each post manually from scratch. No parsers, no runners, no orchestration. Pick a question, decide on the best visual, write the SQL, run R, write the copy. Learn what works. Once the manual workflow is proven across several posts, decide what to automate and how to fit it into the existing pipeline.

---

## The Workflow (per post)

```
1. QUESTION   — pick the question; state what you're trying to show and for whom
2. VISUAL     — decide the chart type and what dimensions the reader needs to see
3. SQL        — write the query by hand against DuckDB
4. EXECUTE    — run the SQL; save result as result.csv
5. CHART      — call R to render the chart; save as chart.png
6. SUMMARY    — write a short data-first interpretation of the output
7. SOCIAL     — refine for X (280 chars) and/or Substack caption
```

Each post lives in `publisher/output/{post_id}/` and produces:
```
publisher/output/{post_id}/
    question.md       ← the question, intent, and visual rationale
    query.sql         ← hand-written SQL
    result.csv        ← output dataframe
    chart.png         ← R chart output
    summary.md        ← written interpretation
    post_draft.md     ← X post + Substack caption
    notes.md          ← what worked, what didn't, what to change
```

---

## Post Tracker

| ID | Question | Template | Status | Notes |
|----|----------|----------|--------|-------|
| p001 | TBD | TBD | — | First post — pick in session |

---

## Question Bank

Questions to draw from. Not fully specified — review and refine before running.

We are switching to a Topic mdoel instead of a chart output model. This brings us closer to insights and allows us to flexibly ship multiple interesting views of the same topic.

These include:
- Housing
    - Vacancy Rates
    - New Builds
    - Owner vs Buyer
- Affordability
    - Rental Costs
    - Inflation
- Labor
- Industry
- Economics
- Wages
- Demographics
    - Education
    - Race
    - Sex
    - Population
- Migration

**Ranking**
- Which metros have the highest rent-to-income ratios in 2023?
- Which states have the highest median household income in 2023?
- Which metros have the highest share of cost-burdened renters in 2023?
- Which metros have the tightest housing markets by vacancy rate in 2023?
- Which metros are the most racially and ethnically diverse in 2023?

**Trend**
- How has median gross rent changed in Austin, Denver, Nashville, and Charlotte since 2018?
- How has the national vacancy rate trended since 2015?
- How has median household income trended across Southern states since 2015?

**Compare Selected**
- Compare median household income in Austin, Nashville, Denver, and Charlotte over the last decade
- Compare 5-year population growth in Sun Belt vs Rust Belt metros

**Distribution**
- How is rent-to-income distributed across US metros in 2023?
- How is median age distributed across US metros in 2023?

**Benchmark**
- How does Miami's share of cost-burdened renters compare to the national average in 2023?
- How does Phoenix's median gross rent compare to the Western US average in 2023?

**Growth**
- Which metros have had the fastest 5-year population growth since 2018?
- Which metros have seen the fastest per capita income growth over the last 5 years?

**Ideas (not yet scoped)**
- Rent-to-income vs. income growth scatter — which metros are getting more vs. less affordable?
- Permits per 1000 housing units — who is actually building?
- Gini index ranking — which metros have the highest income inequality?

---

## Learnings Log

Captured after each post. Feeds pipeline integration decisions later.

*(empty — fill after first post)*

---

## Pipeline Integration (deferred)

After 3–5 manual posts, revisit:
- Which steps were mechanical and repeatable? → candidates for automation
- Which steps required judgment every time? → keep manual
- What fields does a queue entry actually need to make a run unambiguous?
- What does the existing pipeline get right vs. wrong for this workflow?
- What needs to change in `app/` to fit the proven manual flow?
