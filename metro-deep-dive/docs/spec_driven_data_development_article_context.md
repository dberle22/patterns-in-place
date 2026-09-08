---
title: "Spec-Driven Data Development — Article Brief"
date: 2026-09-06
audience: product and leadership
format: argument supported by a project case study
---

# Spec-Driven Data Development — Article Brief

## The argument

The Industry Explorer gives us a concrete case for spec-driven data development.

The argument is not that a specification makes a data product perfect on the first attempt. The stronger and more credible claim is:

> A specification gives a data product a shared language before the logic disappears into code. It makes the questions, sources, assumptions, outputs, and definition of done visible enough to build against—and visible enough to revise when the work teaches us something new.

For a product and leadership audience, this is mainly a story about coordination, learning, and organizational memory. The durable output is not only an application. It is a record of what the team meant, what it built, what changed, and why.

## The case study

Metro Area Explorer is a collection of small, market-parameterized research applications intended to support the longer-form Metro Deep Dive series. Industry was the first section and the testbed for the method.

The team began with an expansive but ambiguous question: **What drives a metro economy?** The Industry specification turned that question into six analytical deliverables, with named sources, controls, expected outputs, acceptance criteria, and open decisions. Richmond was the proving ground, while the principal economic queries were built around a CBSA identifier so they could be exercised for other metros.

The result is an author-facing research workbench, not a finished reader-facing publication. That distinction became clear during review and is important to the story: the product's job is to help an analyst find and support claims that can later become a report.

## What is already built

The live Industry Explorer contains five analytical pages:

1. **Industry makeup and change** — employment and GDP mix, change over time, benchmark context, specialization, shift-share, and wage context.
2. **Spatial clusters** — tract-level industry concentration, job density, jobs per resident, and county GDP context.
3. **Job centers** — major employment centers, workplace-versus-resident-worker imbalance, sector pull, and a shortlist used by the infrastructure analysis.
4. **Infrastructure context** — cached OSM infrastructure layers, nearby institutional and amenity context, and a first-pass job-center typology. Overture data was evaluated and ingested, but not rendered after review found its taxonomy too noisy for the intended claims.
5. **Regional fit** — industry and GDP mix against model-derived peer metros, plus GDP, income, pay, and diversification context.

A sixth page on AI exposure was also built, including NAICS and SOC crosswalk work. Review showed that it was the start of a separate argument rather than another Industry Explorer view, so it was removed from the live shell and carried into the downstream [AI Inversion analysis](../analysis_program/01_ai_inversion/ai_inversion_spec.md).

The supporting system includes:

- an active [Industry specification](../metro-area-explorer/industry/SPEC_INDUSTRY.md);
- a [decision log](../metro-area-explorer/industry/decisions.md) with 26 dated entries;
- a shared data-preparation layer and separate page modules;
- automated tests for the major analytical paths;
- an [archived first version](../archive/metro-area-explorer/industry_v0_2026-08-08/);
- a [review and revision plan](../metro-area-explorer/industry/v1_review_plan.md);
- reusable Foundations data, geography, peer, and visual components;
- a repo-local workflow for drafting future section specifications.

## The strongest proof points

### 1. The spec made an ambiguous request buildable

“Explain Richmond's economy” leaves basic decisions unresolved: employment or GDP, which taxonomy, which year, compared with whom, at what geography, and for which audience. The spec separated those decisions into bounded analytical questions and attached sources and acceptance criteria to each one.

This made the work divisible across data preparation, analysis, interface development, and review without requiring every decision to be rediscovered inside the code.

### 2. Existing foundations reduced reinvention

The workbench reuses established QCEW, BEA, LODES, OEWS, population, geography, and peer-market assets. That meant the section could begin from governed economic data and shared visual patterns rather than rebuilding every source from raw files.

The accurate claim is that the workbench is **grounded in Foundations**, not that every calculation is fully semantic-layer-driven. Significant analytical logic still lives inside the section.

### 3. A stable interface survived a failed data-source path

The infrastructure page provides the clearest implementation story. The first OSM acquisition approaches did not work reliably at Richmond scale. The team tried several routes before a provider-backed extraction succeeded.

Because acquisition was separated from application preparation and the cache shape was already defined, the successful output could be promoted into the interface the app expected. The acquisition method changed without requiring the analytical page to be redesigned.

### 4. The spec made revision legible

