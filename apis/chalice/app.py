import os

from chalice import Chalice
import boto3
import requests

from chalicelib.storage import S3Storage, BallDontLieStorage

app = Chalice(app_name="bbprop-api")


@app.route("/nextjs")
def scrape_and_deploy():
    """Trigger Cloud Run, Vercel deploy hook, and store bet values .csv.

    Lambda function must have permission to access S3 bucket.
    """
    #     res = requests.get(f'{os.getenv("GCLOUD_API")}/selenium')
    # store = S3Storage(boto3.session.Session(), bucket="bbprop")
    # store.csv_to_dataframe("bets/2021-02-25T21:15:38.csv")

    return {"hello": os.getenv("GCLOUD_API")}


@app.route("/players")
def players():
    """Send BallDontLie players to Cloud Run."""
    store = BallDontLieStorage(S3Storage(boto3.session.Session(), bucket="bbprop"))
    players = store.players()
    return players
