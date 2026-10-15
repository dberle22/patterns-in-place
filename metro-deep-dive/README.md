# metro-deep-dive (legacy)

**Status:** Legacy
**Updated:** 2026-09-29

This is the original Metro Deep Dive tree. It has been replaced by [`metro-deep-dive-program/`](../metro-deep-dive-program/README.md), which holds all current Deep Dive work.

**Don't build new work here.** New engines, analyses and issues go in the program.

**Retirement is a separate, future project.** This folder will eventually be reviewed and archived, with anything still useful moved into the program or `foundations/`. That review hasn't started. Until it does, nothing here gets moved or deleted, and the notes below are only an inventory.

---

## What's here

| Folder / file | What it is | Last changed | State |
|---|---|---|---|
| `metro-area-explorer/` | Section-by-section explorer apps: `industry/` (Industry Explorer) and `place_intelligence/` (Jacksonville site and catchment work) | 2026-09 | **Depended on** by the program (see below) |
| `research-tool/` | The Deep Dive Research Tool, a Streamlit app for exploring one metro | 2026-07 | Paused but launchable |
| `markets/` | Per-market Quarto scaffolds by act: `_template/`, `jacksonville/`, `richmond_va/` (includes the Richmond spec) | 2026-09 | Reference; Richmond is paused |
| `analysis_program/` | `01_ai_inversion/` spec and notes | 2026-08 | Reference; continued as Thematic A1 in the program |
| `docs/` | Analysis program, question banks, article-writer context notes | 2026-09 | Reference; the program doc sits above these |
| `templates/` | `metro_deep_dive_template_guidance.md`: the four-act template and fixed spine | 2026-07 | Reference; source for the fixed-spine decision |
| `metro_deep_dive_build_approach.md` | The build approach decision record | 2026-07 | Reference; see `docs/decisions/2026-07_deep-dive-fixed-spine.md` |
| `RESEARCH_TOOL_ROADMAP.md` | Research tool spec and build sequence | 2026-07 | Paused |
| `mart/` | DDL for an earlier `mart_deep_dive` schema | 2026-07 | Reference |
| `pipelines/`, `config/`, `outputs/` | Shared DB helper, local config template, output placeholder | 2026-06 to 07 | Unclear whether anything still uses them; check during the review |
| `tests/` | Tests for the industry, place intelligence, parcel and zone map code | 2026-08 | Runs with the code it tests |
| `archive/` | Retail Opportunity Finder apps and library, early market work, `industry_v0` | 2026-07 | Already archived |

## Still depended on

Update these before moving anything:

- `metro-deep-dive-program/engines/infrastructure/sources/osm_infrastructure.yml` reads OSM extracts from `metro-area-explorer/industry/outputs/` and `metro-area-explorer/place_intelligence/outputs/`.
- `metro-deep-dive-program/analyses/explanation/catchment/test_catchment.py` reads Jacksonville site artifacts from `metro-area-explorer/place_intelligence/outputs/`.
- `scripts/start_research_tool.sh` launches `research-tool/app.py`.
- `metro-deep-dive-program/metro_deep_dive_program.md` names several docs here (build approach, template guidance, analysis program, question banks, research tool roadmap) as the documents it sits above.

## Notes for the retirement review

- Five files in `metro-area-explorer/industry/` are byte-identical to copies in `archive/metro-area-explorer/industry_v0_2026-08-08/`, and `exploration/place_intelligence/ORIGINAL_SPEC.md` duplicates `metro-area-explorer/place_intelligence/SPEC_PLACE_INTELLIGENCE.md`. Keep them until the review.
- `mart_explanation_q6` in the warehouse belongs to the program, not this folder, but is also unresolved (see `docs/ARCHITECTURE.md` → Open items).

## Running the research tool

From the repo root:

```bash
scripts/start_research_tool.sh
```

The launcher finds the repo root, sets `DB_PATH` to `foundations/etl/data/duckdb/patterns_in_place.duckdb` by default, and uses the first Python environment that has Streamlit (`area-explorer/.venv`, then `.venv312`).
