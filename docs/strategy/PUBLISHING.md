# Publishing

**Status:** Active — kept as reference while Publisher is paused
**Updated:** 2026-09-29

How Patterns in Place publishes: why, in what streams, in what formats and in what voice. This is the plan to pick back up when Publisher resumes. It consolidates the strategy notes from the retired Obsidian vault (the July 14 publishing plan, the editorial strategy and the format standards); the rest of that material was dropped.

---

## Why we publish

Publishing has two jobs: **prove what the platform and its builder can do**, and **build the Patterns in Place brand and an audience that cares about what it finds.** Both require the same thing: shipping regularly and in public.

The platform is analytically ready. The gap has always been output, not ideas or infrastructure.

**Positioning:** Patterns in Place is an independent urban data publication. We build open analyses and tools for US housing, demographics and economic geography, from raw public data through to interactive maps.

**Primary reader:** the curious researcher or data nerd (see [the audience decision](../decisions/2026-06_metro-deep-dive-audience.md)). Investors and people choosing where to live are secondary.

## Four streams

| Stream | What it is | Cadence | Where |
|---|---|---|---|
| **Chart a day** | One chart, one finding, a short post. The heartbeat that shows the project is active. | Daily when running | X, Bluesky |
| **Metro Deep Dive** | One market serialized act by act; each act stands alone and adds up to the full picture. The flagship. | One market over 6–8 weeks | Substack |
| **Public releases** | Citable data releases such as the [public CBSA panel](../../public-cbsa-panel/README.md). | Per release | Public repo, Zenodo, Substack announcement |
| **Technical posts** | How the platform was built. Written only after a milestone ships. | When a gate clears | Substack, LinkedIn, Hacker News for launches |

The streams feed each other: each Deep Dive act produces 2–3 charts for chart a day in the same week, and a national finding introduced in a Deep Dive can become a standalone Data Take.

**Technical posts are gated**, so we only write about things that have proven themselves in public:

| Post | Gate |
|---|---|
| Visual library and chart engine | About 10 chart-a-day posts live |
| Semantic layer | After the visual library post |
| Gold layer and DuckDB warehouse | After the first Deep Dive publishes |
| Publisher pipeline and skills | After the warehouse post |
| Public CBSA panel: how it was built | After v2026.1 is public |
| Stoop, Area Explorer, Chatbot launches | When each product ships |

**The weekly question:** is the Deep Dive moving, and did at least one chart go out? If yes, everything else is secondary.

## What this is not

- Not a daily content machine across five platforms.
- Not a simultaneous launch of every product.
- Not blocked on finishing a method before anything publishes.
- Not driven by outreach; distribution follows content.

## Formats

| Format | Length | Visuals | Use it for | Template |
|---|---|---|---|---|
| **Metro Deep Dive** | Serialized by act | Fixed spine plus flex | One market, full narrative | Governed by the [MDD program](../../metro-deep-dive-program/metro_deep_dive_program.md) and its [fixed spine](../decisions/2026-07_deep-dive-fixed-spine.md) |
| **Opportunity List** | 800–1,200 words | 1–3 plus a list of 5–12 places | A filter applied across places | [opportunity_list.md](../../publisher/content/templates/opportunity_list.md) |
| **Data Take** | 500–900 words | Exactly 1 | One question, one finding, one argument | [data_take.md](../../publisher/content/templates/data_take.md) |
| **Technical Deep Dive** | 1,200–2,000 words | Code plus 1–2 diagrams | A real build decision and its trade-offs | [technical_deep_dive.md](../../publisher/content/templates/technical_deep_dive.md) |

If a Data Take drifts past 1,000 words, it probably wants to be an Opportunity List. If a Technical Deep Dive drifts past 2,000, it's probably two pieces.

## Should we write this piece?

Run every idea through five questions. A piece that fails one gets reframed or dropped.

1. **Question:** does it answer a real question about a place, with a finding you can state in one sentence?
2. **Format:** does it fit one of the four formats? Be skeptical of "this needs a new format".
3. **Data:** can the existing warehouse answer it? If it needs new ingestion, defer unless the analysis justifies the build.
4. **Visual:** is there at least one chart, map or table that anchors it?
5. **Reader:** can you name who it's for?

Ideas that haven't passed yet live in [publisher/content/IDEAS.md](../../publisher/content/IDEAS.md).

## What we don't publish

- National macro takes: interest rates, recession calls, GDP commentary. This is about place.
- Politics, except where the data unavoidably points to a policy cause.
- Personal essays.
- Takes without a dataset the reader can see.
- Places where the data is too thin (ACS small-area estimates get shaky below about 20,000 people).
- Stock picks, REIT recommendations or specific property recommendations.

## Voice

- **Lead with the finding.** The first sentence names the surprise.
- **Name the place.** "Jacksonville", not "a southern metro".
- **Show the chart early.** Most readers won't scroll far.
- **One anchoring number,** not seven.
- **Earn every adjective.** "Booming" needs a number.
- **Acknowledge limitations** and never overclaim.
- **No throat-clearing**, and end on a takeaway, not a summary.
- Plain English; no consulting-deck nouns.

## Charts and brand

The brand uses the visual library's current palette and style guide ([visual_style_guide_and_standards.md](../../foundations/visual_library/docs/visual_style_guide_and_standards.md)). No change to the brand identity has been decided.

Palette-independent habits for every published chart:

- Cite the source, with its vintage, on the chart.
- Give the reader one obvious place to look: one anchoring number or one highlighted series.
- Never use stock images; the hero image is always a chart or map from the piece.
