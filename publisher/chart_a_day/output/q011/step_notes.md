## q011 manual run notes

- Question: How does Miami's share of cost-burdened renters compare to the national average in 2023?
- Template / chart type: `benchmark` / `bar_chart`
- Run scope: both

### What worked

- The benchmark pattern is straightforward when the national comparison lives in the same mart as the focal metro value.
- Both renders make the core point clearly: Miami sits well above the national renter-burden share in `2023`.
- The one-bar-plus-benchmark-line structure is readable in both stacks and works for a short social post.

### What needed adjustment

- The Python wrapper again had to wait for the SQL extract to finish before reading `result.csv`; the manual run order matters more than the wrapper assumes.
- Python still compresses subtitle and caption text more than the R reference, especially on a single-bar chart where the extra whitespace makes the difference more obvious.
- The benchmark label placement in Python is acceptable, but still less polished than the R reference treatment.

### Data notes

- Final result set contains one focal CBSA row plus the benchmark value embedded on the row.
- Miami-Fort Lauderdale-West Palm Beach, FL — `63.1%`
- United States benchmark — `50.4%`
- Gap vs US benchmark — about `12.8` percentage points.

### Parity verdict

- Verdict: `match_with_minor_drift`
- Remaining drift is presentation-level: Python title/subtitle/caption density and slightly rougher benchmark annotation placement.
- This run is ready to count as `ran`.
