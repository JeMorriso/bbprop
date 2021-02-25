from flask import Flask, jsonify

# Add chromedriver binary to path.
import chromedriver_binary  # noqa: F401

# from bbprop.pinnacle import Pinnacle
from middlewares import driver, balldontliestorage_local, balldontliestorage_s3


def create_app(
    driver_args=["--headless", "--disable-gpu", "--no-sandbox", "window-size=1024,768"]
):
    app = Flask(__name__)

    @app.route("/selenium")
    def scrape():
        # TODO: add exception handling.
        driver(driver_args, balldontliestorage_s3())
        return jsonify(success=True), 200

    @app.route("/test-selenium")
    def test_scrape():
        """This route will only work on Flask because local storage."""
        driver(driver_args, balldontliestorage_local())
        return jsonify(success=True), 200
        # try:
        #     driver(driver_args, balldontliestorage_local())
        #     return jsonify(success=True), 200
        # except:
        #     return jsonify(success=False), 500

    return app
