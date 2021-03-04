import os
from datetime import datetime

from chalice import Chalice
import boto3
import requests
import pandas as pd

from chalicelib.storage import S3Storage, BallDontLieStorage

app = Chalice(app_name="bbprop-api")


def store_bet_values_dataframe(df, store):
    """Store new bet values dataframe into 'latest' folder.

    Easiest way to designate file to use for new deployment.
    """
    path = f"{store.latest_dir}/{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}.csv"
    store.dataframe_to_csv(df, path)


def archive_latest_bet_values_file(store):
    """Move old bet values file out of 'latest' folder."""
    # There should only be 1 file in 'latest' directory...
    fs = store.find_files(f"{store.latest_dir}/")
    for source in fs:
        if "csv" in source:
            fname = source.split("/")[-1]
            dest = f"{store.bets_dir}/{fname}"
            store.move_file(source, dest)


@app.route("/nextjs")
def nextjs():
    store = S3Storage(boto3.session.Session(), bucket="bbprop")
    latest_file = store.find_file(store.latest_dir)
    bet_values = store.csv_to_dataframe(latest_file)
    bv_json = bet_values.to_json(orient="records")
    return bv_json


@app.schedule("rate(1 hour)")
def scrape_and_deploy(event):
    """Trigger Cloud Run, Vercel deploy hook, and store bet values .csv.

    Lambda function must have permission to access S3 bucket.
    """
    res = requests.get(f'{os.getenv("GCLOUD_API")}/selenium')

    bet_values = pd.read_json(res.json(), orient="records")
    store = S3Storage(boto3.session.Session(), bucket="bbprop")
    archive_latest_bet_values_file(store)
    store_bet_values_dataframe(bet_values, store)

    res = requests.post(os.getenv("DEPLOY_HOOK"))

    # TODO: return?


@app.route("/players")
def players():
    """Send BallDontLie players to Cloud Run."""
    store = BallDontLieStorage(S3Storage(boto3.session.Session(), bucket="bbprop"))
    players = store.players()
    return players
