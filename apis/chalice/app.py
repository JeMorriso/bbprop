import os
from datetime import datetime

from chalice import Chalice
import boto3
import requests
import pandas as pd

from chalicelib.storage import S3Storage, BallDontLieStorage

app = Chalice(app_name="bbprop-api")


def store_bet_values_dataframe(df, store):
    path = f"{store.bets_dir}/{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}.csv"
    store.dataframe_to_csv(df, path)


@app.schedule("rate(1 hour)")
def scrape_and_deploy(event):
    """Trigger Cloud Run, Vercel deploy hook, and store bet values .csv.

    Lambda function must have permission to access S3 bucket.
    """
    res = requests.get(f'{os.getenv("GCLOUD_API")}/selenium')

    bet_values = pd.read_json(res.json(), orient="records")
    store = S3Storage(boto3.session.Session(), bucket="bbprop")
    store_bet_values_dataframe(bet_values, store)

    res = requests.post(os.getenv("DEPLOY_HOOK"))

    # TODO: return?


@app.route("/players")
def players():
    """Send BallDontLie players to Cloud Run."""
    store = BallDontLieStorage(S3Storage(boto3.session.Session(), bucket="bbprop"))
    players = store.players()
    return players
