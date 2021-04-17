import os
from datetime import datetime
from typing import Optional

from chalice import Chalice
import boto3
import requests
import pandas as pd

from chalicelib.storage import S3Storage, LeagueStorage

app = Chalice(app_name="bbprop-api")


def store_factory(league_root_dir, store=None):
    """Generate storage object if store is not None.

    Passing store as a parameter aids debugging.

    Only returns LeagueStorage with S3Storage, because LocalStorage does not implement
    the necessary functions e.g. find_file.
    """
    if store is None:
        store = LeagueStorage(
            S3Storage(boto3.session.Session(), "bbprop"), league_root_dir
        )

    return store


def store_bet_values_dataframe(df, store):
    """Store new bet values dataframe into 'latest' folder.

    Easiest way to designate file to use for new deployment.
    """
    path = f"{store.latest_dir}/{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}.csv"
    store.store.dataframe_to_csv(df, path)


def archive_latest_bet_values_file(store):
    """Move old bet values file out of 'latest' folder."""
    # There should only be 1 file in 'latest' directory...
    fs = store.store.find_files(store.latest_dir)
    for source in fs:
        fname = source.split("/")[-1]
        dest = f"{store.bets_dir}/{fname}"
        store.store.move_file(source, dest)


def fetch_and_store_data(league, store):
    res = requests.get(f'{os.getenv("GCLOUD_API")}/{league}')

    bet_values = pd.read_json(res.json(), orient="records")
    # If there are no bets (E.G. all-star break).
    if bet_values.empty:
        return False

    archive_latest_bet_values_file(store)
    store_bet_values_dataframe(bet_values, store)
    return True


def get_players_from_store(league: str, store: Optional[LeagueStorage] = None):
    """
    Args:
        league: League of interest.
        store: LeagueStorage object to use. This parameter is added to make debugging
            easier.
    """
    store = store_factory(league, store)
    players = store.players()
    return players


def get_latest_from_store(league: str, store: Optional[LeagueStorage] = None):
    """
    Args:
        league: League of interest.
        store: LeagueStorage object to use. This parameter is added to make debugging
            easier.
    """
    store = store_factory(league, store)
    latest = store.latest()
    return latest


@app.route("/nextjs")
def nextjs():
    """Used by Next.js during deployment."""
    # TODO: handle NHL using 2nd route
    return get_latest_from_store("nba")


@app.route("/nba-players")
def nba_players():
    """Send NBA players to Cloud Run."""
    return get_players_from_store("NBA")


@app.route("/nhl-players")
def nhl_players():
    """Send NHL players to Cloud Run."""
    return get_players_from_store("NHL")


@app.schedule("rate(1 hour)")
def fetch_and_deploy(event):
    """Trigger Cloud Run, Vercel deploy hook, and store bet values .csv.

    Lambda function must have permission to access S3 bucket.

    Returns:
        None
    """
    nba_store = store_factory("NBA")
    new_data = fetch_and_store_data("nba", nba_store)
    if new_data:
        requests.post(os.getenv("DEPLOY_HOOK"))
