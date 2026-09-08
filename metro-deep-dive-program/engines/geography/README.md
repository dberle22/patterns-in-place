# Geography Engine

This folder is the repository entry point for the platform-wide geography
engine. Canonical production tables and ETL live under `foundations/`; stable
consumer helpers move to `foundations/geography/` once two consumers use the
same interface unchanged.

Start with:

- [Geography Engine Build Plan](GEOGRAPHY_ENGINE_BUILD_PLAN.md)
- [Geography Crosswalk Infrastructure Spec](geo_spec.md)
- [Contract](CONTRACT.md)
- [Audit notes](NOTES.md)

Purpose:

- provide shared geographic helpers, rollups, labels, and readable crosswalks used across multiple analyses

Expected first responsibilities:

- clarify the `dim_geo` path
- identify needed rollups and labels
- document vintage and boundary handling
