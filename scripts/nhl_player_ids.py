from time import sleep
import json

from nhlpy import team

if __name__ == "__main__":
    players = []
    # NHL team ids are in this range.
    for i in range(1, 55):
        t = team.Team(i)
        roster = t.roster()
        sleep(1)
        if "messageNumber" in roster:
            continue

        if not roster["teams"][0]["active"]:
            continue

        for p in roster["teams"][0]["roster"]["roster"]:
            players.append(p["person"])

    with open("tests/json/players/nhl_players.json", "w") as f:
        json.dump(players, f)
