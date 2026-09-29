# Changelog

This project follows versioned, immutable data releases. Published versions are never silently
replaced; corrections ship as a new version with a coverage and schema comparison.

## Unreleased v2026.1

### Added

- Static OMB 2023 county-to-CBSA crosswalk for 935 current CBSAs.
- 2012–2024 ACS employment-composition and affordability panel fields.
- 2012–2024 county-derived BEA real GDP total and three optional GDP-industry shares.
- FY2012–FY2024 county-derived HUD two-bedroom FMR and FMR gap.
- Field-level source, formula, vintage, null-behavior, and coverage documentation.

### Intentionally excluded

- Zillow and Zillow-derived values; BEA RPP and metro real-personal-income fields; BEA GDP
  industry HHI; BFS, CBP, QCEW, CHAS, permits, vacancy, and occupancy measures.
