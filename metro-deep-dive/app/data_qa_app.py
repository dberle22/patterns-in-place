"""Data QA App — Surface 3: coverage and data health dashboard."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC_PATH = _REPO_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

import duckdb
import pandas as pd
import streamlit as st

from retail_opportunity_finder.utils.config import get_db_path, load_data_sources, load_settings
from retail_opportunity_finder.app.data_qa import (
    parcel_geometry_coverage,
    score_coverage,
    table_inventory,
    tract_coverage,
    zone_build_coverage,
)

st.set_page_config(page_title="Data QA", layout="wide")
st.title("Data QA Dashboard")

_settings = load_settings()
_market_key = _settings.get("default_market_key", "jacksonville_fl")
_market = _settings["markets"][_market_key]
_cbsa_code = _market["cbsa_code"]


@st.cache_resource
def _get_con():
    return duckdb.connect(str(get_db_path()), read_only=True)


con = _get_con()

tabs = st.tabs([
    "Source & Tables",
    "Tract Coverage",
    "Zone Coverage",
    "Parcel Geometry",
    "Score Coverage",
    "Eligibility Gates",
    "Build Freshness",
])

# ── Tab 1: Source connections + table inventory ───────────────────────────────

with tabs[0]:
    st.subheader("Source Connections")

    sources = load_data_sources()
    db_path = get_db_path()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**App database**")
        if db_path.exists():
            size_mb = db_path.stat().st_size / 1_048_576
            st.success(f"{db_path.name} — {size_mb:.1f} MB")
        else:
            st.error(f"Not found: `{db_path}`")

    with col2:
        st.markdown("**Upstream source (metro_deep_dive)**")
        if sources is None:
            st.warning("data_sources.yaml absent — cloud mode, no upstream source.")
        else:
            metro_path = Path(sources.get("metro_duckdb_path", ""))
            if metro_path.exists():
                size_mb = metro_path.stat().st_size / 1_048_576
                st.success(f"{metro_path.name} — {size_mb:.1f} MB")
            else:
                st.error(f"Not found: `{metro_path}`")

    if sources is not None:
        st.markdown("**Parcel geometry root**")
        geom_root = Path(sources.get("parcel_geom_root", ""))
        if geom_root.exists():
            parquet_files = list(geom_root.rglob("*.parquet"))
            st.success(
                f"{geom_root} — {len(parquet_files)} Parquet file(s) found"
                if parquet_files
                else f"{geom_root} — exists but no Parquet files"
            )
        else:
            st.error(f"Not found: `{geom_root}`")

    st.divider()
    st.subheader("Table Inventory")

    inv = table_inventory(con)
    status_icons = {"ok": "✅", "empty": "⚠️", "missing": "❌"}
    inv["status"] = inv["status"].map(lambda s: f"{status_icons.get(s, '')} {s}")
    inv["rows"] = inv["rows"].apply(lambda v: f"{int(v):,}" if pd.notna(v) else "—")

    st.dataframe(inv, use_container_width=True, hide_index=True)
    st.caption(
        f"Total tables expected: {len(inv)}  |  "
        f"OK: {(inv['status'].str.startswith('✅')).sum()}  |  "
        f"Empty: {(inv['status'].str.startswith('⚠️')).sum()}  |  "
        f"Missing: {(inv['status'].str.startswith('❌')).sum()}"
    )

# ── Tab 2: Tract coverage ─────────────────────────────────────────────────────

with tabs[1]:
    st.subheader(f"Tract Feature Coverage — {_market['label']} (CBSA {_cbsa_code})")

    tc = tract_coverage(con, _cbsa_code)
    if tc.empty:
        st.warning("No tract_features rows found for this CBSA.")
    else:
        tc["coverage_pct"] = tc["coverage_pct"].map(lambda v: f"{v:.1f}%")
        st.dataframe(tc, use_container_width=True, hide_index=True)

        total = tc["total"].iloc[0]
        st.caption(f"{total:,} total tracts in this CBSA.")

# ── Tab 3: Zone build coverage ────────────────────────────────────────────────

with tabs[2]:
    st.subheader("Zone Build Coverage")

    zc = zone_build_coverage(con, _market_key)
    if zc.empty:
        st.warning("No zone coverage data found.")
    else:
        zc["coverage_pct"] = zc["coverage_pct"].map(lambda v: f"{v:.1f}%")
        st.dataframe(zc, use_container_width=True, hide_index=True)
        st.caption(
            "Cluster coverage uses cluster_assignments (explicit tract→zone mapping). "
            "Contiguity is a proxy via distinct tract_geoids in parcel_shortlist."
        )

# ── Tab 4: Parcel geometry coverage ──────────────────────────────────────────

with tabs[3]:
    st.subheader("Parcel Geometry Coverage by County")

    pgc = parcel_geometry_coverage(con)
    if pgc.empty:
        st.warning("No retail_parcels rows found.")
    else:
        pgc["coverage_pct"] = pgc["coverage_pct"].map(lambda v: f"{v:.1f}%")
        st.dataframe(pgc, use_container_width=True, hide_index=True)

        total_p = pgc["total_parcels"].sum()
        total_g = pgc["with_geometry"].sum()
        st.metric(
            "Overall geometry coverage",
            f"{total_g / total_p * 100:.1f}%",
            f"{total_g:,} of {total_p:,} parcels",
        )

# ── Tab 5: Score coverage ─────────────────────────────────────────────────────

with tabs[4]:
    st.subheader("Score Coverage (cluster zone system)")

    sc = score_coverage(con, _market_key)
    if sc.empty:
        st.warning("No parcel_shortlist rows found for cluster zone system.")
    else:
        sc["coverage_pct"] = sc["coverage_pct"].map(lambda v: f"{v:.1f}%")
        st.dataframe(sc, use_container_width=True, hide_index=True)

# ── Tab 6: Eligibility gates ──────────────────────────────────────────────────

with tabs[5]:
    st.subheader("Eligibility Gate Summary")

    gate_df = con.execute(
        """
        SELECT
            SUM(gate_pop)     AS pass_pop,
            SUM(gate_price)   AS pass_price,
            SUM(gate_density) AS pass_density,
            SUM(eligible_v1)  AS pass_all,
            COUNT(*)          AS total
        FROM rof_gold.tract_features
        WHERE cbsa_code = ?
        """,
        [_cbsa_code],
    ).df()

    if gate_df.empty or gate_df["total"].iloc[0] == 0:
        st.warning("No tract_features data found.")
    else:
        total = int(gate_df["total"].iloc[0])
        gates = {
            "Population (gate_pop)": int(gate_df["pass_pop"].iloc[0]),
            "Price Headroom (gate_price)": int(gate_df["pass_price"].iloc[0]),
            "Density (gate_density)": int(gate_df["pass_density"].iloc[0]),
            "All Gates (eligible_v1)": int(gate_df["pass_all"].iloc[0]),
        }

        cols = st.columns(4)
        for (label, passing), col in zip(gates.items(), cols):
            pct = passing / total * 100
            col.metric(label, f"{passing} / {total}", f"{pct:.1f}% pass")

        st.divider()
        st.subheader("Gate Combinations")

        combo_df = con.execute(
            """
            SELECT
                gate_pop, gate_price, gate_density, eligible_v1,
                COUNT(*) AS tracts
            FROM rof_gold.tract_features
            WHERE cbsa_code = ?
            GROUP BY 1, 2, 3, 4
            ORDER BY eligible_v1 DESC, gate_pop DESC, gate_price DESC, gate_density DESC
            """,
            [_cbsa_code],
        ).df()
        combo_df["pct_of_total"] = (combo_df["tracts"] / total * 100).map(
            lambda v: f"{v:.1f}%"
        )
        st.dataframe(combo_df, use_container_width=True, hide_index=True)

# ── Tab 7: Build freshness ────────────────────────────────────────────────────

with tabs[6]:
    st.subheader("Build Freshness")

    freshness = con.execute(
        """
        SELECT market_key, cbsa_name, build_source, run_timestamp
        FROM rof_gold.market_profiles
        ORDER BY market_key
        """
    ).df()

    if freshness.empty:
        st.warning("No market_profiles rows found.")
    else:
        st.dataframe(freshness, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("**App database file**")
    db_path = get_db_path()
    if db_path.exists():
        import datetime
        mtime = datetime.datetime.fromtimestamp(db_path.stat().st_mtime)
        st.markdown(
            f"`{db_path.name}` — last modified **{mtime.strftime('%Y-%m-%d %H:%M:%S')}**"
        )
    else:
        st.error("App database file not found.")
