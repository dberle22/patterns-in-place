# Vacancy Rates — Task Checklist
**Topic:** Housing vacancy rates  
**Last updated:** 2026-05-13  
**Owner key:** 👤 Me &nbsp;|&nbsp; 🤖 Agent &nbsp;|&nbsp; 🤝 Both

---

## Artifact Guide (per insight)

Each insight folder produces these files in sequence:

| # | File | Who | When |
|---|------|-----|------|
| 1 | `question.md` | 👤 | Before EDA — state the question, angle, and visual hypothesis |
| 2 | EDA queries | 🤖 | Agent explores the data; we review together |
| 3 | `findings.md` | 🤝 | After EDA — key stats, surprises, data notes |
| 4 | `query.sql` | 🤖 | Chart-ready query in line chart contract format |
| 5 | `result.csv` | 🤖 | Execute query, save output |
| 6 | `chart_config.json` | 🤖 | R config: title, subtitle, dimensions, label style |
| 7 | `chart.png` | 🤖 | Rscript renders chart; you review |
| 8 | `summary.md` | 🤝 | 2–3 sentence data-first interpretation |
| 9 | `post_draft.md` | 🤝 | X post + thread + Substack caption |

---

## Insight 1 — National Trend (`national_trend/`)

**Question:** How has the US housing vacancy rate changed since 2019?  
**Chart:** Single-line, 2012–2024  
**Platform:** X + Substack

- [x] **1.** Write `question.md` — question, angle, visual hypothesis, audience 👤
- [x] **2.** EDA — agent explores years, geo levels, value range, national series 🤖
- [x] **3.** Write `findings.md` — key stats from EDA, data notes, confirmed angle 🤝
- [x] **4.** Write `query.sql` — chart-ready, line contract format 🤖
- [x] **5.** Execute query → `result.csv` 🤖
- [x] **6.** Write `chart_config.json` 🤖
- [x] **7.** Render → `chart.png` 🤖
- [x] **8.** Review chart — title, axis, shape, social dimensions 👤
- [x] **9.** Write `summary.md` 🤝
- [x] **10.** Write `post_draft.md` 🤝
- [x] **11.** Mark ready to publish 👤

---

## Insight 2 — Metro Rankings (`metro_rankings/`)

**Question:** Which major metros have the tightest and loosest housing markets in 2024?  
**Chart:** Horizontal bar chart, top 20 CBSAs (pop > 250k)  
**Platform:** X + Substack  
**Dependency:** None — can build in parallel with Insight 1

- [x] **1.** Write `question.md` 👤
- [x] **2.** EDA — explore CBSA rankings, population filter options, value distribution 🤖
- [x] **3.** Write `findings.md` 🤝
- [x] **4.** Write `query.sql` 🤖
- [x] **5.** Execute query → `result.csv` 🤖
- [x] **6.** Write `chart_config.json` 🤖
- [x] **7.** Render → `chart.png` 🤖
- [x] **8.** Review chart 👤
- [x] **9.** Write `summary.md` 🤝
- [x] **10.** Write `post_draft.md` 🤝
- [x] **11.** Mark ready to publish 👤

---

## Insight 3 — State Map (`state_map/`)

**Question:** Which states have the tightest housing markets — and which have tightened the most since 2019?  
**Chart:** Choropleth — 2024 vacancy rate + change from 2019  
**Platform:** Substack  
**Dependency:** None — but most complex chart; build after Insights 1–2 to confirm workflow

- [x] **1.** Write `question.md` 👤
- [x] **2.** EDA — state-level rates, 2019 vs 2024 change, regional patterns 🤖
- [x] **3.** Write `findings.md` 🤝
- [x] **4.** Write `query.sql` 🤖
- [x] **5.** Execute query → `result.csv` 🤖
- [x] **6.** Write `chart_config.json` — choropleth config is more involved; may iterate 🤖
- [x] **7.** Render → `chart.png` 🤖
- [x] **8.** Review chart 👤
- [x] **9.** Write `summary.md` 🤝
- [x] **10.** Write `post_draft.md` 🤝
- [x] **11.** Mark ready to publish 👤

---

## Insight 4 — Regional Trends (`regional_trends/`)

**Question:** How have vacancy rates moved across the four Census regions since 2019?  
**Chart:** Multi-line, 4 series, 2019–2024  
**Platform:** Substack  
**Dependency:** Build last — deepens the national trend story from Insight 1

- [x] **1.** Write `question.md` 👤
- [x] **2.** EDA — regional series, confirm 4 regions, relative compression 🤖
- [x] **3.** Write `findings.md` 🤝
- [x] **4.** Write `query.sql` 🤖
- [x] **5.** Execute query → `result.csv` 🤖
- [x] **6.** Write `chart_config.json` 🤖
- [x] **7.** Render → `chart.png` 🤖
- [x] **8.** Review chart 👤
- [x] **9.** Write `summary.md` 🤝
- [x] **10.** Write `post_draft.md` 🤝
- [x] **11.** Mark ready to publish 👤
