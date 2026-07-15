from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, DimensionOverride, NumberFormat, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q005")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"
ALT_CHART_PATH = OUTPUT_DIR / "chart_alt.png"


SERIES_LABELS = {
    "Austin-Round Rock-San Marcos, TX": "Austin",
    "Dallas-Fort Worth-Arlington, TX": "Dallas-Fort Worth",
    "Houston-Pasadena-The Woodlands, TX": "Houston",
    "Phoenix-Mesa-Chandler, AZ": "Phoenix",
    "Atlanta-Sandy Springs-Roswell, GA": "Atlanta",
    "Tampa-St. Petersburg-Clearwater, FL": "Tampa",
    "Orlando-Kissimmee-Sanford, FL": "Orlando",
    "Nashville-Davidson--Murfreesboro--Franklin, TN": "Nashville",
}


def with_display_labels(df: pd.DataFrame) -> pd.DataFrame:
    # Short metro labels keep the social-sized legend readable for multi-series trends.
    labeled = df.copy()
    labeled["series"] = labeled["series"].map(lambda value: SERIES_LABELS.get(value, value))
    if "geo_name" in labeled.columns:
        labeled["geo_name"] = labeled["geo_name"].map(lambda value: SERIES_LABELS.get(value, value))
    return labeled


def render_line(df: pd.DataFrame, theme: Theme) -> None:
    request = ChartRequest(
        data=df,
        chart_type="line_chart",
        theme=theme,
        column_mapping={
            "period": "period",
            "metric_value": "value",
            "series": "series",
        },
        title="How has median household income trended in Sun Belt metros since 2015?",
        subtitle="Austin, Dallas, Houston, Phoenix, Atlanta, Tampa, Orlando, and Nashville | 2015-2023 annual series",
        number_format=NumberFormat(unit="usd", decimals=0),
        field_values={"y_label": "Median household income ($)"},
        dimensions=DimensionOverride(width=1100, height=620),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )
    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


def render_alt_slope(df: pd.DataFrame, theme: Theme) -> None:
    alt_df = df.loc[df["period"].astype(str).isin(["2015", "2023"])].copy()
    request = ChartRequest(
        data=alt_df,
        chart_type="slopegraph",
        theme=theme,
        title="Alternative view: median household income in selected Sun Belt metros, 2015 vs 2023",
        subtitle="Two-point framing across eight selected Sun Belt metros",
        number_format=NumberFormat(unit="usd", decimals=0),
        output=OutputConfig(save=True, path=ALT_CHART_PATH, format="png"),
    )
    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


def main() -> None:
    df = pd.read_csv(RESULT_PATH)
    theme = Theme.default()
    theme.fonts["family"] = "Arial"
    labeled_df = with_display_labels(df)
    render_line(labeled_df, theme)
    render_alt_slope(labeled_df, theme)


if __name__ == "__main__":
    main()
