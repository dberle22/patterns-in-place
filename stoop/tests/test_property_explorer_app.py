import pandas as pd

from nyc_property_finder.app.explorer import (
    PropertyFilters,
    apply_property_filters,
    available_poi_categories,
    display_category_counts,
    join_shortlist_status,
    load_shortlist,
    make_shortlist_id,
    parse_poi_category_counts,
    score_label,
    score_status_message,
    selected_property_id,
    sort_properties,
    table_exists,
    upsert_shortlist_row,
)
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.services.schema import initialize_database


def _context_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "property_id": "p1",
                "address": "1 Main St",
                "active": True,
                "listing_type": "rental",
                "source": "streeteasy_saved",
                "price": 3200,
                "beds": 1,
                "baths": 1,
                "nta_name": "Boerum Hill",
                "nearest_subway_distance_miles": 0.2,
                "poi_category_counts": '{"bookstores": 2, "restaurants": 1}',
                "property_fit_score": 78,
                "mobility_score": 92,
                "personal_fit_score": 55,
            },
            {
                "property_id": "p2",
                "address": "2 Broad St",
                "active": True,
                "listing_type": "sale",
                "source": "zillow_saved",
                "price": 900000,
                "beds": 2,
                "baths": 2,
                "nta_name": "Financial District",
                "nearest_subway_distance_miles": 0.8,
                "poi_category_counts": '{"museums": 1}',
                "property_fit_score": 66,
                "mobility_score": 80,
                "personal_fit_score": 20,
            },
            {
                "property_id": "p3",
                "address": "3 Old St",
                "active": False,
                "listing_type": "rental",
                "source": "streeteasy_saved",
                "price": 2500,
                "beds": 0,
                "baths": 1,
                "nta_name": "Boerum Hill",
                "nearest_subway_distance_miles": None,
                "poi_category_counts": "{}",
                "property_fit_score": None,
                "mobility_score": None,
                "personal_fit_score": None,
            },
        ]
    )


def test_parse_poi_category_counts_handles_json_dict_and_invalid_values() -> None:
    assert parse_poi_category_counts('{"bookstores": 2, "bad": "x", "zero": 0}') == {
        "bookstores": 2
    }
    assert parse_poi_category_counts({"restaurants": 3}) == {"restaurants": 3}
    assert parse_poi_category_counts("not json") == {}
    assert display_category_counts("{}") == "No nearby personal POIs in the MVP radius"
    assert display_category_counts('{"coffee_shops": 1}') == "coffee shops: 1"


def test_available_poi_categories_collects_context_json_keys() -> None:
    assert available_poi_categories(_context_fixture()) == ["bookstores", "museums", "restaurants"]


def test_apply_property_filters_uses_context_fields_and_poi_category_presence() -> None:
    filters = PropertyFilters(
        include_inactive=False,
        listing_types=("rental",),
        sources=("streeteasy_saved",),
        ntas=("Boerum Hill",),
        price_min=3000,
        price_max=4000,
        min_beds=1,
        min_baths=1,
        max_subway_distance_miles=0.5,
        min_property_fit_score=70,
        min_mobility_score=90,
        min_personal_fit_score=50,
        poi_categories=("bookstores",),
    )

    filtered = apply_property_filters(_context_fixture(), filters)

    assert filtered["property_id"].tolist() == ["p1"]


def test_sort_properties_uses_null_safe_stable_ordering() -> None:
    sorted_context = sort_properties(_context_fixture(), "Best overall fit")

    assert sorted_context["property_id"].tolist() == ["p1", "p2", "p3"]


def test_selected_property_id_keeps_current_selection_when_visible() -> None:
    context = _context_fixture()

    assert selected_property_id("p2", context) == "p2"
    assert selected_property_id("missing", context) == "p1"
    assert selected_property_id(None, pd.DataFrame()) is None


def test_score_labels_and_status_messages_do_not_zero_fill_null_scores() -> None:
    assert score_label(None) == "Unavailable"
    assert score_label(87.4) == "87/100"
    assert "Neighborhood metrics are unavailable" in score_status_message(
        "neighborhood", "unavailable"
    )
    assert "reweighted" in score_status_message(
        "property_fit", "reweighted_missing_components"
    )


def test_join_shortlist_status_adds_status_and_notes() -> None:
    context = _context_fixture()
    shortlist = pd.DataFrame(
        [{"property_id": "p1", "status": "active", "notes": "Tour this one"}]
    )

    joined = join_shortlist_status(context, shortlist)

    row = joined[joined["property_id"] == "p1"].iloc[0]
    assert row["shortlist_status"] == "active"
    assert row["shortlist_notes"] == "Tour this one"


def test_shortlist_upsert_persists_status_and_notes(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"
    initialize_database(database_path)

    assert table_exists(database_path, "property_explorer_gold.fct_user_shortlist")

    shortlist_id = upsert_shortlist_row(
        database_path,
        user_id="local_default",
        property_id="p1",
        status="active",
        notes="Tour this one",
    )
    assert shortlist_id == make_shortlist_id("local_default", "p1")

    upsert_shortlist_row(
        database_path,
        user_id="local_default",
        property_id="p1",
        status="archived",
        notes="Passed",
    )

    shortlist = load_shortlist(database_path, "local_default")

    assert len(shortlist) == 1
    assert shortlist.iloc[0]["status"] == "archived"
    assert shortlist.iloc[0]["notes"] == "Passed"

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        row_count = duckdb_service.query_df(
            "SELECT COUNT(*) AS n FROM property_explorer_gold.fct_user_shortlist"
        )["n"].iloc[0]

    assert row_count == 1

