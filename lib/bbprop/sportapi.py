import logging
import time
import functools

from requests.exceptions import ReadTimeout

from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerGameLogs
import pandas as pd

logger = logging.getLogger(__name__)

"""Classes for interfacing with NBA and NHL APIs.

Extracting game logs for players is the name of the game.
"""


class NBA:
    def __init__(self):
        pass

    def timeout_retry(timeout):
        def timeout_args_wrapper(fn):
            @functools.wraps(fn)
            def wrapper(*args):
                while True:
                    try:
                        time.sleep(1)
                        return fn(*args)
                    except ReadTimeout:
                        time.sleep(timeout)

            return wrapper

        return timeout_args_wrapper

    # player_by_name = timeout_retry(10)(player_by_name)
    # @timeout_retry(10)
    def player_by_name(self, name):
        ps = players.find_players_by_full_name(name)
        if len(ps) == 0:
            logger.warning(f'Could not find player "{name}".')
            return {}
        elif len(ps) > 1:
            logger.warning(f'Multiple player matches for "{name}".')
            return {}
        else:
            return ps[0]

    # @timeout_retry(10)
    def season_game_log(self, player_id, season):
        # season or date range...
        try:
            return PlayerGameLogs(
                player_id_nullable=player_id, season_nullable=season
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
