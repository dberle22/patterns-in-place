# Commute Sheds Engine

Builds a tract-to-tract LODES OD artifact for one CBSA at a time in the shared
DuckDB database. It is intentionally incremental: no national tract-pair mart
is created.

Run from the repository root:

```sh
python3 metro-deep-dive-program/engines/commute_sheds/build_tract_commute_shed.py --cbsa-code 40060 --scope workplace_side
```

Use `--scope either_endpoint` only when outbound resident flows are required.
That scope must read `aux` assets from every available workplace state, because
LODES is partitioned by workplace state. See `CONTRACT.md` for the difference.
