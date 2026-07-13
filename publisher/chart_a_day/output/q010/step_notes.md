## q010 manual run notes

- Question: How is median age distributed across US metros in 2023?
- Template / chart type: `distribution` / `boxplot`
- Run scope: both

### What worked

- Both stacks render the same underlying age distribution clearly once the result set is kept in a single canonical group.
- The updated Python single-group boxplot layout carries over well here and avoids the weak vertical composition we saw earlier.

### What needed adjustment

- Python still compresses title, subtitle, and caption text more than the R reference.
- The Python export keeps denser axis tick labeling than the R version, which adds a little noise to an otherwise simple distribution view.

### Data notes

- Final result set contains `193` CBSAs with population `>= 250k` in `2023`, excluding Puerto Rico.
- Median age is centered in the upper 30s, with the youngest large metros near `25.6` and the oldest near `53.5`.

### Parity verdict

- Verdict: `match_with_minor_drift`
- Remaining drift is presentation-level, not analytical.
- This run is ready to count as `ran`.
