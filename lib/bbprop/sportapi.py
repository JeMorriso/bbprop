import logging
import time
import functools

import requests
from requests.exceptions import ReadTimeout
import pandas as pd

logger = logging.getLogger(__name__)

"""Classes for interfacing with NBA and NHL APIs.

Extracting game logs for players is the name of the game.
"""


def timeout_retry(timeout):
    def timeout_args_wrapper(fn):
        @functools.wraps(fn)
        def wrapper(*args):
            while True:
                try:
                    time.sleep(1)
                    return fn(*args)
                except ReadTimeout:
                    # TODO: not sure what type of exception would be thrown from
                    # BallDontLie.
                    time.sleep(timeout)

        return wrapper

    return timeout_args_wrapper


class NHL:
    """NHL API interface using nhlpy."""

    def __init__(self, players):
        self.players = players

    def player_by_name(self, name):
        pass

    def season_game_log(self, player_id, season):
        pass

    def season_game_log_by_name(self, player_name, season):
        pass


class BallDontLie:
    def __init__(self, players):
        self.url = "https://www.balldontlie.io/api/v1"
        self.players = {k.lower(): v for k, v in players.items()}

    def player_by_name(self, name):
        """Get the BallDontLie player from a name.

        Functions as a getter.
        """
        try:
            return self.players[name.lower()]
        except KeyError:
            logger.warning(f'Could not find player "{name}".')
            return {}

    @timeout_retry(10)
    def season_game_log(self, player_id, season):
        """Get player's game logs for season.

        season parameter looks like '2020'
        """
        res = requests.get(
            f"{self.url}/stats?seasons[]={season}&player_ids[]={player_id}&per_page=100"
        )
        data = res.json()["data"]
        if not data:
            logger.warning(
                f"Player with id {player_id} has no game logs for season {season}."
            )
        return data

    def season_game_log_by_name(self, name, season):
        player = self.player_by_name(name)
        if player:
            logger.info(f"Retrieving game logs for {name}...")
            return self.season_game_log(player["id"], season)
        else:
            return []


class BallDontLieAdapter(BallDontLie):
    """Adapt output from BallDontLie to the format returned from official NBA API."""

    def __init__(self, players):
        super().__init__(players)

    def _adapt_season_string(self, season):
        return season.split("-")[0]

    def _clean_game_logs(self, game_logs):
        def adapt_season_to_nba(season):
            return f"{season}-{season % 2000 + 1}"

        def count_double(game):
            count = 0
            for cat in ("ast", "blk", "stl", "pts", "reb"):
                count += int(game[cat] > 9)
            return count

        cleaned = []
        for g in game_logs:
            date_ = g["game"]["date"].split("T")[0]
            season = adapt_season_to_nba(g["game"]["season"])
            doubles = count_double(g)
            double_double = 1 if doubles > 1 else 0
            triple_double = 1 if doubles > 2 else 0
            pname = f"{g['player']['first_name']} {g['player']['last_name']}"

            cleaned.append(
                {
                    "GAME_DATE": date_,
                    "SEASON_YEAR": season,
                    "PTS": g["pts"],
                    "AST": g["ast"],
                    "STL": g["stl"],
                    "TOV": g["turnover"],
                    "FG3M": g["fg3m"],
                    "REB": g["reb"],
                    "BLK": g["blk"],
                    "DD2": double_double,
                    "TD3": triple_double,
                    "PLAYER_ID": g["player"]["id"],
                    "PLAYER_NAME": pname,
                    "PLAYER_FIRST_NAME": g["player"]["first_name"],
                    "PLAYER_LAST_NAME": g["player"]["last_name"],
                    "TEAM_ABBREVIATION": g["team"]["abbreviation"],
                    "TEAM_ID": g["team"]["id"],
                    "HOME_TEAM_ID": g["game"]["home_team_id"],
                    "AWAY_TEAM_ID": g["game"]["visitor_team_id"],
                }
            )
        return pd.DataFrame(cleaned)

    def season_game_log(self, player_id, season):
        """Get player's game logs for season, and convert into target format.

        Note that the season parameter is of the same form as NBA.season_game_log().
        Looks like '2020-21'
        """
        game_logs = super().season_game_log(
            player_id, self._adapt_season_string(season)
        )
        glg = pd.DataFrame(game_logs)
        return glg

    def season_game_log_by_name(self, name, season):
        player = self.player_by_name(name)
        if player:
            glg = super().season_game_log(player["id"], season)
            return self._clean_game_logs(glg)
        else:
            return pd.DataFrame()
