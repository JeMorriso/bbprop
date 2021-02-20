import json

import pytest

from bbprop.pinnacle import Pinnacle, PinnacleGame
from app.app import create_app


@pytest.fixture
def app():
    return create_app(["--disable-gpu", "--no-sandbox", "window-size=1024,768"])


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
