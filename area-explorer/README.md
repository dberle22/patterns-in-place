# Area Explorer

Metric-first interactive dashboards for the Patterns in Place data platform. You pick a theme, subject, topic, or metric — the map and charts update around that selection across all geographies.

## Product structure

Three independent Streamlit apps connected by a landing page. Each is self-contained; cross-links open in a new tab.

| App | Audience | Intelligence frames | Status |
|---|---|---|---|
| `apps/cbsa_internal/` | Dan (analytical) | Yes — clusters, scores, peers | Phase 1 |
| `apps/cbsa_public/` | Readers / clients | No — metrics + benchmarks | Phase 2 |
| `apps/county_explorer/` | Both | No | Phase 3 |
| `landing/` | Both | — | Phase 2 |

See `AREA_EXPLORER_ROADMAP.md` for the full spec, layout, technical decisions, and build phases.

## Running the apps

Set the DB connection env var, then launch the desired app:

```bash
export DB_CONNECTION="/path/to/patterns_in_place/foundations/data/foundations.duckdb"

# CBSA Internal (analytical, with Intelligence frames)
streamlit run apps/cbsa_internal/app.py

# CBSA Public (reader-facing, no frame scores)
streamlit run apps/cbsa_public/app.py

# County Explorer
streamlit run apps/county_explorer/app.py
```

The existing `app/data_explorer.py` and `app/explorer_utils.py` are migration-state reference — they remain runnable but are being replaced by the new structure above.

## Shared library

`shared/` contains the query layer, catalog loader, GeoJSON utilities, benchmark helpers, and reusable UI components. App files do not contain SQL or data logic — all of that lives in `shared/`.

## Related products

- **Deep Dive Research Tool** (`metro-deep-dive/RESEARCH_TOOL_ROADMAP.md`) — place-first research surface; pick a metro and see its full profile. Different entry point, different purpose.
- **Chatbot / Publisher** (`publisher/`) — question-first entry point. NL → SQL → chart pipeline.
