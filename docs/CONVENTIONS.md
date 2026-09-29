# Documentation Conventions

**Status:** Active
**Updated:** 2026-09-29

How docs in this repo are named, structured, kept current and retired. The docs are written for Dan and AI agents; public-facing docs are built separately for each release (e.g. `public-cbsa-panel/`).

Apply these rules to new docs and to old docs **as you touch them**. Don't sweep through old docs to retrofit them.

---

## 1. Every area folder has a README

Each top-level area (and each major subfolder with its own purpose, e.g. `foundations/etl/`) has a `README.md` with these sections, in this order:

1. **What it is**, in two sentences.
2. **Status**: Active, Paused or Legacy, and the date it was last worked on. The labels must match [STATUS.md](STATUS.md) and the root [README.md](../README.md) folder map.
3. **How to run it**: commands from the repo root, which Python environment, and which environment variables.
4. **Key docs**, in reading order.
5. **Depends on / depended on by**: which folders it reads from and which read from it.
6. **Where we left off** (Paused and Legacy areas only): the last thing done and the first thing to do on return.

Active areas also have a `ROADMAP.md`.

A README is an entry point, not a spec. If a section grows past a screen, move the detail into its own doc and link to it.

## 2. Doc types

Name planning docs `<SCOPE>_<TYPE>.md` in capitals, e.g. `POI_ENGINE_BUILD_PLAN.md` or `EXPLANATION_Q2_AUDIT.md`. `README.md` and `ROADMAP.md` go without a scope.

| Type | Purpose | Lifecycle |
|---|---|---|
| `README` | Entry point for a folder | Always current |
| `ROADMAP` | What's next for an area | Always current |
| `SPEC` | What we're building and why | Frozen once built; later changes get a dated note at the top |
| `BUILD_PLAN` | Task list with checkboxes | Archived when all tasks are done |
| `CONTRACT` | An interface other code relies on: tables, columns, functions | Always current; update it in the same change as the code |
| `AUDIT` / `REVIEW` | Findings at a point in time | Dated in the header; never edited afterwards |
| `NOTES` | Working notes and open questions | Pruned, or archived when the work closes |
| `DECISIONS` | Dated records of choices that shouldn't be re-argued | Append-only; a reversal is a new entry |

**Names already in use** stay as they are. Treat them as the closest type:

| Existing name | Treat as |
|---|---|
| `PLAN`, `TASKS` | `BUILD_PLAN` |
| `PROPOSAL` | `SPEC` before approval |
| `decision_log`, `decisions`, `METHOD_RECORD` | `DECISIONS` |
| `FEEDBACK` | `REVIEW` |
| `HANDOFF_PROMPT` | `NOTES`; delete once the handoff is done unless it has lasting value |
| `MIGRATION` | `BUILD_PLAN`; archive when the migration is complete |
| `METHODOLOGY`, `TAXONOMY`, `USAGE`, `CHANGELOG` | Reference docs; always current |

**Not covered here:** data dictionary entries (`foundations/data_dictionary/`), chart specs (`foundations/visual_library/`) and generated outputs follow their own folder conventions.

## 3. Status header

Every `SPEC`, `BUILD_PLAN`, `ROADMAP`, `NOTES`, `AUDIT` and `REVIEW` starts with this header under its title:

```markdown
**Status:** Active | Done | Superseded
**Updated:** YYYY-MM-DD
**Superseded by:** path/to/newer_doc.md
```

- Leave out `Superseded by` unless it applies.
- For `AUDIT` and `REVIEW`, `Updated` is the date of the review.
- When a doc is superseded, add the pointer in the same change that creates its replacement.

## 4. Archiving

Finished or superseded material is **moved**, never copied, to:

```
<area>/archive/YYYY-MM_<name>/
```

- `YYYY-MM` is the month it was archived. `<name>` says what it was, e.g. `2026-08_industry_v0`.
- Root-level docs are archived to `docs/archive/`.
- Leave a one-line pointer in the README or roadmap that used to link to it.
- Don't archive a file that live code or docs still reference. Move the reference first.

## 5. One owner per topic

When two docs could answer the same question, one of them owns it and the other links to it. Current owners:

| Topic | Owner |
|---|---|
| Folder map, DB path, Python environments | Root [README.md](../README.md) |
| Where each area stands and its next step | [STATUS.md](STATUS.md); the root README's status labels must match it |
| Strategy and sequencing across areas | [ROADMAP.md](ROADMAP.md) |
| Area task lists | Each area's `ROADMAP.md` or build plan, linked from STATUS |
| Publishing strategy | [strategy/PUBLISHING.md](strategy/PUBLISHING.md) |
| What we're building, the thinking model, principles | [OVERVIEW.md](OVERVIEW.md) |
| Data flow, warehouse schemas, folder dependencies | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Vocabulary | [GLOSSARY.md](GLOSSARY.md) |
| Repo-wide and product-wide decisions | [decisions/](decisions/README.md) |
| Agent behaviour and coding rules | [AGENTS.md](../AGENTS.md) |
| Documentation rules | This file |
| Per-table definitions | `foundations/data_dictionary/` |
| Metric and model definitions | `foundations/semantic_layer/` |

