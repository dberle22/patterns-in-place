## q008 manual run notes

- Question: Compare population growth over the last 5 years in the 5 fastest-growing metros.
- Template / chart type: `compare_selected` / `line_chart`
- Run scope: both

### What worked

- The indexed-series approach made the comparison much easier to read than raw population levels would have.
- Both renders tell the same story: the selected metros cluster fairly tightly through 2020, then Provo and Greeley separate more clearly by 2022-2023.
- The SQL logic for selecting the top five `2023` growth leaders and then pulling the full `2018-2023` history worked well.

### What needed adjustment

- The first SQL draft failed on a simple alias mismatch in the final `order by`, which is a reminder that these manual runs still benefit from a quick query-only validation before the render step.
- Python keeps the legend outside the plotting area and compresses the title/caption more than the R reference.
- The Python line chart also flattens the vertical story somewhat by using a broader y-range than the R reference.

### Data notes

- Final result set contains `30` rows: `5` selected CBSAs across `2018-2023`.
- Selected metros:
  - Provo-Orem-Lehi, UT
  - Greeley, CO
  - Myrtle Beach-Conway-North Myrtle Beach, SC
  - Austin-Round Rock-San Marcos, TX
  - Boise City, ID
- All series are indexed to `2018 = 100`.

### Parity verdict

- Verdict: `match_with_minor_drift`
- Remaining drift is mostly layout-level in Python: legend placement, title/caption density, and y-scale emphasis.
- This run is ready to count as `ran`.
