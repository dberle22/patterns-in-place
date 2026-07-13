from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, DimensionOverride, NumberFormat, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q026")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"
MPL_CACHE_DIR = Path("/tmp/mpl_cache_q026")
XDG_CACHE_DIR = Path("/tmp/xdg_cache_q026")


def main() -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    XDG_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
    os.environ.setdefault("XDG_CACHE_HOME", str(XDG_CACHE_DIR))

    df = pd.read_csv(RESULT_PATH)
    df["geometry"] = df["geometry_json"].apply(json.loads)

    theme = Theme.default()
    theme.fonts["family"] = "Arial"

    request = ChartRequest(
        data=df,
        chart_type="proportional_symbol_map",
        theme=theme,
        column_mapping={"geometry": "geometry"},
        title="Where is population growth concentrated across US metros?",
        subtitle="CBSAs with population above 100k | Bubble size = 2018-2023 growth rate | Color = Census region",
        number_format=NumberFormat(unit="percent", decimals=1),
        field_values={"color_mode": "color_group", "label_include_value": False},
        dimensions=DimensionOverride(width=980, height=720),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )

    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


if __name__ == "__main__":
    main()
