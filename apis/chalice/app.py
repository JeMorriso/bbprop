from chalice import Chalice
import boto3

from chalicelib.storage import S3Storage

app = Chalice(app_name="bbprop-api")


@app.route("/nextjs")
def get_static_data():
    """Return data from most recent bet values .csv.

    Lambda function must have permission to access S3 bucket.
    """
    store = S3Storage(boto3.session.Session(), bucket="bbprop")
    store.csv_to_dataframe("bets/2021-02-25T21:15:38.csv")
    pass

    return {"hello": "world"}
