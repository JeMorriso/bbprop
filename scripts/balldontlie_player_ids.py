import json
import time

import pandas as pd
import requests


def try_find_player(fname, lname):

    res = requests.get(f"{url}/players?search={lname}&per_page=100")
    results = res.json()["data"]

    matches = [
        x for x in results if fname == x["first_name"] and lname == x["last_name"]
    ]
    return matches


url = "https://balldontlie.io/api/v1"

df = pd.read_csv("scripts/data/NBA2021pergame.csv")
df["Player"] = df["Player"].str.split("\\").str[0]

players = {}

for i, row in df.iterrows():
    pname = row.loc["Player"]
    fname, *lname = pname.split()
    lname = " ".join(lname)

    matches = try_find_player(fname, lname)
    if not matches or len(matches) > 1:
        print(f"Couldn't find player {fname} {lname}")
    else:
        match = matches.pop()
        players[pname] = match

    time.sleep(1)

with open("scripts/data/balldontlie_players2.json", "w") as f:
    json.dump(players, f)
