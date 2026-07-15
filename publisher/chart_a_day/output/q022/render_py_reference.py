from pathlib import Path
import faulthandler
import sys
import warnings

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, DimensionOverride, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q022")
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

    request = ChartRequest(
        data=df,
        chart_type="correlation_heatmap",
        theme=theme,
        title="How correlated are rent burden, vacancy rate, income growth, and population growth across US metros?",
        subtitle="CBSAs with population above 250k | Spearman correlation | 2023 cross-section with 5-year growth metrics",
        field_values={"method": "spearman", "order_method": "clustered", "show_cell_labels": True},
        dimensions=DimensionOverride(width=860, height=760),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )

    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


if __name__ == "__main__":
    main()
