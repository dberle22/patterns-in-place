# Line Contract Review (Proposed)

## Status
Proposed for confirmation.

## Required Fields (Proposal)
- `geo_level`
- `geo_id`
- `geo_name`
- `period`
- `metric_id`
- `metric_label`
- `metric_value`
- `source`
- `vintage`

## Optional Fields (Proposal)
- `time_window`
- `group`
- `highlight_flag`
- `benchmark_value`
- `index_base_period`
- `note`

## Rationale
- Keep minimum required fields focused on universal rendering.
- Keep transformation and benchmarking fields optional to support multiple line variants without over-constraining base datasets.

## Review Questions
1. Should `time_window` be required when variant is not `single`?
2. Should `group` be required for benchmark comparison mode?
3. Do we require `index_base_period` for any row where `time_window = indexed`?
