## q025 manual run notes

- Question: Where is Phoenix in the national vacancy landscape?
- Template / chart type: `map` / `highlight_context_map`
- Run scope: both

### What worked

- The SQL path successfully joined `gold.housing_core_wide`, `gold.dim_geo`, and `geo.cbsas`, and the result set carried both `geometry_json` for Python and `geom_wkt` for R.
- Phoenix is highlighted correctly in both outputs, and the R reference map reads well as a focal-market context map.
- Excluding Alaska, Hawaii, and Puerto Rico improved the framing relative to the first draft.
- After the renderer fix pass, the Python map now uses the available canvas much more effectively, keeps the vacancy-tier legend outside the plotted geography, and explains the highlight role separately from the color tiers.

### What needed adjustment

- `.venv312` can now connect to DuckDB, but its DuckDB setup does not have the `spatial` extension installed locally, so the q025 extract still had to use the system Python path that already had `LOAD spatial` available.
- The first Python render was materially off relative to the R reference: the map footprint was tiny inside the canvas and the legend treatment did not communicate the vacancy-rate tiers clearly.
- The Python renderer now reserves dedicated legend space, labels the highlighted geography directly, and separates tier encoding from map-role annotation.
- Python also emitted a new font-cache warning pattern for this Matplotlib map path, even though it completed successfully with `MPLBACKEND=Agg` and a writable `MPLCONFIGDIR`.

### Data notes

- Final result set contains `192` CBSAs with population `>= 250k` in `2024`, excluding AK, HI, and PR.
- Phoenix-Mesa-Chandler, AZ has a `2024` vacancy rate of about `8.5%`, placing it in the `Balanced (8-12%)` tier.
- Context tiers used:
  - `Very tight (<5%)`
  - `Tight (5-8%)`
  - `Balanced (8-12%)`
  - `Loose (12%+)`

### Parity verdict

- Verdict: `match_with_minor_drift`
- The Python highlight-context map is now close enough in composition and legend treatment to count as a real parity candidate, even though the R reference still feels slightly more spacious and polished.
- This run should count as `ran` in the backlog and as a completed Phase 5 parity item.
