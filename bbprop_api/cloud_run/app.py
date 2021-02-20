from flask import Flask, jsonify

# Add chromedriver binary to path.
import chromedriver_binary  # noqa: F401

from bbprop.pinnacle import Pinnacle
from bbprop.sportapi import NBA
from middlewares import s3storage, write_nba_game_logs


def create_app(
    driver_args=["--headless", "--disable-gpu", "--no-sandbox", "window-size=1024,768"]
):
    app = Flask(__name__)

    @app.route("/selenium")
    def scrape():
        with Pinnacle(*driver_args) as pin:
            pg = pin.league()

        return jsonify(pg.related)

    @app.route("/nba_game_logs")
    def nightly_game_logs():
        write_nba_game_logs(s3storage())
        # Return status code 200.
        return jsonify(success=True)

    @app.route("/test-s3-conn")
    def foo():
        # return jsonify(bucket=os.getenv("S3_BUCKET"))
        bucket = s3storage()

        df = bucket.csv_to_dataframe("game-logs/Andre Drummond.csv")
        return jsonify(df.to_json(orient="records"))

    @app.route("/test-nba-conn")
    def bar():
        nba = NBA()
        return jsonify(nba.player_by_name("Bradley Beal"))

    @app.route("/test-s3-player-names")
    def baz():
        bucket = s3storage()
        return jsonify(bucket.player_names())

    @app.route("/test-nba-season-game-log-by-name")
    def quux():
        nba = NBA()
        df = nba.season_game_log_by_name("Bradley Beal")
        return jsonify(df.to_json(orient="records"))

    @app.route("/test-s3-dataframe-to-csv")
    def qux():
        bucket = s3storage()

        df = bucket.csv_to_dataframe("game-logs/Andre Drummond.csv")
        bucket.dataframe_to_csv(df, "game-logs/Andre Drummond.csv")

        return jsonify(success=True)

    return app
