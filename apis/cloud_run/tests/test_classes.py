import os

import requests
import pytest


class TestLocal:
    # See Pytest Flask docs about client - it's from Flask
    def test_selenium(self, client, accept_json, app):
        res = client.get("/selenium", headers=accept_json)
        assert len(res.json) > 0


class TestDocker:
    """Class for testing local Docker instance, and Docker instance deployed to Cloud
    Run.
    """

    @pytest.mark.parametrize(
        "api_url", [(os.getenv("LOCAL_API")), (os.getenv("GCLOUD_API"))]
    )
    def test_selenium(self, api_url):
        res = requests.get(f"{api_url}/selenium")
        assert len(res.json()) > 0


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
