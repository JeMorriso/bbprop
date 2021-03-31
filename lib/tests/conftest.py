import json
from pathlib import Path
import os

import pytest
import pandas as pd
import boto3

from bbprop.pinnacle import Pinnacle, PinnacleNBA, PinnacleNHL
from bbprop.sportapi import BallDontLieAdapter
from bbprop.betrange import Last10, Last3, Last5, Season
from bbprop.storage import LocalStorage, S3Storage, BallDontLieStorage

# from apis.cloud_run.middlewares import TranslationFactory


@pytest.fixture
def pinnaclenba():
    return Pinnacle(PinnacleNBA())


@pytest.fixture
def pinnaclenhl():
    return Pinnacle(PinnacleNHL())


@pytest.fixture
def pin_nba_merged(pinnaclenba, nba_matchups, nba_straight):
    nba_matchups = pinnaclenba.filter_matchups_props(nba_matchups)
    m_ids = pinnaclenba.parse_matchup_ids(nba_matchups)
    nba_straight = pinnaclenba.filter_straight_props(nba_straight, m_ids)
    merged = pinnaclenba.merge_matchups_and_straight(nba_matchups, nba_straight)
    return merged


@pytest.fixture
def pin_nhl_merged(pinnaclenhl, nhl_matchups, nhl_straight):
    nhl_matchups = pinnaclenhl.filter_matchups_props(nhl_matchups)
    m_ids = pinnaclenhl.parse_matchup_ids(nhl_matchups)
    nhl_straight = pinnaclenhl.filter_straight_props(nhl_straight, m_ids)
    merged = pinnaclenhl.merge_matchups_and_straight(nhl_matchups, nhl_straight)
    return merged


@pytest.fixture
def pin_nba_cleaned(pinnaclenba, nba_matchups, nba_straight):
    pinnaclenba.props = pinnaclenba.prop_bets(
        nba_matchups, nba_straight, pinnaclenba.league.categories
    )
    return pinnaclenba


@pytest.fixture
def pin_nhl_cleaned(pinnaclenhl, nhl_matchups, nhl_straight):
    pinnaclenhl.props = pinnaclenhl.prop_bets(
        nhl_matchups, nhl_straight, pinnaclenhl.league.categories
    )
    return pinnaclenhl


# @pytest.fixture
# def translationfactory():
#     return TranslationFactory()


@pytest.fixture
def nba_straight():
    with open("tests/json/pinnacle-nba-straight.json", "r") as f:
        return json.load(f)


@pytest.fixture
def nba_matchups():
    with open("tests/json/pinnacle-nba-matchups.json", "r") as f:
        return json.load(f)


@pytest.fixture
def nhl_straight():
    with open("tests/json/pinnacle-nhl-straight.json", "r") as f:
        return json.load(f)


@pytest.fixture
def nhl_matchups():
    with open("tests/json/pinnacle-nhl-matchups.json", "r") as f:
        return json.load(f)
    pass


@pytest.fixture
def balldontlie():
    with open("tests/json/players/balldontlie_players.json", "r") as f:
        players = json.load(f)
    return BallDontLieAdapter(players)


@pytest.fixture
def last3():
    return Last3()


@pytest.fixture
def last5():
    return Last5()


@pytest.fixture
def last10():
    return Last10()


@pytest.fixture
def season():
    return Season()


@pytest.fixture
def nba_gamelogs():
    dfs = {}
    p = Path("tests/csv/nba/game-logs")
    for fp in p.iterdir():
        with open(fp, "r") as f:
            # p_name = " ".join(str(fp).split()[:2]).split("/")[-1]
            p_name = str(fp).split("/")[-1].split(".")[0]
            dfs[p_name] = pd.read_csv(f)
    return dfs


@pytest.fixture
def balldontlie_gamelogs():
    dfs = {}
    p = Path("tests/csv/balldontlie/game-logs")
    for fp in p.iterdir():
        with open(fp, "r") as f:
            # p_name = " ".join(str(fp).split()[:2]).split("/")[-1]
            p_name = str(fp).split("/")[-1].split(".")[0]
            dfs[p_name] = pd.read_csv(f)
    return dfs


@pytest.fixture
def balldontliestorage_local():
    localstorage = LocalStorage("tests/json")
    return BallDontLieStorage(localstorage)


@pytest.fixture
def balldontliestorage_s3(s3storage):
    return BallDontLieStorage(s3storage)


@pytest.fixture
def localstorage():
    return LocalStorage("tests/csv")


@pytest.fixture
def s3storage():
    return S3Storage(
        # session=boto3.session.Session(profile_name="default"),
        session=boto3.session.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        ),
        bucket=os.getenv("S3_BUCKET"),
    )


@pytest.fixture
def tests3storage(s3storage):
    """Use test directories in s3 bucket."""
    s3storage.bets_dir = "tests"
    s3storage.latest_dir = "tests/test_sub"
    return s3storage
