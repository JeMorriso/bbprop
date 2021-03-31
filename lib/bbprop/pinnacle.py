import logging
from typing import Dict, Tuple

import requests

from bbprop.bet import Bet

logger = logging.getLogger(__name__)


class PinnacleNBA:
    id_ = 487
    categories = {
        "points": ("PTS",),
        "assists": ("AST",),
        "turnovers": ("TOV",),
        "3 point fg": ("FG3M",),
        "rebounds": ("REB",),
        "blocks": ("BLK",),
        "pts+rebs+asts": ("PTS", "REB", "AST"),
        "steals+blocks": ("STL", "BLK"),
        "double+double": ("DD2",),
        "triple+double": ("TD3",),
    }


class PinnacleNHL:
    id_ = 1456
    categories = {
        "points": ("PTS",),
        "goals": ("G",),
        "assists": ("A",),
        "shots on goal": ("SOG",),
        "saves": ("SV",),
    }


class Pinnacle:
    def __init__(self, league, run=False):
        self.league = league
        self.api_prefix = "http://guest.api.arcadia.pinnacle.com/0.1/leagues"
        self.straight = self.matchups = []
        self.props = []

        if run:
            self.run()

    def run(self):
        self.matchups, self.straight = self.fetch_data(self.api_prefix, self.league.id_)
        self.props = self.prop_bets(
            self.matchups, self.straight, self.league.categories
        )

    def fetch_data(self, prefix, id_):
        logger.info("Fetching Pinnacle data...")

        matchups = f"{prefix}/{id_}/matchups"
        straight = f"{prefix}/{id_}/markets/straight"

        data = []
        for r in [matchups, straight]:
            res = requests.get(r)
            data.append(res.json())

        return data

    def filter_matchups_props(self, matchups):
        def f(d):
            try:
                return d["special"]["category"] == "Player Props"
            except KeyError:
                return False

        filtered = list(filter(f, matchups))
        return filtered

    def filter_straight_props(self, straight, prop_ids):
        straight_props = [s for s in straight if s["matchupId"] in prop_ids]
        return straight_props

    def merge_matchups_and_straight(self, matchups, straight):
        m_dict = {m["id"]: m for m in matchups}
        s_dict = {s["matchupId"]: s for s in straight}
        props = {}
        for k, v in m_dict.items():
            to_pop = []
            if k in props:
                logger.warning(f"ID: {k} occurs multiple times in matchups. Skipping.")
                to_pop.append(k)
            elif k not in s_dict:
                logger.warning(f"ID: {k} doesn't have any prices. Skipping.")
            else:
                props[k] = {"matchup": v, "straight": s_dict[k]}
        for k in to_pop:
            props.pop(k, None)
        return props

    def validate_prop_alignments(self, alignments):
        # TODO: better checking
        home = alignments["home"]
        away = alignments["away"]
        return home, away

    def parse_alignments(self, participants):
        alignments = {}
        for p in participants:
            alignments[p["alignment"]] = p["name"]
        return alignments

    def parse_bet_options(self, matchup, straight):
        # TODO: potentially error checking here
        m_options = matchup["participants"]
        s_options = straight["prices"]
        s_options_dict = {s["participantId"]: s for s in s_options}
        options = []
        for o in m_options:
            options.append(
                {
                    "option": o["name"],
                    "points": s_options_dict[o["id"]]["points"],
                    "line": s_options_dict[o["id"]]["price"],
                }
            )
        return options

    def parse_matchup_id(self, matchup):
        return matchup["id"]

    def parse_matchup_ids(self, matchups):
        matchup_ids = [self.parse_matchup_id(m) for m in matchups]
        return set(matchup_ids)

    def parse_description(self, desc: str, categories: Dict) -> Tuple[str]:
        """Parse player description into name and scoring categories.

        Returns:
            Tuple of name and category string.
        """

        # TODO: regex
        oi = desc.find("(")
        ci = desc.find(")")
        if oi == -1 or ci == -1:
            logger.warning(f'Prop description is malformed: "{desc}".')
            return "", ()

        name = desc[:oi].strip()
        pin_cat = desc[oi + 1 : ci]  # noqa: E203
        try:
            cat = categories[pin_cat.lower()]
        except KeyError:
            logger.warning(f'Could not find scoring category "{pin_cat}".')
            cat = ()
        return name, cat

    def parse_prop(self, matchup, straight, categories):
        alignments = self.parse_alignments(matchup["parent"]["participants"])
        home, away = self.validate_prop_alignments(alignments)
        option_prices = self.parse_bet_options(matchup, straight)
        name, market = self.parse_description(
            matchup["special"]["description"], categories
        )

        bets = []
        for o in option_prices:
            option, points, line = [o[k] for k in ("option", "points", "line")]

            bets.append(Bet(home, away, name, option, market, points, line, "Pinnacle"))
        return bets

    def parse_props(self, merged, categories):

        bets = []
        for k, v in merged.items():
            m, s = [v[kk] for kk in ["matchup", "straight"]]
            try:
                bets.extend(self.parse_prop(m, s, categories))
            except:  # noqa: E722
                logger.exception("An exception occurred processing the following prop:")
                logger.error(f"Matchup:\n{m}")
                logger.error(f"Straight:\n{s}")
        return bets

    def prop_bets(self, matchups, straight, categories):
        matchups_props = self.filter_matchups_props(matchups)
        prop_ids = self.parse_matchup_ids(matchups_props)
        straight_props = self.filter_straight_props(straight, prop_ids)

        merged = self.merge_matchups_and_straight(matchups_props, straight_props)

        bets = self.parse_props(merged, categories)
        return bets
