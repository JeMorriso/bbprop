# import os

# import requests
# import pytest

# from app.app import app


# @pytest.fixture
# def app():
#     return create_app(["--disable-gpu", "--no-sandbox", "window-size=1024,768"])


# class TestLocal:
#     # See Pytest Flask docs about client - it's from Flask
#     def test_selenium(self, client, accept_json, app):
#         res = client.get("/selenium", headers=accept_json)
#         assert res.status_code == 200


# class TestDocker:
#     """Class for testing local Docker instance, and Docker instance deployed to Cloud
#     Run.
#     """

# @pytest.mark.parametrize(
#     "api_url", [(os.getenv("LOCAL_API")), (os.getenv("GCLOUD_API"))]
# )
# def test_selenium(self, api_url):
#     res = requests.get(f"{api_url}/selenium")
#     assert res.status_code == 200
