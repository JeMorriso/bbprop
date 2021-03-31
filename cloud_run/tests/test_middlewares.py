import pytest

from app.middlewares import retrieve_game_logs, clean_player_names, driver


def test_translation_factory(pin_nba_cleaned, translationfactory, balldontlie):
    name_fn = translationfactory.translator("NBA", "Pinnacle")
    cleaned = clean_player_names(pin_nba_cleaned.props, name_fn)
    for p in cleaned:
        assert p.name.lower() in balldontlie.players
    pass


def test_retrieve_game_logs(pin_nba_cleaned, balldontlie):
    # get unique players
    players = list(set([p.name for p in pin_nba_cleaned.props]))
    game_logs = retrieve_game_logs(players, balldontlie)
    for k, v in game_logs.items():
        assert not v.empty


def test_nba_driver(pin_nba_cleaned, balldontlie):
    # No need to test them all.
    pin_nba_cleaned.props = pin_nba_cleaned.props[:5]
    bet_values = driver(pin_nba_cleaned, balldontlie, "NBA")
    assert bet_values
