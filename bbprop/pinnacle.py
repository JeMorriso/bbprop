import json
from typing import Dict, Tuple
import logging

from seleniumwire import webdriver

from bbprop.bet import Bet

logger = logging.getLogger(__name__)


class PinnacleGame:
    def __init__(self, straight, related, clean=True):
        """Store captured information about available bets on Pinnacle for a game.

        Attributes:
            straight: Response from Pinnacle, to merge.
            related: Response from Pinnacle, to merge.
        """
        self.straight = straight
        self.related = related

        self._props_dict = {}
        self.props = []

        if clean:
            # self._props_dict = self._build_props()
            self.props = self.prop_bets()

    def _parse_description(self, desc: str) -> Tuple[str]:
        """Parse player description into name and scoring categories.

        Returns:
            Tuple of name and category string.
        """
        translations = {
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

        oi = desc.find("(")
        ci = desc.find(")")
        if oi == -1 or ci == -1:
            logger.warning(f'Prop description is malformed: "{desc}".')
            return "", ()

        name = desc[:oi].strip()
        pin_cat = desc[oi + 1 : ci]
        try:
            cat = translations[pin_cat.lower()]
        except KeyError:
            logger.warning(f'Could not find scoring category "{pin_cat}".')
            cat = ()
        return name, cat

    def prop_bets(self) -> Dict:
        """Merge straight and related props.

        Return:
            Prop bet information merged into one dictionary.
        """

        def prop_filter(d):
            try:
                return d["special"]["category"] == "Player Props"
            except KeyError:
                return False

        def team(teams, alignment):
            return next(
                part["name"]
                for part in p["parent"]["participants"]
                if part["alignment"] == alignment
            )

        logger.info("Getting prop bets...")

        # Filter out prop bets.
        related = list(filter(prop_filter, self.related))
        straight_dict = {s["matchupId"]: s for s in self.straight}

        # Pull info from related list.
        bets = []
        for p in related:
            try:
                matchup_id = None

                bet_info = {"sportsbook": "Pinnacle"}

                matchup_id = p["id"]
                option_ids = {}

                options = p["participants"]
                for o in options:
                    option_ids[o["id"]] = o["name"]

                bet_info["name"], bet_info["market"] = self._parse_description(
                    p["special"]["description"]
                )

                teams = p["parent"]["participants"]
                bet_info["home"] = team(teams, "home")
                bet_info["away"] = team(teams, "away")

                bet_options = []
                straight_options = straight_dict[matchup_id]["prices"]
                for id_, name in option_ids.items():
                    match = next(
                        s for s in straight_options if s["participantId"] == id_
                    )
                    bet_options.append(
                        {
                            "option": name,
                            "points": match["points"],
                            "line": match["price"],
                        }
                    )
                for bo in bet_options:
                    bets.append(Bet(**bet_info, **bo))
            except (KeyError, TypeError):
                # Got TypeError one time in testing but not sure how.
                logger.warning(
                    f"Data for matchup with id {matchup_id} is not shaped as expected."
                )

        return bets


class Pinnacle:
    def __init__(self):
        self.base_url = "https://www.pinnacle.com/en/basketball/nba/matchups"

        opts = webdriver.ChromeOptions()
        opts.add_argument("--headless")

        self._props_dict = {}
        self.driver = webdriver.Chrome(options=opts)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def _game_id(self, url):
        """Return game ID from game URL.

        URL may have trailing forward slash.

        Example:
            https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441/
        """
        if url[-1] == "/":
            url = url[:-1]
        return url.split("/").pop()

    def _find_request(self, regex, url=None):
        """
        Find request matching search term from list of request requested by the browser.

        Args:
            regex: Regex search term.
            url: URL to go to.

        Returns:
            The matching request.

        Raises:
            TimeOutException: If regex doesn't lead to any matches.
        """
        if url is not None:
            del self.driver.requests
            self.driver.get(url)

        return self.driver.wait_for_request(regex)

    def iterate_games(self, tab_fn):
        pass

    def game(self, click_el=None, url=None):
        """Go to Pinnacle game page, capture relevant requests.

        Return:
            Object containing formatted list of bets.
        """
        del self.driver.requests

        logger.info("Intercepting game response files...")

        if url is not None:
            self.driver.get(url)
        elif click_el is not None:
            click_el.click()

        curr = self.driver.current_url
        game_id = self._game_id(curr)
        straight = f"guest.api.arcadia.pinnacle.com/0.1/matchups/{game_id}/markets/related/straight"
        related = f"guest.api.arcadia.pinnacle.com/0.1/matchups/{game_id}/related"

        data = []
        for r in [straight, related]:
            match = self._find_request(r)
            data.append(json.loads(match.response.body))

        return PinnacleGame(*data)

    def league(self):
        del self.driver.requests
        self.driver.get(self.base_url)

        logger.info("Intercepting league response files...")

        related = "guest.api.arcadia.pinnacle.com/0.1/leagues/487/matchups"
        straight = "guest.api.arcadia.pinnacle.com/0.1/leagues/487/markets/straight"

        data = []
        for r in [straight, related]:
            match = self._find_request(r)
            data.append(json.loads(match.response.body))

        return PinnacleGame(*data)
