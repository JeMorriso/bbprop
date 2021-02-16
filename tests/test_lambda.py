from chalice.test import Client
from bbprop_api.app import app


def test_nba_player_by_name():
    with Client(app) as client:
        res = client.lambda_.invoke(
            "nba_player_by_name", {"player_name": "Bradley Beal"}
        )
        assert res.payload["full_name"] == "Bradley Beal"
        # assert res.payload == {"event": {"player_name": "Bradley Beal"}}


def test_nba_player_game_log():
    with Client(app) as client:
        res = client.lambda_.invoke(
            "nba_player_by_name", {"player_name": "Bradley Beal"}
        )
        assert res.payload["full_name"] == "Bradley Beal"