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


OUTPUT_DIR = Path("publisher/chart_a_day/output/q028")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"
MPL_CACHE_DIR = Path("/tmp/mpl_cache_q028")
XDG_CACHE_DIR = Path("/tmp/xdg_cache_q028")


def main() -> None:
    faulthandler.enable()
    warnings.filterwarnings(
        "ignore",
        message="the convert_dtype parameter is deprecated.*",
        category=FutureWarning,
    )

    os.environ.setdefault("MPLBACKEND", "Agg")
    MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    XDG_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
    os.environ.setdefault("XDG_CACHE_HOME", str(XDG_CACHE_DIR))

    df = pd.read_csv(RESULT_PATH)
    theme = Theme.default()
    theme.fonts["family"] = "Arial"

    request = ChartRequest(
        data=df,
        chart_type="hexbin",
        theme=theme,
        title="How does median age cluster against rent burden across all US metros?",
        subtitle="All CBSAs | 2023 cross-section | Hexbin density view of aging and affordability pressure",
        number_format=NumberFormat(unit="count", decimals=1),
        field_values={"method": "hex", "bins": 30},
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
