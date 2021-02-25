import os

from chalice.test import Client
import requests

# import pytest

from apis.chalice.app import app


def test_nextjs_local():
    with Client(app) as client:
        res = client.http.get("/nextjs")
        assert res.json_body == {"hello": "world"}


def test_nextjs_remote():
    res = requests.get(f'{os.getenv("LAMBDA_API")}/nextjs')
    assert res.json() == {"hello": "world"}
    pass
