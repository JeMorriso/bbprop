from flask import Flask, jsonify

# Add chromedriver binary to path.
import chromedriver_binary  # noqa: F401

from bbprop.pinnacle import Pinnacle


def create_app(
    driver_args=["--headless", "--disable-gpu", "--no-sandbox", "window-size=1024,768"]
):
    app = Flask(__name__)

    @app.route("/selenium")
    def scrape():
        # TODO: return straight, related, and bets dictionary.
        with Pinnacle(*driver_args) as pin:
            pg = pin.league()

        return jsonify(pg.related)

    return app
