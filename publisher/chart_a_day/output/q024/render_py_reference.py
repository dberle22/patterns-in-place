from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, DimensionOverride, NumberFormat, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q024")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"


def main() -> None:
    df = pd.read_csv(RESULT_PATH)
    df["geometry"] = df["geometry_json"].apply(json.loads)

    theme = Theme.default()
    theme.fonts["family"] = "Arial"

    request = ChartRequest(
        data=df,
        chart_type="choropleth",
        theme=theme,
        column_mapping={"geometry": "geometry"},
        title="Which states have the highest share of cost-burdened renters in 2023?",
        subtitle="Contiguous 48 states plus DC | 2023 snapshot | Darker states = higher renter cost burden",
        number_format=NumberFormat(unit="count", decimals=1),
        field_values={"variant": "continuous"},
        dimensions=DimensionOverride(width=960, height=700),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )

    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


if __name__ == "__main__":
    main()
