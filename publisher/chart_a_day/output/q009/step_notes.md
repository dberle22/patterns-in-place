## q009 manual run notes

- Question: How is rent-to-income distributed across US metros in 2023?
- Template / chart type: `distribution` / `boxplot`
- Run scope: both

### What worked

- Both stacks render the same overall distribution cleanly once the result set is kept in one canonical group.
- Excluding Puerto Rico produced a cleaner major-CBSA US distribution view and avoided outliers that were more about territory coverage than the intended national metro story.
- The Python boxplot path works as long as the wrapper preserves canonical `metric_value` instead of remapping it away.

### What needed adjustment

- The first Python wrapper broke because `metric_value` was mapped to a generic `value` field, but the Python boxplot prep expects the canonical `metric_value` column to survive.
- Python originally compressed the metadata text at the top of the chart more than the R reference.
- Python originally defaulted to a vertical single-group layout, but the renderer now flips single-group boxplots horizontally to match the stronger R presentation.

### Data notes

- Final result set contains `193` CBSAs with population `>= 250k` in `2023`, excluding Puerto Rico.
- Distribution is concentrated in the high teens to low 20s, with a long upper tail and visible high outliers near `29%`.
- Miami remains one of the clearest upper-tail metros in this distribution.

### Parity verdict

- Verdict: `match_with_minor_drift`
- Remaining drift is modest presentation polish around title/caption density, not chart structure or analytical story.
- This run is ready to count as `ran`.
