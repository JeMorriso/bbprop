import json

from seleniumwire import webdriver

from typing import List, Dict


class Pinnacle:
    def __init__(self):
        self.base_url = "https://www.pinnacle.com/en/basketball/nba/matchups"

        opts = webdriver.ChromeOptions()
        opts.add_argument("--headless")
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
        del self.driver.requests

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

        return data

    def filter_straight(self, criteria):
        """Filter out elements from straight dictionary that match criteria."""
        pass

    def build_props(self, straight: List[Dict], related: List[Dict]) -> Dict:
        """Merge straight and related props.

        Args:
            straight: Response from Pinnacle, to merge.
            related: Response from Pinnacle, to merge.

        Return:
            Prop bet information merged into one dictionary.
        """

        def prop_filter(d):
            try:
                return d["special"]["category"] == "Player Props"
            except KeyError:
                return False

        # Filter out prop bets.
        related_props = list(filter(prop_filter, related))

        # Pull info from related list.
        props = {}
        for p in related_props:
            k = p["id"]
            v = {"description": p["special"]["description"]}
            for part in p["participants"]:
                v[part["id"]] = {"name": part["name"]}
            props[k] = v

        # Merge info from straight list.
        for p in straight:
            if p["matchupId"] in props:
                for d in p["prices"]:
                    props[p["matchupId"]][d["participantId"]].update(d)

        return props
