import json

from seleniumwire import webdriver

from bbprop.pinnacle import Pinnacle


class TestPinnacle(Pinnacle):
    def __init__(self):
        super().__init__()

        self.driver = webdriver.Chrome()


def test_game_id():
    id_ = 1249774441
    url1 = "https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441"
    url2 = "https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441/"

    with TestPinnacle() as pin:
        assert int(pin._game_id(url1)) == id_
        assert int(pin._game_id(url2)) == id_


def test_game():
    with TestPinnacle() as pin:
        data = pin.game(
            url="https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441"
        )
    print(data)


def test_build_props():
    ls = []
    for f in ["tests/json/straight.json", "tests/json/related.json"]:
        with open(f, "r") as ff:
            ls.append(json.load(ff))
    with TestPinnacle() as pin:
        pin.build_props(*ls)
