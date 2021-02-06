import logging
from typing import Optional, Dict, List, Tuple

from nba_api.stats.static import players

logger = logging.getLogger(__name__)


class PinnacleNBA:
    def _parse_description(self, desc: str) -> Tuple[str]:
        """Parse player description into name and scoring categories.

        Returns:
            Tuple of name and category string.
        """
        oi = desc.find("(")
        ci = desc.find(")")
        if oi == -1 or ci == -1:
            logger.warning(f'Prop description is malformed: "{desc}".')
            return "", ""

        name = desc[:oi].strip()
        cat = desc[oi + 1 : ci]
        return name, cat

    def player_from_description(self, desc: str) -> Dict:
        """From Pinnacle prop description, find a player's name and NBA ID."""
        name, _ = self._parse_description(desc)

        if not name:
            return {}

        ps = players.find_players_by_full_name(name)
        if len(ps) == 0:
            logger.warning(f'Could not find player "{name}".')
            return {}
        elif len(ps) > 1:
            logger.warning(f'Multiple player matches for "{name}".')
            return {}
        else:
            return ps[0]

    def categories_from_description(self, desc: str) -> Tuple[str]:
        """From Pinnacle prop description, find the prop's scoring categories, as named
        in NBA API.

        Returns:
            Tuple of categories the prop includes.
        """
        translations = {
            "points": ("pts"),
            "assists": ("ast"),
            "turnovers": ("tov"),
            "3 point fg": ("fg3m"),
            "rebounds": ("reb"),
            "pts+rebs+asts": ("pts", "reb", "ast"),
            "steals+blocks": ("stl", "blk"),
            "double+double": ("dd2"),
        }
        _, cat = self._parse_description(desc)
        cat = cat.lower()
        try:
            return translations[cat]
        except KeyError:
            logger.warning(f'Could not find scoring category "{cat}".')
            return ()

    def merge_props_and_players(self, props: Dict):
        """Get NBA player information for each prop bet dict."""
        merged = []
        for id_, p in props.items():
            desc = p["description"]
            player = self.player_from_description(desc)
            cats = self.categories_from_description(desc)
            if not player or not cats:
                continue

            m = {
                "name": player["full_name"],
            }
