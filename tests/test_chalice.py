import os

from chalice.test import Client
from chalice import Chalice
import requests
from flask import jsonify

from chalicelib.storage import LocalStorage, BallDontLieStorage
from apis.chalice.app import app


testapp = Chalice(app_name="test-bbprop-api")


@testapp.route("/players")
def players():
    """Send BallDontLie players to Cloud Run."""
    store = BallDontLieStorage(LocalStorage("tests/json"))
    players = store.players()
    return players
    # return jsonify(players)


def test_nextjs_local():
    with Client(app) as client:
        res = client.http.get("/nextjs")
        assert res.json_body == {"hello": "world"}


def test_nextjs_remote():
    res = requests.get(f'{os.getenv("LAMBDA_API")}/nextjs')
    assert res.json() == {"hello": "world"}
    pass


def test_testapp_player():
    with Client(testapp) as client:
        res = client.http.get("/players")
        assert len(res.json_body) > 0


def test_app_player():
    res = requests.get(f'{os.getenv("LAMBDA_API")}/players')
    assert len(res.json()) > 0
