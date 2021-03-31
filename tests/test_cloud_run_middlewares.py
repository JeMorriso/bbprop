import pytest

from apis.cloud_run.middlewares import (
    retrieve_game_logs,
    assert_bets,
    calc_bet_values,
    bet_values_dataframe,
    clean_player_names,
)


class TestMiddlewares:
    """Placed in this directory to take advantage of conftest.py."""

    def test_translation_factory(
        self, pin_nba_cleaned, translationfactory, balldontlie
    ):
        name_fn = translationfactory.translator("NBA", "Pinnacle")
        cleaned = clean_player_names(pin_nba_cleaned.props, name_fn)
        for p in cleaned:
            assert p.name.lower() in balldontlie.players
        pass

    # @pytest.mark.parametrize(
    #     "pin",
    #     [(pytest.lazy_fixture("pinnaclegame")), (pytest.lazy_fixture("pinnaclegame2"))],
    # )
    # def test_driver(self, pin, balldontlie_gamelogs):
    #     """Test the functions in 'driver' without actually scraping.

    #     Changes in driver need to be copied here...
    #     """
    #     cleaned_props = clean_pinnacle_props(pin.prop_bets())
    #     game_logs = balldontlie_gamelogs
    #     bets = assert_bets(cleaned_props, game_logs)

    #     bet_values = calc_bet_values(bets, game_logs)
    #     df = bet_values_dataframe(bet_values)
    #     assert len(df) > 0

    # @pytest.mark.parametrize(
    #     "pin",
    #     [(pytest.lazy_fixture("pinnaclegame")), (pytest.lazy_fixture("pinnaclegame2"))],
    # )
    # def test_retrieve_game_logs(self, pin, balldontliestorage_local):
    #     # get unique players
    #     players = list(set([p.name for p in pin.prop_bets()]))
    #     game_logs = retrieve_game_logs(players, balldontliestorage_local)
    #     for k, v in game_logs.items():
    #         assert not v.empty
