"""Shared data prep and cached-overlay helpers for Metro Area Explorer Industry.

This module keeps acquisition separate from app prep. D1-D3 still read
governed Gold/Silver tables directly, while D4 reads cached market
extracts written by the dedicated `ingest_spatial.py` script.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
import math
from pathlib import Path
import sys
from typing import Iterable
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import duckdb
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
CHART_ENGINE_ROOT = REPO_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from chart_engine import ChartRequest, NumberFormat, Theme, render


DB_PATH = REPO_ROOT / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
SQL_ROOT = Path(__file__).resolve().parent / "sql"
DEFAULT_MARKET_ID = "40060"
MIN_REQUIRED_SECTORS = 8
MIN_BUMP_YEARS = 3
D5_DEFAULT_PEER_COUNT = 5
D1_SPECIALIZATION_TOP_SECTORS = 12
D6_SECTOR_TARGET_YEAR = 2024
D6_OCCUPATION_TARGET_YEAR = 2025
FELTEN_REFERENCE_ROOT = Path(__file__).resolve().parent / "reference_data"
FELTEN_WORKBOOK_PATH = FELTEN_REFERENCE_ROOT / "AIOE_DataAppendix.xlsx"
FELTEN_WORKBOOK_URL = "https://github.com/AIOE-Data/AIOE/blob/main/AIOE_DataAppendix.xlsx"
FELTEN_COVERAGE_REVIEW_ROOT = Path(__file__).resolve().parent / "outputs" / "national" / "d6_coverage_review"
FELTEN_NAICS_FINAL_CROSSWALK_PATH = FELTEN_COVERAGE_REVIEW_ROOT / "felten_naics_crosswalk_final.csv"
FELTEN_SOC_FINAL_CROSSWALK_PATH = FELTEN_COVERAGE_REVIEW_ROOT / "felten_soc_crosswalk_final.csv"

EMPLOYMENT_SECTORS = [
    ("ag_mining", "Agriculture & Mining"),
    ("construction", "Construction"),
    ("manufacturing", "Manufacturing"),
    ("wholesale", "Wholesale"),
    ("retail", "Retail"),
    ("transport_util", "Transport & Utilities"),
    ("information", "Information"),
    ("finance_real", "Finance & Real Estate"),
    ("professional", "Professional Services"),
    ("educ_health", "Education & Health"),
    ("arts_accomm_food", "Arts, Accommodation & Food"),
    ("other_services", "Other Services"),
]

GDP_SECTORS = [
    ("natural_resources", "Natural Resources"),
    ("manufacturing", "Manufacturing"),
    ("construction", "Construction"),
    ("trade", "Trade"),
    ("transportation", "Transportation"),
    ("information", "Information"),
    ("fire", "Finance, Insurance & Real Estate"),
    ("professional", "Professional Services"),
    ("edu_health", "Education & Health"),
    ("leisure", "Leisure"),
    ("gov", "Government"),
]

OCCUPATION_BUCKET_LABELS = {
    "management_professional": "Management & professional",
    "service": "Service",
    "production_transportation": "Production & transportation",
    "other": "Other",
    "stem": "STEM overlay",
}


@dataclass(frozen=True)
class BasisMetadata:
    """Static metadata that keeps UI copy and chart copy consistent."""

    basis: str
    label: str
    chart_metric_id: str
    chart_metric_label: str
    source_label: str
    raw_prefix: str
    share_prefix: str
    sectors: list[tuple[str, str]]


BASIS_CONFIG = {
    "employment_share": BasisMetadata(
        basis="employment_share",
        label="Private employment share",
        chart_metric_id="industry_private_employment_share",
        chart_metric_label="Private employment share",
        source_label="QCEW private employment share",
        raw_prefix="qcew_private_emp_",
        share_prefix="pct_qcew_private_emp_",
        sectors=EMPLOYMENT_SECTORS,
    ),
    "employment_share_fallback": BasisMetadata(
        basis="employment_share",
        label="Private employment share",
        chart_metric_id="industry_private_employment_share",
        chart_metric_label="Private employment share",
        source_label="ACS employment share fallback",
        raw_prefix="acs_ind_",
        share_prefix="pct_acs_ind_",
        sectors=EMPLOYMENT_SECTORS,
    ),
    "gdp_share": BasisMetadata(
        basis="gdp_share",
        label="Real GDP share",
        chart_metric_id="industry_real_gdp_share",
        chart_metric_label="Real GDP share",
        source_label="BEA real GDP share",
        raw_prefix="real_gdp_",
        share_prefix="pct_real_gdp_",
        sectors=GDP_SECTORS,
    ),
}

DIVISION_ID_TO_NAME = {
    "1": "New England",
    "2": "Middle Atlantic",
    "3": "East North Central",
    "4": "West North Central",
    "5": "South Atlantic",
    "6": "East South Central",
    "7": "West South Central",
    "8": "Mountain",
    "9": "Pacific",
}

D2_SECTOR_COLOR_HEX = {
    "ag_mining": "#6A994E",
    "construction": "#D08C60",
    "manufacturing": "#355070",
    "wholesale": "#6D597A",
    "retail": "#E56B6F",
    "transport_util": "#4D908E",
    "information": "#577590",
    "finance_real": "#B56576",
    "professional": "#3A86FF",
    "educ_health": "#2A9D8F",
    "arts_accomm_food": "#F4A261",
    "other_services": "#8D99AE",
}

# LODES uses a finer workplace-industry split than D1. We collapse those raw
# tract columns into the same broad D1 families so the map speaks the same
# language as the current-mix and change views.
TRACT_SECTOR_COMPONENTS = {
    "ag_mining": [
        "jobs_ind_ag_forest_fish_hunt",
        "jobs_ind_mining_quarry_oil_gas",
    ],
    "construction": ["jobs_ind_construction"],
    "manufacturing": ["jobs_ind_manufacturing"],
    "wholesale": ["jobs_ind_wholesale"],
    "retail": ["jobs_ind_retail"],
    "transport_util": [
        "jobs_ind_transport_warehouse",
        "jobs_ind_utilities",
    ],
    "information": ["jobs_ind_information"],
    "finance_real": [
        "jobs_ind_finance_insurance",
        "jobs_ind_real_estate",
    ],
    "professional": [
        "jobs_ind_professional_scientific_technical",
        "jobs_ind_management_companies",
        "jobs_ind_admin_support_waste",
    ],
    "educ_health": [
        "jobs_ind_educational_services",
        "jobs_ind_health_care_social_assistance",
    ],
    "arts_accomm_food": [
        "jobs_ind_arts_entertainment_recreation",
        "jobs_ind_accommodation_food",
    ],
    # Public administration does not have its own D1 bucket, so we keep it with
    # the residual services family rather than dropping those jobs from the map.
    "other_services": [
        "jobs_ind_other_services",
        "jobs_ind_public_administration",
    ],
}

COUNTY_GDP_SECTOR_COLUMNS = {
    "ag_mining": "pct_real_gdp_natural_resources",
    "construction": "pct_real_gdp_construction",
    "manufacturing": "pct_real_gdp_manufacturing",
    "wholesale": "pct_real_gdp_trade",
    "retail": "pct_real_gdp_trade",
    "transport_util": "pct_real_gdp_transportation",
    "information": "pct_real_gdp_information",
    "finance_real": "pct_real_gdp_fire",
    "professional": "pct_real_gdp_professional",
    "educ_health": "pct_real_gdp_edu_health",
    "arts_accomm_food": "pct_real_gdp_leisure",
    "other_services": "pct_calc_real_gdp_other",
}

LODES_INDUSTRY_LABELS = [
    ("ag_forest_fish_hunt", "Agriculture, Forestry, Fishing & Hunting"),
    ("mining_quarry_oil_gas", "Mining, Quarrying, Oil & Gas"),
    ("utilities", "Utilities"),
    ("construction", "Construction"),
    ("manufacturing", "Manufacturing"),
    ("wholesale", "Wholesale"),
    ("retail", "Retail"),
    ("transport_warehouse", "Transportation & Warehousing"),
    ("information", "Information"),
    ("finance_insurance", "Finance & Insurance"),
    ("real_estate", "Real Estate"),
    ("professional_scientific_technical", "Professional, Scientific & Technical"),
    ("management_companies", "Management of Companies"),
    ("admin_support_waste", "Admin, Support & Waste"),
    ("educational_services", "Educational Services"),
    ("health_care_social_assistance", "Health Care & Social Assistance"),
    ("arts_entertainment_recreation", "Arts, Entertainment & Recreation"),
    ("accommodation_food", "Accommodation & Food"),
    ("other_services", "Other Services"),
    ("public_administration", "Public Administration"),
]

D3_DEFAULT_TRACT_JOBS_FLOOR = 2500
D3_DEFAULT_TOP_TRACTS = 15
D3_MAP_MODE_LABELS = {
    "top_jobs": "Largest job centers",
    "top_ratio": "Highest jobs-to-workers",
    "top_selected_sector": "Selected sector centers",
}
D4_DEFAULT_SELECTED_SECTOR = "professional"
D4_DEFAULT_TOP_POP_TRACTS = 12
D4_DEFAULT_TOP_JOB_CENTER_TRACTS = 12
D4_DEFAULT_SHORTLIST_COUNT = 8
D4_DEFAULT_BUFFER_MILES = 2.0
D4_DEFAULT_BASE_SURFACE = "jobs_total"
SPATIAL_OUTPUTS_ROOT = Path(__file__).resolve().parent / "outputs"
SPATIAL_OUTPUT_DIR_ALIASES = {
    "40060": "richmond_va",
}

COMMON_SPATIAL_COLUMNS = [
    "market_id",
    "source_system",
    "source_id",
    "feature_name",
    "layer_group",
    "category",
    "subcategory",
    "geometry_type",
    "geometry",
    "centroid_lat",
    "centroid_lon",
    "attributes_json",
    "extract_date",
]

D4_LAYER_STYLES = {
    "osm_lines": {"label": "OSM infrastructure lines", "color": [31, 78, 121, 180]},
    "osm_polygons": {"label": "OSM infrastructure polygons", "color": [65, 105, 185, 90]},
    "osm_points": {"label": "OSM infrastructure points", "color": [22, 101, 52, 170]},
    "overture_pois": {"label": "Overture POIs", "color": [191, 84, 0, 190]},
    "population_markers": {"label": "Population centers", "color": [167, 85, 31, 180]},
    "job_center_markers": {"label": "Job centers", "color": [111, 29, 27, 210]},
}

D4_INTERPRETATION_LABELS = {
    "highways": "Highways",
    "rail": "Rail",
    "airports": "Airports",
    "ports": "Ports",
    "warehouses_logistics": "Warehouses / logistics",
    "hospitals": "Hospitals",
    "universities": "Universities",
    "schools": "Schools",
    "groceries": "Groceries",
}

D2_TOOLTIP_FIELDS = [
    "sector_label",
    "dominant_sector_label",
    "selected_share_pct",
    "selected_jobs",
    "jobs_total",
    "selected_gdp_share_pct",
]

TRACT_GEOMETRY_SIMPLIFY_TOLERANCE = 0.001
COUNTY_GEOMETRY_SIMPLIFY_TOLERANCE = 0.001


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open the standard repo DuckDB in read-only mode."""
    return duckdb.connect(str(DB_PATH), read_only=True)


@lru_cache(maxsize=None)
def _read_sql_file(filename: str) -> str:
    """Read one section-owned SQL asset and cache it for repeated app use."""
    return (SQL_ROOT / filename).read_text(encoding="utf-8")


def _latest_year_note(rows: pd.DataFrame, share_prefix: str, basis_label: str) -> str:
    if rows.empty:
        return f"{basis_label} history unavailable."
    mask = rows[[column for column in rows.columns if column.startswith(share_prefix)]].notna().any(axis=1)
    usable = rows.loc[mask, "year"]
    if usable.empty:
        return f"{basis_label} history unavailable."
    return f"{basis_label} through {int(usable.max())}."


def get_cbsa_options() -> pd.DataFrame:
    """Return CBSA choices that have at least one industry mart row."""
    con = get_connection()
    try:
        return con.execute(
            """
            SELECT
                geo_id AS market_id,
                geo_name
            FROM patterns_in_place.gold.economics_industry_wide
            WHERE geo_level = 'cbsa'
            GROUP BY 1, 2
            ORDER BY geo_name
            """
        ).fetchdf()
    finally:
        con.close()


