from nyc_property_finder.utils.hashing import generate_property_id


def test_generate_property_id_is_stable_for_same_inputs() -> None:
    first = generate_property_id(
        source="streeteasy",
        source_listing_id="123",
        address="1 Main St",
        lat=40.7128,
        lon=-74.006,
    )
    second = generate_property_id(
        source="  StreetEasy ",
        source_listing_id="123",
        address="1 MAIN ST",
        lat=40.7128001,
        lon=-74.0060001,
    )

    assert first == second
    assert first.startswith("prop_")


def test_generate_property_id_changes_when_listing_changes() -> None:
    first = generate_property_id("streeteasy", "123", "1 Main St", 40.7128, -74.006)
    second = generate_property_id("streeteasy", "456", "1 Main St", 40.7128, -74.006)

    assert first != second
