from pathlib import Path
import faulthandler
import sys
import warnings

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, DimensionOverride, NumberFormat, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q019")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"

SHORT_NAMES = {
    "Austin-Round Rock-San Marcos, TX": "Austin",
    "Dallas-Fort Worth-Arlington, TX": "Dallas-Fort Worth",
    "Phoenix-Mesa-Chandler, AZ": "Phoenix",
    "Nashville-Davidson--Murfreesboro--Franklin, TN": "Nashville",
    "Charlotte-Concord-Gastonia, NC-SC": "Charlotte",
    "Atlanta-Sandy Springs-Roswell, GA": "Atlanta",
    "Tampa-St. Petersburg-Clearwater, FL": "Tampa",
    "Orlando-Kissimmee-Sanford, FL": "Orlando",
}


def main() -> None:
    faulthandler.enable()
    warnings.filterwarnings(
        "ignore",
        message="the convert_dtype parameter is deprecated.*",
        category=FutureWarning,
    )

    df = pd.read_csv(RESULT_PATH)
    df["geo_name"] = df["geo_name"].map(lambda value: SHORT_NAMES.get(value, value))
    theme = Theme.default()
    theme.fonts["family"] = "Arial"
    print("rendering q019 heatmap table...")

    request = ChartRequest(
        data=df,
        chart_type="heatmap_table",
        theme=theme,
        title="How do rent burden, vacancy rate, and population growth compare across Sun Belt metros in 2023?",
        subtitle="Austin plus 7 Sun Belt peers | Fill shows a metric-specific housing-stress percentile within major metros",
        number_format=NumberFormat(unit="percent", decimals=1),
        field_values={
            "normalize": False,
            "fill_value_field": "normalized_value",
            "label_value_field": "metric_value",
            "show_cell_labels": True,
            "legend_title": "Stress percentile",
            "auto_label_max_cells": 30,
        },
        dimensions=DimensionOverride(width=900, height=520),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )

    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


if __name__ == "__main__":
    main()
