import pandas as pd

from nyc_property_finder.pipelines.build_tract_to_nta import read_tract_to_nta_equivalency


def test_read_tract_to_nta_equivalency_normalizes_source_columns(tmp_path) -> None:
    path = tmp_path / "tract_to_nta.csv"
    pd.DataFrame(
        [
            {
                "GEOID": "36061000100",
                "NTACode": "MN0101",
                "NTAName": "Test Manhattan NTA",
                "BoroName": "Manhattan",
                "CDTACode": "MN01",
                "CDTAName": "Test CDTA",
            }
        ]
    ).to_csv(path, index=False)

    mapping = read_tract_to_nta_equivalency(path)

    assert mapping.iloc[0]["tract_id"] == "36061000100"
    assert mapping.iloc[0]["nta_id"] == "MN0101"
    assert mapping.iloc[0]["nta_name"] == "Test Manhattan NTA"
    assert mapping.iloc[0]["borough"] == "Manhattan"
