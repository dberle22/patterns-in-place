# POI Source Inventory

This directory holds source-specific acquisition declarations. The current
Overture Places baseline is declared in [overture_places.yml](overture_places.yml).
The older pilot release (`2026-06-17.0`) remains audit evidence only because it
is no longer present in Overture's public bucket; see [the audit notes](../NOTES.md).

Keep source configurations declarative and market-parameterized. A source run
must identify its release, governed boundary, query or partition, cache
location, and row accounting. Do not place downloaded source caches here.

Run a declared market with:

```sh
python3 metro-deep-dive-program/engines/poi/acquire_overture_places.py --market richmond_va
```

Add `--dry-run` to inspect the Geography-resolved boundary and source counts
without writing a cache. Runs are written below `engines/poi/outputs/`, which
is intentionally local and ignored by Git.