The first full review clarified that the Explorer was an internal research workbench. It also led to revised comparisons, improved reading aids, and the removal of the AI-exposure page.

D6 was not simply abandoned. The spec and decision log preserve why it moved, what work remained reusable, and where the analysis went next. This is a strong leadership lesson: specifications are valuable even when scope changes because they make the change explicit rather than accidental.

## The honest limits

The project supports an argument for disciplined iteration, not automatic correctness or production readiness.

- The specification is still marked `active_review`; this is a substantial working system, not a declared final release.
- The main economic paths are parameterized by metro, but the external infrastructure cache currently exists only for Richmond.
- Not every acceptance criterion and implementation detail remained perfectly synchronized as the work evolved.
- Tests help establish repeatability, but they do not replace data-domain judgment. This review found a de-scoped D6 query using an incomplete county join key even though its structural tests passed. The lesson for the article is simple: a strong data specification also needs grain, key, reconciliation, and plausibility rules.
- The repository records decisions well, but it does not provide a clean non-spec baseline for claims such as “X percent faster” or “Y percent cheaper.” Avoid invented productivity estimates.

These limits strengthen the central argument. The value of the method is not that mistakes disappear; it is that decisions, interfaces, tests, and revisions become inspectable.

## Recommended article shape

1. **Open with the ambiguity.** Use “show us what drives Richmond's economy” to reveal the decisions hidden inside a simple product request.
2. **Introduce the experiment.** Explain the operating model: specification first, data preparation and workbench second, with decisions and review captured throughout.
3. **Show what the specification unlocked.** Use three examples rather than touring every screen: the explicit definition of industry makeup, the infrastructure source substitution behind a stable interface, and reuse of the existing peer-market system.
4. **Show what the build taught us.** Explain the author-workbench decision and why AI exposure moved into its own analysis.
5. **Acknowledge the limit.** A green software test suite is not the same as a trustworthy data contract; domain invariants still matter.
6. **End on the organizational payoff.** The reusable asset is a body of definitions, decisions, interfaces, and lessons that lowers the cost and ambiguity of the next section.

## Working thesis

> Data products often fail because meaning stays implicit until it is buried in code. Spec-driven development gives those decisions a place to live, makes complex work easier to divide, and makes learning easier to incorporate. The Industry Explorer shows that the payoff is not first-pass perfection but better, more accountable iteration.

Possible titles:

- **The Spec Is Not the Plan: Building Data Products That Can Survive What We Learn**
- **From Dashboard Brief to Research Workbench**
- **Specifications as Organizational Memory for Data Products**
- **A Green Test Suite Is Not a Data Contract**

## Primary source trail

Start with these files when drafting:

1. [Metro Area Explorer README](../metro-area-explorer/README.md)
2. [Industry specification](../metro-area-explorer/industry/SPEC_INDUSTRY.md)
3. [Decision log](../metro-area-explorer/industry/decisions.md)
4. [v1 review plan](../metro-area-explorer/industry/v1_review_plan.md)
5. [Industry app shell](../metro-area-explorer/industry/app.py)
6. [Infrastructure proposal](../metro-area-explorer/industry/POI_INFRA_PROPOSAL.md) and [Richmond source review](../metro-area-explorer/industry/RICHMOND_POI_INFRA_REVIEW.md)
7. [Felten crosswalk method](../metro-area-explorer/industry/FELTEN_CROSSWALK_METHOD.md)
8. [AI Inversion analysis plan](../analysis_program/01_ai_inversion/ai_inversion_spec.md)

The supplied [article-writer context prompt](industry_explorer_article_writer_context.md) is best treated as a later fact-checking checklist. It is primarily a status-reconciliation prompt, not the narrative brief for the article.

## Drafting prompt

Write an article for a product and leadership audience arguing for spec-driven data development, using the Metro Area Explorer Industry workbench as the case study. Begin with the ambiguity hidden inside the request to explain what drives a metro economy. Show how the specification made the work buildable by naming the analytical questions, sources, outputs, acceptance criteria, and open decisions. Center the evidence on three moments: defining industry makeup, changing the infrastructure acquisition path without redesigning the page, and moving AI exposure into a better downstream product after review. Be candid that specifications and tests do not eliminate errors; they make assumptions and revisions easier to find and correct. Conclude that the principal payoff is a durable body of shared decisions that improves coordination, learning, and reuse. Avoid unsupported claims about speed, full automation, or production readiness.
