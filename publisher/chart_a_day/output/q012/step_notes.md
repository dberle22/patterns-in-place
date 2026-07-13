## q012 manual run notes

- Question: How does Phoenix's median gross rent compare to the Western US average in 2023?
- Template / chart type: `benchmark` / `bar_chart`
- Run scope: both

### What worked

- Both stacks render the same benchmark comparison cleanly with Phoenix slightly below the Western-region average.
- The single-bar benchmark path remains a good regression checkpoint for benchmark spacing and annotation.

### What needed adjustment

- Python still packs the metadata block more tightly than the R reference.
- The benchmark callout remains readable, but the R version still feels a bit more deliberate in how it balances the bar, benchmark line, and empty space.

### Data notes

- Final result set contains one highlighted metro row for `Phoenix-Mesa-Chandler, AZ`.
- Phoenix's `2023` median gross rent is about `$1,572`.
- The Western-region benchmark across CBSAs with population `>= 250k` is about `$1,659`.

### Parity verdict

- Verdict: `match_with_minor_drift`
- Remaining drift is mostly benchmark annotation polish, not chart logic.
- This run is ready to count as `ran`.
