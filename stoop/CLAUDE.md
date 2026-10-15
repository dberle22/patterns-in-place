# CLAUDE.md

See `<monorepo-root>/AGENTS.md` for full behavioral guidelines.
See `stoop/AGENTS.md` for stoop-specific additions.

## Quick orientation

`stoop/` is the home of Stoop Explore and Stoop Search within the
`patterns-in-place` monorepo.

- Boot the app: `streamlit run app/stoop_explore.py` from `stoop/`
- Core library: `src/nyc_property_finder/`
- Data: `data/processed/nyc_property_finder.duckdb` (local-only, gitignored)
- Product strategy: `docs/product_strategy.md`; open questions for Explore and Search
  are at the end of `docs/README.md`
