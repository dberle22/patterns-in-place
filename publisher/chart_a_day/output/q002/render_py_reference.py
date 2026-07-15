from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, NumberFormat, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q002")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"


def main() -> None:
    df = pd.read_csv(RESULT_PATH)
    theme = Theme.default()
    theme.fonts["family"] = "Arial"

    request = ChartRequest(
        data=df,
        chart_type="bar_chart",
        theme=theme,
        column_mapping={
            "geo_name": "entity",
            "metric_value": "value",
            "rank_desc": "rank",
        },
        title="Which states have the highest median household income in 2023?",
        subtitle="Top 10 states by median household income | District of Columbia included",
        number_format=NumberFormat(unit="currency", decimals=0),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )

    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


if __name__ == "__main__":
    main()
