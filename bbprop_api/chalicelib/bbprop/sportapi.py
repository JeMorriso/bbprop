import logging

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