def get_market_surface(market_id: str) -> pd.DataFrame:
    """Pull the full CBSA-year panel from the Gold industry mart."""
    con = get_connection()
    try:
        return con.execute(
            """
            SELECT *
            FROM patterns_in_place.gold.economics_industry_wide
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
            ORDER BY year
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()


def get_market_surfaces(market_ids: Iterable[str]) -> pd.DataFrame:
    """Pull the full CBSA-year panel for multiple markets in one pass."""
    market_id_list = [str(market_id) for market_id in market_ids if str(market_id)]
    if not market_id_list:
        return pd.DataFrame()

    placeholders = ", ".join(["?"] * len(market_id_list))
    con = get_connection()
    try:
        return con.execute(
            f"""
            SELECT *
            FROM patterns_in_place.gold.economics_industry_wide
            WHERE geo_level = 'cbsa'
              AND geo_id IN ({placeholders})
            ORDER BY geo_id, year
            """,
            market_id_list,
        ).fetchdf()
    finally:
        con.close()


def get_market_context(market_id: str) -> dict[str, str | None]:
    """Return the market's division and region context from the Gold geography dimension."""
    con = get_connection()
    try:
        row = con.execute(
            """
            SELECT
                geo_id AS market_id,
                geo_name,
                division_id,
                division_name,
                region_name
            FROM patterns_in_place.gold.dim_geo
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()

    if row.empty:
        return {
            "market_id": str(market_id),
            "geo_name": None,
            "division_id": None,
            "division_name": None,
            "region_name": None,
        }
    return row.iloc[0].to_dict()


def _load_xlsx_shared_strings(zip_file: ZipFile) -> list[str]:
    """Read workbook shared strings so we can parse the Felten workbook without extra deps."""
    if "xl/sharedStrings.xml" not in zip_file.namelist():
        return []

    root = ET.fromstring(zip_file.read("xl/sharedStrings.xml"))
    namespace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    out: list[str] = []
    for item in root.findall(f"{namespace}si"):
        out.append("".join(node.text or "" for node in item.iter(f"{namespace}t")))
    return out


def _read_felten_sheet(sheet_name: str) -> pd.DataFrame:
    """Parse one Felten appendix tab from the section-owned Excel workbook.

    We read the XML directly because the local app/test environment does not
    guarantee `openpyxl`, and D6 only needs a small, stable subset of sheets.
    """
    if not FELTEN_WORKBOOK_PATH.exists():
        return pd.DataFrame()

    namespace = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rel_namespace = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    with ZipFile(FELTEN_WORKBOOK_PATH) as workbook_zip:
        workbook_root = ET.fromstring(workbook_zip.read("xl/workbook.xml"))
        rels_root = ET.fromstring(workbook_zip.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels_root}
        sheet_lookup = {
            sheet.attrib["name"]: sheet.attrib[f"{rel_namespace}id"]
            for sheet in workbook_root.find("a:sheets", namespace)
        }
        target = sheet_lookup.get(sheet_name)
        if target is None:
            return pd.DataFrame()

        shared_strings = _load_xlsx_shared_strings(workbook_zip)
        sheet_xml = ET.fromstring(workbook_zip.read(f"xl/{rel_map[target]}"))
        cell_namespace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        rows: list[list[str]] = []
        for row in sheet_xml.iter(f"{cell_namespace}row"):
            values: list[str] = []
            for cell in row.iter(f"{cell_namespace}c"):
                value_node = cell.find(f"{cell_namespace}v")
                if value_node is None:
                    values.append("")
                    continue
                if cell.attrib.get("t") == "s":
                    values.append(shared_strings[int(value_node.text)])
                else:
                    values.append(value_node.text or "")
            rows.append(values)

    if not rows:
        return pd.DataFrame()

    header = [str(value).strip() for value in rows[0]]
    body = rows[1:]
    return pd.DataFrame(body, columns=header)


@lru_cache(maxsize=None)
def get_felten_appendix_a() -> pd.DataFrame:
    """Return Appendix A occupation exposure rows with canonical SOC columns."""
    rows = _read_felten_sheet("Appendix A")
    if rows.empty:
        return pd.DataFrame(columns=["soc_code", "soc_title_felten", "aioe_score"])

    rows = rows.rename(
        columns={
            "SOC Code": "soc_code",
            "Occupation Title": "soc_title_felten",
            "AIOE": "aioe_score",
        }
    ).copy()
    rows["soc_code"] = rows["soc_code"].astype(str).str.strip()
    rows["soc_title_felten"] = rows["soc_title_felten"].astype(str).str.strip()
    rows["aioe_score"] = pd.to_numeric(rows["aioe_score"], errors="coerce")
    return rows.dropna(subset=["soc_code"]).reset_index(drop=True)


@lru_cache(maxsize=None)
def get_felten_appendix_b() -> pd.DataFrame:
    """Return Appendix B industry exposure rows with canonical 4-digit NAICS columns."""
    rows = _read_felten_sheet("Appendix B")
    if rows.empty:
        return pd.DataFrame(columns=["industry_code", "industry_title_felten", "aiie_score"])

    rows = rows.rename(
        columns={
            "NAICS": "industry_code",
            "Industry Title": "industry_title_felten",
            "AIIE": "aiie_score",
        }
    ).copy()
    rows["industry_code"] = rows["industry_code"].astype(str).str.strip()
    rows["industry_title_felten"] = rows["industry_title_felten"].astype(str).str.strip()
    rows["aiie_score"] = pd.to_numeric(rows["aiie_score"], errors="coerce")
    rows = rows[rows["industry_code"].str.fullmatch(r"\d{4}", na=False)].reset_index(drop=True)
    rows = (
        rows.groupby("industry_code", as_index=False)
        .agg(
            industry_title_felten=(
                "industry_title_felten",
                lambda values: " / ".join(pd.Series(values).dropna().astype(str).unique().tolist()),
            ),
            aiie_score=("aiie_score", "mean"),
        )
    )
    return rows


@lru_cache(maxsize=None)
def get_felten_naics_crosswalk_final() -> pd.DataFrame:
    """Return the final app-facing NAICS crosswalk built from audit outputs."""
    if not FELTEN_NAICS_FINAL_CROSSWALK_PATH.exists():
        return pd.DataFrame(
            columns=[
                "our_naics_code",
                "our_name",
                "felten_naics_code",
                "felten_naics_name",
                "felten_score",
                "match_basis",
                "manual_notes",
                "review_source",
            ]
        )

    rows = pd.read_csv(FELTEN_NAICS_FINAL_CROSSWALK_PATH, dtype=str).copy()
    if rows.empty:
        return rows
    rows["our_naics_code"] = rows["our_naics_code"].astype(str).str.strip()
    rows["felten_naics_code"] = rows["felten_naics_code"].astype(str).str.strip()
    rows["felten_score"] = pd.to_numeric(rows["felten_score"], errors="coerce")
    return rows


@lru_cache(maxsize=None)
def get_felten_soc_crosswalk_final() -> pd.DataFrame:
    """Return the final app-facing SOC crosswalk built from audit outputs."""
    if not FELTEN_SOC_FINAL_CROSSWALK_PATH.exists():
        return pd.DataFrame(
            columns=[
                "our_soc_code",
                "our_name",
                "felten_soc_code",
                "felten_soc_name",
                "felten_score",
                "match_basis",
                "manual_notes",
                "review_source",
            ]
        )

    rows = pd.read_csv(FELTEN_SOC_FINAL_CROSSWALK_PATH, dtype=str).copy()
    if rows.empty:
        return rows
    rows["our_soc_code"] = rows["our_soc_code"].astype(str).str.strip()
    rows["felten_soc_code"] = rows["felten_soc_code"].astype(str).str.strip()
    rows["felten_score"] = pd.to_numeric(rows["felten_score"], errors="coerce")
    return rows


def _get_felten_industry_join_code(industry_code: str | None) -> str | None:
    """Map live QCEW 4-digit rows onto Felten Appendix B's older/aggregate code scheme.

    Felten's appendix is a published static snapshot built on an older NAICS
    vintage, so some current QCEW industry groups only line up after a small,
    explicit back-map to the older or aggregate code family.
    """
    if industry_code is None:
        return None

    code = str(industry_code).strip()
    fallback_map = {
        "4451": "4450",
        "4452": "4450",
        "4492": "4431",
        "4551": "4520",
        "4552": "4520",
        "4561": "4461",
        "4571": "4471",
        "4581": "4481",
        "4591": "4511",
        "4599": "4539",
        "5132": "5112",
    }
    if code in fallback_map:
        return fallback_map[code]
    if code.startswith("423") and code not in {"4231", "4234", "4238"}:
        return "4230"
    if code.startswith("424") and code not in {"4243", "4245", "4251"}:
        return "4240"
    if code.startswith("484"):
        return "4840"
    if code.startswith("517"):
        return "5170"
    if code in {"5221", "5223"}:
        return "5220"
    if code.startswith("523"):
        return "5230"
    if code.startswith("531"):
        return "5310"
    if code in {"3321", "3322", "3323", "3324", "3325", "3326", "3329"}:
        return "3320"
    if code in {"3331", "3332", "3334", "3339"}:
        return "3330"
    return code


def _map_naics4_to_d1_sector(industry_code: str | None) -> str | None:
    """Collapse 4-digit NAICS rows back into the broad D1 employment taxonomy."""
    if industry_code is None:
        return None
    code = str(industry_code).strip()
    if len(code) < 2 or not code[:2].isdigit():
        return None

    prefix2 = code[:2]
    if prefix2 in {"11", "21"}:
        return "ag_mining"
    if prefix2 == "22" or prefix2 in {"48", "49"}:
        return "transport_util"
    if prefix2 == "23":
        return "construction"
    if prefix2 in {"31", "32", "33"}:
        return "manufacturing"
    if prefix2 == "42":
        return "wholesale"
    if prefix2 in {"44", "45"}:
        return "retail"
    if prefix2 == "51":
        return "information"
    if prefix2 in {"52", "53"}:
        return "finance_real"
    if prefix2 in {"54", "55", "56"}:
        return "professional"
    if prefix2 in {"61", "62"}:
        return "educ_health"
    if prefix2 in {"71", "72"}:
        return "arts_accomm_food"
    if prefix2 in {"81", "92"}:
        return "other_services"
    return None


def _sector_label_lookup() -> dict[str, str]:
    """Return a stable label lookup for the broad D1 sector family."""
    return {sector_id: sector_label for sector_id, sector_label in EMPLOYMENT_SECTORS}


def _load_spatial(con: duckdb.DuckDBPyConnection) -> None:
    """Load DuckDB spatial helpers for geometry export if available."""
    con.execute("LOAD spatial;")


def get_d2_sector_options() -> list[tuple[str, str]]:
    """Return the harmonized D1 sector options used by the D2 maps."""
    return EMPLOYMENT_SECTORS.copy()


def _geometry_sql(column: str, tolerance: float) -> str:
    """Return a simplified GeoJSON export expression for DuckDB spatial."""
    return (
        "ST_AsGeoJSON("
        f"ST_SimplifyPreserveTopology({column}, {tolerance})"
        ")"
    )


def _hex_to_rgba(hex_color: str, alpha: int = 190) -> list[int]:
    """Convert a hex color to the RGBA lists that PyDeck expects."""
    hex_color = hex_color.lstrip("#")
    return [int(hex_color[i : i + 2], 16) for i in (0, 2, 4)] + [alpha]


def _interpolate_rgba(start_hex: str, end_hex: str, t: float, alpha: int = 190) -> list[int]:
    """Blend between two hex colors for sequential choropleth fills."""
    start = _hex_to_rgba(start_hex, alpha)
    end = _hex_to_rgba(end_hex, alpha)
    clamped = max(0.0, min(1.0, float(t)))
    return [
        int(start[channel] + clamped * (end[channel] - start[channel]))
        for channel in range(4)
    ]


def _iter_geometry_points(geometry: dict | list | None):
    """Yield lon/lat points from GeoJSON-like polygon coordinates."""
    if geometry is None:
        return
    if isinstance(geometry, dict):
        yield from _iter_geometry_points(geometry.get("coordinates"))
        return
    if isinstance(geometry, list):
        if geometry and isinstance(geometry[0], (int, float)) and len(geometry) >= 2:
            yield float(geometry[0]), float(geometry[1])
            return
        for value in geometry:
            yield from _iter_geometry_points(value)


def _build_view_state(features: list[dict]) -> dict[str, float]:
    """Estimate a reasonable market-centered view state from polygon features."""
    lons: list[float] = []
    lats: list[float] = []
    for feature in features:
        for lon, lat in _iter_geometry_points(feature.get("geometry")):
            lons.append(lon)
            lats.append(lat)

    if not lons or not lats:
        return {"longitude": -77.436, "latitude": 37.540, "zoom": 8.0}

    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    span = max(max_lon - min_lon, max_lat - min_lat)
    if span > 4:
        zoom = 6.0
    elif span > 2:
        zoom = 7.0
    elif span > 1:
        zoom = 8.0
    elif span > 0.5:
        zoom = 9.0
    else:
        zoom = 10.0

    return {
        "longitude": (min_lon + max_lon) / 2,
        "latitude": (min_lat + max_lat) / 2,
        "zoom": zoom,
    }


def _safe_pct(value: float | int | None) -> str:
    """Format ratio-like values for hover copy."""
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):.1%}"


def _safe_count(value: float | int | None) -> str:
    """Format count-like values for hover copy."""
    if value is None or pd.isna(value):
        return "—"
    return f"{int(round(float(value))):,}"


def _safe_miles(value: float | int | None) -> str:
    """Format straight-line distance values for D4 interpretation copy."""
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):.1f} mi"


def _haversine_miles(
    lat1: float | int | None,
    lon1: float | int | None,
    lat2: float | int | None,
    lon2: float | int | None,
) -> float | None:
    """Return great-circle distance in miles between two points."""
    if any(pd.isna(value) for value in [lat1, lon1, lat2, lon2]):
        return None

    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 3958.8 * c


def _build_tract_map_rows(market_id: str = DEFAULT_MARKET_ID) -> pd.DataFrame:
    """Query latest tract-level LODES rows and collapse them to the D1 sector families."""
    con = get_connection()
    try:
        _load_spatial(con)
        geometry_sql = _geometry_sql("g.geom", TRACT_GEOMETRY_SIMPLIFY_TOLERANCE)
        rows = con.execute(
            f"""
            WITH market_counties AS (
                SELECT DISTINCT county_geoid
                FROM patterns_in_place.silver.xwalk_cbsa_county
                WHERE cbsa_code = ?
            ),
            latest_year AS (
                SELECT MAX(year) AS year
                FROM patterns_in_place.silver.lehd_lodes_wac
                WHERE geo_level = 'tract'
            ),
            latest_population_year AS (
                SELECT MAX(year) AS year
                FROM patterns_in_place.gold.population_demographics
                WHERE geo_level = 'tract'
            ),
            latest_rac_year AS (
                SELECT MAX(year) AS year
                FROM patterns_in_place.silver.lehd_lodes_rac
                WHERE geo_level = 'tract'
            )
            SELECT
                w.geo_id AS tract_geoid,
                w.geo_name AS tract_name,
                w.year,
                w.jobs_total,
                r.workers_total,
                p.pop_total,
                g.land_area_sqmi,
                ST_X(ST_Centroid(g.geom)) AS centroid_lon,
                ST_Y(ST_Centroid(g.geom)) AS centroid_lat,
                w.jobs_ind_ag_forest_fish_hunt,
                w.jobs_ind_mining_quarry_oil_gas,
                w.jobs_ind_utilities,
                w.jobs_ind_construction,
                w.jobs_ind_manufacturing,
                w.jobs_ind_wholesale,
                w.jobs_ind_retail,
                w.jobs_ind_transport_warehouse,
                w.jobs_ind_information,
                w.jobs_ind_finance_insurance,
                w.jobs_ind_real_estate,
                w.jobs_ind_professional_scientific_technical,
                w.jobs_ind_management_companies,
                w.jobs_ind_admin_support_waste,
                w.jobs_ind_educational_services,
                w.jobs_ind_health_care_social_assistance,
                w.jobs_ind_arts_entertainment_recreation,
                w.jobs_ind_accommodation_food,
                w.jobs_ind_other_services,
                w.jobs_ind_public_administration,
                g.county_geoid,
                {geometry_sql} AS geometry_json
            FROM patterns_in_place.silver.lehd_lodes_wac w
            INNER JOIN patterns_in_place.geo.tracts_all_us g
                ON w.geo_id = g.tract_geoid
            INNER JOIN market_counties c
                ON g.county_geoid = c.county_geoid
            LEFT JOIN patterns_in_place.gold.population_demographics p
                ON w.geo_id = p.geo_id
               AND p.geo_level = 'tract'
               AND p.year = (SELECT year FROM latest_population_year)
            LEFT JOIN patterns_in_place.silver.lehd_lodes_rac r
                ON w.geo_id = r.geo_id
               AND r.geo_level = 'tract'
               AND r.year = (SELECT year FROM latest_rac_year)
            WHERE w.geo_level = 'tract'
              AND w.year = (SELECT year FROM latest_year)
            ORDER BY w.geo_id
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()

    if rows.empty:
        return rows

    for sector_id, components in TRACT_SECTOR_COMPONENTS.items():
        rows[f"d2_jobs_{sector_id}"] = rows[components].sum(axis=1, min_count=1)
        denominator = rows["jobs_total"].where(rows["jobs_total"].notna() & (rows["jobs_total"] != 0))
        rows[f"d2_share_{sector_id}"] = rows[f"d2_jobs_{sector_id}"] / denominator

    sector_ids = [sector_id for sector_id, _ in EMPLOYMENT_SECTORS]
    job_columns = [f"d2_jobs_{sector_id}" for sector_id in sector_ids]
    sector_lookup = dict(EMPLOYMENT_SECTORS)
    rows["dominant_sector_id"] = (
        rows[job_columns]
        .idxmax(axis=1)
        .str.removeprefix("d2_jobs_")
    )
    rows["dominant_sector_label"] = rows["dominant_sector_id"].map(sector_lookup)
    rows["dominant_sector_jobs"] = rows.apply(
        lambda row: row.get(f"d2_jobs_{row['dominant_sector_id']}"),
        axis=1,
    )
    rows["dominant_sector_share"] = rows.apply(
        lambda row: row.get(f"d2_share_{row['dominant_sector_id']}"),
        axis=1,
    )
    jobs_total_denominator = rows["jobs_total"].where(rows["jobs_total"].notna() & (rows["jobs_total"] != 0))
    workers_total_denominator = rows["workers_total"].where(
        rows["workers_total"].notna() & (rows["workers_total"] != 0)
    )
    pop_denominator = rows["pop_total"].where(rows["pop_total"].notna() & (rows["pop_total"] != 0))
    area_denominator = rows["land_area_sqmi"].where(rows["land_area_sqmi"].notna() & (rows["land_area_sqmi"] != 0))
    rows["jobs_to_workers_ratio"] = jobs_total_denominator / workers_total_denominator
    rows["jobs_per_resident"] = jobs_total_denominator / pop_denominator
    rows["jobs_per_sqmi"] = jobs_total_denominator / area_denominator
    rows["geometry"] = rows["geometry_json"].apply(json.loads)
    return rows


def _build_county_gdp_rows(market_id: str = DEFAULT_MARKET_ID) -> pd.DataFrame:
    """Query latest county GDP-share rows with county geometry for the selected market."""
    con = get_connection()
    try:
        _load_spatial(con)
        geometry_sql = _geometry_sql("g.geom", COUNTY_GEOMETRY_SIMPLIFY_TOLERANCE)
        rows = con.execute(
            f"""
            WITH market_counties AS (
                SELECT DISTINCT county_geoid
                FROM patterns_in_place.silver.xwalk_cbsa_county
                WHERE cbsa_code = ?
            ),
            latest_year AS (
                SELECT MAX(year) AS year
                FROM patterns_in_place.gold.economics_industry_wide
                WHERE geo_level = 'county'
                  AND pct_real_gdp_trade IS NOT NULL
            )
            SELECT
                i.geo_id AS county_geoid,
                i.geo_name AS county_name,
                i.year,
                i.real_gdp_total,
                i.pct_real_gdp_natural_resources,
                i.pct_real_gdp_manufacturing,
                i.pct_real_gdp_construction,
                i.pct_real_gdp_trade,
                i.pct_real_gdp_transportation,
                i.pct_real_gdp_information,
                i.pct_real_gdp_fire,
                i.pct_real_gdp_professional,
                i.pct_real_gdp_edu_health,
                i.pct_real_gdp_leisure,
                i.pct_real_gdp_gov,
                i.pct_calc_real_gdp_other,
                {geometry_sql} AS geometry_json
            FROM patterns_in_place.gold.economics_industry_wide i
            INNER JOIN market_counties c
                ON i.geo_id = c.county_geoid
            INNER JOIN patterns_in_place.geo.counties g
                ON i.geo_id = g.county_geoid
            WHERE i.geo_level = 'county'
              AND i.year = (SELECT year FROM latest_year)
            ORDER BY i.geo_id
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()

    if rows.empty:
        return rows

    rows["geometry"] = rows["geometry_json"].apply(json.loads)
    return rows


def get_d2_tract_map_payload(
    market_id: str = DEFAULT_MARKET_ID,
    mode: str = "top_industry",
    selected_sector: str = "professional",
) -> dict[str, object]:
    """Return tract features, legend metadata, and map framing for the D2 tract map."""
    rows = _build_tract_map_rows(market_id)
    if rows.empty:
        return {"features": [], "view_state": _build_view_state([]), "rows": rows}

    sector_lookup = dict(EMPLOYMENT_SECTORS)
    features: list[dict] = []
    legend_rows: list[dict] = []
    if mode == "top_industry":
        seen = set()
        for _, row in rows.iterrows():
            sector_id = row["dominant_sector_id"]
            fill_color = _hex_to_rgba(D2_SECTOR_COLOR_HEX[sector_id], 190)
            if sector_id not in seen:
                seen.add(sector_id)
                legend_rows.append(
                    {
                        "Sector": sector_lookup[sector_id],
                        "Color": D2_SECTOR_COLOR_HEX[sector_id],
                    }
                )
            properties = {
                "tract_geoid": row["tract_geoid"],
                "tract_name": row["tract_name"],
                "jobs_total": _safe_count(row["jobs_total"]),
                "dominant_sector_label": row["dominant_sector_label"],
                "selected_jobs": _safe_count(row["dominant_sector_jobs"]),
                "selected_share_pct": _safe_pct(row["dominant_sector_share"]),
                "fill_color": fill_color,
            }
            features.append(
                {
                    "type": "Feature",
                    "geometry": row["geometry"],
                    "properties": properties,
                }
            )
        map_title = "Dominant industry by tract"
        map_subtitle = f"Latest LODES workplace jobs ({int(rows['year'].iloc[0])}) collapsed to the D1 sector taxonomy"
    else:
        sector_label = sector_lookup[selected_sector]
        share_column = f"d2_share_{selected_sector}"
        jobs_column = f"d2_jobs_{selected_sector}"
        max_share = rows[share_column].max(skipna=True)
        if pd.isna(max_share) or max_share <= 0:
            max_share = 1.0
        for _, row in rows.iterrows():
            share_value = row[share_column]
            ratio = 0.0 if pd.isna(share_value) else float(share_value) / float(max_share)
            fill_color = _interpolate_rgba("#EAF2FF", "#1259C3", ratio, 195)
            properties = {
                "tract_geoid": row["tract_geoid"],
                "tract_name": row["tract_name"],
                "jobs_total": _safe_count(row["jobs_total"]),
                "sector_label": sector_label,
                "selected_jobs": _safe_count(row[jobs_column]),
                "selected_share_pct": _safe_pct(share_value),
                "fill_color": fill_color,
            }
            features.append(
                {
                    "type": "Feature",
                    "geometry": row["geometry"],
                    "properties": properties,
                }
            )
        legend_rows = [
            {"Share level": "Low", "Color": "#EAF2FF"},
            {"Share level": "High", "Color": "#1259C3"},
        ]
        map_title = f"{sector_label} share by tract"
        map_subtitle = f"Share of tract workplace jobs in {sector_label} ({int(rows['year'].iloc[0])})"

    return {
        "features": features,
        "legend": pd.DataFrame(legend_rows),
        "view_state": _build_view_state(features),
        "rows": rows,
        "title": map_title,
        "subtitle": map_subtitle,
        "year": int(rows["year"].iloc[0]),
    }


def get_d2_county_gdp_map_payload(
    market_id: str = DEFAULT_MARKET_ID,
    selected_sector: str = "professional",
) -> dict[str, object]:
    """Return county GeoJSON features for the selected D1 GDP-share comparison view."""
    rows = _build_county_gdp_rows(market_id)
    if rows.empty:
        return {"features": [], "view_state": _build_view_state([]), "rows": rows}

    sector_label = dict(EMPLOYMENT_SECTORS)[selected_sector]
    share_column = COUNTY_GDP_SECTOR_COLUMNS[selected_sector]
    max_share = rows[share_column].max(skipna=True)
    if pd.isna(max_share) or max_share <= 0:
        max_share = 1.0

    features: list[dict] = []
    for _, row in rows.iterrows():
        share_value = row[share_column]
        ratio = 0.0 if pd.isna(share_value) else float(share_value) / float(max_share)
        fill_color = _interpolate_rgba("#FFF1E6", "#BC4B1D", ratio, 190)
        properties = {
            "county_geoid": row["county_geoid"],
            "county_name": row["county_name"],
            "sector_label": sector_label,
            "selected_gdp_share_pct": _safe_pct(share_value),
            "real_gdp_total": _format_raw_value(row["real_gdp_total"], "gdp_share"),
            "fill_color": fill_color,
        }
        features.append(
            {
                "type": "Feature",
                "geometry": row["geometry"],
                "properties": properties,
            }
        )

    return {
        "features": features,
        "legend": pd.DataFrame(
            [
                {"Share level": "Low", "Color": "#FFF1E6"},
                {"Share level": "High", "Color": "#BC4B1D"},
            ]
        ),
        "view_state": _build_view_state(features),
        "rows": rows,
        "title": f"{sector_label} county GDP share",
        "subtitle": f"County share of real GDP in {sector_label} ({int(rows['year'].iloc[0])})",
        "year": int(rows["year"].iloc[0]),
    }


def get_d3_cbsa_summary(market_id: str = DEFAULT_MARKET_ID) -> dict[str, object]:
    """Return the latest CBSA labor-pull summary from the governed Gold LODES mart."""
    con = get_connection()
    try:
        rows = con.execute(
            """
            SELECT
                geo_id AS market_id,
                geo_name,
                year,
                jobs_total,
                workers_total,
                jobs_minus_workers,
                jobs_to_workers_ratio
            FROM patterns_in_place.gold.economics_lodes_wide
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
            ORDER BY year DESC
            LIMIT 1
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()

    if rows.empty:
        return {}

    row = rows.iloc[0].to_dict()
    row["jobs_total_label"] = _safe_count(row.get("jobs_total"))
    row["workers_total_label"] = _safe_count(row.get("workers_total"))
    row["jobs_minus_workers_label"] = _safe_count(row.get("jobs_minus_workers"))
    ratio_value = row.get("jobs_to_workers_ratio")
    row["jobs_to_workers_ratio_label"] = "—" if pd.isna(ratio_value) else f"{float(ratio_value):.2f}x"
    return row


def _build_d3_takeaway(
    summary: dict[str, object],
    tract_rows: pd.DataFrame,
    imbalance_rows: pd.DataFrame,
) -> str | None:
    """Build the short D3 synthesis sentence from the measured tract and industry signals."""
    if not summary or tract_rows.empty or imbalance_rows.empty:
        return None

    top_job_center = tract_rows.sort_values(
        ["jobs_total", "jobs_to_workers_ratio"],
        ascending=[False, False],
        kind="mergesort",
    ).iloc[0]
    positive = imbalance_rows[imbalance_rows["share_gap"] > 0].head(2)["industry_label"].tolist()
    negative = imbalance_rows[imbalance_rows["share_gap"] < 0].tail(1)["industry_label"].tolist()
    if not positive:
        return None

    pull_clause = ", ".join(positive)
    release_clause = f" while {negative[0]} looks more residence-heavy" if negative else ""
    return (
        f"{summary['geo_name']} has {summary['jobs_to_workers_ratio_label']} jobs per resident worker in "
        f"{int(summary['year'])}, with {top_job_center['tract_name']} standing out as its largest tract job center. "
        f"The strongest workplace pull shows up in {pull_clause}{release_clause}."
    )


def get_d3_tract_job_centers(
    market_id: str = DEFAULT_MARKET_ID,
    min_jobs_total: int = D3_DEFAULT_TRACT_JOBS_FLOOR,
    selected_sector: str = "professional",
    top_n: int = D3_DEFAULT_TOP_TRACTS,
) -> dict[str, pd.DataFrame | int]:
    """Return tract job-center rankings for the D3 page.

    We keep this on top of the existing D2 tract surface so D3 and D2 interpret
    the same latest-year workplace geography rather than diverging.
    """
    rows = _build_tract_map_rows(market_id).copy()
    if rows.empty:
        return {
            "all_rows": rows,
            "top_jobs": rows,
            "top_ratio": rows,
            "top_selected_sector": rows,
            "selected_sector": selected_sector,
            "min_jobs_total": min_jobs_total,
        }

    sector_lookup = dict(EMPLOYMENT_SECTORS)
    share_column = f"d2_share_{selected_sector}"
    jobs_column = f"d2_jobs_{selected_sector}"
    filtered = rows[rows["jobs_total"].fillna(0) >= int(min_jobs_total)].copy()

    top_jobs = filtered.sort_values(
        ["jobs_total", "jobs_to_workers_ratio"],
        ascending=[False, False],
        kind="mergesort",
        na_position="last",
    ).head(top_n)
    top_ratio = filtered.dropna(subset=["jobs_to_workers_ratio"]).sort_values(
        ["jobs_to_workers_ratio", "jobs_total"],
        ascending=[False, False],
        kind="mergesort",
        na_position="last",
    ).head(top_n)
    top_selected_sector = filtered.sort_values(
        [share_column, jobs_column, "jobs_total"],
        ascending=[False, False, False],
        kind="mergesort",
        na_position="last",
    ).head(top_n)

    return {
        "all_rows": rows,
        "top_jobs": top_jobs,
        "top_ratio": top_ratio,
        "top_selected_sector": top_selected_sector,
        "selected_sector": selected_sector,
        "selected_sector_label": sector_lookup[selected_sector],
        "selected_sector_jobs_column": jobs_column,
        "selected_sector_share_column": share_column,
        "min_jobs_total": int(min_jobs_total),
    }


def get_d3_job_center_shortlist(
    market_id: str = DEFAULT_MARKET_ID,
    min_jobs_total: int = D3_DEFAULT_TRACT_JOBS_FLOOR,
    selected_sector: str = D4_DEFAULT_SELECTED_SECTOR,
    top_n: int = D4_DEFAULT_SHORTLIST_COUNT,
) -> pd.DataFrame:
    """Return a reusable D3 shortlist that D4 can enrich without manual export.

    This shortlist intentionally favors the largest tract job centers first,
    because D4 is meant to explain the metro's main employment nodes rather than
    re-rank tracts around one specific infrastructure feature.
    """
    payload = get_d3_tract_job_centers(
        market_id=market_id,
        min_jobs_total=min_jobs_total,
        selected_sector=selected_sector,
        top_n=max(int(top_n), D4_DEFAULT_SHORTLIST_COUNT),
    )
    rows = payload["top_jobs"].copy()
    if rows.empty:
        return rows

    selected_sector_label = payload["selected_sector_label"]
    share_column = payload["selected_sector_share_column"]
    jobs_column = payload["selected_sector_jobs_column"]
    rows["selected_sector_label"] = selected_sector_label
    rows["selected_sector_jobs"] = rows[jobs_column]
    rows["selected_sector_share"] = rows[share_column]
    rows["shortlist_rank"] = range(1, len(rows) + 1)
    rows["shortlist_basis"] = "largest_job_centers"
    rows["shortlist_note"] = rows.apply(
        lambda row: (
            f"Ranked #{int(row['shortlist_rank'])} by tract workplace jobs and "
            f"kept as a D4 interpretation candidate. {selected_sector_label} accounts for "
            f"{_safe_pct(row['selected_sector_share'])} of tract jobs."
        ),
        axis=1,
    )
    return rows.head(int(top_n)).reset_index(drop=True)


def get_d3_industry_imbalance(market_id: str = DEFAULT_MARKET_ID) -> pd.DataFrame:
    """Return the latest workplace-vs-resident industry imbalance surface for one CBSA."""
    con = get_connection()
    industry_select_sql = ",\n                ".join(
        [
            f"jobs_ind_{industry_id}, workers_ind_{industry_id}, pct_point_gap_ind_{industry_id}"
            for industry_id, _ in LODES_INDUSTRY_LABELS
        ]
    )
    try:
        rows = con.execute(
            f"""
            SELECT
                geo_id AS market_id,
                geo_name,
                year,
                {industry_select_sql}
            FROM patterns_in_place.gold.economics_lodes_wide
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
            ORDER BY year DESC
            LIMIT 1
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()

    if rows.empty:
        return pd.DataFrame(
            columns=[
                "market_id",
                "geo_name",
                "year",
                "industry_id",
                "industry_label",
                "jobs_total",
                "workers_total",
                "share_gap",
            ]
        )

    row = rows.iloc[0]
    records = []
    for industry_id, industry_label in LODES_INDUSTRY_LABELS:
        records.append(
            {
                "market_id": row["market_id"],
                "geo_name": row["geo_name"],
                "year": int(row["year"]),
                "industry_id": industry_id,
                "industry_label": industry_label,
                "jobs_total": pd.to_numeric(row.get(f"jobs_ind_{industry_id}"), errors="coerce"),
                "workers_total": pd.to_numeric(row.get(f"workers_ind_{industry_id}"), errors="coerce"),
                "share_gap": pd.to_numeric(row.get(f"pct_point_gap_ind_{industry_id}"), errors="coerce"),
            }
        )

    imbalance = pd.DataFrame.from_records(records)
    if imbalance.empty:
        return imbalance
    return imbalance.sort_values("share_gap", ascending=False, kind="mergesort").reset_index(drop=True)


def get_d3_page_payload(
    market_id: str = DEFAULT_MARKET_ID,
    min_jobs_total: int = D3_DEFAULT_TRACT_JOBS_FLOOR,
    selected_sector: str = "professional",
    top_n: int = D3_DEFAULT_TOP_TRACTS,
) -> dict[str, object]:
    """Bundle the D3 page payload so the Streamlit page stays thin."""
    tract_payload = get_d3_tract_job_centers(
        market_id=market_id,
        min_jobs_total=min_jobs_total,
        selected_sector=selected_sector,
        top_n=top_n,
    )
    summary = get_d3_cbsa_summary(market_id)
    imbalance = get_d3_industry_imbalance(market_id)
    takeaway = _build_d3_takeaway(summary, tract_payload["all_rows"], imbalance)
    return {
        "summary": summary,
        "tract_payload": tract_payload,
        "imbalance": imbalance,
        "takeaway": takeaway,
    }


def get_d3_map_payload(
    market_id: str = DEFAULT_MARKET_ID,
    min_jobs_total: int = D3_DEFAULT_TRACT_JOBS_FLOOR,
    selected_sector: str = "professional",
    mode: str = "top_jobs",
    top_n: int = D3_DEFAULT_TOP_TRACTS,
) -> dict[str, object]:
    """Return a tract map payload for the D3 job-centers page.

    This keeps D3 spatially legible without introducing a second, unrelated
    geography surface. We use the same tract geometry as D2 and highlight the
    leading tracts for the selected ranking mode.
    """
    tract_payload = get_d3_tract_job_centers(
        market_id=market_id,
        min_jobs_total=min_jobs_total,
        selected_sector=selected_sector,
        top_n=top_n,
    )
    rows = tract_payload["all_rows"]
    if rows.empty:
        return {
            "features": [],
            "view_state": _build_view_state([]),
            "rows": rows,
            "legend": pd.DataFrame(),
            "title": "D3 tract map",
            "subtitle": "",
        }

    highlighted_rows = tract_payload[mode]
    highlighted_ids = set(highlighted_rows["tract_geoid"].tolist())
    sector_label = tract_payload["selected_sector_label"]
    share_column = tract_payload["selected_sector_share_column"]
    jobs_column = tract_payload["selected_sector_jobs_column"]

    if mode == "top_ratio":
        metric_column = "jobs_to_workers_ratio"
        title = "Highest jobs-to-workers tracts"
        subtitle = (
            f"Highlighted tracts have at least {int(min_jobs_total):,} workplace jobs and the strongest "
            "jobs-to-resident-workers ratios."
        )
        start_hex, end_hex = "#E0F2FE", "#075985"
    elif mode == "top_selected_sector":
        metric_column = share_column
        title = f"{sector_label} workplace centers"
        subtitle = (
            f"Highlighted tracts have at least {int(min_jobs_total):,} workplace jobs and the largest "
            f"{sector_label} job concentrations."
        )
        start_hex, end_hex = "#ECFCCB", "#3F6212"
    else:
        metric_column = "jobs_total"
        title = "Largest tract job centers"
        subtitle = (
            f"Highlighted tracts have at least {int(min_jobs_total):,} workplace jobs and the largest "
            "absolute job counts."
        )
        start_hex, end_hex = "#DBEAFE", "#1D4ED8"

    highlighted_max = highlighted_rows[metric_column].max(skipna=True)
    if pd.isna(highlighted_max) or float(highlighted_max) <= 0:
        highlighted_max = 1.0

    features: list[dict] = []
    for _, row in rows.iterrows():
        tract_geoid = row["tract_geoid"]
        is_highlighted = tract_geoid in highlighted_ids
        metric_value = row.get(metric_column)
        ratio = 0.0 if pd.isna(metric_value) else float(metric_value) / float(highlighted_max)
        fill_color = (
            _interpolate_rgba(start_hex, end_hex, ratio, 205)
            if is_highlighted
            else [222, 226, 230, 85]
        )
        line_color = [66, 66, 66, 120] if is_highlighted else [140, 140, 140, 60]
        features.append(
            {
                "type": "Feature",
                "geometry": row["geometry"],
                "properties": {
                    "tract_geoid": tract_geoid,
                    "tract_name": row["tract_name"],
                    "highlight_status": "Highlighted" if is_highlighted else "Other tract",
                    "dominant_sector_label": row["dominant_sector_label"],
                    "jobs_total": _safe_count(row["jobs_total"]),
                    "workers_total": _safe_count(row["workers_total"]),
                    "jobs_to_workers_ratio_label": (
                        "—"
                        if pd.isna(row["jobs_to_workers_ratio"])
                        else f"{float(row['jobs_to_workers_ratio']):.2f}x"
                    ),
                    "selected_sector_label": sector_label,
                    "selected_sector_jobs": _safe_count(row[jobs_column]),
                    "selected_sector_share_pct": _safe_pct(row[share_column]),
                    "metric_value_label": (
                        _safe_pct(metric_value)
                        if mode == "top_selected_sector"
                        else (
                            "—"
                            if pd.isna(metric_value)
                            else (
                                f"{float(metric_value):.2f}x"
                                if mode == "top_ratio"
                                else _safe_count(metric_value)
                            )
                        )
                    ),
                    "fill_color": fill_color,
                    "line_color": line_color,
                },
            }
        )

    return {
        "features": features,
        "view_state": _build_view_state(features),
        "rows": rows,
        "highlight_rows": highlighted_rows,
        "legend": pd.DataFrame(
            [
                {"Group": "Highlighted job centers", "Color": end_hex},
                {"Group": "Other tracts", "Color": "#DEE2E6"},
            ]
        ),
        "title": title,
        "subtitle": subtitle,
        "mode": mode,
        "selected_sector_label": sector_label,
        "min_jobs_total": int(min_jobs_total),
    }


def get_spatial_output_dir(market_id: str = DEFAULT_MARKET_ID) -> Path:
    """Return the app-local cache directory for one market's D4 extracts."""
    direct_path = SPATIAL_OUTPUTS_ROOT / str(market_id)
    if direct_path.exists():
        return direct_path

    alias = SPATIAL_OUTPUT_DIR_ALIASES.get(str(market_id))
    if alias:
        alias_path = SPATIAL_OUTPUTS_ROOT / alias
        if alias_path.exists():
            return alias_path

    return direct_path


def _empty_spatial_frame() -> pd.DataFrame:
    """Return the normalized empty frame for cached spatial layers."""
    return pd.DataFrame(columns=COMMON_SPATIAL_COLUMNS)


def _load_cached_parquet(path: Path) -> pd.DataFrame:
    """Read a cached parquet file without requiring a separate parquet engine."""
    if not path.exists():
        return _empty_spatial_frame()

    con = duckdb.connect()
    try:
        frame = con.execute("SELECT * FROM read_parquet(?)", [str(path)]).fetchdf()
    finally:
        con.close()

    for column in COMMON_SPATIAL_COLUMNS:
        if column not in frame.columns:
            frame[column] = None

    if "geometry" in frame.columns:
        frame["geometry"] = frame["geometry"].apply(
            lambda value: json.loads(value) if isinstance(value, str) and value else value
        )
    for column in ["centroid_lat", "centroid_lon"]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    for column in ["attributes_json", "source_id", "feature_name", "layer_group", "category", "subcategory"]:
        if column in frame.columns:
            frame[column] = frame[column].fillna("")
    return frame[COMMON_SPATIAL_COLUMNS].copy()


def load_spatial_manifest(market_id: str = DEFAULT_MARKET_ID) -> dict[str, object]:
    """Load the D4 extract manifest when one has been written for the market."""
    manifest_path = get_spatial_output_dir(market_id) / "spatial_manifest.json"
    if not manifest_path.exists():
        return {
            "market_id": str(market_id),
            "layers": [],
            "notes": [
                "No cached D4 spatial manifest is present yet.",
                "Run ingest_spatial.py before expecting OSM or Overture overlays in the app.",
            ],
        }

    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _layer_rows_to_geojson_features(rows: pd.DataFrame) -> list[dict]:
    """Turn cached geometry rows into GeoJSON features for pydeck rendering."""
    features: list[dict] = []
    if rows.empty:
        return features

    for _, row in rows.iterrows():
        geometry = row.get("geometry")
        if not geometry:
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "feature_name": row.get("feature_name") or "Unnamed feature",
                    "layer_group": row.get("layer_group") or "unclassified",
                    "category": row.get("category") or "infrastructure",
                    "source_system": row.get("source_system") or "unknown",
                },
            }
        )
    return features


def _build_population_markers(rows: pd.DataFrame, top_n: int) -> pd.DataFrame:
    """Surface the largest tract population centers as overlay markers."""
    if rows.empty:
        return pd.DataFrame(
            columns=["tract_geoid", "tract_name", "centroid_lat", "centroid_lon", "pop_total", "label", "metric"]
        )

    markers = rows.dropna(subset=["centroid_lat", "centroid_lon", "pop_total"]).copy()
    if markers.empty:
        return markers

    markers = markers.sort_values("pop_total", ascending=False, kind="mergesort").head(int(top_n))
    markers["label"] = markers["tract_name"]
    markers["metric"] = markers["pop_total"].map(_safe_count)
    return markers[
        ["tract_geoid", "tract_name", "centroid_lat", "centroid_lon", "pop_total", "label", "metric"]
    ].reset_index(drop=True)


def _build_job_center_markers(
    market_id: str,
    top_n: int,
    selected_sector: str,
) -> pd.DataFrame:
    """Surface the largest tract job centers as overlay markers."""
    payload = get_d3_tract_job_centers(
        market_id=market_id,
        min_jobs_total=D3_DEFAULT_TRACT_JOBS_FLOOR,
        selected_sector=selected_sector,
        top_n=top_n,
    )
    rows = payload["top_jobs"].copy()
    if rows.empty:
        return pd.DataFrame(
            columns=[
                "tract_geoid",
                "tract_name",
                "centroid_lat",
                "centroid_lon",
                "jobs_total",
                "dominant_sector_label",
                "label",
                "metric",
            ]
        )

    rows = rows.dropna(subset=["centroid_lat", "centroid_lon"]).copy()
    rows["label"] = rows["tract_name"]
    rows["metric"] = rows["jobs_total"].map(_safe_count)
    return rows[
        [
            "tract_geoid",
            "tract_name",
            "centroid_lat",
            "centroid_lon",
            "jobs_total",
            "dominant_sector_label",
            "label",
            "metric",
        ]
    ].reset_index(drop=True)


def get_d4_base_map_payload(
    market_id: str = DEFAULT_MARKET_ID,
    base_surface: str = D4_DEFAULT_BASE_SURFACE,
    selected_sector: str = D4_DEFAULT_SELECTED_SECTOR,
) -> dict[str, object]:
    """Return the D4 tract fill payload for either total jobs or sector share."""
    if base_surface == "selected_industry":
        payload = get_d2_tract_map_payload(
            market_id=market_id,
            mode="selected_industry",
            selected_sector=selected_sector,
        )
        payload["base_surface"] = "selected_industry"
        return payload

    rows = _build_tract_map_rows(market_id)
    if rows.empty:
        return {"features": [], "view_state": _build_view_state([]), "rows": rows, "base_surface": "jobs_total"}

    max_jobs = rows["jobs_total"].max(skipna=True)
    if pd.isna(max_jobs) or float(max_jobs) <= 0:
        max_jobs = 1.0

    features: list[dict] = []
    for _, row in rows.iterrows():
        jobs_total = row.get("jobs_total")
        ratio = 0.0 if pd.isna(jobs_total) else float(jobs_total) / float(max_jobs)
        fill_color = _interpolate_rgba("#F3E8FF", "#6B21A8", ratio, 205)
        properties = {
            "tract_geoid": row["tract_geoid"],
            "tract_name": row["tract_name"],
            "dominant_sector_label": row["dominant_sector_label"],
            "jobs_total": _safe_count(jobs_total),
            "label": "Total workplace jobs",
            "metric": _safe_count(jobs_total),
            "fill_color": fill_color,
        }
        features.append(
            {
                "type": "Feature",
                "geometry": row["geometry"],
                "properties": properties,
            }
        )

    return {
        "features": features,
        "legend": pd.DataFrame(
            [
                {"Level": "Lower tract job count", "Color": "#F3E8FF"},
                {"Level": "Higher tract job count", "Color": "#6B21A8"},
            ]
        ),
        "view_state": _build_view_state(features),
        "rows": rows,
        "title": "Total workplace jobs by tract",
        "subtitle": f"Latest LODES tract workplace jobs ({int(rows['year'].iloc[0])})",
        "year": int(rows["year"].iloc[0]),
        "base_surface": "jobs_total",
    }


def _build_d4_feature_catalog(
    osm_lines: pd.DataFrame,
    osm_polygons: pd.DataFrame,
    osm_points: pd.DataFrame,
    overture_pois: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Collect the D4 feature groups that feed the first-pass tract enrichment."""
    empty = pd.DataFrame(columns=["feature_name", "centroid_lat", "centroid_lon", "source_system"])
    catalogs: dict[str, pd.DataFrame] = {}

    def _with_required_columns(rows: pd.DataFrame) -> pd.DataFrame:
        if rows.empty:
            return empty.copy()
        return rows.dropna(subset=["centroid_lat", "centroid_lon"]).copy()

    catalogs["highways"] = _with_required_columns(osm_lines[osm_lines["layer_group"] == "highways"])
    catalogs["rail"] = _with_required_columns(osm_lines[osm_lines["layer_group"] == "rail"])
    catalogs["airports"] = _with_required_columns(
        pd.concat(
            [
                osm_polygons[osm_polygons["layer_group"] == "airports"],
                osm_points[osm_points["layer_group"] == "airports"],
                overture_pois[overture_pois["subcategory"] == "airport"],
            ],
            ignore_index=True,
        )
    )
    catalogs["ports"] = _with_required_columns(
        pd.concat(
            [
                osm_polygons[osm_polygons["layer_group"] == "ports"],
                osm_points[osm_points["layer_group"] == "ports"],
                overture_pois[overture_pois["subcategory"] == "port"],
            ],
            ignore_index=True,
        )
    )
    catalogs["warehouses_logistics"] = _with_required_columns(
        pd.concat(
            [
                osm_polygons[osm_polygons["layer_group"] == "warehouses_logistics"],
                osm_points[osm_points["layer_group"] == "warehouses_logistics"],
                overture_pois[overture_pois["subcategory"] == "warehouse_logistics"],
            ],
            ignore_index=True,
        )
    )
    catalogs["hospitals"] = _with_required_columns(overture_pois[overture_pois["subcategory"] == "hospital"])
    catalogs["universities"] = _with_required_columns(
        overture_pois[overture_pois["subcategory"] == "college_university"]
    )
    catalogs["schools"] = _with_required_columns(
        overture_pois[
            overture_pois["subcategory"].isin(
                [
                    "elementary_school",
                    "middle_school",
                    "high_school",
                    "preschool",
                    "specialty_school",
                    "place_of_learning",
                ]
            )
        ]
    )
    catalogs["groceries"] = _with_required_columns(overture_pois[overture_pois["subcategory"] == "grocery"])
    return catalogs


def _summarize_nearby_features(
    tract_row: pd.Series,
    feature_catalog: dict[str, pd.DataFrame],
    buffer_miles: float,
) -> dict[str, object]:
    """Count or flag nearby D4 features around one shortlisted tract centroid."""
    summary: dict[str, object] = {}
    for feature_key, rows in feature_catalog.items():
        if rows.empty:
            summary[f"{feature_key}_count"] = 0
            summary[f"{feature_key}_present"] = False
            summary[f"{feature_key}_nearest_miles"] = None
            continue

        distances = rows.apply(
            lambda row: _haversine_miles(
                tract_row["centroid_lat"],
                tract_row["centroid_lon"],
                row["centroid_lat"],
                row["centroid_lon"],
            ),
            axis=1,
        ).dropna()
        if distances.empty:
            summary[f"{feature_key}_count"] = 0
            summary[f"{feature_key}_present"] = False
            summary[f"{feature_key}_nearest_miles"] = None
            continue

        nearby = distances[distances <= float(buffer_miles)]
        summary[f"{feature_key}_count"] = int(len(nearby))
        summary[f"{feature_key}_present"] = bool(len(nearby))
        summary[f"{feature_key}_nearest_miles"] = float(distances.min())
    return summary


def _classify_d4_job_center(row: pd.Series) -> tuple[str, str]:
    """Apply a transparent first-pass typology to one shortlisted tract."""
    infra_score = (
        int(row.get("highways_present", False))
        + int(row.get("rail_present", False))
        + int(row.get("airports_present", False))
        + int(row.get("ports_present", False))
        + min(int(row.get("warehouses_logistics_count", 0)), 2)
    )
    institution_score = (
        min(int(row.get("hospitals_count", 0)), 2)
        + min(int(row.get("universities_count", 0)), 2)
        + min(int(row.get("schools_count", 0)), 1)
    )
    dominant_sector = row.get("dominant_sector_id")

    if infra_score >= 3 and dominant_sector in {"transport_util", "manufacturing", "wholesale", "construction"}:
        return (
            "Infrastructure / logistics-led",
            "Nearby corridors and freight-oriented features outweigh the institutional signals in this tract's buffer.",
        )
    if institution_score >= 2 and dominant_sector in {"educ_health", "professional", "other_services"}:
        return (
            "Institutional",
            "Hospitals, universities, or schools show up repeatedly near this tract, which fits an institutional employment center read.",
        )
    if dominant_sector in {"professional", "finance_real", "information"} and infra_score <= 1 and institution_score <= 1:
        return (
            "Office / professional",
            "The dominant sector leans office-oriented and the nearby freight or institutional anchors are limited in this first-pass buffer.",
        )
    return (
        "Mixed",
        "No single infrastructure or institutional signal dominates this tract strongly enough to treat it as a pure one-type center in v1.",
    )


def _build_d4_typology_evidence(row: pd.Series) -> str:
    """Write short, review-friendly evidence text for one D4 tract read."""
    evidence_parts: list[str] = []
    for feature_key, label in D4_INTERPRETATION_LABELS.items():
        count = int(row.get(f"{feature_key}_count", 0) or 0)
        if count > 0:
            evidence_parts.append(f"{count} {label.lower()}")
    if not evidence_parts:
        evidence_parts.append("no first-wave features inside the current buffer")
    nearest_highway = row.get("highways_nearest_miles")
    if nearest_highway is not None and not pd.isna(nearest_highway):
        evidence_parts.append(f"nearest highway at {_safe_miles(nearest_highway)}")
    return "; ".join(evidence_parts)


def get_d4_job_center_interpretation(
    market_id: str = DEFAULT_MARKET_ID,
    selected_sector: str = D4_DEFAULT_SELECTED_SECTOR,
    min_jobs_total: int = D3_DEFAULT_TRACT_JOBS_FLOOR,
    shortlist_count: int = D4_DEFAULT_SHORTLIST_COUNT,
    buffer_miles: float = D4_DEFAULT_BUFFER_MILES,
) -> dict[str, object]:
    """Build the D4 job-center shortlist, enrichment table, and typology reads."""
    output_dir = get_spatial_output_dir(market_id)
    osm_lines = _load_cached_parquet(output_dir / "osm_infrastructure_lines.parquet")
    osm_polygons = _load_cached_parquet(output_dir / "osm_infrastructure_polygons.parquet")
    osm_points = _load_cached_parquet(output_dir / "osm_infrastructure_points.parquet")
    overture_pois = _load_cached_parquet(output_dir / "overture_pois.parquet")
    shortlist = get_d3_job_center_shortlist(
        market_id=market_id,
        min_jobs_total=min_jobs_total,
        selected_sector=selected_sector,
        top_n=shortlist_count,
    )
    if shortlist.empty:
        return {
            "shortlist": shortlist,
            "table": shortlist,
            "selected_detail": {},
            "buffer_miles": float(buffer_miles),
            "notes": ["No D3 shortlist was available for D4 interpretation."],
        }

    feature_catalog = _build_d4_feature_catalog(
        osm_lines=osm_lines,
        osm_polygons=osm_polygons,
        osm_points=osm_points,
        overture_pois=overture_pois,
    )
    enriched_rows = shortlist.copy()
    summaries = enriched_rows.apply(
        lambda row: _summarize_nearby_features(
            tract_row=row,
            feature_catalog=feature_catalog,
            buffer_miles=buffer_miles,
        ),
        axis=1,
        result_type="expand",
    )
    enriched_rows = pd.concat([enriched_rows.reset_index(drop=True), summaries.reset_index(drop=True)], axis=1)
    typology_rows = enriched_rows.apply(_classify_d4_job_center, axis=1, result_type="expand")
    typology_rows.columns = ["interpretation_type", "interpretation_rationale"]
    enriched_rows = pd.concat([enriched_rows, typology_rows], axis=1)
    enriched_rows["interpretation_evidence"] = enriched_rows.apply(_build_d4_typology_evidence, axis=1)
    enriched_rows["selected_sector_share_label"] = enriched_rows["selected_sector_share"].map(_safe_pct)
    enriched_rows["jobs_total_label"] = enriched_rows["jobs_total"].map(_safe_count)
    enriched_rows["jobs_to_workers_ratio_label"] = enriched_rows["jobs_to_workers_ratio"].apply(
        lambda value: "—" if pd.isna(value) else f"{float(value):.2f}x"
    )

    display_columns = [
        "shortlist_rank",
        "tract_name",
        "dominant_sector_label",
        "jobs_total_label",
        "jobs_to_workers_ratio_label",
        "interpretation_type",
        "highways_count",
        "rail_count",
        "warehouses_logistics_count",
        "hospitals_count",
        "universities_count",
        "schools_count",
        "groceries_count",
        "interpretation_evidence",
    ]
    table = enriched_rows[display_columns].rename(
        columns={
            "shortlist_rank": "Rank",
            "tract_name": "Tract",
            "dominant_sector_label": "Dominant sector",
            "jobs_total_label": "Workplace jobs",
            "jobs_to_workers_ratio_label": "Jobs / workers",
            "interpretation_type": "Typology read",
            "highways_count": "Highways",
            "rail_count": "Rail",
            "warehouses_logistics_count": "Warehouses",
            "hospitals_count": "Hospitals",
            "universities_count": "Universities",
            "schools_count": "Schools",
            "groceries_count": "Groceries",
            "interpretation_evidence": "Evidence",
        }
    )

    first_row = enriched_rows.iloc[0].to_dict()
    notes = [
        (
            f"D4 uses a {float(buffer_miles):.1f}-mile straight-line buffer around shortlisted tract centroids. "
            "These are geometric proximity signals, not network-access or travel-time measures."
        )
    ]
    return {
        "shortlist": enriched_rows,
        "table": table,
        "selected_detail": first_row,
        "buffer_miles": float(buffer_miles),
        "notes": notes,
    }


def get_d4_overlay_payload(
    market_id: str = DEFAULT_MARKET_ID,
    selected_sector: str = D4_DEFAULT_SELECTED_SECTOR,
    base_surface: str = D4_DEFAULT_BASE_SURFACE,
    max_population_markers: int = D4_DEFAULT_TOP_POP_TRACTS,
    max_job_markers: int = D4_DEFAULT_TOP_JOB_CENTER_TRACTS,
    interpretation_buffer_miles: float = D4_DEFAULT_BUFFER_MILES,
    shortlist_count: int = D4_DEFAULT_SHORTLIST_COUNT,
    min_jobs_total: int = D3_DEFAULT_TRACT_JOBS_FLOOR,
) -> dict[str, object]:
    """Bundle the cache-backed D4 overlays with D2/D3 analytical context."""
    output_dir = get_spatial_output_dir(market_id)
    manifest = load_spatial_manifest(market_id)

    osm_lines = _load_cached_parquet(output_dir / "osm_infrastructure_lines.parquet")
    osm_polygons = _load_cached_parquet(output_dir / "osm_infrastructure_polygons.parquet")
    osm_points = _load_cached_parquet(output_dir / "osm_infrastructure_points.parquet")
    overture_pois = _load_cached_parquet(output_dir / "overture_pois.parquet")

    base_payload = get_d4_base_map_payload(
        market_id=market_id,
        base_surface=base_surface,
        selected_sector=selected_sector,
    )
    population_markers = _build_population_markers(base_payload["rows"], max_population_markers)
    job_center_markers = _build_job_center_markers(
        market_id=market_id,
        top_n=max_job_markers,
        selected_sector=selected_sector,
    )
    interpretation = get_d4_job_center_interpretation(
        market_id=market_id,
        selected_sector=selected_sector,
        min_jobs_total=min_jobs_total,
        shortlist_count=shortlist_count,
        buffer_miles=interpretation_buffer_miles,
    )

    layer_summary = pd.DataFrame(
        [
            {
                "layer_key": "osm_lines",
                "label": D4_LAYER_STYLES["osm_lines"]["label"],
                "row_count": int(len(osm_lines)),
                "groups": ", ".join(sorted(value for value in osm_lines["layer_group"].unique() if value)) or "—",
            },
            {
                "layer_key": "osm_polygons",
                "label": D4_LAYER_STYLES["osm_polygons"]["label"],
                "row_count": int(len(osm_polygons)),
                "groups": ", ".join(sorted(value for value in osm_polygons["layer_group"].unique() if value)) or "—",
            },
            {
                "layer_key": "osm_points",
                "label": D4_LAYER_STYLES["osm_points"]["label"],
                "row_count": int(len(osm_points)),
                "groups": ", ".join(sorted(value for value in osm_points["layer_group"].unique() if value)) or "—",
            },
        ]
    )

    notes = list(manifest.get("notes", []))
    if osm_lines.empty and osm_polygons.empty and osm_points.empty and overture_pois.empty:
        notes.append("No cached OSM or Overture records were found for this market yet.")
    notes.extend(interpretation.get("notes", []))

    return {
        "market_id": str(market_id),
        "selected_sector": selected_sector,
        "base_surface": base_surface,
        "base_payload": base_payload,
        "view_state": base_payload.get("view_state", _build_view_state([])),
        "osm_lines": osm_lines,
        "osm_polygons": osm_polygons,
        "osm_points": osm_points,
        "overture_pois": overture_pois,
        "osm_line_features": _layer_rows_to_geojson_features(osm_lines),
        "osm_polygon_features": _layer_rows_to_geojson_features(osm_polygons),
        "osm_point_features": _layer_rows_to_geojson_features(osm_points),
        "population_markers": population_markers,
        "job_center_markers": job_center_markers,
        "interpretation": interpretation,
        "layer_summary": layer_summary,
        "manifest": manifest,
        "notes": notes,
        "overlay_order": [
            "tract_fill",
            "osm_lines",
            "osm_polygons",
            "population_markers",
            "job_center_markers",
        ],
    }


def _count_present_sector_shares(rows: pd.DataFrame, share_prefix: str, sector_keys: Iterable[str]) -> pd.Series:
    share_columns = [f"{share_prefix}{sector_key}" for sector_key in sector_keys]
    return rows[share_columns].notna().sum(axis=1)


def _employment_basis_key(rows: pd.DataFrame) -> str:
    """Choose QCEW unless the market is too sparse and needs ACS fallback."""
    qcew_counts = _count_present_sector_shares(
        rows,
        BASIS_CONFIG["employment_share"].share_prefix,
        [sector_key for sector_key, _ in EMPLOYMENT_SECTORS],
    )
    qcew_usable = rows["qcew_private_emp_total"].notna() & (qcew_counts >= MIN_REQUIRED_SECTORS)
    return "employment_share" if bool(qcew_usable.any()) else "employment_share_fallback"


def _build_basis_rows(
    rows: pd.DataFrame,
    market_id: str,
    basis_key: str,
    other_latest_year: int | None = None,
) -> pd.DataFrame:
    """Reshape a basis from wide Gold columns into the normalized app surface."""
    cfg = BASIS_CONFIG[basis_key]
    sector_keys = [sector_key for sector_key, _ in cfg.sectors]
    share_columns = [f"{cfg.share_prefix}{sector_key}" for sector_key in sector_keys]
    raw_columns = [f"{cfg.raw_prefix}{sector_key}" for sector_key in sector_keys]
    keep_columns = ["geo_name", "year", *share_columns, *raw_columns]
    source_rows = rows[keep_columns].copy()

    melted_shares = source_rows.melt(
        id_vars=["geo_name", "year"],
        value_vars=share_columns,
        var_name="sector_share_column",
        value_name="share_value",
    )
    melted_shares["sector_id"] = melted_shares["sector_share_column"].str.removeprefix(cfg.share_prefix)

    melted_raw = source_rows.melt(
        id_vars=["geo_name", "year"],
        value_vars=raw_columns,
        var_name="sector_raw_column",
        value_name="raw_value",
    )
    melted_raw["sector_id"] = melted_raw["sector_raw_column"].str.removeprefix(cfg.raw_prefix)

    tidy = melted_shares.merge(
        melted_raw[["geo_name", "year", "sector_id", "raw_value"]],
        on=["geo_name", "year", "sector_id"],
        how="left",
    )
    tidy["share_value"] = pd.to_numeric(tidy["share_value"], errors="coerce")
    tidy["raw_value"] = pd.to_numeric(tidy["raw_value"], errors="coerce")
    tidy = tidy[tidy["share_value"].notna()].copy()
    label_lookup = dict(cfg.sectors)
    tidy["sector_label"] = tidy["sector_id"].map(label_lookup)
    tidy["basis"] = cfg.basis
    tidy["market_id"] = str(market_id)
    tidy["source_label"] = cfg.source_label
    tidy["geo_name"] = tidy["geo_name"].astype(str)

    if tidy.empty:
        return tidy

    latest_year = int(tidy["year"].max())
    vintage_note = f"{cfg.label} through {latest_year}."
    if other_latest_year is not None and other_latest_year != latest_year:
        vintage_note = f"{vintage_note} Alternate basis latest year: {other_latest_year}."

    # Normalize to the surfaced sector universe so the stacked chart always
    # represents a full 100% composition, even when the underlying source
    # leaves a small residual outside the broad-family rollup we expose here.
    share_totals = tidy.groupby("year")["share_value"].transform("sum")
    tidy["share_value"] = tidy["share_value"] / share_totals.where(share_totals != 0)
    tidy["latest_available_year_for_basis"] = latest_year
    tidy["vintage_note"] = vintage_note
    tidy["display_order"] = (
        tidy.sort_values(["year", "share_value", "sector_label"], ascending=[True, False, True], kind="mergesort")
        .groupby("year")
        .cumcount()
        .add(1)
    )
    tidy["basis_label"] = cfg.label
    return tidy[
        [
            "market_id",
            "geo_name",
            "basis",
            "basis_label",
            "year",
            "sector_id",
            "sector_label",
            "share_value",
            "raw_value",
            "display_order",
            "latest_available_year_for_basis",
            "source_label",
            "vintage_note",
        ]
    ].sort_values(["basis", "year", "display_order", "sector_label"], kind="mergesort")


def _format_raw_value(raw_value: float | int | None, basis: str) -> str:
    """Format raw levels for chart tooltips without changing the shared renderer."""
    if raw_value is None or pd.isna(raw_value):
        return ""
    numeric = float(raw_value)
    if basis == "gdp_share":
        if abs(numeric) >= 1_000_000_000:
            return f"${numeric / 1_000_000_000:.1f}B"
        if abs(numeric) >= 1_000_000:
            return f"${numeric / 1_000_000:.1f}M"
        return f"${numeric:,.0f}"
    return f"{numeric:,.0f}"


def get_d1_surface(market_id: str = DEFAULT_MARKET_ID) -> pd.DataFrame:
    """Return the normalized D1 surface for both employment and GDP views."""
    market_rows = get_market_surface(market_id)
    if market_rows.empty:
        return pd.DataFrame(
            columns=[
                "market_id",
                "geo_name",
                "basis",
                "basis_label",
                "year",
                "sector_id",
                "sector_label",
                "share_value",
                "raw_value",
                "display_order",
                "latest_available_year_for_basis",
                "source_label",
                "vintage_note",
            ]
        )

    employment_key = _employment_basis_key(market_rows)
    employment_preview = _build_basis_rows(market_rows, market_id, employment_key)
    gdp_preview = _build_basis_rows(market_rows, market_id, "gdp_share")

    employment_latest = int(employment_preview["latest_available_year_for_basis"].iloc[0]) if not employment_preview.empty else None
    gdp_latest = int(gdp_preview["latest_available_year_for_basis"].iloc[0]) if not gdp_preview.empty else None

    employment = _build_basis_rows(market_rows, market_id, employment_key, gdp_latest)
    gdp = _build_basis_rows(market_rows, market_id, "gdp_share", employment_latest)
    return pd.concat([employment, gdp], ignore_index=True)


def get_d1_basis_frames(market_id: str = DEFAULT_MARKET_ID) -> dict[str, pd.DataFrame]:
    """Return explicit per-basis data frames for the app tabs."""
    surface = get_d1_surface(market_id)
    return {
        "employment_share": get_basis_slice(surface, "employment_share"),
        "gdp_share": get_basis_slice(surface, "gdp_share"),
    }


def _build_benchmark_rows_from_states(
    state_rows: pd.DataFrame,
    basis_key: str,
    benchmark_geo_id: str,
    benchmark_geo_name: str,
) -> pd.DataFrame:
    """Aggregate state rows into a benchmark frame using the same sector definitions as the market frame."""
    cfg = BASIS_CONFIG[basis_key]
    sector_keys = [sector_key for sector_key, _ in cfg.sectors]
    raw_columns = [f"{cfg.raw_prefix}{sector_key}" for sector_key in sector_keys]
    aggregated = (
        state_rows.groupby("year", as_index=False)[raw_columns]
        .sum(min_count=1)
        .sort_values("year", kind="mergesort")
    )
    if aggregated.empty:
        return pd.DataFrame()

    total_raw = aggregated[raw_columns].sum(axis=1, min_count=1)
    tidy_parts: list[pd.DataFrame] = []
    for sector_key, sector_label in cfg.sectors:
        raw_column = f"{cfg.raw_prefix}{sector_key}"
        sector_df = aggregated[["year", raw_column]].rename(columns={raw_column: "raw_value"}).copy()
        sector_df["share_value"] = sector_df["raw_value"] / total_raw.where(total_raw != 0)
        sector_df["sector_id"] = sector_key
        sector_df["sector_label"] = sector_label
        tidy_parts.append(sector_df)

    tidy = pd.concat(tidy_parts, ignore_index=True)
    tidy = tidy[tidy["share_value"].notna()].copy()
    if tidy.empty:
        return tidy

    tidy["market_id"] = benchmark_geo_id
    tidy["geo_name"] = benchmark_geo_name
    tidy["basis"] = cfg.basis
    tidy["basis_label"] = cfg.label
    tidy["source_label"] = cfg.source_label
    tidy["latest_available_year_for_basis"] = int(tidy["year"].max())
    tidy["vintage_note"] = f"{cfg.label} through {int(tidy['year'].max())}."
    tidy["display_order"] = (
        tidy.sort_values(["year", "share_value", "sector_label"], ascending=[True, False, True], kind="mergesort")
        .groupby("year")
        .cumcount()
        .add(1)
    )
    return tidy[
        [
            "market_id",
            "geo_name",
            "basis",
            "basis_label",
            "year",
            "sector_id",
            "sector_label",
            "share_value",
            "raw_value",
            "display_order",
            "latest_available_year_for_basis",
            "source_label",
            "vintage_note",
        ]
    ].sort_values(["year", "display_order", "sector_label"], kind="mergesort")


def _build_benchmark_rows_from_aggregated(
    aggregated_rows: pd.DataFrame,
    basis_key: str,
) -> pd.DataFrame:
    """Reshape an already-aggregated benchmark surface into the shared D1/D5 basis contract."""
    if aggregated_rows.empty:
        return pd.DataFrame()

    cfg = BASIS_CONFIG[basis_key]
    sector_keys = [sector_key for sector_key, _ in cfg.sectors]
    raw_columns = [f"{cfg.raw_prefix}{sector_key}" for sector_key in sector_keys]
    keep_columns = ["benchmark_geo_id", "benchmark_geo_name", "year", *raw_columns]
    source_rows = aggregated_rows[keep_columns].copy()
    total_raw = source_rows[raw_columns].sum(axis=1, min_count=1)

    tidy_parts: list[pd.DataFrame] = []
    for sector_key, sector_label in cfg.sectors:
        raw_column = f"{cfg.raw_prefix}{sector_key}"
        sector_df = source_rows[
            ["benchmark_geo_id", "benchmark_geo_name", "year", raw_column]
        ].rename(columns={raw_column: "raw_value"})
        sector_df["share_value"] = sector_df["raw_value"] / total_raw.where(total_raw != 0)
        sector_df["sector_id"] = sector_key
        sector_df["sector_label"] = sector_label
        tidy_parts.append(sector_df)

    tidy = pd.concat(tidy_parts, ignore_index=True)
    tidy = tidy[tidy["share_value"].notna()].copy()
    if tidy.empty:
        return tidy

    tidy["market_id"] = tidy["benchmark_geo_id"]
    tidy["geo_name"] = tidy["benchmark_geo_name"]
    tidy["basis"] = cfg.basis
    tidy["basis_label"] = cfg.label
    tidy["source_label"] = cfg.source_label
    tidy["latest_available_year_for_basis"] = int(tidy["year"].max())
    tidy["vintage_note"] = f"{cfg.label} through {int(tidy['year'].max())}."
    tidy["display_order"] = (
        tidy.sort_values(["year", "share_value", "sector_label"], ascending=[True, False, True], kind="mergesort")
        .groupby(["benchmark_geo_id", "year"])
        .cumcount()
        .add(1)
    )
    return tidy[
        [
            "market_id",
            "geo_name",
            "basis",
            "basis_label",
            "year",
            "sector_id",
            "sector_label",
            "share_value",
            "raw_value",
            "display_order",
            "latest_available_year_for_basis",
            "source_label",
            "vintage_note",
        ]
    ].sort_values(["market_id", "year", "display_order", "sector_label"], kind="mergesort")


def get_benchmark_basis_frames(market_id: str = DEFAULT_MARKET_ID) -> dict[str, dict[str, pd.DataFrame]]:
    """Build explicit US and division benchmark frames from state rows."""
    context = get_market_context(market_id)
    division_id = context.get("division_id")

    con = get_connection()
    try:
        benchmark_rows = con.execute(
            _read_sql_file("d5_industry_state_benchmarks.sql"),
            [division_id, division_id, division_id],
        ).fetchdf()
    finally:
        con.close()

    if benchmark_rows.empty:
        return {
            "employment_share": {"us": pd.DataFrame(), "division": pd.DataFrame()},
            "gdp_share": {"us": pd.DataFrame(), "division": pd.DataFrame()},
        }

    employment_rows = _build_benchmark_rows_from_aggregated(benchmark_rows, "employment_share")
    gdp_rows = _build_benchmark_rows_from_aggregated(benchmark_rows, "gdp_share")
    return {
        "employment_share": {
            "us": employment_rows[employment_rows["market_id"] == "us"].copy(),
            "division": employment_rows[employment_rows["market_id"].str.startswith("division:")].copy(),
        },
        "gdp_share": {
            "us": gdp_rows[gdp_rows["market_id"] == "us"].copy(),
            "division": gdp_rows[gdp_rows["market_id"].str.startswith("division:")].copy(),
        },
    }


def get_basis_slice(surface: pd.DataFrame, basis: str) -> pd.DataFrame:
    """Filter the normalized surface to one basis."""
    return surface[surface["basis"] == basis].copy()


def get_available_years_for_basis_rows(basis_rows: pd.DataFrame) -> list[int]:
    """Return available years directly from one basis data frame."""
    return sorted(int(year) for year in basis_rows["year"].dropna().unique().tolist())


def get_available_years(surface: pd.DataFrame, basis: str) -> list[int]:
    """Return available years in ascending order for one basis."""
    basis_rows = get_basis_slice(surface, basis)
    return get_available_years_for_basis_rows(basis_rows)


def get_latest_year_for_basis_rows(basis_rows: pd.DataFrame) -> int | None:
    """Return the latest available year directly from one basis data frame."""
    years = get_available_years_for_basis_rows(basis_rows)
    return years[-1] if years else None


def get_latest_year(surface: pd.DataFrame, basis: str) -> int | None:
    """Return the latest available year for one basis."""
    basis_rows = get_basis_slice(surface, basis)
    return get_latest_year_for_basis_rows(basis_rows)


def get_basis_title_for_rows(basis_rows: pd.DataFrame) -> str:
    """Build a stable section title from one basis data frame."""
    if basis_rows.empty:
        return "Industry makeup unavailable"
    return f"{basis_rows['basis_label'].iloc[0]} — {basis_rows['geo_name'].iloc[0]}"


def get_basis_title(surface: pd.DataFrame, basis: str) -> str:
    """Build a stable section title for app copy and charts."""
    basis_rows = get_basis_slice(surface, basis)
    return get_basis_title_for_rows(basis_rows)


def has_sufficient_bump_history_for_basis_rows(basis_rows: pd.DataFrame, min_years: int = MIN_BUMP_YEARS) -> bool:
    """Return whether one basis data frame has enough time points for a bump chart."""
    return len(get_available_years_for_basis_rows(basis_rows)) >= min_years


def has_sufficient_bump_history(surface: pd.DataFrame, basis: str, min_years: int = MIN_BUMP_YEARS) -> bool:
    """Return whether there are enough time points for a bump chart."""
    basis_rows = get_basis_slice(surface, basis)
    return has_sufficient_bump_history_for_basis_rows(basis_rows, min_years)


def get_takeaway_for_basis_rows(basis_rows: pd.DataFrame) -> str | None:
    """Summarize the largest share gainer and loser from one basis data frame."""
    if basis_rows.empty:
        return None

    years = get_available_years_for_basis_rows(basis_rows)
    if len(years) < 2:
        return None

    start_year = years[0]
    end_year = years[-1]
    start_rows = basis_rows[basis_rows["year"] == start_year][["sector_id", "sector_label", "share_value"]].rename(
        columns={"share_value": "start_share"}
    )
    end_rows = basis_rows[basis_rows["year"] == end_year][["sector_id", "sector_label", "share_value"]].rename(
        columns={"share_value": "end_share"}
    )
    delta = start_rows.merge(end_rows, on=["sector_id", "sector_label"], how="inner")
    if delta.empty:
        return None

    delta["share_delta"] = delta["end_share"] - delta["start_share"]
    delta = delta.sort_values(["share_delta", "sector_label"], ascending=[False, True], kind="mergesort")
    gainer = delta.iloc[0]
    loser = delta.iloc[-1]
    return (
        f"From {start_year} to {end_year}, {gainer['sector_label']} gained the most share "
        f"({gainer['share_delta']:+.1%}) while {loser['sector_label']} lost the most "
        f"({loser['share_delta']:+.1%})."
    )


def get_takeaway(surface: pd.DataFrame, basis: str) -> str | None:
    """Summarize the largest share gainer and loser from start to end."""
    basis_rows = get_basis_slice(surface, basis)
    return get_takeaway_for_basis_rows(basis_rows)


def prepare_current_mix_chart_data(surface: pd.DataFrame, basis: str, year: int | None = None) -> pd.DataFrame:
    """Return a one-bar stacked dataset for the selected market year."""
    basis_rows = get_basis_slice(surface, basis)
    return prepare_current_mix_chart_data_for_basis_rows(basis_rows, year)


def prepare_current_mix_chart_data_for_basis_rows(basis_rows: pd.DataFrame, year: int | None = None) -> pd.DataFrame:
    """Return a one-bar stacked dataset from one basis data frame."""
    if basis_rows.empty:
        return pd.DataFrame()

    selected_year = int(year) if year is not None else int(basis_rows["latest_available_year_for_basis"].iloc[0])
    selected = basis_rows[basis_rows["year"] == selected_year].copy()
    if selected.empty:
        return pd.DataFrame()

    selected = selected.sort_values(["share_value", "sector_label"], ascending=[False, True], kind="mergesort")
    selected["entity"] = selected["geo_name"]
    selected["value"] = selected["raw_value"]
    selected["series"] = selected["sector_label"]
    selected["time_window"] = selected["year"].astype(str)
    selected["metric_id"] = selected["basis"].map(
        {
            "employment_share": BASIS_CONFIG["employment_share"].chart_metric_id,
            "gdp_share": BASIS_CONFIG["gdp_share"].chart_metric_id,
        }
    )
    selected["metric_label"] = selected["basis"].map(
        {
            "employment_share": BASIS_CONFIG["employment_share"].chart_metric_label,
            "gdp_share": BASIS_CONFIG["gdp_share"].chart_metric_label,
        }
    )
    selected["raw_value_label"] = selected["raw_value"].apply(
        lambda value: _format_raw_value(value, selected["basis"].iloc[0])
    )
    selected["group"] = selected["source_label"] + " | " + selected["vintage_note"]
    selected["source"] = selected["source_label"]
    selected["vintage"] = selected["vintage_note"]
    return selected


def prepare_change_chart_data(surface: pd.DataFrame, basis: str) -> pd.DataFrame:
    """Return one row per sector-year for the D1 bump chart."""
    basis_rows = get_basis_slice(surface, basis)
    return prepare_change_chart_data_for_basis_rows(basis_rows)


def prepare_change_chart_data_for_basis_rows(basis_rows: pd.DataFrame) -> pd.DataFrame:
    """Return one row per sector-year for one basis data frame."""
    if basis_rows.empty:
        return pd.DataFrame()

    highlight_sectors = set()
    latest_year = get_latest_year_for_basis_rows(basis_rows)
    if latest_year is not None:
        latest_rows = basis_rows[basis_rows["year"] == latest_year].sort_values(
            ["share_value", "sector_label"],
            ascending=[False, True],
            kind="mergesort",
        )
        highlight_sectors.update(latest_rows.head(4)["sector_id"].tolist())

    years = get_available_years_for_basis_rows(basis_rows)
    if len(years) >= 2:
        start_rows = basis_rows[basis_rows["year"] == years[0]][["sector_id", "share_value"]].rename(
            columns={"share_value": "start_share"}
        )
        end_rows = basis_rows[basis_rows["year"] == years[-1]][["sector_id", "share_value"]].rename(
            columns={"share_value": "end_share"}
        )
        deltas = start_rows.merge(end_rows, on="sector_id", how="inner")
        if not deltas.empty:
            deltas["share_delta"] = deltas["end_share"] - deltas["start_share"]
            deltas = deltas.sort_values(["share_delta", "sector_id"], ascending=[False, True], kind="mergesort")
            highlight_sectors.update(deltas.head(1)["sector_id"].tolist())
            highlight_sectors.update(deltas.tail(1)["sector_id"].tolist())

    chart_rows = basis_rows.copy()
    chart_rows["geo_level"] = "industry_sector"
    chart_rows["geo_id"] = chart_rows["sector_id"]
    chart_rows["geo_name"] = chart_rows["sector_label"]
    chart_rows["metric_id"] = chart_rows["basis"].map(
        {
            "employment_share": BASIS_CONFIG["employment_share"].chart_metric_id,
            "gdp_share": BASIS_CONFIG["gdp_share"].chart_metric_id,
        }
    )
    chart_rows["metric_label"] = chart_rows["basis"].map(
        {
            "employment_share": BASIS_CONFIG["employment_share"].chart_metric_label,
            "gdp_share": BASIS_CONFIG["gdp_share"].chart_metric_label,
        }
    )
    chart_rows["metric_value"] = chart_rows["share_value"]
    chart_rows["period"] = chart_rows["year"].astype(str)
    chart_rows["group"] = chart_rows["source_label"] + " | " + chart_rows["vintage_note"]
    chart_rows["source"] = chart_rows["source_label"]
    chart_rows["vintage"] = chart_rows["vintage_note"]
    chart_rows["highlight_flag"] = chart_rows["sector_id"].isin(highlight_sectors)
    chart_rows["peer_flag"] = False
    chart_rows["note"] = chart_rows["source_label"]
    return chart_rows[
        [
            "geo_level",
            "geo_id",
            "geo_name",
            "period",
            "metric_id",
            "metric_label",
            "metric_value",
            "source",
            "vintage",
            "group",
            "highlight_flag",
            "peer_flag",
            "note",
        ]
    ].rename(columns={"geo_name": "geo_name"})


def build_current_mix_chart(surface: pd.DataFrame, basis: str, year: int | None = None):
    """Render the D1 stacked current-mix chart with the shared chart engine."""
    basis_rows = get_basis_slice(surface, basis)
    return build_current_mix_chart_for_basis_rows(basis_rows, year)


def build_current_mix_chart_for_basis_rows(basis_rows: pd.DataFrame, year: int | None = None):
    """Render the D1 stacked current-mix chart for one basis data frame."""
    chart_data = prepare_current_mix_chart_data_for_basis_rows(basis_rows, year)
    if chart_data.empty:
        return None

    subtitle = (
        f"{chart_data['metric_label'].iloc[0]} | {int(chart_data['year'].iloc[0])} | "
        f"{chart_data['vintage_note'].iloc[0]}"
    )
    request = ChartRequest(
        data=chart_data,
        chart_type="bar_chart",
        theme=Theme.default(),
        column_mapping={
            "entity": "entity",
            "value": "value",
            "series": "series",
            "share_value": "share_value",
            "metric_label": "metric_label",
            "time_window": "time_window",
            "group": "group",
            "source": "source",
            "vintage": "vintage",
            "raw_value": "raw_value",
            "raw_value_label": "raw_value_label",
        },
        field_values={"variant": "stacked_100"},
        title=get_basis_title_for_rows(basis_rows),
        subtitle=subtitle,
        number_format=NumberFormat(unit="percent", decimals=1),
    )
    return render(request)


def build_change_chart(surface: pd.DataFrame, basis: str):
    """Render the D1 bump chart when enough history is available."""
    basis_rows = get_basis_slice(surface, basis)
    return build_change_chart_for_basis_rows(basis_rows)


def build_change_chart_for_basis_rows(basis_rows: pd.DataFrame):
    """Render the D1 bump chart when enough history is available."""
    if not has_sufficient_bump_history_for_basis_rows(basis_rows):
        return None

    chart_data = prepare_change_chart_data_for_basis_rows(basis_rows)
    if chart_data.empty:
        return None

    request = ChartRequest(
        data=chart_data,
        chart_type="bump_chart",
        theme=Theme.default(),
        column_mapping={
            "geo_level": "geo_level",
            "geo_id": "geo_id",
            "geo_name": "geo_name",
            "period": "period",
            "metric_id": "metric_id",
            "metric_label": "metric_label",
            "metric_value": "metric_value",
            "source": "source",
            "vintage": "vintage",
            "group": "group",
            "highlight_flag": "highlight_flag",
            "peer_flag": "peer_flag",
            "note": "note",
        },
        field_values={
            "entity_strategy": "all",
            "label_mode": "highlight_end",
            "show_points": True,
            "include_highlighted": True,
        },
        title=f"{get_basis_title_for_rows(basis_rows)} rank change",
        subtitle=f"{chart_data['metric_label'].iloc[0]} rank by year | {chart_data['vintage'].iloc[0]}",
        number_format=NumberFormat(unit="percent", decimals=1),
    )
    return render(request)


def build_benchmark_table_for_basis_rows(
    market_rows: pd.DataFrame,
    benchmark_rows: dict[str, pd.DataFrame],
    year: int,
) -> pd.DataFrame:
    """Build a comparison table for market vs US and division shares in a selected year."""
    selected_market = market_rows[market_rows["year"] == int(year)][["sector_id", "sector_label", "share_value"]].rename(
        columns={"share_value": "market_share"}
    )
    if selected_market.empty:
        return pd.DataFrame()

    out = selected_market.copy()
    for benchmark_key, label in [("us", "us"), ("division", "division")]:
        rows = benchmark_rows.get(benchmark_key, pd.DataFrame())
        if rows.empty:
            out[f"{label}_share"] = pd.NA
            out[f"{label}_delta"] = pd.NA
            continue
        selected_benchmark = rows[rows["year"] == int(year)][["sector_id", "share_value"]].rename(
            columns={"share_value": f"{label}_share"}
        )
        out = out.merge(selected_benchmark, on="sector_id", how="left")
        out[f"{label}_delta"] = out["market_share"] - out[f"{label}_share"]

    return out.sort_values(["market_share", "sector_label"], ascending=[False, True], kind="mergesort").reset_index(drop=True)


def _get_latest_lq_year(market_rows: pd.DataFrame) -> int | None:
    """Return the latest year with at least one usable D1 LQ value."""
    lq_columns = [f"lq_{sector_id}" for sector_id, _ in EMPLOYMENT_SECTORS]
    if market_rows.empty:
        return None

    lq_counts = market_rows[lq_columns].notna().sum(axis=1)
    usable_years = market_rows.loc[lq_counts > 0, "year"]
    if usable_years.empty:
        return None
    return int(usable_years.max())


def _get_latest_qcew_growth_year_pair(market_rows: pd.DataFrame) -> tuple[int, int] | None:
    """Return the latest comparable QCEW year pair for sector growth when it exists."""
    raw_columns = [
        f"{BASIS_CONFIG['employment_share'].raw_prefix}{sector_id}"
        for sector_id, _ in EMPLOYMENT_SECTORS
    ]
    if market_rows.empty:
        return None

    present_counts = market_rows[raw_columns].notna().sum(axis=1)
    comparable_years = market_rows.loc[
        market_rows["qcew_private_emp_total"].notna() & (present_counts >= MIN_REQUIRED_SECTORS),
        "year",
    ].dropna()
    comparable_years = sorted(int(year) for year in comparable_years.unique().tolist())
    if len(comparable_years) < 2:
        return None
    return comparable_years[-2], comparable_years[-1]


def build_d1_specialization_payload_from_market_rows(
    market_rows: pd.DataFrame,
    market_id: str = DEFAULT_MARKET_ID,
) -> dict[str, object]:
    """Build the D1 specialization companion payload from one market's Gold rows."""
    empty_rows = pd.DataFrame(
        columns=[
            "sector_id",
            "sector_label",
            "lq_value",
            "latest_employment",
            "latest_share",
            "growth_value",
            "specialization_label",
            "growth_label",
            "latest_employment_label",
        ]
    )
    if market_rows.empty:
        return {
            "mode": "empty",
            "rows": empty_rows,
            "latest_lq_year": None,
            "growth_year_start": None,
            "growth_year_end": None,
            "source_label": "QCEW private employment specialization",
            "summary": None,
            "note": "No QCEW specialization rows were available for this market.",
        }

    latest_lq_year = _get_latest_lq_year(market_rows)
    if latest_lq_year is None:
        return {
            "mode": "empty",
            "rows": empty_rows,
            "latest_lq_year": None,
            "growth_year_start": None,
            "growth_year_end": None,
            "source_label": "QCEW private employment specialization",
            "summary": None,
            "note": "No latest-year location quotient rows were available for this market.",
        }

    latest_row = market_rows[market_rows["year"] == latest_lq_year].copy()
    if latest_row.empty:
        return {
            "mode": "empty",
            "rows": empty_rows,
            "latest_lq_year": latest_lq_year,
            "growth_year_start": None,
            "growth_year_end": None,
            "source_label": "QCEW private employment specialization",
            "summary": None,
            "note": "No latest-year location quotient rows were available for this market.",
        }

    latest_row = latest_row.iloc[0]
    employment_key = _employment_basis_key(market_rows)
    employment_rows = _build_basis_rows(market_rows, market_id, employment_key)
    current_share_lookup = {}
    if not employment_rows.empty:
        latest_share_year = get_latest_year_for_basis_rows(employment_rows)
        if latest_share_year is not None:
            current_share_lookup = (
                employment_rows[employment_rows["year"] == latest_share_year]
                .set_index("sector_id")["share_value"]
                .to_dict()
            )

    growth_pair = _get_latest_qcew_growth_year_pair(market_rows)
    growth_lookup: dict[str, float | None] = {}
    growth_year_start = None
    growth_year_end = None
    if growth_pair is not None:
        growth_year_start, growth_year_end = growth_pair
        growth_start = market_rows[market_rows["year"] == growth_year_start]
        growth_end = market_rows[market_rows["year"] == growth_year_end]
        if not growth_start.empty and not growth_end.empty:
            growth_start_row = growth_start.iloc[0]
            growth_end_row = growth_end.iloc[0]
            for sector_id, _ in EMPLOYMENT_SECTORS:
                raw_column = f"{BASIS_CONFIG['employment_share'].raw_prefix}{sector_id}"
                start_value = pd.to_numeric(growth_start_row.get(raw_column), errors="coerce")
                end_value = pd.to_numeric(growth_end_row.get(raw_column), errors="coerce")
                if pd.isna(start_value) or pd.isna(end_value) or float(start_value) <= 0:
                    growth_lookup[sector_id] = None
                else:
                    growth_lookup[sector_id] = (float(end_value) / float(start_value)) - 1.0

    sector_rows: list[dict[str, object]] = []
    for sector_id, sector_label in EMPLOYMENT_SECTORS:
        lq_value = pd.to_numeric(latest_row.get(f"lq_{sector_id}"), errors="coerce")
        latest_employment = pd.to_numeric(
            latest_row.get(f"{BASIS_CONFIG['employment_share'].raw_prefix}{sector_id}"),
            errors="coerce",
        )
        if pd.isna(lq_value):
            continue

        growth_value = growth_lookup.get(sector_id)
        sector_rows.append(
            {
                "sector_id": sector_id,
                "sector_label": sector_label,
                "lq_value": float(lq_value),
                "latest_employment": None if pd.isna(latest_employment) else float(latest_employment),
                "latest_share": current_share_lookup.get(sector_id),
                "growth_value": growth_value,
            }
        )

    rows = pd.DataFrame(sector_rows)
    if rows.empty:
        return {
            "mode": "empty",
            "rows": empty_rows,
            "latest_lq_year": latest_lq_year,
            "growth_year_start": growth_year_start,
            "growth_year_end": growth_year_end,
            "source_label": "QCEW private employment specialization",
            "summary": None,
            "note": "No usable specialization sectors were returned for this market.",
        }

    # Keep the specialization read editorially simple: first-pass labels highlight
    # what is overrepresented, underrepresented, gaining, or shrinking.
    rows["specialization_label"] = rows["lq_value"].map(
        lambda value: "Specialized" if pd.notna(value) and float(value) >= 1.0 else "Below US mix"
    )
    rows["growth_label"] = rows["growth_value"].map(
        lambda value: "Growing" if pd.notna(value) and float(value) >= 0 else "Shrinking"
    )
    rows["latest_employment_label"] = rows["latest_employment"].map(_safe_count)

    has_growth = rows["growth_value"].notna().any() and growth_year_start is not None and growth_year_end is not None
    if has_growth:
        rows = rows.sort_values(
            ["lq_value", "growth_value", "sector_label"],
            ascending=[False, False, True],
            kind="mergesort",
            na_position="last",
        ).reset_index(drop=True)
        intersection = rows[(rows["lq_value"] >= 1.0) & (rows["growth_value"] >= 0)]
        lead_row = intersection.iloc[0] if not intersection.empty else rows.iloc[0]
        summary = (
            f"{lead_row['sector_label']} stands out as a specialized sector in {latest_lq_year} "
            f"and posted {lead_row['growth_value']:+.1%} employment growth from "
            f"{growth_year_start} to {growth_year_end}."
        )
        note = (
            f"Location quotient uses {latest_lq_year} QCEW private employment. "
            f"Growth compares the latest comparable QCEW pair: {growth_year_start} to {growth_year_end}."
        )
        mode = "scatter"
    else:
        rows = rows.sort_values(
            ["lq_value", "latest_share", "sector_label"],
            ascending=[False, False, True],
            kind="mergesort",
            na_position="last",
        ).head(D1_SPECIALIZATION_TOP_SECTORS).reset_index(drop=True)
        lead_row = rows.iloc[0]
        summary = (
            f"{lead_row['sector_label']} is the clearest specialized sector in {latest_lq_year}, "
            "but the latest comparable QCEW growth pair is unavailable."
        )
        note = (
            f"Location quotient uses {latest_lq_year} QCEW private employment. "
            "Recent QCEW growth could not be computed from the latest comparable year pair, "
            "so this view falls back to a ranked specialization table."
        )
        mode = "table"

    return {
        "mode": mode,
        "rows": rows,
        "latest_lq_year": latest_lq_year,
        "growth_year_start": growth_year_start,
        "growth_year_end": growth_year_end,
        "source_label": "QCEW private employment specialization",
        "summary": summary,
        "note": note,
    }


def get_d1_specialization_payload(market_id: str = DEFAULT_MARKET_ID) -> dict[str, object]:
    """Return the market-scoped D1 specialization companion payload."""
    market_rows = get_market_surface(market_id)
    return build_d1_specialization_payload_from_market_rows(market_rows, market_id=market_id)


def _build_basis_rows_for_market_and_basis(market_rows: pd.DataFrame, market_id: str, basis: str) -> pd.DataFrame:
    """Build one market's normalized D1/D5 basis rows without re-querying DuckDB."""
    employment_key = _employment_basis_key(market_rows)
    employment_preview = _build_basis_rows(market_rows, market_id, employment_key)
    gdp_preview = _build_basis_rows(market_rows, market_id, "gdp_share")

    employment_latest = int(employment_preview["latest_available_year_for_basis"].iloc[0]) if not employment_preview.empty else None
    gdp_latest = int(gdp_preview["latest_available_year_for_basis"].iloc[0]) if not gdp_preview.empty else None

    if basis == "employment_share":
        return _build_basis_rows(market_rows, market_id, employment_key, gdp_latest)
    if basis == "gdp_share":
        return _build_basis_rows(market_rows, market_id, "gdp_share", employment_latest)
    raise ValueError(f"Unsupported basis: {basis}")


def get_basis_rows_for_markets(market_ids: Iterable[str], basis: str) -> pd.DataFrame:
    """Return one normalized basis surface for the requested market ids."""
    market_id_list = [str(market_id) for market_id in market_ids if str(market_id)]
    if not market_id_list:
        return pd.DataFrame()

    all_rows = get_market_surfaces(market_id_list)
    if all_rows.empty:
        return pd.DataFrame()

    parts: list[pd.DataFrame] = []
    for market_id in market_id_list:
        market_rows = all_rows[all_rows["geo_id"] == str(market_id)].copy()
        if market_rows.empty:
            continue
        parts.append(_build_basis_rows_for_market_and_basis(market_rows, market_id, basis))

    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def _format_signed_jobs_count(value: float | int | None) -> str:
    """Format net jobs counts with an explicit sign for D5 benchmark tables."""
    if value is None or pd.isna(value):
        return "—"
    numeric = int(round(float(value)))
    return f"{numeric:+,}"


def get_d5_peer_defaults(market_id: str = DEFAULT_MARKET_ID, peer_count: int = D5_DEFAULT_PEER_COUNT) -> pd.DataFrame:
    """Resolve the default peer set from the Cross-Frame Intelligence similarity bundle."""
    con = get_connection()
    try:
        row = con.execute(
            _read_sql_file("d5_cross_frame_peers.sql"),
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()

    if row.empty:
        return pd.DataFrame(columns=["peer_rank", "peer_market_id", "peer_geo_name", "similarity"])

    record = row.iloc[0]
    peers: list[dict[str, object]] = []
    for rank in range(1, 11):
        peer_code = record.get(f"top10_peer_{rank}_cbsa_code")
        peer_name = record.get(f"top10_peer_{rank}_cbsa_name")
        peer_similarity = record.get(f"top10_peer_{rank}_similarity")
        if pd.isna(peer_code):
            continue
        peers.append(
            {
                "peer_rank": rank,
                "peer_market_id": str(peer_code),
                "peer_geo_name": str(peer_name) if pd.notna(peer_name) else str(peer_code),
                "similarity": pd.to_numeric(peer_similarity, errors="coerce"),
            }
        )

    peer_rows = pd.DataFrame(peers)
    if peer_rows.empty:
        return peer_rows
    return peer_rows.head(int(peer_count)).reset_index(drop=True)


def _resolve_d5_peer_rows(
    market_id: str,
    peer_market_ids: Iterable[str] | None = None,
    peer_count: int = D5_DEFAULT_PEER_COUNT,
) -> pd.DataFrame:
    """Return the selected peer rows, defaulting to the top Cross-Frame peers."""
    default_rows = get_d5_peer_defaults(market_id, 10)
    if peer_market_ids is None:
        return default_rows.head(int(peer_count)).reset_index(drop=True)

    selected_ids = [str(peer_market_id) for peer_market_id in peer_market_ids if str(peer_market_id)]
    if not selected_ids:
        return default_rows.head(int(peer_count)).reset_index(drop=True)

    selected = default_rows[default_rows["peer_market_id"].isin(selected_ids)].copy()
    if selected.empty:
        return pd.DataFrame(columns=default_rows.columns)
    return selected.sort_values("peer_rank", kind="mergesort").reset_index(drop=True)


def get_d5_mix_comparison_payload(
    market_id: str = DEFAULT_MARKET_ID,
    basis: str = "employment_share",
    peer_market_ids: Iterable[str] | None = None,
) -> dict[str, object]:
    """Build the D5 industry or GDP peer-comparison surface for one basis."""
    peer_rows = _resolve_d5_peer_rows(market_id, peer_market_ids)
    selected_peer_ids = peer_rows["peer_market_id"].tolist()
    market_and_peer_ids = [str(market_id), *selected_peer_ids]

    basis_rows = get_basis_rows_for_markets(market_and_peer_ids, basis)
    if basis_rows.empty:
        return {
            "basis": basis,
            "basis_rows": pd.DataFrame(),
            "chart_rows": pd.DataFrame(),
            "benchmark_rows": {},
            "selected_year": None,
            "peer_rows": peer_rows,
            "notes": ["No industry/GDP mix rows were returned for the selected market and peers."],
        }

    market_basis_rows = basis_rows[basis_rows["market_id"] == str(market_id)].copy()
    selected_year = get_latest_year_for_basis_rows(market_basis_rows)
    benchmark_rows = get_benchmark_basis_frames(market_id)[basis]

    chart_parts: list[pd.DataFrame] = []
    entity_rows: list[dict[str, object]] = []
    order_counter = 1
    for entity_type, entity_id, entity_label, entity_rank in [
        ("market", str(market_id), market_basis_rows["geo_name"].iloc[0] if not market_basis_rows.empty else str(market_id), 0),
        *[
            ("peer", peer["peer_market_id"], peer["peer_geo_name"], int(peer["peer_rank"]))
            for _, peer in peer_rows.iterrows()
        ],
    ]:
        entity_basis_rows = basis_rows[basis_rows["market_id"] == str(entity_id)].copy()
        if entity_basis_rows.empty or selected_year is None:
            continue
        selected_rows = prepare_current_mix_chart_data_for_basis_rows(entity_basis_rows, selected_year)
        if selected_rows.empty:
            continue
        selected_rows["entity_type"] = entity_type
        selected_rows["entity_rank"] = entity_rank
        selected_rows["entity_order"] = order_counter
        selected_rows["entity"] = entity_label
        chart_parts.append(selected_rows)
        entity_rows.append(
            {
                "entity": entity_label,
                "entity_type": entity_type,
                "entity_rank": entity_rank,
                "entity_order": order_counter,
            }
        )
        order_counter += 1

    for benchmark_key in ["division", "us"]:
        rows = benchmark_rows.get(benchmark_key, pd.DataFrame())
        if rows.empty or selected_year is None:
            continue
        selected_rows = prepare_current_mix_chart_data_for_basis_rows(rows, selected_year)
        if selected_rows.empty:
            continue
        selected_rows["entity_type"] = "benchmark"
        selected_rows["entity_rank"] = 100 if benchmark_key == "division" else 101
        selected_rows["entity_order"] = order_counter
        chart_parts.append(selected_rows)
        entity_rows.append(
            {
                "entity": str(selected_rows["entity"].iloc[0]),
                "entity_type": "benchmark",
                "entity_rank": 100 if benchmark_key == "division" else 101,
                "entity_order": order_counter,
            }
        )
        order_counter += 1

    chart_rows = pd.concat(chart_parts, ignore_index=True) if chart_parts else pd.DataFrame()
    entity_frame = pd.DataFrame(entity_rows)
    notes = []
    if selected_year is not None:
        notes.append(
            f"{market_basis_rows['basis_label'].iloc[0]} panel uses {selected_year}, the latest year available for {market_basis_rows['geo_name'].iloc[0]}."
        )
    if not benchmark_rows.get("us", pd.DataFrame()).empty:
        notes.append("U.S. and division benchmark rows are first-pass derived from state rows rather than read as native Gold benchmark rows.")

    return {
        "basis": basis,
        "basis_rows": basis_rows,
        "market_rows": market_basis_rows,
        "chart_rows": chart_rows.sort_values(["entity_order", "display_order"], kind="mergesort") if not chart_rows.empty else chart_rows,
        "benchmark_rows": benchmark_rows,
        "selected_year": selected_year,
        "peer_rows": peer_rows,
        "entity_frame": entity_frame,
        "notes": notes,
    }


def build_d5_mix_chart(chart_rows: pd.DataFrame, title: str, subtitle: str):
    """Render the D5 peer-comparison stacked bar chart."""
    if chart_rows.empty:
        return None

    request = ChartRequest(
        data=chart_rows,
        chart_type="bar_chart",
        theme=Theme.default(),
        column_mapping={
            "entity": "entity",
            "value": "value",
            "series": "series",
            "share_value": "share_value",
            "metric_label": "metric_label",
            "time_window": "time_window",
            "group": "group",
            "source": "source",
            "vintage": "vintage",
            "raw_value": "raw_value",
            "raw_value_label": "raw_value_label",
        },
        field_values={"variant": "stacked_100"},
        title=title,
        subtitle=subtitle,
        number_format=NumberFormat(unit="percent", decimals=1),
    )
    return render(request)


def get_d5_lodes_benchmark_surface(
    market_id: str = DEFAULT_MARKET_ID,
    peer_market_ids: Iterable[str] | None = None,
) -> dict[str, object]:
    """Build the D5 jobs-to-workers benchmark surface for the market, peers, division, and U.S."""
    peer_rows = _resolve_d5_peer_rows(market_id, peer_market_ids)
    selected_peer_ids = peer_rows["peer_market_id"].tolist()
    context = get_market_context(market_id)
    division_id = context.get("division_id")

    market_and_peer_ids = [str(market_id), *selected_peer_ids]
    placeholders = ", ".join(["?"] * len(market_and_peer_ids))

    con = get_connection()
    try:
        cbsa_rows = con.execute(
            f"""
            SELECT
                geo_id AS market_id,
                geo_name,
                year,
                jobs_total,
                workers_total,
                jobs_minus_workers,
                jobs_to_workers_ratio
            FROM patterns_in_place.gold.economics_lodes_wide
            WHERE geo_level = 'cbsa'
              AND geo_id IN ({placeholders})
            ORDER BY geo_id, year
            """,
            market_and_peer_ids,
        ).fetchdf()
        benchmark_rows = con.execute(
            _read_sql_file("d5_lodes_benchmarks.sql"),
            [division_id],
        ).fetchdf()
    finally:
        con.close()

    market_rows = cbsa_rows[cbsa_rows["market_id"] == str(market_id)].copy()
    if market_rows.empty:
        return {
            "rows": pd.DataFrame(),
            "selected_year": None,
            "peer_rows": peer_rows,
            "notes": ["No D5 LODES benchmark rows were returned for the selected market."],
        }

    selected_year = int(market_rows["year"].max())
    market_rows = market_rows[market_rows["year"] == selected_year].copy()
    peer_metric_rows = cbsa_rows[
        (cbsa_rows["market_id"].isin(selected_peer_ids))
        & (cbsa_rows["year"] == selected_year)
    ].copy()

    peer_metric_rows = peer_metric_rows.merge(
        peer_rows[["peer_market_id", "peer_rank", "peer_geo_name", "similarity"]],
        left_on="market_id",
        right_on="peer_market_id",
        how="left",
    )
    peer_metric_rows["entity"] = peer_metric_rows["peer_geo_name"].fillna(peer_metric_rows["geo_name"])
    peer_metric_rows["entity_type"] = "peer"
    peer_metric_rows["entity_order"] = peer_metric_rows["peer_rank"].fillna(99).astype(int) + 1

    market_rows["entity"] = market_rows["geo_name"]
    market_rows["entity_type"] = "market"
    market_rows["entity_order"] = 1

    selected_benchmarks = benchmark_rows[benchmark_rows["year"] == selected_year].copy()
    selected_benchmarks["entity"] = selected_benchmarks["benchmark_geo_name"]
    selected_benchmarks["entity_type"] = "benchmark"
    selected_benchmarks["entity_order"] = selected_benchmarks["benchmark_scope"].map({"division": 98, "us": 99})
    selected_benchmarks = selected_benchmarks.rename(columns={"benchmark_geo_id": "market_id", "benchmark_geo_name": "geo_name"})

    keep_columns = [
        "market_id",
        "geo_name",
        "entity",
        "entity_type",
        "entity_order",
        "year",
        "jobs_total",
        "workers_total",
        "jobs_minus_workers",
        "jobs_to_workers_ratio",
    ]
    concat_frames = [
        frame[keep_columns]
        for frame in [market_rows, peer_metric_rows, selected_benchmarks]
        if not frame.empty
    ]
    combined = pd.concat(concat_frames, ignore_index=True)
    combined["jobs_to_workers_ratio_label"] = combined["jobs_to_workers_ratio"].apply(
        lambda value: "—" if pd.isna(value) else f"{float(value):.2f}x"
    )
    combined["jobs_minus_workers_label"] = combined["jobs_minus_workers"].apply(_format_signed_jobs_count)
    combined["jobs_total_label"] = combined["jobs_total"].apply(lambda value: "—" if pd.isna(value) else f"{int(round(float(value))):,}")
    combined["workers_total_label"] = combined["workers_total"].apply(lambda value: "—" if pd.isna(value) else f"{int(round(float(value))):,}")
    combined = combined.sort_values(["entity_order", "entity"], kind="mergesort").reset_index(drop=True)

    notes = [
        f"LODES benchmark panel uses {selected_year}, the latest year available for {market_rows['geo_name'].iloc[0]}.",
        "Division is read from the governed LODES surface; U.S. is first-pass derived from state rows.",
    ]
    return {
        "rows": combined,
        "selected_year": selected_year,
        "peer_rows": peer_rows,
        "notes": notes,
    }


def get_d5_takeaway(
    market_id: str = DEFAULT_MARKET_ID,
    basis: str = "employment_share",
    peer_market_ids: Iterable[str] | None = None,
) -> str | None:
    """Build a short regional-fit synthesis from the D5 mix and LODES benchmark panels."""
    mix_payload = get_d5_mix_comparison_payload(market_id, basis, peer_market_ids)
    lodes_payload = get_d5_lodes_benchmark_surface(market_id, peer_market_ids)

    chart_rows = mix_payload["chart_rows"]
    lodes_rows = lodes_payload["rows"]
    if chart_rows.empty or lodes_rows.empty:
        return None

    market_name = str(lodes_rows[lodes_rows["entity_type"] == "market"]["entity"].iloc[0])
    selected_year = mix_payload["selected_year"]
    lodes_year = lodes_payload["selected_year"]

    market_sector = chart_rows[chart_rows["entity_type"] == "market"][["series", "share_value"]].rename(
        columns={"share_value": "market_share"}
    )
    peer_sector = chart_rows[chart_rows["entity_type"] == "peer"][["series", "share_value"]]
    if market_sector.empty or peer_sector.empty:
        return None

    peer_avg = peer_sector.groupby("series", as_index=False)["share_value"].mean().rename(columns={"share_value": "peer_avg_share"})
    sector_delta = market_sector.merge(peer_avg, on="series", how="inner")
    if sector_delta.empty:
        return None
    sector_delta["share_delta"] = sector_delta["market_share"] - sector_delta["peer_avg_share"]
    top_sector = sector_delta.sort_values(["share_delta", "series"], ascending=[False, True], kind="mergesort").iloc[0]

    ratio_rows = lodes_rows[lodes_rows["entity_type"].isin(["market", "peer"])].dropna(subset=["jobs_to_workers_ratio"]).copy()
    if ratio_rows.empty:
        return None
    ratio_rows = ratio_rows.sort_values(["jobs_to_workers_ratio", "entity"], ascending=[False, True], kind="mergesort").reset_index(drop=True)
    market_rank = int(ratio_rows.index[ratio_rows["entity_type"] == "market"][0]) + 1
    compared_count = int(len(ratio_rows))

    return (
        f"In {selected_year}, {market_name} ran most above its selected-peer average in {top_sector['series']} "
        f"({top_sector['share_delta']:+.1%} share difference). In {lodes_year}, its jobs-to-workers ratio ranked "
        f"{market_rank} of {compared_count} across the selected peer set."
    )


def get_d5_page_payload(
    market_id: str = DEFAULT_MARKET_ID,
    basis: str = "employment_share",
    peer_market_ids: Iterable[str] | None = None,
) -> dict[str, object]:
    """Bundle the D5 page payload so the Streamlit page can stay presentation-focused."""
    mix_payload = get_d5_mix_comparison_payload(market_id, basis, peer_market_ids)
    lodes_payload = get_d5_lodes_benchmark_surface(market_id, peer_market_ids)
    selected_peer_rows = _resolve_d5_peer_rows(market_id, peer_market_ids)

    basis_label = "Employment share" if basis == "employment_share" else "GDP share"
    mix_year = mix_payload.get("selected_year")
    lodes_year = lodes_payload.get("selected_year")
    mix_title = f"D5 — {basis_label} vs peers"
    mix_subtitle = (
        f"{basis_label} | {mix_year} | Market, selected peers, division, and U.S."
        if mix_year is not None
        else f"{basis_label} comparison unavailable"
    )

    return {
        "basis": basis,
        "peer_rows": selected_peer_rows,
        "available_peer_rows": get_d5_peer_defaults(market_id, 10),
        "mix_payload": mix_payload,
        "lodes_payload": lodes_payload,
        "takeaway": get_d5_takeaway(market_id, basis, selected_peer_rows["peer_market_id"].tolist()),
        "mix_title": mix_title,
        "mix_subtitle": mix_subtitle,
        "lodes_title": "D5 — Jobs-to-workers benchmark",
        "lodes_subtitle": (
            f"Jobs-to-workers ratio | {lodes_year} | Market, selected peers, division, and U.S."
            if lodes_year is not None
            else "Jobs-to-workers benchmark unavailable"
        ),
    }


def _get_d6_sector_context(market_id: str, year: int) -> pd.DataFrame:
    """Pull the broad-sector D1 context we want to pair with the detailed Felten join."""
    market_rows = get_market_surface(market_id)
    if market_rows.empty:
        return pd.DataFrame(
            columns=[
                "sector_id",
                "sector_label",
                "employment_share",
                "sector_employment",
                "lq_value",
                "growth_value",
            ]
        )

    selected_rows = market_rows[market_rows["year"] == int(year)]
    if selected_rows.empty:
        selected_rows = market_rows[market_rows["year"] == market_rows["year"].max()]
    if selected_rows.empty:
        return pd.DataFrame()

    selected_row = selected_rows.iloc[0]
    specialization_payload = build_d1_specialization_payload_from_market_rows(market_rows, market_id=market_id)
    growth_lookup = {}
    if not specialization_payload["rows"].empty:
        growth_lookup = specialization_payload["rows"].set_index("sector_id")["growth_value"].to_dict()

    records: list[dict[str, object]] = []
    for sector_id, sector_label in EMPLOYMENT_SECTORS:
        records.append(
            {
                "sector_id": sector_id,
                "sector_label": sector_label,
                "employment_share": pd.to_numeric(selected_row.get(f"pct_qcew_private_emp_{sector_id}"), errors="coerce"),
                "sector_employment": pd.to_numeric(selected_row.get(f"qcew_private_emp_{sector_id}"), errors="coerce"),
                "lq_value": pd.to_numeric(selected_row.get(f"lq_{sector_id}"), errors="coerce"),
                "growth_value": growth_lookup.get(sector_id),
            }
        )
    return pd.DataFrame.from_records(records)


def get_d6_sector_scorecard_payload(
    market_id: str = DEFAULT_MARKET_ID,
    year: int = D6_SECTOR_TARGET_YEAR,
) -> dict[str, object]:
    """Build the D6 sector scorecard from detailed 4-digit NAICS rows plus broad D1 context.

    The repo's curated Silver QCEW table intentionally narrows to broad sector
    families, so D6 reaches down to staging county rows and rolls them back to
    CBSA using the governed county crosswalk. That keeps the Felten join at the
    right 4-digit grain without forcing a wider platform contract first.
    """
    appendix_b = get_felten_appendix_b()
    final_crosswalk = get_felten_naics_crosswalk_final()
    if appendix_b.empty:
        return {
            "selected_year": int(year),
            "market_name": str(market_id),
            "scorecard_rows": pd.DataFrame(),
            "detail_rows": pd.DataFrame(),
            "coverage": {},
            "notes": [
                f"Felten Appendix B was not available at `{FELTEN_WORKBOOK_PATH.relative_to(REPO_ROOT)}`.",
                f"Download source: {FELTEN_WORKBOOK_URL}",
            ],
            "summary": None,
        }

    con = get_connection()
    try:
        detail_rows = con.execute(
            """
            SELECT
                x.cbsa_code AS market_id,
                x.cbsa_name AS geo_name,
                c.period AS year,
                c.industry_code AS industry_code,
                c.industry_title AS industry_title,
                SUM(c.annual_avg_emplvl) AS annual_avg_emplvl
            FROM staging.bls_qcew_county c
            INNER JOIN silver.xwalk_cbsa_county x
                ON c.county_fips_code = x.county_fips
            INNER JOIN silver.bls_qcew_industry_map m
                ON c.industry_code = m.industry_code
            WHERE x.cbsa_code = ?
              AND c.period = ?
              AND c.own_code = '5'
              AND m.code_type = 'naics_industry_group'
            GROUP BY 1, 2, 3, 4, 5
            ORDER BY annual_avg_emplvl DESC, industry_code
            """,
            [str(market_id), int(year)],
        ).fetchdf()
    finally:
        con.close()

    if detail_rows.empty:
        return {
            "selected_year": int(year),
            "market_name": str(market_id),
            "scorecard_rows": pd.DataFrame(),
            "detail_rows": pd.DataFrame(),
            "coverage": {},
            "notes": [f"No 4-digit QCEW industry-group rows were available for market {market_id} in {year}."],
            "summary": None,
        }

    if final_crosswalk.empty:
        detail_rows["felten_industry_code"] = detail_rows["industry_code"].map(_get_felten_industry_join_code)
        detail_rows = detail_rows.merge(
            appendix_b.rename(columns={"industry_code": "felten_industry_code"}),
            on="felten_industry_code",
            how="left",
        )
        detail_rows["match_basis"] = pd.NA
        detail_rows["manual_notes"] = pd.NA
        coverage_note_suffix = "after a small NAICS-vintage fallback map for known code revisions and aggregate appendix rows."
    else:
        detail_rows = detail_rows.merge(
            final_crosswalk.rename(
                columns={
                    "our_naics_code": "industry_code",
                    "felten_naics_code": "felten_industry_code",
                    "felten_naics_name": "industry_title_felten",
                    "felten_score": "aiie_score",
                }
            ),
            on="industry_code",
            how="left",
        )
        coverage_note_suffix = "after applying the final reviewed NAICS crosswalk."
    detail_rows["sector_id"] = detail_rows["industry_code"].map(_map_naics4_to_d1_sector)
    detail_rows["sector_label"] = detail_rows["sector_id"].map(_sector_label_lookup())
    detail_rows["employment_share_of_detail"] = detail_rows["annual_avg_emplvl"] / detail_rows["annual_avg_emplvl"].sum()
    detail_rows["matched_flag"] = detail_rows["aiie_score"].notna()

    sector_context = _get_d6_sector_context(market_id, year)
    sector_rollup = (
        detail_rows.dropna(subset=["sector_id"])
        .groupby(["sector_id", "sector_label"], as_index=False)
        .agg(
            detailed_employment=("annual_avg_emplvl", "sum"),
            matched_employment=("annual_avg_emplvl", lambda values: float(detail_rows.loc[values.index, "annual_avg_emplvl"][detail_rows.loc[values.index, "matched_flag"]].sum())),
        )
    )

    weighted_rows = detail_rows.dropna(subset=["sector_id", "aiie_score"]).copy()
    if weighted_rows.empty:
        scorecard_rows = sector_context.copy()
        scorecard_rows["ai_exposure_score"] = pd.NA
        scorecard_rows["detailed_employment"] = pd.NA
        scorecard_rows["matched_employment"] = pd.NA
        scorecard_rows["match_rate"] = pd.NA
    else:
        weighted_rows["weighted_aiie"] = weighted_rows["annual_avg_emplvl"] * weighted_rows["aiie_score"]
        weighted_sector = weighted_rows.groupby("sector_id", as_index=False).agg(
            matched_employment=("annual_avg_emplvl", "sum"),
            weighted_aiie=("weighted_aiie", "sum"),
        )
        weighted_sector["ai_exposure_score"] = weighted_sector["weighted_aiie"] / weighted_sector["matched_employment"]
        scorecard_rows = sector_context.merge(sector_rollup, on=["sector_id", "sector_label"], how="left")
        scorecard_rows = scorecard_rows.merge(
            weighted_sector[["sector_id", "matched_employment", "ai_exposure_score"]],
            on="sector_id",
            how="left",
            suffixes=("", "_weighted"),
        )
        if "matched_employment_weighted" in scorecard_rows.columns:
            scorecard_rows["matched_employment"] = scorecard_rows["matched_employment_weighted"].combine_first(scorecard_rows["matched_employment"])
            scorecard_rows = scorecard_rows.drop(columns=["matched_employment_weighted"])

    scorecard_rows["match_rate"] = scorecard_rows["matched_employment"] / scorecard_rows["detailed_employment"]
    scorecard_rows["exposure_footprint"] = scorecard_rows["employment_share"] * scorecard_rows["ai_exposure_score"].clip(lower=0)
    scorecard_rows = scorecard_rows.sort_values(
        ["exposure_footprint", "ai_exposure_score", "employment_share"],
        ascending=[False, False, False],
        kind="mergesort",
        na_position="last",
    ).reset_index(drop=True)

    detail_rows["share_within_sector"] = detail_rows.groupby("sector_id")["annual_avg_emplvl"].transform(
        lambda values: values / values.sum() if float(values.sum()) > 0 else pd.NA
    )
    detail_rows["sector_ai_exposure_score"] = detail_rows["sector_id"].map(
        scorecard_rows.set_index("sector_id")["ai_exposure_score"].to_dict()
    )
    detail_rows = detail_rows.sort_values(
        ["sector_label", "annual_avg_emplvl", "industry_code"],
        ascending=[True, False, True],
        kind="mergesort",
    ).reset_index(drop=True)

    total_detail_employment = pd.to_numeric(detail_rows["annual_avg_emplvl"], errors="coerce").sum()
    total_matched_employment = pd.to_numeric(
        detail_rows.loc[detail_rows["matched_flag"], "annual_avg_emplvl"],
        errors="coerce",
    ).sum()
    coverage = {
        "detailed_employment_total": float(total_detail_employment) if pd.notna(total_detail_employment) else None,
        "matched_employment_total": float(total_matched_employment) if pd.notna(total_matched_employment) else None,
        "matched_share_total": (
            float(total_matched_employment) / float(total_detail_employment)
            if total_detail_employment and not pd.isna(total_detail_employment)
            else None
        ),
        "matched_industry_rows": int(detail_rows["matched_flag"].sum()),
        "total_industry_rows": int(len(detail_rows)),
    }

    top_rows = scorecard_rows.dropna(subset=["ai_exposure_score"]).head(2)
    summary = None
    if not top_rows.empty:
        top_row = top_rows.iloc[0]
        summary = (
            f"In {year}, {top_row['sector_label']} carries the strongest combined AI exposure footprint in "
            f"{detail_rows['geo_name'].iloc[0]}. It accounts for {_safe_pct(top_row['employment_share'])} of private "
            f"employment, posts an exposure score of {float(top_row['ai_exposure_score']):.2f}, and has an LQ of "
            f"{float(top_row['lq_value']):.2f}x."
        )

    notes = [
        f"Sector exposure uses Felten Appendix B joined to section-owned `AIOE_DataAppendix.xlsx` at 4-digit NAICS.",
        f"Detailed industry employment comes from `staging.bls_qcew_county`, rolled to CBSA via `silver.xwalk_cbsa_county`, then paired back to the broad D1 sector taxonomy.",
        f"Coverage check: {_safe_pct(coverage.get('matched_share_total'))} of {year} detailed private employment matched a Felten industry score {coverage_note_suffix}",
        "Sector rows show broad D1 sectors for comparability, while the explanation panel preserves the underlying 4-digit detail.",
        "These scores are structural exposure signals, not displacement forecasts.",
    ]

    return {
        "selected_year": int(year),
        "market_name": str(detail_rows['geo_name'].iloc[0]),
        "scorecard_rows": scorecard_rows,
        "detail_rows": detail_rows,
        "coverage": coverage,
        "notes": notes,
        "summary": summary,
    }


def get_d6_occupation_companion_payload(
    market_id: str = DEFAULT_MARKET_ID,
    year: int = D6_OCCUPATION_TARGET_YEAR,
) -> dict[str, object]:
    """Build the D6 occupation companion from detailed OEWS rows plus Felten Appendix A."""
    appendix_a = get_felten_appendix_a()
    final_crosswalk = get_felten_soc_crosswalk_final()
    if appendix_a.empty:
        return {
            "selected_year": int(year),
            "market_name": str(market_id),
            "detail_rows": pd.DataFrame(),
            "family_rows": pd.DataFrame(),
            "coverage": {},
            "notes": [
                f"Felten Appendix A was not available at `{FELTEN_WORKBOOK_PATH.relative_to(REPO_ROOT)}`.",
                f"Download source: {FELTEN_WORKBOOK_URL}",
            ],
            "summary": None,
        }

    con = get_connection()
    try:
        total_row = con.execute(
            """
            SELECT geo_name, employment
            FROM silver.bls_oews
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
              AND year = ?
              AND is_total_occupation
            LIMIT 1
            """,
            [str(market_id), int(year)],
        ).fetchdf()
        detail_rows = con.execute(
            """
            SELECT
                geo_id AS market_id,
                geo_name,
                year,
                soc_code,
                soc_title,
                occupation_bucket,
                is_stem,
                employment,
                location_quotient,
                annual_mean_wage
            FROM silver.bls_oews
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
              AND year = ?
              AND o_group = 'detailed'
            ORDER BY employment DESC NULLS LAST, soc_code
            """,
            [str(market_id), int(year)],
        ).fetchdf()
        family_gold = con.execute(
            """
            SELECT *
            FROM gold.economics_occupation_wide
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
              AND year = ?
            LIMIT 1
            """,
            [str(market_id), int(year)],
        ).fetchdf()
    finally:
        con.close()

    if detail_rows.empty or total_row.empty:
        return {
            "selected_year": int(year),
            "market_name": str(market_id),
            "detail_rows": pd.DataFrame(),
            "family_rows": pd.DataFrame(),
            "coverage": {},
            "notes": [f"No detailed OEWS occupation rows were available for market {market_id} in {year}."],
            "summary": None,
        }

    total_employment = pd.to_numeric(total_row.iloc[0]["employment"], errors="coerce")
    if final_crosswalk.empty:
        detail_rows = detail_rows.merge(appendix_a, on="soc_code", how="left")
        detail_rows["match_basis"] = pd.NA
        detail_rows["manual_notes"] = pd.NA
        occupation_note = "The unmatched remainder is mostly a SOC-vintage issue: OEWS 2025 uses newer detailed codes than the static Felten appendix, and D6 does not invent a synthetic SOC crosswalk in this first pass."
    else:
        detail_rows = detail_rows.merge(
            final_crosswalk.rename(
                columns={
                    "our_soc_code": "soc_code",
                    "felten_soc_code": "felten_soc_code",
                    "felten_soc_name": "soc_title_felten",
                    "felten_score": "aioe_score",
                }
            ),
            on="soc_code",
            how="left",
        )
        occupation_note = "The unmatched remainder reflects the reviewed final SOC crosswalk; D6 now uses the locked section-owned mapping rather than a raw first-pass join."
    detail_rows["employment_share"] = detail_rows["employment"] / total_employment
    detail_rows["matched_flag"] = detail_rows["aioe_score"].notna()
    detail_rows["occupation_bucket_label"] = detail_rows["occupation_bucket"].map(OCCUPATION_BUCKET_LABELS).fillna("Other")
    detail_rows["stem_flag_label"] = detail_rows["is_stem"].map(lambda value: "STEM" if bool(value) else "Non-STEM")
    detail_rows["exposure_footprint"] = detail_rows["employment_share"] * detail_rows["aioe_score"].clip(lower=0)
    detail_rows = detail_rows.sort_values(
        ["exposure_footprint", "employment", "aioe_score"],
        ascending=[False, False, False],
        kind="mergesort",
        na_position="last",
    ).reset_index(drop=True)

    matched_employment = pd.to_numeric(detail_rows.loc[detail_rows["matched_flag"], "employment"], errors="coerce").sum()
    coverage = {
        "employment_total": float(total_employment) if pd.notna(total_employment) else None,
        "matched_employment_total": float(matched_employment) if pd.notna(matched_employment) else None,
        "matched_share_total": (
            float(matched_employment) / float(total_employment)
            if total_employment and not pd.isna(total_employment)
            else None
        ),
        "matched_soc_rows": int(detail_rows["matched_flag"].sum()),
        "total_soc_rows": int(len(detail_rows)),
    }

    family_rows = (
        detail_rows.groupby(["occupation_bucket", "occupation_bucket_label"], as_index=False)
        .agg(
            detailed_employment=("employment", "sum"),
            matched_employment=("employment", lambda values: float(detail_rows.loc[values.index, "employment"][detail_rows.loc[values.index, "matched_flag"]].sum())),
            weighted_aioe=("exposure_footprint", lambda values: float((detail_rows.loc[values.index, "employment"] * detail_rows.loc[values.index, "aioe_score"]).dropna().sum())),
        )
    )
    family_rows["matched_share"] = family_rows["matched_employment"] / family_rows["detailed_employment"]
    family_rows["family_ai_exposure_score"] = family_rows["weighted_aioe"] / family_rows["matched_employment"]

    if not family_gold.empty:
        gold_row = family_gold.iloc[0]
        share_lookup = {
            "management_professional": pd.to_numeric(gold_row.get("oews_pct_emp_management_professional"), errors="coerce"),
            "service": pd.to_numeric(gold_row.get("oews_pct_emp_service"), errors="coerce"),
            "production_transportation": pd.to_numeric(gold_row.get("oews_pct_emp_production_transportation"), errors="coerce"),
            "other": pd.to_numeric(gold_row.get("oews_pct_emp_other"), errors="coerce"),
        }
        lq_lookup = {
            "management_professional": pd.to_numeric(gold_row.get("oews_lq_management_professional"), errors="coerce"),
            "service": pd.to_numeric(gold_row.get("oews_lq_service"), errors="coerce"),
            "production_transportation": pd.to_numeric(gold_row.get("oews_lq_production_transportation"), errors="coerce"),
            "other": pd.to_numeric(gold_row.get("oews_lq_other"), errors="coerce"),
        }
        family_rows["employment_share"] = family_rows["occupation_bucket"].map(share_lookup)
        family_rows["family_lq"] = family_rows["occupation_bucket"].map(lq_lookup)
    else:
        family_rows["employment_share"] = family_rows["detailed_employment"] / total_employment
        family_rows["family_lq"] = pd.NA

    family_rows = family_rows.sort_values(
        ["employment_share", "family_ai_exposure_score"],
        ascending=[False, False],
        kind="mergesort",
        na_position="last",
    ).reset_index(drop=True)

    summary = None
    if not family_rows.empty:
        lead_family = family_rows.iloc[0]
        lead_occ = detail_rows.dropna(subset=["aioe_score"]).iloc[0] if detail_rows["aioe_score"].notna().any() else None
        if lead_occ is not None:
            summary = (
                f"In {year}, {lead_family['occupation_bucket_label']} holds the largest occupation footprint in "
                f"{detail_rows['geo_name'].iloc[0]}, while {lead_occ['soc_title']} is the single highest-footprint "
                f"detailed occupation in the matched Felten join."
            )

    notes = [
        f"Occupation exposure uses Felten Appendix A joined directly to `silver.bls_oews` detailed SOC rows for {year}.",
        f"Coverage check: {_safe_pct(coverage.get('matched_share_total'))} of detailed OEWS employment matched a Felten occupation score.",
        occupation_note,
        f"Broad occupation-family summary uses the {year} `gold.economics_occupation_wide` surface where available for compact share and LQ context.",
        "Sector exposure and occupation exposure are complementary: one is a NAICS-based industry structure read, the other is a SOC-based worker-task read.",
    ]

    return {
        "selected_year": int(year),
        "market_name": str(detail_rows['geo_name'].iloc[0]),
        "detail_rows": detail_rows,
        "family_rows": family_rows,
        "coverage": coverage,
        "notes": notes,
        "summary": summary,
    }


def get_d6_page_payload(market_id: str = DEFAULT_MARKET_ID) -> dict[str, object]:
    """Bundle the D6 sector and occupation surfaces for the Streamlit page."""
    sector_payload = get_d6_sector_scorecard_payload(market_id)
    occupation_payload = get_d6_occupation_companion_payload(market_id)
    interpretation = get_d4_job_center_interpretation(market_id=market_id)
    shortlist = interpretation.get("shortlist", pd.DataFrame())

    top_sector = (
        sector_payload["scorecard_rows"].dropna(subset=["ai_exposure_score"]).head(1)
        if not sector_payload["scorecard_rows"].empty
        else pd.DataFrame()
    )
    sector_note = None
    if not top_sector.empty and not shortlist.empty:
        sector_id = top_sector.iloc[0]["sector_id"]
        overlap = shortlist[shortlist["dominant_sector_id"] == sector_id]
        if not overlap.empty:
            typologies = ", ".join(sorted(overlap["interpretation_type"].dropna().unique().tolist()))
            sector_note = (
                f"The top exposure sector also shows up in the D3/D4 shortlist, where the current tract reads skew {typologies.lower()}."
            )

    return {
        "sector_payload": sector_payload,
        "occupation_payload": occupation_payload,
        "takeaway": sector_note,
    }
