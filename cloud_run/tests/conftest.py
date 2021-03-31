import json

import pytest

from bbprop.pinnacle import Pinnacle, PinnacleNBA, PinnacleNHL
from bbprop.sportapi import BallDontLieAdapter
from app.middlewares import TranslationFactory
from app.app import app as a


@pytest.fixture
def app():
    """Fixture required for Pytest-Flask."""
    return a


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
    pinnaclenba.matchups = nba_matchups
    pinnaclenba.straight = nba_straight
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
def translationfactory():
    return TranslationFactory()


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
