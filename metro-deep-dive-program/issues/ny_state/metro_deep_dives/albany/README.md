# Albany

The Albany-Schenectady-Troy articles in the New York series. Each part has its own folder, matching its vault folder; anything more than one part uses sits here at the root. The [series README](../../README.md) has the wider layout.

## Status

Active, last worked on 2026-11-02. Part 1 is posted. Part 2 follows the growth ranking; the vault's Series Overview has the order.

| Part | Article | Folder | State |
|---|---|---|---|
| 1 | What Albany Actually Is | [part_1/](part_1/) | Posted |
| 2 | Is Albany More Than a Government Town? | [part_2/](part_2/) | Exploration only, started from the Lens 2 commuting notebook |

Part 1's files keep their `ALBANY_LENS1_` names because that piece is finished.

## How to run it

From the repo root, with `.venv-marimo`. `DB_PATH` comes from `.Renviron`.

```
.venv-marimo/bin/marimo edit metro-deep-dive-program/issues/ny_state/metro_deep_dives/albany/part_1/ALBANY_LENS1_VISUALS.py
```

Running a visuals notebook rewrites that part's `output/drafts/`. Three maps (`e6`, `e6b`, `e9`) change by a small number of pixels on every run, even with no code change, so a changed PNG in git doesn't always mean a changed exhibit.

## Folder layout

```
albany/
  README.md
  albany_common.py     paths, constants, shared loaders, map and chart helpers
  albany_explore.py    exploration-only tables, maps and charts
  sql/                 queries more than one part uses
  data/                pulled files, shared by every part
  reference/           hand-curated inputs, shared by every part
  part_<N>/
    ALBANY_PART<N>_OUTLINE.md
    ALBANY_PART<N>_VISUALS_BUILD_PLAN.md
    ALBANY_PART<N>_EXPLORATION.py
    ALBANY_PART<N>_VISUALS.py
    drafts/                     temporary working text, deleted when the work is done
    sql/                        queries only this part uses
    output/                     finals; output/drafts/ for working PNGs
```

- **Article text** lives in the vault, in `metro_deep_dives/albany/part_<N>/`. Use it as context.
- **Queries** start in the part's `sql/` and move to the root `sql/` when a second part needs them. In a notebook, `LENS_SQL_DIR` is the part's folder and `SQL_DIR` is the root's.
- **Helpers** for one exhibit stay in that part's visuals notebook. Anything another part uses moves to `albany_common.py`. No part imports from another part's notebook.
- **`save()`** stays in each visuals notebook because it writes to that part's `output/`.

## Key docs

1. [Series README](../../README.md): layout and naming across the series
2. [Part 1 outline](part_1/ALBANY_LENS1_OUTLINE.md) and [build plan](part_1/ALBANY_LENS1_VISUALS_BUILD_PLAN.md): the worked example, including the review history
3. [Visuals build rules](../../../VISUALS_BUILD_RULES.md): how to go from an outline to print visuals

## Depends on / depended on by

- **Reads from:** the warehouse (read-only), `analyses/explanation/q2_job_proximity/`, `engines/poi/outputs/albany_ny/`, `foundations/etl/reference/ny_county_regions.csv`, and `../../primer/series_intro/` for the infrastructure, canal and Adirondack layers.
- **Read by:** nothing outside this folder.
- **Local-only files:** the OSM, Wikipedia and Census downloads in `data/` are gitignored, and the visuals notebook needs them. Provenance is in [data/anchors_reference_manifest.json](data/anchors_reference_manifest.json).
