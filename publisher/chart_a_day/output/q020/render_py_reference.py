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


OUTPUT_DIR = Path("publisher/chart_a_day/output/q020")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"


def main() -> None:
    faulthandler.enable()
    warnings.filterwarnings(
        "ignore",
        message="the convert_dtype parameter is deprecated.*",
        category=FutureWarning,
    )

    df = pd.read_csv(RESULT_PATH)
    theme = Theme.default()
    theme.fonts["family"] = "Arial"
    print("rendering q020 waterfall...")

    request = ChartRequest(
        data=df,
        chart_type="waterfall",
        theme=theme,
        title="What share of US metros fall into each vacancy rate tier in 2023?",
        subtitle="CBSAs with population 250k+ | Tier shares sum to 100% of the 196-metro universe",
        number_format=NumberFormat(unit="percent", decimals=1),
        field_values={"value_mode": "level"},
        dimensions=DimensionOverride(width=960, height=560),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )

    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


if __name__ == "__main__":
    main()
