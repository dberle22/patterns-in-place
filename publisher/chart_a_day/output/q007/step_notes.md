## q007 manual run notes

- Question: Compare median gross rent in Austin, Nashville, Denver, and Charlotte in 2023.
- Template / chart type: `compare_selected` / `bar_chart`
- Run scope: both

### What worked

- The new `.venv312` setup now covers both DuckDB extraction and Python rendering, so this run used one Python environment end to end.
- The explicit selected-metro SQL pattern worked well for a `compare_selected` question and avoided any ambiguity about which CBSAs belong in the chart.
- Both stacks told the same story: Denver had the highest median gross rent in this peer set, followed by Austin, Nashville, and Charlotte.

### What needed adjustment

- The first R wrapper failed because `prep_bar()` was given the wrong `time_window`; the config had to match the SQL output exactly.
- The R wrapper also expected `label_style = "dollar"` rather than `"currency"`.
- Python still truncates long CBSA labels more aggressively than the R reference and packs subtitle/caption text more tightly.

### Data notes

- Final result set contains four rows, one per selected CBSA.
- Values in the output:
  - Denver-Aurora-Centennial, CO — `$1,813.84`
  - Austin-Round Rock-San Marcos, TX — `$1,635.30`
  - Nashville-Davidson--Murfreesboro--Franklin, TN — `$1,422.75`
  - Charlotte-Concord-Gastonia, NC-SC — `$1,323.00`
- Benchmark used: average median gross rent across CBSAs with population `>= 250k` in `2023` (`$1,285.98`).

### Parity verdict

- Verdict: `match_with_minor_drift`
- Remaining drift is presentation-level: Python label truncation, tighter title/subtitle/caption spacing, and less polished benchmark annotation placement.
- This run is ready to count as `ran`.
