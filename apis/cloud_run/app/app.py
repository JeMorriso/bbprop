from flask import Flask, jsonify

# Add chromedriver binary to path.
import chromedriver_binary  # noqa: F401

from middlewares import driver


def create_app(
    driver_args=["--headless", "--disable-gpu", "--no-sandbox", "window-size=1024,768"]
):
    app = Flask(__name__)

    @app.route("/selenium")
    def scrape():
        # TODO: add exception handling.
        bet_values = driver(driver_args)
        return jsonify(bet_values), 200

    return app
