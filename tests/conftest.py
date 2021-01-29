import json

import pytest
from seleniumwire import webdriver

from bbprop.pinnaclenba import PinnacleNBA
from bbprop.pinnacle import Pinnacle, PinnacleGame


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