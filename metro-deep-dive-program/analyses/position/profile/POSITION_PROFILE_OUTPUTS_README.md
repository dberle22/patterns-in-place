# Position Profile Outputs

This folder's artifacts are QA bundles from a reusable parameterized analysis.

Structure:

- `figures/<cbsa_code>/`
  Lightweight HTML validation visuals written by `profile.py` for that same
  run.

The Marimo notebook renders exploratory outputs in place and does not need to
export files.

Use this layer to inspect whether the analysis behaves plausibly for a target
metro. Do not treat these artifacts as locked issue deliverables or as a
replacement for DuckDB-backed queries.
