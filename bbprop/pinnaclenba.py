import logging
from typing import Optional, Dict

from nba_api.stats.static import players

logger = logging.getLogger(__name__)


class PinnacleNBA:
    def player_from_description(self, desc: str) -> Optional[Dict]:
        """From Pinnacle prop description, find a player's name and NBA ID."""
        pl = desc.split()[:2]
        p_name = " ".join(pl)
        if not all(p.isalpha() for p in pl):
            logger.warning(f'Player name is malformed: "{p_name}".')
            return

        ps = players.find_players_by_full_name(p_name)
        if len(ps) == 0:
            logger.warning(f'Could not find player "{p_name}".')
        elif len(ps) > 1:
            logger.warning(f'Multiple player matches for "{p_name}".')
        else:
            return ps[0]
