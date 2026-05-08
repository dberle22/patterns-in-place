# Patterns in Place — Methodology

The opinionated standards that govern every piece published under Patterns in Place. This is the publication's equivalent of a tracking-plan standards library — the reference docs that make individual analyses feel like part of a coherent body of work rather than a scattered set of one-offs.

---

## What This Is

A four-document standards library for a data publication that operates from raw ingestion through interactive delivery. Each document defines the rules for one layer of the work:

1. **Editorial Pillars** — the five core questions every piece must answer
2. **Format Standards** — the structural specs for the three content formats (Metro Deep Dive, Opportunity List, Data Take)
3. **Data Pipeline Standards** — the Bronze/Silver/Gold architecture and the rules for ingesting, normalizing, and serving data
4. **Visual Design Standards** — the publication's visual identity rules — color, type, charts, maps, exports

Together these documents are the production manual. When a piece feels off, one of these docs has the answer. When a new contributor or future-you picks up the publication, these docs are the orientation.

---

## Who This Is For

- **You, the publisher** — the reference you check when a piece feels inconsistent or unclear
- **Future contributors** — the orientation for anyone who eventually writes under the Patterns in Place masthead
- **Readers who want to understand the methodology** — the public version is the credibility surface
- **Reproducers** — analysts who want to replicate or extend a Patterns in Place piece can use the data pipeline and visual standards to make their work look and feel the same

---

## Folder Structure

```text
methodology/
  README.md                           ← you are here
  editorial_pillars.md                ← the 5 pillars in depth
  format_standards.md                 ← Metro Deep Dive, Opportunity List, Data Take specs
  data_pipeline_standards.md          ← Bronze/Silver/Gold architecture
  visual_design_standards.md          ← color, type, chart, map standards
```

Future additions (in priority order):

- `templates/` — writing scaffolds for each format
- `examples/` — annotated examples of strong vs. weak pieces
- `voice_and_style.md` — the prose-level style guide
- `data_sources_reference.md` — the canonical reference for every data source the pipeline uses

---

## How to Read This in Order

If you're new to the system or returning after time away:

1. Read this README in full.
2. Read `editorial_pillars.md` — the brand promise to readers.
3. Read `format_standards.md` — the production specs.
4. Read `data_pipeline_standards.md` — the structural advantage.
5. Read `visual_design_standards.md` — the credibility layer.

If you've published before and just want the rules: jump straight to whichever standards doc the current piece needs.

---

## The Core Philosophy

**Place over topic.** Every piece is grounded in a specific place — a metro, a county, a neighborhood, a tract. "The data on housing affordability" is a topic. "Why Tampa's affordability index is misleading" is a Patterns in Place piece.

**Pipeline over shortcut.** Every analysis pulls from the Bronze/Silver/Gold pipeline. If a question can't be answered with the pipeline, either extend the pipeline or write a different piece. No one-off scripts that bypass the system.

**Visual identity over speed.** Every chart, every map, every dashboard carries the visual library. A piece that ships without the visual identity is a draft, not a piece.

**Format discipline over experimentation.** The three formats cover the production envelope. New formats get added almost never.

**Five pillars over breadth.** Every piece maps to one of five questions. If a piece doesn't fit a pillar, it's a piece for a different publication.

---

## What This Methodology Does Not Cover (Yet)

By design, the v1 standards library focuses on the publication's editorial and structural disciplines. Several adjacent topics will get their own docs as the publication matures:

- **Detailed prose and style guide** — voice rules live in `editorial_strategy.md` for now; will move to `voice_and_style.md` when the body of work justifies a deeper guide
- **Template files** — the format specs in `format_standards.md` describe the structure; explicit Markdown templates per format come later
- **Data dictionary** — every dataset in the pipeline will eventually have a documented schema; deferred to month 3
- **Chart-by-chart specifications** — the visual standards cover the rules; the Datawrapper templates will be added once the visual library is committed to a public repo

---

## How This Folder Sits Alongside the Strategy Docs

- `../publication_playbook.md` — operational setup; references this folder
- `../editorial_strategy.md` — defines pillars and formats at the strategy level; this folder is the deeper operating manual
- `../distribution_strategy.md` — defines platforms and cadence; this folder is what gets distributed
- `../asset_inventory.md` — current state of assets; the Layer A/B/C structure references the standards in this folder
- `../growth_roadmap.md` — multi-month vision; new methodology docs get added here as the publication grows

When in doubt about a tactical editorial or design decision, the order to consult is: this folder → strategy doc → just ship.

---

## Credits and Roadmap

Built and maintained by the Patterns in Place editorial team (currently a team of one). Roadmap and changelog will live in `CHANGELOG.md` once the public version of this folder ships on GitHub.

Contact: hello@patternsinplace.com (once the email is live — see `../publication_playbook.md` Move 1).
