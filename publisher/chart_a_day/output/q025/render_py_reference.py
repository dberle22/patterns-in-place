from pathlib import Path
import json
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, DimensionOverride, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q025")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"


def main() -> None:
    df = pd.read_csv(RESULT_PATH)
    df["geometry"] = df["geometry_json"].apply(json.loads)
    theme = Theme.default()
    theme.fonts["family"] = "Arial"

    request = ChartRequest(
        data=df,
        chart_type="highlight_context_map",
        theme=theme,
        column_mapping={
            "geometry": "geometry",
            "bin": "bin",
        },
        title="Where is Phoenix in the national vacancy landscape?",
        subtitle="CBSAs with population >= 250k | 2024 snapshot | Context colored by vacancy-rate tier",
        field_values={"variant": "binned"},
        dimensions=DimensionOverride(width=960, height=720),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )

    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


if __name__ == "__main__":
    main()
