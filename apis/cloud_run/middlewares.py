import pandas as pd
import requests

from bbprop.pinnacle import Pinnacle
from bbprop.sportapi import BallDontLieAdapter
from bbprop.betrange import BetRanges, Last3, Last5, Last10, Season

from docker_env import LAMBDA_API


def pinnacle_names_to_balldontlie():
    """PJ Washington -> P.J. Washington"""
    pass


def retrieve_players():
    res = requests.get(f"{LAMBDA_API}/players")
    return res.json()


def retrieve_game_logs(pnames, season="2020-21"):
    players = retrieve_players()
    bdla = BallDontLieAdapter(players)
    game_logs = {}
    for p in pnames:
        glg = bdla.season_game_log_by_name(p, season)
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


def driver(driver_args):

    with Pinnacle(*driver_args) as pin:
        pg = pin.league()
        if pg is None:
            return []

    pnames = list(set([p.name for p in pg.props]))
    game_logs = retrieve_game_logs(pnames)
    bets = assert_bets(pg.props, game_logs)

    bet_values = calc_bet_values(bets, game_logs)
    df = bet_values_dataframe(bet_values)

    return df.to_json(orient="records")
