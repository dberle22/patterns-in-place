from pathlib import Path
import faulthandler
import sys
import warnings

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHART_ENGINE_ROOT = PROJECT_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, NumberFormat, OutputConfig, Theme, render


OUTPUT_DIR = Path("publisher/chart_a_day/output/q017")
RESULT_PATH = OUTPUT_DIR / "result.csv"
CHART_PATH = OUTPUT_DIR / "chart_py.png"


SHORT_NAMES = {
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
    "Boston-Cambridge-Newton, MA-NH": "Boston",
    "San Francisco-Oakland-Fremont, CA": "San Francisco",
    "Riverside-San Bernardino-Ontario, CA": "Riverside",
    "Detroit-Warren-Dearborn, MI": "Detroit",
    "Seattle-Tacoma-Bellevue, WA": "Seattle",
}


def with_display_labels(df: pd.DataFrame) -> pd.DataFrame:
    labeled = df.copy()
    labeled["geo_name"] = labeled["geo_name"].map(lambda value: SHORT_NAMES.get(value, value))
    return labeled


def main() -> None:
    faulthandler.enable()
    warnings.filterwarnings(
        "ignore",
        message="the convert_dtype parameter is deprecated.*",
        category=FutureWarning,
    )

    df = with_display_labels(pd.read_csv(RESULT_PATH))
    theme = Theme.default()
    theme.fonts["family"] = "Arial"
    print("rendering q017 slopegraph...")

    request = ChartRequest(
        data=df,
        chart_type="slopegraph",
        theme=theme,
        title="How did the rent-to-income ratio change between 2018 and 2023 in the 15 largest metros?",
        subtitle="Top 15 CBSAs by 2023 population | Rare affordability improvements are highlighted",
        number_format=NumberFormat(unit="count", decimals=1),
        field_values={"label_mode": "highlight_end", "show_delta_labels": True, "label_max_chars": 24},
        output=OutputConfig(save=True, path=CHART_PATH, format="png"),
    )

    result = render(request)
    if result.warnings:
        for warning in result.warnings:
            print(f"warning: {warning}")
    print(f"saved {result.output_path}")


if __name__ == "__main__":
    main()
