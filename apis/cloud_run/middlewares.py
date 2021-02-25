from datetime import datetime

import pandas as pd
import boto3

from bbprop.storage import S3Storage, LocalStorage, BallDontLieStorage
from bbprop.pinnacle import Pinnacle
from bbprop.sportapi import BallDontLieAdapter
from bbprop.betrange import BetRanges, Last3, Last5, Last10, Season

from docker_env import S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def s3storage():
    return S3Storage(
        # session=boto3.session.Session(profile_name="default"),
        session=boto3.session.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        ),
        bucket=S3_BUCKET,
    )


def get_player_ids():
    """Retrieve player ids from S3 bucket."""
    pass


def balldontliestorage_local():
    localstorage = LocalStorage("tests/localstorage")
    return BallDontLieStorage(localstorage)


def balldontliestorage_s3():
    return BallDontLieStorage(s3storage())


def pinnacle_names_to_balldontlie():
    """PJ Washington -> P.J. Washington"""
    pass


def retrieve_game_logs(pnames, store, season="2020-21"):
    players = store.players()
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


def store_bet_values_dataframe(df, store):
    # path = f"{store.bets_dir()}/{datetime.now().isoformat()}.csv"
    path = (
        f"{store.bets_dir()}/latest/{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}.csv"
    )
    # path = f"{store.bets_dir()}/foo.csv"
    store.store.dataframe_to_csv(df, path)


def driver(driver_args, bdl_store):

    with Pinnacle(*driver_args) as pin:
        pg = pin.league()
        pnames = list(set([p.name for p in pg.props]))
        game_logs = retrieve_game_logs(pnames, bdl_store)
        bets = assert_bets(pg.props, game_logs)

        bet_values = calc_bet_values(bets, game_logs)
        df = bet_values_dataframe(bet_values)

        store_bet_values_dataframe(df, bdl_store)

    return True
