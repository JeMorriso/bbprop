from flask import Flask, jsonify
import chromedriver_binary  # Adds chromedriver binary to path

from bbprop.pinnacle import Pinnacle


def create_app(
    driver_args=["--headless", "--disable-gpu", "--no-sandbox", "window-size=1024,768"]
):
    app = Flask(__name__)

    @app.route("/selenium")
    def scrape():
        pin = Pinnacle(*driver_args)
        pg = pin.league()

        return jsonify(pg.related)

    return app
