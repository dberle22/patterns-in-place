import pandas as pd

from nyc_property_finder.pipelines.build_neighborhood_features import (
    add_missing_tract_feature_rows_from_mapping,
    build_nta_features,
    empty_tract_features_from_mapping,
)


def test_build_nta_features_aggregates_tract_features() -> None:
    tract_features = pd.DataFrame(
        [
            {"tract_id": "t1", "median_income": 100, "median_rent": 10, "median_home_value": 1000},
            {"tract_id": "t2", "median_income": 200, "median_rent": 20, "median_home_value": 2000},
        ]
    )
    for column in ["pct_bachelors_plus", "median_age", "crime_rate_proxy"]:
        tract_features[column] = pd.NA

    mapping = pd.DataFrame(
        [
            {"tract_id": "t1", "nta_id": "n1", "nta_name": "Test NTA", "borough": "Brooklyn"},
            {"tract_id": "t2", "nta_id": "n1", "nta_name": "Test NTA", "borough": "Brooklyn"},
        ]
    )

    nta_features = build_nta_features(tract_features, mapping)

    assert len(nta_features) == 1
    assert nta_features.iloc[0]["nta_id"] == "n1"
    assert nta_features.iloc[0]["borough"] == "Brooklyn"
    assert nta_features.iloc[0]["tract_count"] == 2
    assert nta_features.iloc[0]["median_income"] == 150


def test_build_nta_features_collapses_cross_borough_ntas_to_one_row() -> None:
    tract_features = pd.DataFrame(
        [
            {"tract_id": "t1", "median_income": 100, "median_rent": 10, "median_home_value": 1000},
            {"tract_id": "t2", "median_income": 200, "median_rent": 20, "median_home_value": 2000},
        ]
    )
    for column in ["pct_bachelors_plus", "median_age", "crime_rate_proxy"]:
        tract_features[column] = pd.NA

    mapping = pd.DataFrame(
        [
            {"tract_id": "t1", "nta_id": "n1", "nta_name": "Cross NTA", "borough": "Bronx"},
            {"tract_id": "t2", "nta_id": "n1", "nta_name": "Cross NTA", "borough": "Manhattan"},
        ]
    )

    nta_features = build_nta_features(tract_features, mapping)

    assert len(nta_features) == 1
    assert nta_features.iloc[0]["borough"] == "Bronx / Manhattan"
    assert nta_features.iloc[0]["tract_count"] == 2


def test_empty_tract_features_from_mapping_keeps_target_counties() -> None:
    mapping = pd.DataFrame(
        [
            {"tract_id": "36047000100", "nta_id": "bk1"},
            {"tract_id": "36061000100", "nta_id": "mn1"},
            {"tract_id": "36081000100", "nta_id": "qn1"},
        ]
    )

    features = empty_tract_features_from_mapping(mapping)

    assert features["tract_id"].tolist() == ["36047000100", "36061000100"]
    assert "median_income" in features.columns


def test_add_missing_tract_feature_rows_from_mapping_preserves_source_rows() -> None:
    tract_features = pd.DataFrame(
        [
            {
                "tract_id": "36047000100",
                "median_income": 100,
                "median_rent": 10,
                "median_home_value": 1000,
                "pct_bachelors_plus": 0.5,
                "median_age": 35,
                "crime_rate_proxy": pd.NA,
            }
        ]
    )
    mapping = pd.DataFrame(
        [
            {"tract_id": "36047000100", "nta_id": "bk1"},
            {"tract_id": "36047990100", "nta_id": "bk2"},
            {"tract_id": "36081000100", "nta_id": "qn1"},
        ]
    )

    features = add_missing_tract_feature_rows_from_mapping(tract_features, mapping)

    assert features["tract_id"].tolist() == ["36047000100", "36047990100"]
    assert features.loc[features["tract_id"] == "36047000100", "median_income"].iloc[0] == 100
    assert pd.isna(features.loc[features["tract_id"] == "36047990100", "median_income"].iloc[0])
