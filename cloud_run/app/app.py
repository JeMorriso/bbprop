from flask import Flask, jsonify

# Add chromedriver binary to path.
import chromedriver_binary  # noqa: F401

from middlewares import nhl_driver, nba_driver

app = Flask(__name__)

# @app.route("/selenium")
# def scrape():
#     # TODO: add exception handling.
#     bet_values = driver(driver_args)
#     return jsonify(bet_values), 200


@app.route("/nhl")
def nhl():
    bet_values = nhl_driver()
    return jsonify(bet_values), 200


@app.route("/nba")
def nba():
    bet_values = nba_driver()
    return jsonify(bet_values), 200
