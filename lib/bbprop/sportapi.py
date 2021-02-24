import logging
import time
import functools

import requests
from requests.exceptions import ReadTimeout
from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerGameLogs
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


class NBA:
    """NBA API wrapper class."""

    def __init__(self):
        pass

    def player_by_name(self, name):
        """Get NBA API player dict.

        Does not require timeout_retry because using static data, not API.
        """
        ps = players.find_players_by_full_name(name)
        if len(ps) == 0:
            logger.warning(f'Could not find player "{name}".')
            return {}
        elif len(ps) > 1:
            logger.warning(f'Multiple player matches for "{name}".')
            return {}
        else:
            return ps[0]

    # season_game_log = timeout_retry(10)(season_game_log)
    @timeout_retry(10)
    def season_game_log(self, player_id, season):
        # season or date range...
        try:
            return PlayerGameLogs(
                player_id_nullable=player_id, season_nullable=season, proxy=self.proxy
            ).get_data_frames()[0]
        except IndexError:
            logger.warning(
                f"Player with id {player_id} has no game logs for season {season}."
            )
            return pd.DataFrame()

    def season_game_log_by_name(self, name, season):
        player = self.player_by_name(name)
        if player:
            return self.season_game_log(player["id"], season)
        else:
            return pd.DataFrame()


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
            return self.season_game_log(player["id"], season)
        else:
            return []


class BallDontLieAdapter(BallDontLie):
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
