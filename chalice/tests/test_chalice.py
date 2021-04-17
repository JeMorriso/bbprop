import os

from chalice.test import Client
import requests
import pytest


# from app import app, fetch_and_store_data, get_players_from_store,
# get_latest_from_store
from app import (
    app,
    archive_latest_bet_values_file,
    get_players_from_store,
    get_latest_from_store,
)

########################################
# Local Chalice app
########################################


@pytest.mark.parametrize("league", ["nba", "nhl"])
def test_testapp_player(league):
    with Client(app) as client:
        res = client.http.get(f"/{league}-players")
        assert res.status_code == 200


@pytest.mark.parametrize("league", ["nba", "nhl"])
def test_app_player(league):
    res = requests.get(f'{os.getenv("LAMBDA_API")}/{league}-players')
    assert len(res.json()) > 0


########################################
# Lambda Chalice app
########################################


def test_nextjs_local():
    with Client(app) as client:
        res = client.http.get("/nextjs")
        assert len(res.json_body) > 0


def test_nextjs_remote():
    res = requests.get(f'{os.getenv("LAMBDA_API")}/nextjs')
    assert len(res.json()) > 0


########################################
# Middleware functions
########################################


def test_get_players_from_store(leaguestorage_NBA_test):
    data = get_players_from_store("", leaguestorage_NBA_test)
    assert len(data) > 0


def test_get_latest_from_store(leaguestorage_NBA_test):
    data = get_latest_from_store("", leaguestorage_NBA_test)
    assert len(data) > 0


def test_archive_latest_bet_values_file(leaguestorage_NBA_test, nba_latest):
    archive_latest_bet_values_file(leaguestorage_NBA_test)
    fs = leaguestorage_NBA_test.store.find_files(leaguestorage_NBA_test.latest_dir)
    assert nba_latest not in [f.split("/")[-1] for f in fs]
    # Move it back.
    leaguestorage_NBA_test.store.move_file(
        f"{leaguestorage_NBA_test.bets_dir}/{nba_latest}",
        f"{leaguestorage_NBA_test.latest_dir}/{nba_latest}",
    )
    fs = leaguestorage_NBA_test.store.find_files(leaguestorage_NBA_test.latest_dir)
    assert nba_latest in [f.split("/")[-1] for f in fs]
