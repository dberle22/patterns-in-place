# Project Docs

This folder is organized around canonical references first, planning notes
second, and historical sprint artifacts last. When two docs could cover the
same topic, use the ownership table below to decide which one should be updated.

## Start Here

| Question | Start with |
| --- | --- |
| How is the system supposed to fit together? | `architecture.md` |
| How are Python packages organized and where should code live? | `packages.md` |
| What DuckDB tables power the apps? | `data_model.md` |
| How do I rebuild local data? | `pipeline_plan.md` |
| What POI categories exist, what files, what status? | `poi_categories.md` |
| Where do raw sources, URLs, and caveats live? | `source_inventory.md` |
| What decisions have already been made? | `decision_log.md` |
| What are we building and why? | `planning/product_strategy.md` |
| What should we work on next? | `planning/current_backlog.md` |

## Canonical Ownership

| Topic | Canonical doc |
| --- | --- |
| System architecture and data flow | `architecture.md` |
| Python package boundaries and interactions | `packages.md` |
| Gold table contracts, source/build manifest, and table QA | `data_model.md` |
| Local build order and commands | `pipeline_plan.md` |
| POI category definitions, file sources, and ingestion status | `poi_categories.md` |
| Raw source URLs, local path conventions, and caveats | `source_inventory.md` |
| Durable decisions and rationale | `decision_log.md` |
| Listing CSV input schema | `contracts/listing_csv_contract.md` |
| Stoop Explore app behavior | `app/neighborhood_explorer_app.md` |
| Stoop Explore launch and refresh steps | `app/stoop_explore_launch_runbook.md` |
| Property Explorer app behavior | `app/property_explorer_app.md` |
| Product strategy, apps, and data products | `planning/product_strategy.md` |
| Active backlog and sprint assignments | `planning/current_backlog.md` |
| Historical workstreams (WS1–WS6) | `planning/workstreams.md` |
| Historical workstream context | `planning/next_workstreams_plan.md` |
| Future/post-MVP ideas | `planning/post_mvp_improvements.md` |
| Historical sprint notes | `archive/sprint_artifacts/` |

## Folder Layout

```text
docs/
  README.md
  architecture.md
  packages.md
  data_model.md
  pipeline_plan.md
  source_inventory.md
  decision_log.md
  app/
  contracts/
  planning/
  archive/
```

## Maintenance Rules

- Keep durable project truth in the top-level canonical docs.
- Keep raw-source caveats in `source_inventory.md`, not scattered across runbooks.
- Keep executable build steps in `pipeline_plan.md`.
- Move historical sprint-specific notes to `archive/` once they are no longer
  the current operating guide.
- When a contract changes, update `data_model.md`, `sql/ddl/001_gold_tables.sql`,
  the relevant pipeline/app code, and focused tests together.
