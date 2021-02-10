import time

import pandas as pd

from bbprop.betrange import BetRanges


class TestPinnacle:
    def test_game_id(self, testpinnacle):
        id_ = 1249774441
        url1 = "https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441"
        url2 = "https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441/"

        pin = testpinnacle
        assert int(pin._game_id(url1)) == id_
        assert int(pin._game_id(url2)) == id_

    # Test requires NEW game link
    # def test_game(testpinnacle):
    #     data = testpinnacle.game(
    #         url="https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441"
    #     )
    #     print(data)


class TestPinnacleGame:
    def test_prop_bets(self, pinnaclegame):
        pinnaclegame.prop_bets()


class TestNBA:
    def test_player_by_name(self, pinnaclegame, nba):
        for prop in pinnaclegame.prop_bets():
            p = nba.player_by_name(prop.name)

            print(p)
            if p:
                assert "full_name" in p
            time.sleep(3)

    def test_season_game_log(self, pinnaclegame, nba):
        for prop in pinnaclegame.prop_bets():
            ids = {}
            if prop.name not in ids:
                ids[prop.name] = nba.player_by_name(prop.name)
                glg = nba.season_game_log(ids[prop.name]["id"], "2020-21")
                glg.to_csv(f"tests/csv/{prop.name} 2020-21.csv")

                time.sleep(3)


class TestBetRanges:
    def test_calc_values(self, pinnaclegame, gamelogs, last3, last5, last10, season):
        bets = pinnaclegame.prop_bets()
        bet_values = []
        for b in bets:
            br = BetRanges(b, gamelogs[b.name], last3, last5, last10, season)
            br.calc_values()
            bet_values.append(br)
        assert True

    def test_to_list(self, pinnaclegame, gamelogs, last3, last5, last10, season):
        bets = pinnaclegame.prop_bets()
        bet_values = []
        for b in bets:
            br = BetRanges(b, gamelogs[b.name], last3, last5, last10, season)
            br.calc_values()
            bet_values.append(br)

        bv_list = []
        for br in bet_values:
            bv_list.extend(br.to_list())

        df = pd.DataFrame(bv_list)
        assert True
