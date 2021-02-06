import json
from pathlib import Path

import pytest
import pandas as pd
from seleniumwire import webdriver

from bbprop.pinnaclenba import PinnacleNBA
from bbprop.pinnacle import Pinnacle, PinnacleGame
from bbprop.sportapi import NBA
from bbprop.betrange import Last10, Last3, Last5, Season


class TestPinnacle(Pinnacle):
    def __init__(self):
        super().__init__()

        self.driver = webdriver.Chrome()


@pytest.fixture
def testpinnacle():
    with TestPinnacle() as tp:
        yield tp


@pytest.fixture
def pinnaclenba():
    return PinnacleNBA()


@pytest.fixture
def straight():
    with open("tests/json/straight.json", "r") as f:
        return json.load(f)


@pytest.fixture
def related():
    with open("tests/json/related.json", "r") as f:
        return json.load(f)


@pytest.fixture
def pinnaclegame(straight, related):
    return PinnacleGame(straight, related, False)


@pytest.fixture
def nba():
    return NBA()


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
def gamelogs():
    dfs = {}
    p = Path("tests/csv")
    for fp in p.iterdir():
        with open(fp, "r") as f:
            p_name = " ".join(str(fp).split()[:2]).split("/")[-1]
            dfs[p_name] = pd.read_csv(f)
    return dfs
