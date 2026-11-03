# Upstate, Downstate: Folder Structure

**Status:** Active
**Updated:** 2026-11-02

How this folder is laid out, so every session puts things in the same place. For how to work on the series, start with the [repo context](upstate_downstate_repo_context.md).

## The one rule

**A piece's repo folder mirrors its vault folder.** The vault folder holds the words. The repo folder holds the notebooks and exhibits. When you start a piece, look up its path in the vault and use the same path here.

The vault is at:

```
/Users/danberle/Library/Mobile Documents/iCloud~md~obsidian/Documents/second_brain/patterns_in_place/ny_series/
```

On the Mac it links back to this folder through `repo_ny_state/`.

## Layout

```
ny_state/
  README.md                          this file
  upstate_downstate_repo_context.md  entry doc for Claude Code sessions
  NY_STATEWIDE_DATA_BUILD_PLAN.md    statewide POI and OSM run, deferred work
  question_bank.md                   question IDs and readiness
  exhibit_bank.md                    exhibit IDs and specs
  program_glossary.md                Metro Deep Dive terms
  _archive/<date>/                   snapshots of files before major rewrites
  primer/
    series_intro/
  metro_deep_dives/
    <metro>/                         Albany: albany/part_1, albany/part_2
  regional_deep_dives/
    NY_REGIONS_SPEC.md               region definitions, used across the series
    <piece>/
  rankings_and_analyses/             rankings, reader framings, other statewide analyses
    <piece>/
```

## Inside a piece folder

Create a folder when a piece gets its first notebook or query, not before. Add only the parts the piece uses.

| Path | What goes there |
|---|---|
| `<PIECE>_OUTLINE.md` | Outline, only when the build needs a repo copy. The vault outline is the main one |
| `<PIECE>_VISUALS_BUILD_PLAN.md` | Build plan and review record |
| `<PIECE>_EXPLORATION.py` | Tables, quick views and reads, never for print |
| `<PIECE>_VISUALS.py` | The print exhibits |
| `sql/` | Queries this piece uses |
| `reference/` | Hand-curated inputs, plus a sources file |
| `data/` | Pulled external files, plus a manifest with URL, date and checksum |
| `output/drafts/` | Working PNGs, rewritten on every run |
| `output/` | Finals (PNG and SVG), after sign-off |
| `drafts/` | Temporary working text only, see below |

Build steps and rules are in [VISUALS_BUILD_RULES.md](../VISUALS_BUILD_RULES.md).

## Shared files

- **A metro with several parts** keeps shared files at the metro root: `<metro>_common.py`, `<metro>_explore.py`, `sql/`, `data/` and `reference/`. A query starts in the part's `sql/` and moves to the root when a second part needs it. See the [Albany README](metro_deep_dives/albany/README.md).
- **Statewide layers** (canal, Adirondack and infrastructure) stay in `primer/series_intro/`. Other pieces read them from there and do not copy them.

## Naming

- **Folders:** lowercase with underscores, matching the vault. `part_<N>` for a metro that runs in parts.
- **Notebooks and build docs:** `<PIECE>_EXPLORATION.py`, `<PIECE>_VISUALS.py`, `<PIECE>_VISUALS_BUILD_PLAN.md`. `<PIECE>` is short and uppercase, such as `GROWTH` or `ALBANY_PART2`. Be flexible when a piece needs something else.
- **Exhibits:** PNG names start with the exhibit's short ID in that notebook, such as `e4_peer_table.png`.
- **Finished pieces keep their names.** Don't rename files in a published piece. `ALBANY_LENS1_*` in `albany/part_1/` and `WHAT_NY_IS_*` in `primer/series_intro/` are from before this layout, and other docs cite them by name.

## Article text belongs to the vault

Use the vault's text as context, not a copy in this repo. A working copy here is fine while developing a piece, and it should be deleted when the work is done.

| Piece | Text in the vault |
|---|---|
| Series Intro | `primer/series_intro/Series Intro.md` |
| Albany Part 1 | `metro_deep_dives/albany/part_1/Albany - What Albany Actually Is.md` |
| Albany Part 2 | `metro_deep_dives/albany/part_2/Albany Part 2 - More Than a Government Town.md` |

## Adding a piece

1. Find or create its folder in the vault. New ideas start there, from the outline template.
2. Create the same path here when the first notebook or query appears.
3. At publish, fill in the article's `repo` property in the vault with this folder path, and copy the final PNGs to the vault's `images/`.
