from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import BenchmarkConfig, ChartRequest, NumberFormat, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q012")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"


def main() -> None:
    df = pd.read_csv(RESULT_PATH)
    theme = Theme.default()
    theme.fonts["family"] = "Arial"

    benchmark_value = float(df["benchmark_value"].dropna().iloc[0])

    request = ChartRequest(
        data=df,
        chart_type="bar_chart",
        theme=theme,
        column_mapping={
            "geo_name": "entity",
            "metric_value": "value",
            "rank_desc": "rank",
            "benchmark_value": "benchmark_value",
        },
        title="How does Phoenix's median gross rent compare to the Western US average in 2023?",
        subtitle="Phoenix-Mesa-Chandler, AZ | 2023 snapshot | West benchmark shown for reference",
        benchmark=BenchmarkConfig(
            kind="custom",
            value=benchmark_value,
            label=f"West avg: ${benchmark_value:,.0f}",
        ),
        number_format=NumberFormat(unit="usd", decimals=0),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )

    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


if __name__ == "__main__":
    main()
