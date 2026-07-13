from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, DimensionOverride, NumberFormat, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q004")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"
ALT_CHART_PATH = OUTPUT_DIR / "chart_alt.png"


SERIES_LABELS = {
    "New York-Newark-Jersey City, NY-NJ": "New York",
    "Los Angeles-Long Beach-Anaheim, CA": "Los Angeles",
    "Chicago-Naperville-Elgin, IL-IN": "Chicago",
    "Dallas-Fort Worth-Arlington, TX": "Dallas-Fort Worth",
    "Houston-Pasadena-The Woodlands, TX": "Houston",
    "Washington-Arlington-Alexandria, DC-VA-MD-WV": "Washington, DC",
    "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD": "Philadelphia",
    "Atlanta-Sandy Springs-Roswell, GA": "Atlanta",
    "Miami-Fort Lauderdale-West Palm Beach, FL": "Miami",
    "Phoenix-Mesa-Chandler, AZ": "Phoenix",
}


def with_display_labels(df: pd.DataFrame) -> pd.DataFrame:
    # Short metro labels keep the legend readable while preserving the same series set.
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
        title="How has median gross rent changed in the 10 largest metros since 2018?",
        subtitle="Top 10 CBSAs by 2023 population | 2018-2023 annual series",
        number_format=NumberFormat(unit="usd", decimals=0),
        field_values={"y_label": "Median gross rent ($)"},
        dimensions=DimensionOverride(width=1100, height=620),
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )
    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


def render_alt_slope(df: pd.DataFrame, theme: Theme) -> None:
    alt_df = df.loc[df["period"].astype(str).isin(["2018", "2023"])].copy()
    request = ChartRequest(
        data=alt_df,
        chart_type="slopegraph",
        theme=theme,
        title="Alternative view: median gross rent in the 10 largest metros, 2018 vs 2023",
        subtitle="Top 10 CBSAs by 2023 population | Two-point framing",
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
