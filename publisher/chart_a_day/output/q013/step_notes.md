## q013 manual run notes

- Question: Which metros have had the fastest 5-year population growth since 2018?
- Template / chart type: `growth` / `bar_chart`
- Run scope: both

### What worked

- Both stacks tell the same growth-ranking story cleanly, with the top five highlighted consistently.
- The improved Python bar path handles this larger ranked list better than the earliest CE runs.

### What needed adjustment

- Python still truncates longer metro labels more aggressively than the R reference.
- The Python subtitle/caption stack is denser than the R version, especially on a 15-row ranking chart.

### Data notes

- Final result set contains the top `15` CBSAs by `2023` five-year population growth among metros with population `>= 250k`.
- Top five metros in the extract:
  - `Provo-Orem-Lehi, UT` — `15.7%`
  - `Greeley, CO` — `15.4%`
  - `Myrtle Beach-Conway-North Myrtle Beach, SC` — `15.0%`
  - `Austin-Round Rock-San Marcos, TX` — `14.5%`
  - `Boise City, ID` — `13.9%`

### Parity verdict

- Verdict: `match_with_minor_drift`
- Remaining drift is presentation-level around label density and text spacing.
- This run is ready to count as `ran`.
