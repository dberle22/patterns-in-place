from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, NumberFormat, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q001")
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
        title="Which metros have the highest rent-to-income ratios in 2023?",
        subtitle="Top 15 CBSAs by rent-to-income ratio | Population filter: 250k+ | Puerto Rico metros excluded",
        number_format=NumberFormat(unit="count", decimals=1),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )

    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


if __name__ == "__main__":
    main()
