import pytest


@pytest.mark.parametrize(
    "desc, expected",
    [
        ("Isaac Okoro (Steals+Blocks)(must start)", "Isaac Okoro"),
        ("Foo Bar (Steals+Blocks)(must start)", {}),
        ("James (Steals+Blocks)(must start)", {}),
        ("", {}),
    ],
)
def test_player_from_description(desc, expected, pinnaclenba):
    result = pinnaclenba.player_from_description(desc)
    if not result:
        assert result == expected
    else:
        assert result["full_name"] == expected


@pytest.mark.parametrize(
    "desc, expected",
    [
        ("Isaac Okoro (Steals+Blocks)(must start)", ("stl", "blk")),
        ("Isaac Okoro (points)(must start)", ("pts")),
    ],
)
def test_categories_from_desscription(desc, expected, pinnaclenba):
    assert pinnaclenba.categories_from_description(desc) == expected


def test_merge_props_and_players(straight, related, testpinnacle, pinnaclenba):
    props = testpinnacle.build_props(straight, related)
    pinnaclenba.merge_props_and_players(props)
