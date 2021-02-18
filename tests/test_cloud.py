import os

import requests
import pytest

from pinnacle_driver import driver
from bbprop_api.cloud_run.middlewares import write_nba_game_logs


def test_driver_local(localstorage):
    driver(localstorage)


class TestLocal:
    # See Pytest Flask docs about client - it's from Flask
    def test_local_flask_app(self, client, accept_json, app):
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


class TestDocker:
    def test_docker_flask_app(self):
        # Docker container must be running locally
        res = requests.get("http://localhost:8080/selenium")
        assert len(res.json()) > 0

    def test_docker_flask_s3_conn(self):
        res = requests.get("http://localhost:8080/test-s3-conn")
        assert len(res.json()) > 0

    def test_docker_flask_nba_game_logs(self, s3storage):

        pass


class TestGCloud:
    def test_gcloud_flask_app(self):
        res = requests.get(f"{os.getenv('GCLOUD_API')}/selenium")
        assert len(res.json()) > 0
