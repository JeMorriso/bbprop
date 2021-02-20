import os

import requests
import pytest

from pinnacle_driver import driver
from bbprop_api.cloud_run.middlewares import write_nba_game_logs


def test_driver_local(localstorage):
    driver(localstorage)


class TestLocal:
    # See Pytest Flask docs about client - it's from Flask
    def test_selenium(self, client, accept_json, app):
        res = client.get("/selenium", headers=accept_json)
        assert len(res.json) > 0

    @pytest.mark.parametrize(
        "store",
        [(pytest.lazy_fixture("localstorage")), (pytest.lazy_fixture("s3storage"))],
    )
    def test_write_nba_game_logs(self, store):
        old_count = len(store.player_names())
        write_nba_game_logs(store)
        new_count = len(store.player_names())
        assert old_count == new_count

    def test_get_nba_game_logs(self):
        pass

    def test_test_s3_conn(self, client, accept_json, app):
        res = client.get("/test-s3-conn", headers=accept_json)
        # res.json not res.json() - pytest-flask, not requests.
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

    @pytest.mark.parametrize(
        "api_url", [(os.getenv("LOCAL_API")), (os.getenv("GCLOUD_API"))]
    )
    def test_test_s3_conn(self, api_url):
        res = requests.get(f"{api_url}/test-s3-conn")
        assert len(res.json()) > 0

    @pytest.mark.parametrize(
        "api_url", [(os.getenv("LOCAL_API")), (os.getenv("GCLOUD_API"))]
    )
    def test_test_nba_conn(self, api_url):
        res = requests.get(f"{api_url}/test-nba-conn")
        assert len(res.json()) > 0

    @pytest.mark.parametrize(
        "api_url", [(os.getenv("LOCAL_API")), (os.getenv("GCLOUD_API"))]
    )
    def test_test_s3_player_names(self, api_url):
        res = requests.get(f"{api_url}/test-s3-player-names")
        assert len(res.json()) > 0

    @pytest.mark.parametrize(
        "api_url", [(os.getenv("LOCAL_API")), (os.getenv("GCLOUD_API"))]
    )
    def test_test_nba_season_game_log_by_name(self, api_url):
        res = requests.get(f"{api_url}/test-nba-season-game-log-by-name")
        assert len(res.json()) > 0

    @pytest.mark.parametrize(
        "api_url", [(os.getenv("LOCAL_API")), (os.getenv("GCLOUD_API"))]
    )
    def test_test_s3_dataframe_to_csv(self, api_url):
        res = requests.get(f"{api_url}/test-s3-dataframe-to-csv")
        assert len(res.json()) > 0

    @pytest.mark.parametrize(
        "api_url", [(os.getenv("LOCAL_API")), (os.getenv("GCLOUD_API"))]
    )
    def test_nba_game_logs(self, api_url, s3storage):
        """Test nba_game_logs route that will be run nightly.

        s3storage and storage object in container must point to the same bucket.
        """
        old_count = len(s3storage.player_names())
        res = requests.get(f"{api_url}/nba_game_logs")
        new_count = len(s3storage.player_names())
        assert old_count == new_count
        assert res.status_code == 200
