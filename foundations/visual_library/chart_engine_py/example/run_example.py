"""
This is everything a caller in ANY consuming repo (PiP, work, whatever)
needs to write. No imports from prep/, render/, registry.py, or specs.py
— render_chart() and Theme are the entire public API.
"""

import sys

import pandas as pd

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from chart_engine import ContractError, Theme, render_chart

# The package now ships a canonical PiP theme, so the simplest consumer path
# is "load the default theme and render." A caller that wants custom branding
# can still point Theme.from_yaml() at its own override file.
theme = Theme.default()

# --- Example 1: bar chart (ranking) ---------------------------------
rent_burden = pd.DataFrame({
    "cbsa_name": ["Miami", "Los Angeles", "New York", "Riverside", "San Diego"],
    "rent_to_income_pct": [42.1, 39.8, 37.5, 36.2, 35.9],
})

bar = render_chart(
    data=rent_burden,
    chart_type="bar_chart",
    theme=theme,
    column_mapping={"cbsa_name": "entity", "rent_to_income_pct": "value"},
)
bar.save(str(Path(__file__).parent / "output_bar.html"))
print("Saved output_bar.html")

# --- Example 2: line chart (trend, metro vs national) ----------------
income_trend = pd.DataFrame({
    "year": [2019, 2020, 2021, 2022, 2023] * 2,
    "median_income": [58000, 59500, 62000, 65500, 68200,
                       57000, 58200, 60100, 62800, 65000],
    "geo": ["Jacksonville"] * 5 + ["US National"] * 5,
})

line = render_chart(
    data=income_trend,
    chart_type="line_chart",
    theme=theme,
    column_mapping={"year": "period", "median_income": "value", "geo": "series"},
)
line.save(str(Path(__file__).parent / "output_line.html"))
print("Saved output_line.html")

# --- Example 3: contract validation catching a bad input -------------
bad_data = pd.DataFrame({"cbsa_name": ["Miami"], "some_other_column": [1]})
try:
    render_chart(
        data=bad_data,
        chart_type="bar_chart",
        theme=theme,
        column_mapping={"cbsa_name": "entity"},  # 'value' still missing on purpose
    )
except ContractError as e:
    print(f"\nContract validation caught the bad input as intended:\n  {e}")
