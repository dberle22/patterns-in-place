"""Build national audit-ready Felten crosswalk review files for D6.

The goal is not to assert a final governed concordance. The goal is to produce
reviewable audit tables that show:
- our code/name
- Felten code/name
- current match status
- national employment weight and share
- top candidate suggestions for unresolved rows

These files are intended to support a one-time manual review that we can later
defend in an appendix or methods note.
"""

from __future__ import annotations

from difflib import SequenceMatcher
import importlib.util
import re
import sys
from pathlib import Path

import pandas as pd


SECTION_ROOT = Path(__file__).resolve().parent
DATA_PREP_PATH = SECTION_ROOT / "data_prep.py"
OUTPUT_DIR = SECTION_ROOT / "outputs" / "national" / "d6_coverage_review"
NAICS_YEAR = 2024
SOC_YEAR = 2025
SOC_CROSSWALK_PATH = OUTPUT_DIR / "soc_2010_to_2018_crosswalk.xlsx"


def _load_data_prep():
    """Import the section-owned prep module so the audit stays aligned to D6 logic."""
    spec = importlib.util.spec_from_file_location("industry_d6_audit_data_prep", DATA_PREP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _normalize_title(value: str | None) -> str:
    """Normalize titles for light-touch similarity review."""
    if value is None:
        return ""
    out = str(value).lower().strip()
    out = out.replace("&", " and ")
    out = re.sub(r"\bnaics\s+\d{4}\b", " ", out)
    out = out.replace("mfg.", "manufacturing")
    out = out.replace("mfg", "manufacturing")
    out = re.sub(r"[^a-z0-9]+", " ", out)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def _score_titles(left: str, right: str) -> float:
    """Return a simple similarity score for human review ranking."""
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def _load_xlsx_shared_strings(path: Path) -> list[str]:
    """Load XLSX shared strings so we can parse workbook XML without extra deps."""
    from zipfile import ZipFile
    from xml.etree import ElementTree as ET

    with ZipFile(path) as workbook_zip:
        if "xl/sharedStrings.xml" not in workbook_zip.namelist():
            return []
        root = ET.fromstring(workbook_zip.read("xl/sharedStrings.xml"))
        namespace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        out: list[str] = []
        for item in root.findall(f"{namespace}si"):
            out.append("".join(node.text or "" for node in item.iter(f"{namespace}t")))
        return out


def _load_soc_crosswalk() -> pd.DataFrame:
    """Read the official BLS SOC crosswalk workbook already added to the repo."""
    from zipfile import ZipFile
    from xml.etree import ElementTree as ET

    if not SOC_CROSSWALK_PATH.exists():
        return pd.DataFrame(
            columns=[
                "soc_2010_code",
                "soc_2010_title",
                "soc_2018_code",
                "soc_2018_title",
            ]
        )

    shared_strings = _load_xlsx_shared_strings(SOC_CROSSWALK_PATH)
    with ZipFile(SOC_CROSSWALK_PATH) as workbook_zip:
        root = ET.fromstring(workbook_zip.read("xl/worksheets/sheet1.xml"))
        namespace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        rows: list[list[str]] = []
        for row in root.iter(f"{namespace}row"):
            values: list[str] = []
            for cell in row.iter(f"{namespace}c"):
                value_node = cell.find(f"{namespace}v")
                if value_node is None:
                    values.append("")
                    continue
                if cell.attrib.get("t") == "s":
                    values.append(shared_strings[int(value_node.text)])
                else:
                    values.append(value_node.text or "")
            rows.append(values)

    header_idx = next(
        (
            idx
            for idx, row in enumerate(rows)
            if row[:4] == ["2010 SOC Code", "2010 SOC Title", "2018 SOC Code", "2018 SOC Title"]
        ),
        None,
    )
    if header_idx is None:
        return pd.DataFrame()

    data_rows = rows[header_idx + 1 :]
    out = pd.DataFrame(data_rows, columns=["soc_2010_code", "soc_2010_title", "soc_2018_code", "soc_2018_title"])
    out = out[(out["soc_2010_code"] != "") & (out["soc_2018_code"] != "")].copy()
    return out.reset_index(drop=True)


def _top_title_candidates(
    source_code: str,
    source_title: str,
    candidates: pd.DataFrame,
    code_prefix_len: int,
    code_column: str,
    title_column: str,
    score_column: str | None,
    score_floor: float = 0.30,
    top_n: int = 3,
) -> list[dict[str, object]]:
    """Return the strongest title candidates within a coarse code family."""
    normalized_source = _normalize_title(source_title)
    code_prefix = str(source_code)[:code_prefix_len]
    scoped = candidates[candidates[code_column].astype(str).str.startswith(code_prefix)].copy()
    if scoped.empty:
        scoped = candidates.copy()

    scoped["normalized_title"] = scoped[title_column].map(_normalize_title)
    scoped["match_score"] = scoped["normalized_title"].map(lambda value: _score_titles(normalized_source, value))
    scoped = scoped.sort_values(["match_score", code_column], ascending=[False, True], kind="mergesort")
    scoped = scoped[scoped["match_score"] >= score_floor].head(top_n)

    out: list[dict[str, object]] = []
    for _, row in scoped.iterrows():
        out.append(
            {
                "candidate_code": row[code_column],
                "candidate_title": row[title_column],
                "candidate_score": float(row["match_score"]),
                "candidate_felten_score": row[score_column] if score_column else pd.NA,
            }
        )
    return out


def _candidate_columns(record: dict[str, object], candidates: list[dict[str, object]]) -> dict[str, object]:
    """Flatten top candidates into stable CSV columns."""
    for idx in range(3):
        if idx < len(candidates):
            record[f"candidate_{idx + 1}_code"] = candidates[idx]["candidate_code"]
            record[f"candidate_{idx + 1}_title"] = candidates[idx]["candidate_title"]
            record[f"candidate_{idx + 1}_score"] = candidates[idx]["candidate_score"]
            record[f"candidate_{idx + 1}_felten_score"] = candidates[idx].get("candidate_felten_score", pd.NA)
        else:
            record[f"candidate_{idx + 1}_code"] = pd.NA
            record[f"candidate_{idx + 1}_title"] = pd.NA
            record[f"candidate_{idx + 1}_score"] = pd.NA
            record[f"candidate_{idx + 1}_felten_score"] = pd.NA
    return record


def _load_national_naics_rows(mod) -> pd.DataFrame:
    """Build the national 4-digit NAICS employment surface from staged county QCEW."""
    con = mod.get_connection()
    try:
        rows = con.execute(
            """
            SELECT
                c.industry_code AS our_code,
                c.industry_title AS our_name,
                SUM(c.annual_avg_emplvl) AS our_weight
            FROM staging.bls_qcew_county c
            INNER JOIN silver.bls_qcew_industry_map m
                ON c.industry_code = m.industry_code
            WHERE c.period = ?
              AND c.own_code = '5'
              AND m.code_type = 'naics_industry_group'
            GROUP BY 1, 2
            ORDER BY our_weight DESC, our_code
            """,
            [NAICS_YEAR],
        ).fetchdf()
    finally:
        con.close()

    rows["felten_code"] = rows["our_code"].map(mod._get_felten_industry_join_code)
    rows = rows.merge(
        mod.get_felten_appendix_b().rename(
            columns={
                "industry_code": "felten_code",
                "industry_title_felten": "felten_name",
                "aiie_score": "felten_score",
            }
        ),
        on="felten_code",
        how="left",
    )
    rows["matched_flag"] = rows["felten_score"].notna()
    total_weight = pd.to_numeric(rows["our_weight"], errors="coerce").sum()
    rows["our_share_of_total"] = rows["our_weight"] / total_weight
    return rows


def _load_national_soc_rows(mod) -> pd.DataFrame:
    """Build the national detailed SOC employment surface from state OEWS rows.

    We use the state slice because the first-pass OEWS Gold notes already treat
    state rows as the best national reconstruction base.
    """
    con = mod.get_connection()
    try:
        rows = con.execute(
            """
            SELECT
                soc_code AS our_code,
                soc_title AS our_name,
                occupation_bucket AS our_group_id,
                SUM(employment) AS our_weight
            FROM silver.bls_oews
            WHERE geo_level = 'state'
              AND year = ?
              AND o_group = 'detailed'
            GROUP BY 1, 2, 3
            ORDER BY our_weight DESC NULLS LAST, our_code
            """,
            [SOC_YEAR],
        ).fetchdf()
    finally:
        con.close()

    rows = rows.merge(
        mod.get_felten_appendix_a().rename(
            columns={
                "soc_code": "felten_code",
                "soc_title_felten": "felten_name",
                "aioe_score": "felten_score",
            }
        ),
        left_on="our_code",
        right_on="felten_code",
        how="left",
    )
    rows["matched_flag"] = rows["felten_score"].notna()
    rows["our_group_label"] = rows["our_group_id"].map(mod.OCCUPATION_BUCKET_LABELS).fillna("Other")
    total_weight = pd.to_numeric(rows["our_weight"], errors="coerce").sum()
    rows["our_share_of_total"] = rows["our_weight"] / total_weight
    return rows


def _official_soc_candidates(our_code: str, our_name: str, crosswalk_rows: pd.DataFrame) -> list[dict[str, object]]:
    """Return official BLS 2010-SOC predecessor candidates for one 2018 SOC code."""
    if crosswalk_rows.empty:
        return []

    scoped = crosswalk_rows[crosswalk_rows["soc_2018_code"] == str(our_code)].copy()
    if scoped.empty:
        return []

    normalized_our_title = _normalize_title(our_name)
    scoped["candidate_score"] = scoped["soc_2010_title"].map(
        lambda value: _score_titles(normalized_our_title, _normalize_title(value))
    )
    scoped = scoped.sort_values(
        ["candidate_score", "soc_2010_code"],
        ascending=[False, True],
        kind="mergesort",
    ).head(3)

    out: list[dict[str, object]] = []
    for _, row in scoped.iterrows():
        out.append(
            {
                "candidate_code": row["soc_2010_code"],
                "candidate_title": row["soc_2010_title"],
                "candidate_score": float(row["candidate_score"]),
                "candidate_felten_score": row.get("aioe_score", pd.NA),
            }
        )
    return out


def _build_naics_audit(mod) -> pd.DataFrame:
    """Build the national NAICS audit table."""
    our_rows = _load_national_naics_rows(mod)
    felten_rows = mod.get_felten_appendix_b().rename(
        columns={"industry_code": "felten_code", "industry_title_felten": "felten_name", "aiie_score": "felten_score"}
    ).copy()
    rows: list[dict[str, object]] = []
    used_felten_codes = set()
    unmatched_candidate_codes = set()

    for _, row in our_rows.iterrows():
        matched_flag = bool(row["matched_flag"])
        record = {
            "audit_status": "matched" if matched_flag else "unmatched_our_code",
            "needs_manual_review": not matched_flag,
            "our_code": row["our_code"],
            "our_name": row["our_name"],
            "our_naics_prefix": str(row["our_code"])[:3],
            "our_weight": row["our_weight"],
            "our_share_of_total": row["our_share_of_total"],
            "felten_code": row["felten_code"] if matched_flag else pd.NA,
            "felten_name": row["felten_name"] if matched_flag else pd.NA,
            "felten_score": row["felten_score"] if matched_flag else pd.NA,
            "felten_naics_prefix": str(row["felten_code"])[:3] if matched_flag else pd.NA,
            "same_prefix_flag": True if matched_flag else pd.NA,
            "match_basis": "current_d6_join" if matched_flag else pd.NA,
            "normalized_our_name": _normalize_title(row["our_name"]),
            "normalized_felten_name": _normalize_title(row["felten_name"]) if matched_flag else pd.NA,
        }
        if matched_flag:
            used_felten_codes.add(str(row["felten_code"]))
            record = _candidate_columns(record, [])
        else:
            candidates = _top_title_candidates(
                source_code=row["our_code"],
                source_title=row["our_name"],
                candidates=felten_rows,
                code_prefix_len=3,
                code_column="felten_code",
                title_column="felten_name",
                score_column="felten_score",
            )
            unmatched_candidate_codes.update(str(candidate["candidate_code"]) for candidate in candidates)
            record = _candidate_columns(record, candidates)
        rows.append(record)

    candidate_only_codes = sorted(unmatched_candidate_codes - used_felten_codes)
    if candidate_only_codes:
        candidate_rows = felten_rows[felten_rows["felten_code"].astype(str).isin(candidate_only_codes)].copy()
        for _, row in candidate_rows.iterrows():
            candidates = _top_title_candidates(
                source_code=row["felten_code"],
                source_title=row["felten_name"],
                candidates=our_rows,
                code_prefix_len=3,
                code_column="our_code",
                title_column="our_name",
                score_column=None,
            )
            record = {
                "audit_status": "unmatched_felten_code",
                "needs_manual_review": True,
                "our_code": pd.NA,
                "our_name": pd.NA,
                "our_naics_prefix": pd.NA,
                "our_weight": pd.NA,
                "our_share_of_total": pd.NA,
                "felten_code": row["felten_code"],
                "felten_name": row["felten_name"],
                "felten_score": row["felten_score"],
                "felten_naics_prefix": str(row["felten_code"])[:3],
                "same_prefix_flag": pd.NA,
                "match_basis": pd.NA,
                "normalized_our_name": pd.NA,
                "normalized_felten_name": _normalize_title(row["felten_name"]),
            }
            record = _candidate_columns(record, candidates)
            rows.append(record)

    return pd.DataFrame(rows).sort_values(
        ["audit_status", "our_share_of_total", "our_code", "felten_code"],
        ascending=[True, False, True, True],
        kind="mergesort",
        na_position="last",
    )


def _build_soc_audit(mod) -> pd.DataFrame:
    """Build the national SOC audit table."""
    our_rows = _load_national_soc_rows(mod)
    felten_rows = mod.get_felten_appendix_a().rename(
        columns={"soc_code": "felten_code", "soc_title_felten": "felten_name", "aioe_score": "felten_score"}
    ).copy()
    crosswalk_rows = _load_soc_crosswalk()
    if not crosswalk_rows.empty:
        crosswalk_rows = crosswalk_rows.merge(
            felten_rows[["felten_code", "felten_score"]].rename(columns={"felten_code": "soc_2010_code"}),
            on="soc_2010_code",
            how="left",
        )
    rows: list[dict[str, object]] = []
    used_felten_codes = set()
    unmatched_candidate_codes = set()

    for _, row in our_rows.iterrows():
        matched_flag = bool(row["matched_flag"])
        record = {
            "audit_status": "matched" if matched_flag else "unmatched_our_code",
            "needs_manual_review": not matched_flag,
            "our_code": row["our_code"],
            "our_name": row["our_name"],
            "our_group_label": row["our_group_label"],
            "our_soc_major_group": str(row["our_code"])[:2],
            "our_weight": row["our_weight"],
            "our_share_of_total": row["our_share_of_total"],
            "felten_code": row["felten_code"] if matched_flag else pd.NA,
            "felten_name": row["felten_name"] if matched_flag else pd.NA,
            "felten_score": row["felten_score"] if matched_flag else pd.NA,
            "felten_soc_major_group": str(row["felten_code"])[:2] if matched_flag else pd.NA,
            "same_major_group_flag": True if matched_flag else pd.NA,
            "match_basis": "current_d6_join" if matched_flag else pd.NA,
            "normalized_our_name": _normalize_title(row["our_name"]),
            "normalized_felten_name": _normalize_title(row["felten_name"]) if matched_flag else pd.NA,
        }
        if matched_flag:
            used_felten_codes.add(str(row["felten_code"]))
            record = _candidate_columns(record, [])
        else:
            candidates = _official_soc_candidates(row["our_code"], row["our_name"], crosswalk_rows)
            if not candidates:
                candidates = _top_title_candidates(
                    source_code=row["our_code"],
                    source_title=row["our_name"],
                    candidates=felten_rows,
                    code_prefix_len=2,
                    code_column="felten_code",
                    title_column="felten_name",
                    score_column="felten_score",
                )
            unmatched_candidate_codes.update(str(candidate["candidate_code"]) for candidate in candidates)
            record = _candidate_columns(record, candidates)
        rows.append(record)

    candidate_only_codes = sorted(unmatched_candidate_codes - used_felten_codes)
    if candidate_only_codes:
        candidate_rows = felten_rows[felten_rows["felten_code"].astype(str).isin(candidate_only_codes)].copy()
        for _, row in candidate_rows.iterrows():
            candidates = _top_title_candidates(
                source_code=row["felten_code"],
                source_title=row["felten_name"],
                candidates=our_rows,
                code_prefix_len=2,
                code_column="our_code",
                title_column="our_name",
                score_column=None,
            )
            record = {
                "audit_status": "unmatched_felten_code",
                "needs_manual_review": True,
                "our_code": pd.NA,
                "our_name": pd.NA,
                "our_group_label": pd.NA,
                "our_soc_major_group": pd.NA,
                "our_weight": pd.NA,
                "our_share_of_total": pd.NA,
                "felten_code": row["felten_code"],
                "felten_name": row["felten_name"],
                "felten_score": row["felten_score"],
                "felten_soc_major_group": str(row["felten_code"])[:2],
                "same_major_group_flag": pd.NA,
                "match_basis": pd.NA,
                "normalized_our_name": pd.NA,
                "normalized_felten_name": _normalize_title(row["felten_name"]),
            }
            record = _candidate_columns(record, candidates)
            rows.append(record)

    return pd.DataFrame(rows).sort_values(
        ["audit_status", "our_share_of_total", "our_code", "felten_code"],
        ascending=[True, False, True, True],
        kind="mergesort",
        na_position="last",
    )


def _recommend_from_candidates(
    rows: pd.DataFrame,
    kind: str,
) -> pd.DataFrame:
    """Create first-pass recommendations for currently unmatched rows.

    These are review suggestions only. We bias toward conservative recommendations
    that stay within the same code family and have reasonably strong title support.
    """
    unmatched = rows[rows["audit_status"] == "unmatched_our_code"].copy()
    if unmatched.empty:
        return unmatched

    recommendations: list[dict[str, object]] = []
    for _, row in unmatched.iterrows():
        candidate_code = row.get("candidate_1_code")
        candidate_title = row.get("candidate_1_title")
        candidate_score = pd.to_numeric(row.get("candidate_1_score"), errors="coerce")
        if pd.isna(candidate_code):
            recommended = False
            confidence = "none"
            rationale = "No candidate was generated."
        else:
            if kind == "soc":
                same_group = str(row["our_soc_major_group"]) == str(candidate_code)[:2]
                exact_name = row["normalized_our_name"] == _normalize_title(candidate_title)
                if same_group and (exact_name or (pd.notna(candidate_score) and float(candidate_score) >= 0.80)):
                    recommended = True
                    confidence = "high"
                    rationale = "Same SOC major group with strong title alignment."
                elif same_group and pd.notna(candidate_score) and float(candidate_score) >= 0.55:
                    recommended = True
                    confidence = "medium"
                    rationale = "Same SOC major group with moderate title alignment."
                else:
                    recommended = False
                    confidence = "low"
                    rationale = "Candidate exists but title alignment is still weak."
            else:
                same_prefix = str(row["our_naics_prefix"]) == str(candidate_code)[:3]
                exact_name = row["normalized_our_name"] == _normalize_title(candidate_title)
                if same_prefix and (exact_name or (pd.notna(candidate_score) and float(candidate_score) >= 0.75)):
                    recommended = True
                    confidence = "high"
                    rationale = "Same 3-digit NAICS family with strong title alignment."
                elif same_prefix and pd.notna(candidate_score) and float(candidate_score) >= 0.50:
                    recommended = True
                    confidence = "medium"
                    rationale = "Same 3-digit NAICS family with moderate title alignment."
                else:
                    recommended = False
                    confidence = "low"
                    rationale = "Candidate exists but title alignment is still weak."

        recommendations.append(
            {
                "our_code": row["our_code"],
                "our_name": row["our_name"],
                "our_weight": row["our_weight"],
                "our_share_of_total": row["our_share_of_total"],
                "recommended_felten_code": candidate_code,
                "recommended_felten_name": candidate_title,
                "recommended_score": candidate_score,
                "recommended_felten_score": row.get("candidate_1_felten_score"),
                "recommend_match": recommended,
                "confidence": confidence,
                "rationale": rationale,
            }
        )

    out = pd.DataFrame(recommendations)
    return out.sort_values(
        ["recommend_match", "our_share_of_total", "our_code"],
        ascending=[False, False, True],
        kind="mergesort",
        na_position="last",
    )


def _apply_recommendations(audit_rows: pd.DataFrame, recommendations: pd.DataFrame, kind: str) -> pd.DataFrame:
    """Apply accepted first-pass recommendations to produce a scenario audit view."""
    if audit_rows.empty:
        return audit_rows.copy()

    out = audit_rows.copy()
    out["post_review_status"] = out["audit_status"]
    out["review_action"] = pd.NA
    out["multiple_candidate_flag"] = out["candidate_2_code"].notna()

    if recommendations.empty:
        return out

    accepted = recommendations[recommendations["recommend_match"] == True].copy()
    if accepted.empty:
        return out

    accepted = accepted.rename(
        columns={
            "confidence": "recommendation_confidence",
            "rationale": "recommendation_rationale",
        }
    )
    accepted = accepted[
        [
            "our_code",
            "recommended_felten_code",
            "recommended_felten_name",
            "recommended_score",
            "recommendation_confidence",
            "recommendation_rationale",
        ]
    ].copy()

    out = out.merge(accepted, on="our_code", how="left")
    apply_mask = (
        (out["audit_status"] == "unmatched_our_code")
        & out["recommended_felten_code"].notna()
    )

    out.loc[apply_mask, "post_review_status"] = "matched_via_recommendation"
    out.loc[apply_mask, "review_action"] = "accept_first_pass_recommendation"
    out.loc[apply_mask, "felten_code"] = out.loc[apply_mask, "recommended_felten_code"]
    out.loc[apply_mask, "felten_name"] = out.loc[apply_mask, "recommended_felten_name"]
    out.loc[apply_mask, "match_basis"] = "first_pass_recommendation"
    out.loc[apply_mask, "normalized_felten_name"] = out.loc[apply_mask, "recommended_felten_name"].map(_normalize_title)

    if kind == "soc":
        out.loc[apply_mask, "felten_soc_major_group"] = out.loc[apply_mask, "recommended_felten_code"].astype(str).str[:2]
        out.loc[apply_mask, "same_major_group_flag"] = (
            out.loc[apply_mask, "our_soc_major_group"]
            == out.loc[apply_mask, "felten_soc_major_group"]
        )
    else:
        out.loc[apply_mask, "felten_naics_prefix"] = out.loc[apply_mask, "recommended_felten_code"].astype(str).str[:3]
        out.loc[apply_mask, "same_prefix_flag"] = (
            out.loc[apply_mask, "our_naics_prefix"]
            == out.loc[apply_mask, "felten_naics_prefix"]
        )

    return out.sort_values(
        ["post_review_status", "our_share_of_total", "our_code", "felten_code"],
        ascending=[True, False, True, True],
        kind="mergesort",
        na_position="last",
    )


def _build_remaining_review_queue(rows: pd.DataFrame, kind: str) -> pd.DataFrame:
    """Create a documented second-pass queue for the gaps left after first-pass recommendations."""
    if rows.empty:
        return rows.copy()

    review_rows: list[dict[str, object]] = []
    for _, row in rows.iterrows():
        score_1 = pd.to_numeric(row.get("candidate_1_score"), errors="coerce")
        score_2 = pd.to_numeric(row.get("candidate_2_score"), errors="coerce")
        normalized_our = row.get("normalized_our_name") or _normalize_title(row.get("our_name"))
        normalized_c1 = _normalize_title(row.get("candidate_1_title"))
        score_gap = pd.NA if pd.isna(score_1) or pd.isna(score_2) else float(score_1) - float(score_2)
        exact_title = bool(normalized_our and normalized_our == normalized_c1)
        has_multiple = bool(row.get("multiple_candidate_flag"))

        if kind == "soc":
            if exact_title or (pd.notna(score_1) and float(score_1) >= 0.85):
                bucket = "likely_manual_accept"
                reason = "Top candidate is effectively an exact rename or a very strong title match."
            elif has_multiple and pd.notna(score_gap) and float(score_gap) <= 0.08:
                bucket = "needs_user_choice"
                reason = "Multiple SOC candidates are close enough that a documented human choice is safer."
            elif pd.notna(score_1) and float(score_1) >= 0.50:
                bucket = "likely_manual_accept"
                reason = "Top candidate has a reasonably strong title match and no equally strong runner-up."
            else:
                bucket = "leave_unmatched_for_now"
                reason = "Title support is still weak, so we should not force a manual override yet."
        else:
            if exact_title or (pd.notna(score_1) and float(score_1) >= 0.84):
                bucket = "likely_manual_accept"
                reason = "Top candidate is effectively the same NAICS concept under an older Felten label."
            elif has_multiple and pd.notna(score_gap) and float(score_gap) <= 0.08:
                bucket = "needs_user_choice"
                reason = "Multiple NAICS candidates are too close to choose automatically."
            else:
                bucket = "leave_unmatched_for_now"
                reason = "Title support is too weak for a one-time override without more manual review."

        review_rows.append(
            {
                "our_code": row.get("our_code"),
                "our_name": row.get("our_name"),
                "our_weight": row.get("our_weight"),
                "our_share_of_total": row.get("our_share_of_total"),
                "candidate_1_code": row.get("candidate_1_code"),
                "candidate_1_title": row.get("candidate_1_title"),
                "candidate_1_score": row.get("candidate_1_score"),
                "candidate_1_felten_score": row.get("candidate_1_felten_score"),
                "candidate_2_code": row.get("candidate_2_code"),
                "candidate_2_title": row.get("candidate_2_title"),
                "candidate_2_score": row.get("candidate_2_score"),
                "candidate_2_felten_score": row.get("candidate_2_felten_score"),
                "candidate_3_code": row.get("candidate_3_code"),
                "candidate_3_title": row.get("candidate_3_title"),
                "candidate_3_score": row.get("candidate_3_score"),
                "candidate_3_felten_score": row.get("candidate_3_felten_score"),
                "multiple_candidate_flag": has_multiple,
                "review_bucket": bucket,
                "review_reason": reason,
                "manual_decision": pd.NA,
                "manual_notes": pd.NA,
            }
        )

    return pd.DataFrame(review_rows).sort_values(
        ["review_bucket", "our_share_of_total", "our_code"],
        ascending=[True, False, True],
        kind="mergesort",
        na_position="last",
    )


def _write_markdown_summary(
    naics_audit: pd.DataFrame,
    soc_audit: pd.DataFrame,
    naics_recs: pd.DataFrame,
    soc_recs: pd.DataFrame,
    naics_post: pd.DataFrame,
    soc_post: pd.DataFrame,
) -> None:
    """Write a markdown file that tracks the audit work and current national coverage."""
    def summarize(rows: pd.DataFrame) -> pd.DataFrame:
        summary = (
            rows.groupby("audit_status", dropna=False, as_index=False)
            .agg(
                row_count=("audit_status", "size"),
                weighted_share=("our_share_of_total", "sum"),
            )
            .sort_values("audit_status", kind="mergesort")
        )
        return summary

    def summarize_post(rows: pd.DataFrame) -> pd.DataFrame:
        summary = (
            rows.groupby("post_review_status", dropna=False, as_index=False)
            .agg(
                row_count=("post_review_status", "size"),
                weighted_share=("our_share_of_total", "sum"),
            )
            .sort_values("post_review_status", kind="mergesort")
        )
        return summary

    naics_summary = summarize(naics_audit)
    soc_summary = summarize(soc_audit)
    naics_post_summary = summarize_post(naics_post)
    soc_post_summary = summarize_post(soc_post)

    lines = [
        "# Felten Crosswalk Audit",
        "",
        "National-weighted audit surface for the Industry D6 Felten joins.",
        "",
        "## What These Files Are",
        "",
        "- `audit_felten_naics_national_2024.csv` tracks current and unresolved 4-digit NAICS matches against Felten Appendix B.",
        "- `audit_felten_soc_national_2025.csv` tracks current and unresolved detailed SOC matches against Felten Appendix A.",
        "- `our_weight` is the national employment weight from the live platform source.",
        "- `our_share_of_total` is that code's share of the national employment base used for the audit.",
        "- `audit_status` shows whether the row is already matched, unmatched on our side, or unmatched on the Felten side.",
        "",
        "## Current National NAICS Audit Status",
        "",
    ]
    for _, row in naics_summary.iterrows():
        share = row["weighted_share"]
        share_label = "—" if pd.isna(share) else f"{float(share):.1%}"
        lines.append(f"- `{row['audit_status']}`: {int(row['row_count'])} rows, {share_label} of national detailed NAICS employment")

    lines.extend(
        [
            "",
            "## Current National SOC Audit Status",
            "",
        ]
    )
    for _, row in soc_summary.iterrows():
        share = row["weighted_share"]
        share_label = "—" if pd.isna(share) else f"{float(share):.1%}"
        lines.append(f"- `{row['audit_status']}`: {int(row['row_count'])} rows, {share_label} of national detailed SOC employment")

    lines.extend(
        [
            "",
            "## How To Use This",
            "",
            "- Review `matched` rows only when you want to audit an existing automatic join.",
            "- Review `unmatched_our_code` rows first because those represent current platform coverage gaps.",
            "- Review `unmatched_felten_code` rows second because those are unused Felten candidates that may justify a one-time override.",
            "- Candidate columns are review hints, not final crosswalk decisions.",
        ]
    )

    naics_high = int(((naics_recs["recommend_match"] == True) & (naics_recs["confidence"] == "high")).sum()) if not naics_recs.empty else 0
    soc_high = int(((soc_recs["recommend_match"] == True) & (soc_recs["confidence"] == "high")).sum()) if not soc_recs.empty else 0
    naics_med = int(((naics_recs["recommend_match"] == True) & (naics_recs["confidence"] == "medium")).sum()) if not naics_recs.empty else 0
    soc_med = int(((soc_recs["recommend_match"] == True) & (soc_recs["confidence"] == "medium")).sum()) if not soc_recs.empty else 0
    lines.extend(
        [
            "",
            "## First-Pass Recommendation Counts",
            "",
            f"- NAICS: `{naics_high}` high-confidence and `{naics_med}` medium-confidence unmatched-our-code recommendations",
            f"- SOC: `{soc_high}` high-confidence and `{soc_med}` medium-confidence unmatched-our-code recommendations",
        ]
    )

    lines.extend(
        [
            "",
            "## Post-Recommendation Scenario",
            "",
            "Assumption: accept every current `recommend_match = True` row as a one-time reviewed override.",
            "",
            "### NAICS After Applying Recommendations",
            "",
        ]
    )
    for _, row in naics_post_summary.iterrows():
        share = row["weighted_share"]
        share_label = "—" if pd.isna(share) else f"{float(share):.1%}"
        lines.append(f"- `{row['post_review_status']}`: {int(row['row_count'])} rows, {share_label} of national detailed NAICS employment")

    lines.extend(
        [
            "",
            "### SOC After Applying Recommendations",
            "",
        ]
    )
    for _, row in soc_post_summary.iterrows():
        share = row["weighted_share"]
        share_label = "—" if pd.isna(share) else f"{float(share):.1%}"
        lines.append(f"- `{row['post_review_status']}`: {int(row['row_count'])} rows, {share_label} of national detailed SOC employment")

    (OUTPUT_DIR / "audit_crosswalk_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Write the national audit CSVs and markdown analysis summary."""
    mod = _load_data_prep()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    naics_audit = _build_naics_audit(mod)
    soc_audit = _build_soc_audit(mod)

    naics_path = OUTPUT_DIR / "audit_felten_naics_national_2024.csv"
    soc_path = OUTPUT_DIR / "audit_felten_soc_national_2025.csv"
    naics_rec_path = OUTPUT_DIR / "recommended_felten_naics_overrides_initial.csv"
    soc_rec_path = OUTPUT_DIR / "recommended_felten_soc_overrides_initial.csv"
    naics_post_path = OUTPUT_DIR / "audit_felten_naics_national_2024_post_recommendation.csv"
    soc_post_path = OUTPUT_DIR / "audit_felten_soc_national_2025_post_recommendation.csv"
    naics_remaining_path = OUTPUT_DIR / "remaining_felten_naics_gaps_national_2024.csv"
    soc_remaining_path = OUTPUT_DIR / "remaining_felten_soc_gaps_national_2025.csv"
    naics_review_path = OUTPUT_DIR / "remaining_felten_naics_review_queue_national_2024.csv"
    soc_review_path = OUTPUT_DIR / "remaining_felten_soc_review_queue_national_2025.csv"
    notes_path = OUTPUT_DIR / "audit_crosswalk_notes.txt"
    naics_recs = _recommend_from_candidates(naics_audit, kind="naics")
    soc_recs = _recommend_from_candidates(soc_audit, kind="soc")
    naics_post = _apply_recommendations(naics_audit, naics_recs, kind="naics")
    soc_post = _apply_recommendations(soc_audit, soc_recs, kind="soc")
    naics_remaining = naics_post[naics_post["post_review_status"] == "unmatched_our_code"].copy()
    soc_remaining = soc_post[soc_post["post_review_status"] == "unmatched_our_code"].copy()
    naics_review = _build_remaining_review_queue(naics_remaining, kind="naics")
    soc_review = _build_remaining_review_queue(soc_remaining, kind="soc")

    naics_audit.to_csv(naics_path, index=False)
    soc_audit.to_csv(soc_path, index=False)
    naics_recs.to_csv(naics_rec_path, index=False)
    soc_recs.to_csv(soc_rec_path, index=False)
    naics_post.to_csv(naics_post_path, index=False)
    soc_post.to_csv(soc_post_path, index=False)
    naics_remaining.to_csv(naics_remaining_path, index=False)
    soc_remaining.to_csv(soc_remaining_path, index=False)
    naics_review.to_csv(naics_review_path, index=False)
    soc_review.to_csv(soc_review_path, index=False)
    notes_path.write_text(
        "\n".join(
            [
                "Felten audit crosswalk notes",
                "",
                "These audit CSVs are review artifacts, not final governed concordances.",
                "They use national employment weights, not Richmond-only weights.",
                "Each row shows our code/name, the currently matched Felten code/name when one exists, and audit status.",
                "",
                "Audit statuses:",
                "- matched: current D6 join already links the pair",
                "- unmatched_our_code: our code has no current Felten match; candidate columns suggest review targets",
                "- unmatched_felten_code: a Felten code appears as a review candidate but is not currently used by the D6 join",
                "",
                "Use:",
                "- Confirm existing matches",
                "- Fill in manual one-time overrides for unmatched rows",
                "- Preserve the review trail for an appendix or methods note",
                "",
                "Post-recommendation scenario files assume every current `recommend_match = True` row is accepted.",
                "Remaining gap files show the unresolved unmatched-our-code rows after that scenario is applied.",
                "Review queue files classify those remaining gaps into likely manual accepts, needs-user-choice rows, and leave-unmatched-for-now rows.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _write_markdown_summary(naics_audit, soc_audit, naics_recs, soc_recs, naics_post, soc_post)

    print(naics_path)
    print(soc_path)
    print(naics_rec_path)
    print(soc_rec_path)
    print(naics_post_path)
    print(soc_post_path)
    print(naics_remaining_path)
    print(soc_remaining_path)
    print(naics_review_path)
    print(soc_review_path)
    print(notes_path)
    print(OUTPUT_DIR / "audit_crosswalk_analysis.md")


if __name__ == "__main__":
    main()
