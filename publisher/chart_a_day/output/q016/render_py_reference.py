from pathlib import Path
import faulthandler
import os
import sys
import warnings

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, DimensionOverride, NumberFormat, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q016")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"
ALT_CHART_PATH = OUTPUT_DIR / "chart_alt.png"
MPL_CACHE_DIR = Path("/tmp/mpl_cache_q016")


def render_scatter(df: pd.DataFrame, theme: Theme) -> None:
    request = ChartRequest(
        data=df,
        chart_type="scatter",
        theme=theme,
        title="How does rent-to-income ratio correlate with 5-year population growth across major metros?",
        subtitle="Major CBSAs with population 500k+ | X = 2018-2023 population growth | Y = 2023 rent-to-income ratio",
        number_format=NumberFormat(unit="count", decimals=1),
        field_values={"highlight_mode": "labels", "add_quadrants": True, "add_reference_line": False},
        dimensions=DimensionOverride(width=980, height=620),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )
    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


def render_hexbin(df: pd.DataFrame, theme: Theme) -> None:
    request = ChartRequest(
        data=df,
        chart_type="hexbin",
        theme=theme,
        title="Alternative view: growth and rent pressure across major metros",
        subtitle="Major CBSAs with population 500k+ | Hexbin density view",
        number_format=NumberFormat(unit="count", decimals=1),
        output=OutputConfig(save=True, path=ALT_CHART_PATH, format="png"),
    )
    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


def main() -> None:
    faulthandler.enable()
    warnings.filterwarnings(
        "ignore",
        message="the convert_dtype parameter is deprecated.*",
        category=FutureWarning,
    )

    # Hexbin uses Matplotlib static export, so make the backend/cache explicit.
    os.environ.setdefault("MPLBACKEND", "Agg")
    MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))

    df = pd.read_csv(RESULT_PATH)
    theme = Theme.default()
    theme.fonts["family"] = "Arial"
    print("rendering q016 scatter...")
    render_scatter(df, theme)
    print("rendering q016 optional hexbin fallback...")
    try:
        render_hexbin(df, theme)
    except Exception as exc:
        # The fallback chart is useful for QA, but it should not hide the
        # success or failure state of the primary scatter render.
        print(f"warning: optional hexbin fallback failed: {exc}")


if __name__ == "__main__":
    main()
