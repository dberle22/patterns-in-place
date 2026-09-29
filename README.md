# Patterns in Place

Patterns in Place is a data platform and research engine for US places. It turns public economic, demographic and place data into a shared warehouse, then builds analysis products on top of it: Metro Deep Dives, a public CBSA panel, interactive explorers and published charts.

**Layer model:** Places and Points data → medallion warehouse (staging → Silver → Gold → marts) → semantic layer → Intelligence Framework (Character, Livability, Opportunity) → products.

Read this file first. Agent behaviour rules are in [AGENTS.md](AGENTS.md).

## Folder map

| Folder | What it is | Status | Start with |
|---|---|---|---|
| `foundations/` | ETL, DuckDB warehouse, semantic layer, data dictionary, visual library, loaders. A dependency for every product, not a product itself. | Active | [semantic_layer/README.md](foundations/semantic_layer/README.md), [data_dictionary/README.md](foundations/data_dictionary/README.md) |
| `metro-deep-dive-program/` | The canonical Metro Deep Dive build: engines, analyses, issues. | Active | [metro_deep_dive_program.md](metro-deep-dive-program/metro_deep_dive_program.md) |
| `public-cbsa-panel/` | Release workspace for the public Metro & Micro Panel; v2026.1 published 2026-09-28. | Active | [README.md](public-cbsa-panel/README.md) |
| `exploration/` | Ad hoc analysis before it is standardized. Never ships directly. | Active | [README.md](exploration/README.md) |
| `metro-deep-dive/` | Legacy Deep Dive tree, retiring into `metro-deep-dive-program/`. The research tool and some code the program depends on still live here. | Legacy | [README.md](metro-deep-dive/README.md) |
| `area-explorer/` | Streamlit CBSA explorer apps. | Paused | [README.md](area-explorer/README.md) |
| `publisher/` | NL-to-SQL chatbot, chart-a-day pipeline, editorial content. Has shipped work. | Paused | [README.md](publisher/README.md) |
| `stoop/` | NYC neighborhood explorer. The public app link is still live. | Paused | [docs/README.md](stoop/docs/README.md) |
| `docs/` | Repo-wide context: status, roadmap, overview, architecture, glossary, conventions, decisions. | Active | [STATUS.md](docs/STATUS.md) |
| `scripts/` | Repo-level launchers (e.g. `start_research_tool.sh`). | — | — |
| `config/` | Local R environment helper. | — | — |

Details and next steps per area: [docs/STATUS.md](docs/STATUS.md). **Status meanings:** Active = in development. Paused = not in development, intended to resume. Legacy = kept only until its live parts move elsewhere; don't build new work here.

**Local only (gitignored):** `notes/` is an old Obsidian vault of early strategy notes. It is being reviewed and retired; don't treat it as a current source of truth.

## Context docs

| To understand | Read |
|---|---|
| Where each area stands and what's next | [docs/STATUS.md](docs/STATUS.md) |
| Strategy and sequencing across areas | [docs/ROADMAP.md](docs/ROADMAP.md) |
| What we're building and how we think about places | [docs/OVERVIEW.md](docs/OVERVIEW.md) |
| Data flow, warehouse schemas, which folder reads what | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Vocabulary (frames, acts, marts, zones) | [docs/GLOSSARY.md](docs/GLOSSARY.md) |
| Decisions not to re-argue | [docs/decisions/](docs/decisions/README.md) |
| How to write and maintain docs | [docs/CONVENTIONS.md](docs/CONVENTIONS.md) |

Intelligence Framework methodology is still in `exploration/intelligence_framework/docs/`, with its history in [INTELLIGENCE_LAYER_ROADMAP.md](INTELLIGENCE_LAYER_ROADMAP.md); both are moving as part of the docs overhaul.

## Warehouse

The canonical DuckDB file is `foundations/etl/data/duckdb/patterns_in_place.duckdb` (gitignored, built locally).

Point code at it with the `DB_PATH` environment variable. R scripts read it from `.Renviron`; Python reads it from the shell. Some tools use their own name for the same path:

| Tool | Variable |
|---|---|
| R ETL (`foundations/etl/`) | `DB_PATH` |
| Area Explorer | `DB_CONNECTION`, falls back to `DB_PATH` |
| Research tool launcher | `DB_PATH`, defaults to the canonical path |
| Public CBSA panel build | `--db` flag, or `PIP_FOUNDATIONS_DUCKDB` |

## Python environments

There are several environments because the areas pin different library versions (pandas 3 vs 2.2). Use the one that matches the work:

| Environment | Python | Use for |
|---|---|---|
| `.venv-marimo` | 3.12, pandas 3 | Metro Deep Dive program marimo notebooks |
| `.venv312` | 3.12, pandas 2.2 | Publisher chart-a-day and `chart_engine_py` |
| `area-explorer/.venv` | 3.12 | Area Explorer apps and the research tool |

All environments are gitignored and local to this machine. R work uses the system R install. Stoop has no environment set up in this repo yet; its docs assume one from before the monorepo migration.

## Ground rules

- `foundations/` is shared. Products read from it; they never keep their own copies of its assets.
- Nothing ships straight from `exploration/`. Promote work into `foundations/` or a product folder first.
- No machine-specific absolute paths in committed files. Use repo-relative paths or environment variables.
- Full agent guidelines: [AGENTS.md](AGENTS.md).
