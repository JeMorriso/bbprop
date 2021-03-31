import os

import requests
import pytest
from dotenv import load_dotenv

load_dotenv()


class TestLocal:
    # See Pytest Flask docs about client - it's from Flask
    def test_nba(self, client, accept_json):
        res = client.get("/nba", headers=accept_json)
        assert res.status_code == 200


class TestDocker:
    """Class for testing local Docker instance, and Docker instance deployed to Cloud
    Run.
    """

    @pytest.mark.parametrize(
        "api_url", [(os.getenv("LOCAL_API")), (os.getenv("GCLOUD_API"))]
    )
    def test_nba(self, api_url):
        res = requests.get(f"{api_url}/nba")
        assert res.status_code == 200
