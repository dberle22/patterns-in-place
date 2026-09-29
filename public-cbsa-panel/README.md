# Metro & Micro Panel Release Workspace

This private workspace prepares **Patterns in Place: Metro & Micro Panel**, a small, citable public release from the Patterns in Place Gold layer. It is intentionally separate from the eventual `pip-metro-micro-panel` public repository: v2026.1 exports from the private Gold DuckDB, while the released data, documentation, and public-safe build code will later be copied into that standalone repository.

## v2026.1 contract

The release contains a static current-vintage `cbsa_county_crosswalk` and two CBSA-year panels: `economics_industry_wide` and `affordability_wide`. It includes all 935 current metropolitan and micropolitan CBSAs. The frozen scope and public allowlists are in [v2026.1_scope.md](spec/v2026.1_scope.md).

## Local release build

The release builder is intentionally private-monorepo tooling. It takes an explicit Foundations
DuckDB path and writes a new, gitignored output directory; it never records the local input path
in the public manifest.

```sh
python3 public-cbsa-panel/scripts/build_release.py \
  --db foundations/etl/data/duckdb/patterns_in_place.duckdb \
  --output public-cbsa-panel/output/v2026.1 \
  --version v2026.1
```

The command assumes it is run from the monorepo root. You can instead set
`PIP_FOUNDATIONS_DUCKDB` and pass `--db "$PIP_FOUNDATIONS_DUCKDB"`; Python does not load R's
`.Renviron` automatically.

The command validates the allowlist, keys, CBSA universe, null thresholds, and held-back source
boundary before writing ZSTD Parquet files, a bundled DuckDB with `_manifest`, `manifest.json`,
and `coverage_report.md`. To compare a refresh with a preceding release, pass
`--prior-manifest <path>`; row-count or schema changes require the explicit
`--allow-coverage-change` flag.

The detailed build flow and implementation choices are documented in [BUILD.md](BUILD.md).
Run the focused validation fixtures with:

```sh
python3 -m unittest public-cbsa-panel/tests/test_release_validation.py
```

The complete sequenced workplan, acceptance criteria, and Dan-owned publication tasks are in [BUILD_PLAN.md](BUILD_PLAN.md).

## Release sequence

- [x] Define v2026.1 table boundaries and exclusions.
- [x] Complete Epic 1: audit lineage and freeze `config/tables.yml`.
  - [x] Inventory candidate fields and inspect live Gold/crosswalk coverage.
  - [x] Confirm public `value_to_income` is ACS-based rather than Zillow-based.
  - [x] Resolve the primary-state derivation from the existing governed geography model.
  - [x] Record authoritative source-family references.
  - [x] Review sparse BEA/HUD coverage and approve the final field treatment.
  - [x] Freeze the approved allowlist in `config/tables.yml`.
- [x] Complete Epics 2–3: build the exporter, validation, and coverage report.
- [x] Complete Epic 4 documentation and configurable examples; run them against the canonical public URL during Epic 5.
- [ ] Complete Epic 5: establish public accounts and publish v2026.1.
- [ ] Complete Epic 6: publish the analysis and outreach materials.
- [ ] Complete Epic 7: automate source checks and prepare v2 candidates.

## Handoff rule

No build code, documentation, or output becomes public until the lineage audit has confirmed that every released field is in scope and has no Zillow dependency.
