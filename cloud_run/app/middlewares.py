# import logging

import pandas as pd
import requests

from bbprop.pinnacle import Pinnacle, PinnacleNBA, PinnacleNHL
from bbprop.sportapi import BallDontLieAdapter, NHL
from bbprop.betrange import BetRanges, Last3, Last5, Last10, Season

from app.docker_env import LAMBDA_API

# logging.basicConfig(
#     level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)


class TranslationFactory:
    def __init__(self):
        self.pinnacle_to_bdl = {
            "PJ Washington": "P.J. Washington",
            "Robert Williams": "Robert Williams III",
            "Marcus Morris Sr.": "Marcus Morris",
        }
        self.player_dicts = {"NBA": {"Pinnacle": self.pinnacle_to_bdl}}

    def translator(self, league, sportsbook):
        name_dict = self.player_dicts[league][sportsbook]

        def f(name):
            return name_dict[name] if name in name_dict else name

        return f

    pass


def clean_player_names(props, fn):
    """Convert Pinnacle player names to BallDontLie player names on the prop dict."""
    # TODO: handle NHL, NBA - can use factory function
    for p in props:
        p.name = fn(p.name)
    return props


def retrieve_players():
    # TODO: need 2 different routes for NBA, NHL
    res = requests.get(f"{LAMBDA_API}/players")
    return res.json()


def retrieve_game_logs(pnames, sport_api, season="2020-21"):
    game_logs = {}
    for p in pnames:
        glg = sport_api.season_game_log_by_name(p, season)
        if not glg.empty:
            game_logs[p] = glg
    return game_logs


def assert_bets(bets, game_logs):
    """Return list of bets which have corresponding game logs."""
    return [b for b in bets if b.name in game_logs]


def ranges():
    """Return list of range-type objects to use."""
    return Last3(), Last5(), Last10(), Season()


def calc_bet_values(bets, game_logs):
    bet_values = []
    rs = ranges()
    for bet in bets:
        glg = game_logs[bet.name]
        br = BetRanges(bet, glg, *rs)
        br.calc_values()
        bet_values.append(br)
    return bet_values


def bet_values_dataframe(bet_values):
    bv_list = []
    for br in bet_values:
        bv_list.extend(br.to_list())
    return pd.DataFrame(bv_list)


# def driver(driver_args):

#     with Pinnacle(*driver_args) as pin:
#         pg = pin.league()
#         if pg is None:
#             return []

#     cleaned_props = clean_pinnacle_props(pg.props)
#     # pnames = list(set([p.name for p in pg.props]))
#     pnames = list(set([p.name for p in cleaned_props]))
#     game_logs = retrieve_game_logs(pnames)
#     # bets = assert_bets(pg.props, game_logs)
#     bets = assert_bets(cleaned_props, game_logs)

#     bet_values = calc_bet_values(bets, game_logs)
#     df = bet_values_dataframe(bet_values)

#     return df.to_json(orient="records")


def driver(pin, sport_api, league_name):

    tf = TranslationFactory()
    name_fn = tf.translator(league_name, "Pinnacle")
    cleaned_props = clean_player_names(pin.props, name_fn)

    pnames = list(set([p.name for p in cleaned_props]))
    game_logs = retrieve_game_logs(pnames, sport_api)
    bets = assert_bets(cleaned_props, game_logs)

    bet_values = calc_bet_values(bets, game_logs)
    df = bet_values_dataframe(bet_values)

    return df.to_json(orient="records")


def nhl_driver():
    return driver(Pinnacle(PinnacleNHL(), True), NHL(), "NHL")


def nba_driver():
    players = retrieve_players()
    return driver(Pinnacle(PinnacleNBA(), True), BallDontLieAdapter(players), "NBA")
