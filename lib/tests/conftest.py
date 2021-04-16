import json
import os

import pytest
import boto3
from dotenv import load_dotenv

from bbprop.pinnacle import Pinnacle, PinnacleNBA, PinnacleNHL
from bbprop.sportapi import BallDontLieAdapter
from bbprop.betrange import Last10, Last3, Last5, Season
from bbprop.storage import LeagueStorage, S3Storage

load_dotenv()


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
    with open("tests/json/NBA/players.json", "r") as f:
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
def s3storage():
    """S3Storage configured with tests/ directory as its root dir."""
    return S3Storage(
        session=boto3.session.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        ),
        bucket=os.getenv("S3_BUCKET"),
        dir="tests",
    )


@pytest.fixture
def s3storage_prod():
    return S3Storage(
        session=boto3.session.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        ),
        bucket=os.getenv("S3_BUCKET"),
        dir="",
    )


@pytest.fixture
def leaguestorage_NBA(s3storage_prod):
    return LeagueStorage(s3storage_prod, "NBA")
