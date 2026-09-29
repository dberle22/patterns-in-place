# Candidate Scan Analysis

Purpose:

- provide the internal all-market surface for choosing which CBSA to review next
- port the useful Candidate List behavior from the legacy Research Tool into Marimo
- update the scan to use the current Position and Time-Series contracts

Start with `POSITION_CANDIDATE_DISCOVERY_NOTEBOOK.py` for a light,
plain-language market-discovery workflow. Use
`POSITION_CANDIDATE_SCAN_NOTEBOOK.py` for transparent component ranks, legacy
comparison, sensitivity, and QA once a discussion shortlist emerges.

See [POSITION_CANDIDATE_SCAN_SPEC.md](POSITION_CANDIDATE_SCAN_SPEC.md) for the
analysis boundary and
[POSITION_CANDIDATE_SCAN_BUILD_PLAN.md](POSITION_CANDIDATE_SCAN_BUILD_PLAN.md)
for the high-level implementation sequence.
