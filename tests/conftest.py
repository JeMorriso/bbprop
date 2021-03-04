import json
from pathlib import Path
import os

import pytest
import pandas as pd
import boto3

from bbprop.pinnacle import Pinnacle, PinnacleGame
from bbprop.sportapi import NBA, BallDontLieAdapter
from bbprop.betrange import Last10, Last3, Last5, Season
from bbprop.storage import LocalStorage, S3Storage, BallDontLieStorage

# from bbprop_api.cloud_run.app import create_app


# @pytest.fixture
# def app():
#     return create_app(["--disable-gpu", "--no-sandbox", "window-size=1024,768"])


@pytest.fixture
def testpinnacle():
    with Pinnacle() as tp:
        yield tp


@pytest.fixture
def straight():
    with open("tests/json/straight.json", "r") as f:
        return json.load(f)


@pytest.fixture
def related():
    with open("tests/json/related.json", "r") as f:
        return json.load(f)


@pytest.fixture
def homepage_straight():
    with open("tests/json/nba-homepage-straight.json", "r") as f:
        return json.load(f)


@pytest.fixture
def homepage_matchups():
    with open("tests/json/nba-homepage-matchups.json", "r") as f:
        return json.load(f)


@pytest.fixture
def pinnaclegame(straight, related):
    return PinnacleGame(straight, related, False)


@pytest.fixture
def pinnaclegame2(homepage_straight, homepage_matchups):
    return PinnacleGame(homepage_straight, homepage_matchups, False)


@pytest.fixture
def nba():
    return NBA()


@pytest.fixture
def balldontlie():
    with open("tests/json/players/balldontlie_players.json", "r") as f:
        players = json.load(f)
    return BallDontLieAdapter(players)


# @pytest.fixture
# def betranges():
#     return BetRanges()


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
