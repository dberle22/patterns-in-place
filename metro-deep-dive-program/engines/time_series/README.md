# Time-Series / Trajectory Engine

This engine builds the first versioned, DuckDB-backed trajectory mart. It
currently covers a 50-metric direct recurring panel, a stable 396-CBSA
universe, and a common 2023 end vintage. The eight derived-change candidates
remain documented for later review rather than scored in this panel.

Run the build from the repository root:

```bash
python3 metro-deep-dive-program/engines/time_series/build_time_series_engine.py
```

Use `--dry-run` to calculate and validate the full panel without writing. The
builder resolves `DB_PATH` from the environment or repository `.Renviron`; it
does not contain a machine-specific database path.

The canonical outputs are the four `mart_intelligence.intelligence_trajectory_*`
tables described in [CONTRACT.md](CONTRACT.md). `outputs/review/` receives
Parquet snapshots and the threshold-sensitivity CSV copied from those tables;
they are review artifacts, not downstream inputs.

See [TIME_SERIES_ENGINE_BUILD_PLAN.md](TIME_SERIES_ENGINE_BUILD_PLAN.md) for
the agreed method, inventory, and remaining expansion work. See
[time_series_architecture.drawio](time_series_architecture.drawio) for the
editable architecture, and [NOTES.md](NOTES.md) for the pilot-vintage decision
and legacy Phase 6 disposition.

## Use the engine

1. Open the Position Trajectory notebook to inspect frame paths, metric
   evidence, coverage, and turn-status results for a selected CBSA.
2. Before rebuilding, close Marimo notebooks or other Python processes that
   hold a connection to DuckDB.
3. Run the dry build first:

   ```bash
   python3 metro-deep-dive-program/engines/time_series/build_time_series_engine.py --dry-run
   ```

4. Review the console counts and `outputs/review/` artifacts. If they are
   acceptable, run the same command without `--dry-run` to replace the four
   canonical trajectory tables together.

## Expand the KPI panel

The registry at `config/trajectory_metrics.yml` is the only place to add a
scored KPI. Add a direct recurring annual series only after confirming its Gold
source has one CBSA-year row, supports the configured start/end years, and has
an explicit frame, topic, transformation, polarity, and compatible windows.

Each registry entry requires `metric_id`, `metric_label`, `frame_id`,
`topic_id`, `source_table`, `source_column`, `transform`, `polarity`, and
`windows`. Metric IDs must be unique across the full registry. When the same
underlying source is intentionally used in two frames, give the second use a
clear frame-qualified metric ID while retaining its original source column.

Do not add derived-change fields just because they are available. The current
derived-change review queue is documented in the build plan; prefer the
underlying annual level series unless acceleration or deceleration is the
explicit analytical target. After every registry change, run the dry build,
inspect coverage and topic balance in the notebook, then materialize once.
