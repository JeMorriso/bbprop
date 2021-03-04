import os

from chalice.test import Client
from chalice import Chalice
import requests
from flask import jsonify
import boto3
import pandas as pd

from chalicelib.storage import LocalStorage, BallDontLieStorage, S3Storage
from apis.chalice.app import (
    app,
    store_bet_values_dataframe,
    archive_latest_bet_values_file,
)


testapp = Chalice(app_name="test-bbprop-api")


@testapp.route("/players")
def players():
    """Send BallDontLie players to Cloud Run."""
    store = BallDontLieStorage(LocalStorage("tests/json"))
    players = store.players()
    return players
    # return jsonify(players)


# @testapp.route('')


def fake_scrape_and_deploy(event):
    """It looks like Chalice doesn't offer a way to invoke a scheduled function
    locally.
    """
    res = requests.get(f'{os.getenv("GCLOUD_API")}/selenium')

    bet_values = pd.read_json(res.json(), orient="records")
    store = S3Storage(boto3.session.Session(), bucket="bbprop")
    store_bet_values_dataframe(bet_values, store)

    # res = requests.post(os.getenv("DEPLOY_HOOK"))


def test_nextjs_local():
    with Client(app) as client:
        res = client.http.get("/nextjs")
        assert len(res.json_body) > 0


def test_nextjs_remote():
    res = requests.get(f'{os.getenv("LAMBDA_API")}/nextjs')
    assert len(res.json()) > 0


def test_testapp_player():
    with Client(testapp) as client:
        res = client.http.get("/players")
        assert len(res.json_body) > 0


def test_app_player():
    res = requests.get(f'{os.getenv("LAMBDA_API")}/players')
    assert len(res.json()) > 0


def test_scrape_and_deploy():
    # Same test event on Lambda.
    fake_event = {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "1970-01-01T00:00:00Z",
        "region": "us-west-2",
        "resources": ["arn:aws:events:us-west-2:123456789012:rule/ExampleRule"],
        "version": "",
        "detail": {},
    }
    fake_scrape_and_deploy(fake_event)


def test_archive_previous_bet_values_file(tests3storage):
    latest_files = tests3storage.find_files(tests3storage.latest_dir)
    archive_latest_bet_values_file(tests3storage)
    # The directory itself matches...
    assert len(tests3storage.find_files(tests3storage.latest_dir)) == 1

    # put the files back
    for f in latest_files:
        if "csv" in f:
            fname = f.split("/")[-1]
            source = f"{tests3storage.bets_dir}/{fname}"
            dest = f"{tests3storage.latest_dir}/{fname}"
            tests3storage.find_file(f"{tests3storage.bets_dir}/{fname}")
            tests3storage.move_file(source, dest)

    assert len(tests3storage.find_files(tests3storage.latest_dir)) > 1


def test_store_bet_values_dataframe(tests3storage):
    df = tests3storage.csv_to_dataframe("tests/bar.csv")
    store_bet_values_dataframe(df, tests3storage)
