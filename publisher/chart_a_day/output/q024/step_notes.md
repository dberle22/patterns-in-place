## q024 manual run notes

- Question: Which states have the highest share of cost-burdened renters in 2023?
- Template / chart type: `map` / `choropleth`
- Run scope: both

### What worked

- The SQL output now carries both `geom_wkt` for the R path and `geometry_json` for the Python path, which let us render the same result set through both stacks.
- Both renders tell the same story: renter cost burden is highest in Florida, California, and Nevada in this 2023 snapshot.
- The R reference render is social-ready and gives us a stable visual benchmark for the Python geo path.

### What needed adjustment

- DuckDB needed `LOAD spatial` before the result extract because the geometry export uses `st_asgeojson()` and `st_astext()`.
- Python choropleth export needed `MPLBACKEND=Agg` plus a writable `MPLCONFIGDIR` to render reliably in this environment.
- The packaged Python theme still resolved to `Inter` here, so the manual render script had to force `Arial` as a local fallback.
- The first Python geo render felt cramped and used a misleading light-high color read, so the renderer was updated to use darker-high sequential blues plus figure-level title/layout treatment that better matches the stated visual contract.

### Data notes

- Final extract includes 49 rows: the contiguous 48 states plus DC.
- Alaska, Hawaii, and Puerto Rico were excluded to keep the map framing aligned across both renderers.
- Top five states in the result set:
  - Florida — `58.7%`
  - California — `54.7%`
  - Nevada — `54.3%`
  - Louisiana — `53.9%`
  - Colorado — `52.2%`

### Parity verdict

- Verdict: `match_with_minor_drift`
- Remaining drift is now mostly presentation-level in Python: title/caption spacing and the more compact map footprint relative to the R reference.
- This run should count as `ran` and as the first completed geo/manual parity proof point.
