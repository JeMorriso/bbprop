import time

import pandas as pd
import pytest
import requests

from bbprop.betrange import BetRanges
from pinnacle_driver import driver


class TestPinnacle:
    def test_game_id(self, testpinnacle):
        id_ = 1249774441
        url1 = "https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441"
        url2 = "https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441/"

        pin = testpinnacle
        assert int(pin._game_id(url1)) == id_
        assert int(pin._game_id(url2)) == id_

    # Test requires NEW game link
    # def test_game(testpinnacle):
    #     data = testpinnacle.game(
    #         url="https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441"
    #     )
    #     print(data)

    def test_league(self, testpinnacle):
        pg = testpinnacle.league()
        assert len(pg.props) > 0


class TestPinnacleGame:
    @pytest.mark.parametrize(
        "pin",
        [(pytest.lazy_fixture("pinnaclegame")), (pytest.lazy_fixture("pinnaclegame2"))],
    )
    def test_prop_bets(self, pin):
        pin.prop_bets()


class TestNBA:
    def test_player_by_name(self, pinnaclegame, nba):
        for prop in pinnaclegame.prop_bets():
            p = nba.player_by_name(prop.name)

            print(p)
            if p:
                assert "full_name" in p
            time.sleep(3)

    @pytest.mark.parametrize(
        "pin",
        [(pytest.lazy_fixture("pinnaclegame")), (pytest.lazy_fixture("pinnaclegame2"))],
    )
    def test_season_game_log(self, pin, nba):
        ids = {}
        for prop in pin.prop_bets():
            if "washington" in prop.name.lower():
                assert True
                pass
            if prop.name not in ids:
                try:
                    ids[prop.name] = nba.player_by_name(prop.name)
                    glg = nba.season_game_log(ids[prop.name]["id"], "2020-21")
                    glg.to_csv(f"tests/csv/game-logs/{prop.name}.csv")
                except KeyError:
                    pass
                time.sleep(3)


class TestBetRanges:
    @pytest.mark.parametrize(
        "pin",
        [(pytest.lazy_fixture("pinnaclegame")), (pytest.lazy_fixture("pinnaclegame2"))],
    )
    def test_calc_values(self, pin, gamelogs, last3, last5, last10, season):
        bets = pin.prop_bets()
        bet_values = []
        for b in bets:
            br = BetRanges(b, gamelogs[b.name], last3, last5, last10, season)
            br.calc_values()
            bet_values.append(br)
        assert len(bet_values) > 0

    @pytest.mark.parametrize(
        "pin",
        [(pytest.lazy_fixture("pinnaclegame")), (pytest.lazy_fixture("pinnaclegame2"))],
    )
    def test_to_list(self, pin, gamelogs, last3, last5, last10, season):
        bets = pin.prop_bets()
        bet_values = []
        for b in bets:
            try:
                br = BetRanges(b, gamelogs[b.name], last3, last5, last10, season)
                br.calc_values()
                bet_values.append(br)
            except KeyError:
                continue

        bv_list = []
        for br in bet_values:
            bv_list.extend(br.to_list())

        df = pd.DataFrame(bv_list)
        assert len(df) > 0


def test_driver_local(localstorage):
    driver(localstorage)


def test_s3_storage_write(localstorage, s3storage):
    df = localstorage.csv_to_dataframe(
        f"{localstorage.game_log_dir}/Andre Drummond.csv"
    )

    s3storage.dataframe_to_csv(df, "Andre Drummond.csv")


def test_s3_storage_read(s3storage):
    df = s3storage.csv_to_dataframe("Andre Drummond.csv")
    assert len(df) > 0


# See Pytest Flask docs about client - it's from Flask
def test_local_flask_app(client, accept_json, app):
    res = client.get("/selenium", headers=accept_json)
    assert len(res.json) > 0


def test_docker_flask_app():
    # Docker container must be running locally
    res = requests.get("http://localhost:8080/selenium")
    assert len(res.json()) > 0
