from chalice import Chalice

app = Chalice(app_name="bbprop-api")


@app.route("/nextjs")
def get_static_data():
    """Return data from most recent bet values .csv."""
    return {"hello": "world"}
