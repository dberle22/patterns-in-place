# Overview

**Status:** Active
**Updated:** 2026-09-29

What Patterns in Place is, how we think about places, and how the parts of this repo feed each other. For folder-level detail see the root [README.md](../README.md); for how data moves through the system see [ARCHITECTURE.md](ARCHITECTURE.md); for terms see [GLOSSARY.md](GLOSSARY.md).

---

## What we're building

Patterns in Place is a data platform and research engine for US places. We take raw public economic, demographic and place data, transform it into a shared warehouse, and build research and products on top of it.

The claim behind it: a place can be *understood*, not just described. Raw metrics answer narrow questions one at a time (median rent, unemployment). We want to answer the bigger ones: what kind of place is this, how does it compare, what is it like, and where inside it is the action.

The primary reader is the curious researcher or data nerd: someone who wants the structural patterns under a city, not the headline stats. Investors and people deciding where to live are secondary readers, served by specific sections or specific pieces rather than by the whole.

## The layer model

Everything is built in layers. Each layer consumes the one below it and never re-implements it.

```
Raw sources      Places (geographies: US → tract)  +  Points (POIs, parcels)
      ↓
Warehouse        staging → Silver → Gold → marts           (foundations/etl, DuckDB)
      ↓
Meaning          semantic layer: tables, metrics, joins, themes, questions
      ↓
Intelligence     Character · Livability · Opportunity frames, Cross-Frame, trajectory, zones
      ↓
Products         Metro Deep Dive · public CBSA panel · explorers · published charts
```

**Places** are geographic units, from the whole US down to census tracts and ZCTAs. **Points** are individual locations: points of interest, parcels, listings. They join to Places through spatial assignment (point → tract → larger geographies).

## How we think about a question

Three independent frameworks combine to produce any piece of work. We pick a question, decide which data answers it, then choose how to express the answer.

**1. Themes organize the data.** Data rolls up from raw data points to metrics, to topics (housing, labor, age, industry), to three themes:

- **Character**: who lives here and what makes the place distinct. Descriptive, not normative; there is no good or bad Character.
- **Livability**: whether day-to-day conditions support a good life (affordability, health, access, environment).
- **Opportunity**: economic prospects for residents, investors and businesses.

A topic can serve more than one theme. The themes became the three frames of the Intelligence Framework, and the frames are kept separate on purpose: one "best place" score would average away real tensions, such as a metro that's great for building wealth and rough to live in.

**2. Questions are organized separately from data**, because the two don't map one to one. Questions come in three levels:

| Level | Example | Answer |
|---|---|---|
| High | Is this a good place to live? | No direct answer; spans all three themes and is subjective |
| Medium | What are the most affordable housing markets? | One theme and topic; needs analysis across several metrics |
| Low | Which 5 markets have the lowest rent-to-income? | Direct answer from existing data |

A **user profile** modifies the question: "a good place to live" means different things for a retiree than for a young parent. Low-level questions can stand alone, which is what the chatbot and chart-a-day pipeline answer.

**3. Output frameworks express the answer.** These are the recurring shapes an answer takes:

- **Benchmark**: one place against a reference group.
- **Ranking**: many places ordered by a metric.
- **Trend**: one place or metric over time.
- **Cluster / classification**: places or points grouped by similarity.
- **Score / index**: several metrics combined into one signal.
- **Deep Dive**: a full profile of one place across themes.

The same output can be delivered at different fidelity (a static chart or an interactive explorer) without changing the method.

## How the areas feed each other

```
exploration/  ──(promote when it proves out)──→  foundations/
                                                     │
                     ┌───────────────────────────────┼─────────────────────────┐
                     ↓                               ↓                         ↓
       metro-deep-dive-program/            public-cbsa-panel/         paused products
       (destination product)               (citable releases          (area-explorer, publisher,
       engines → analyses → issues          from Gold)                  stoop)
                     │
                     └──(an engine used unchanged by two consumers)──→  foundations/
```

- **`foundations/`** is infrastructure: the warehouse, semantic layer, Intelligence marts, data dictionary and visual library. It's a dependency, not a product.
- **Metro Deep Dive** is the destination product: long-form, rigorous, comparable market reports. The program works backward from the issue we want to publish, to the analyses that answer it, to the reusable engines underneath. The Intelligence Framework acts as the router, deciding which analyses a given market gets.
- **The public CBSA panel** is a small, citable public release built from Gold tables.
- **`exploration/`** is where analysis starts before it's standardized. Nothing ships from it directly.
- **Area Explorer, Publisher and Stoop** are paused. They consume the same shared core, so they can resume without rebuilding their data.

## Principles

- **Build once, upstream.** When a product needs something reusable, it's built as an engine or in `foundations/`, not inside the product.
- **Promote on reuse, not on hope.** An engine moves into `foundations/` once two consumers use it unchanged.
- **Comparability over novelty.** Deep Dive issues share a fixed spine so markets can be read against each other. Published issues are dated artifacts and aren't backfilled.
- **Same machinery for every frame.** All Intelligence frames use one pipeline, so the method is learned once and outputs are comparable.
- **Frames are lenses, not sections.** Character, Livability and Opportunity inform what to ask; they are not the chapters of a report.

## Where to go next

| To understand | Read |
|---|---|
| Current status of each area | [STATUS.md](STATUS.md) |
| What's next, and in what order | [ROADMAP.md](ROADMAP.md) |
| Warehouse, marts and data flow | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Vocabulary | [GLOSSARY.md](GLOSSARY.md) |
| Decisions not to re-argue | [decisions/](decisions/README.md) |
| The Metro Deep Dive program | [metro_deep_dive_program.md](../metro-deep-dive-program/metro_deep_dive_program.md) |
| The Intelligence Framework method | [intelligence_framework_overview.md](../exploration/intelligence_framework/docs/intelligence_framework_overview.md) |
