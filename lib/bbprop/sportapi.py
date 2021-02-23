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
        return self.players[name.lower()]

    @timeout_retry(10)
    def season_game_log(self, player_id, season):
        """Get player's game logs for season.

        season parameter looks like '2020'
        """
        res = requests.get(
            f"{self.url}/stats?seasons[]={season}&player_ids[]={player_id}&per_page=100"
        )
        return res.json()["data"]

        # TODO: season parameter of different form than NBA class
        pass

    def season_game_log_by_name(self, name, season):
        return self.season_game_log(self.players[name]["id"], season)


class BallDontLieAdapter(BallDontLie):
    def __init__(self, players):
        super().__init__(players)

    def _adapt_season_string(self, season):
        return season.split("-")[0]

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
        return self.season_game_log(self.players[name]["id"], season)
