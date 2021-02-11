import os

from chalice import Chalice, Cron
import boto3

from chalicelib.pinnacle_driver import driver
from chalicelib.bbprop.storage import S3Storage
from chalicelib.bbprop.sportapi import NBA

app = Chalice(app_name="bbprop-api")


@app.route("/")
def get_static_data():
    """Return data from most recent bet values .csv."""
    return {"hello": "world"}


# Run every hour
@app.schedule(Cron(0, 0 / 1, "*", "*", "?", "*"))
def get_prop_data(event):
    """Get prop bet data from Pinnacle and write to .csv."""
    print("hello from get_prop_data")
    s3 = S3Storage(
        session=boto3.session.Session(profile_name="default"),
        bucket=os.getenv("S3_BUCKET"),
    )
    driver(s3)
    pass


# Run every day at 11 AM UTC.
@app.schedule(Cron(0, 11, "*", "*", "?", "*"))
def get_nba_data(event):
    """Get player game logs from NBA API."""
    pass


###########################################################
# Test functions - build up lambda functionality
###########################################################
@app.lambda_function()
def nba_player_by_name(event, context):
    nba = NBA()
    return nba.player_by_name(event["player_name"])


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
