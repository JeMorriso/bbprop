import pytest

from bbprop.pinnaclenba import PinnacleNBA


@pytest.mark.parametrize(
    "desc, expected",
    [
        ("Isaac Okoro (Steals+Blocks)(must start)", "Isaac Okoro"),
        ("Foo Bar (Steals+Blocks)(must start)", None),
        ("James (Steals+Blocks)(must start)", None),
        ("", None),
    ],
)
def test_player_from_description(desc, expected):
    result = PinnacleNBA().player_from_description(desc)
    if result is None:
        assert result == expected
    else:
        assert result["full_name"] == expected
