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


OUTPUT_DIR = Path("publisher/chart_a_day/output/q021")
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
    print("rendering q021 strength strip...")

    request = ChartRequest(
        data=df,
        chart_type="strength_strip",
        theme=theme,
        title="How does Austin rank across housing stress indicators in 2023?",
        subtitle="Austin vs large-metro median benchmark | Rightward percentile means more housing stress or demand pressure",
        number_format=NumberFormat(unit="percent", decimals=1),
        field_values={"normalize": False, "metric_order": ["rent_to_income", "vacancy_rate", "pop_growth_5yr", "cost_burden_share"]},
        dimensions=DimensionOverride(width=920, height=460),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )

    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


if __name__ == "__main__":
    main()
