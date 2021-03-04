import time

import pandas as pd
import pytest

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

    def test_league(self, testpinnacle):
        pg = testpinnacle.league()
        assert len(pg.props) > 0


class TestPinnacleGame:
    @pytest.mark.parametrize(
        "pin",
        [(pytest.lazy_fixture("pinnaclegame")), (pytest.lazy_fixture("pinnaclegame2"))],
    )
    def test_prop_bets(self, pin):
        pin.prop_bets()


class TestNBA:
    def test_player_by_name(self, pinnaclegame, nba):
        for prop in pinnaclegame.prop_bets():
            p = nba.player_by_name(prop.name)

            print(p)
            if p:
                assert "full_name" in p
            time.sleep(3)

    @pytest.mark.parametrize(
        "pin",
        [(pytest.lazy_fixture("pinnaclegame")), (pytest.lazy_fixture("pinnaclegame2"))],
    )
    def test_season_game_log(self, pin, nba):
        ids = {}
        for prop in pin.prop_bets():
            if "washington" in prop.name.lower():
                assert True
                pass
            if prop.name not in ids:
                try:
                    ids[prop.name] = nba.player_by_name(prop.name)
                    glg = nba.season_game_log(ids[prop.name]["id"], "2020-21")
                    glg.to_csv(f"tests/csv/nba/game-logs/{prop.name}.csv")
                except KeyError:
                    pass
                time.sleep(3)


class TestBallDontLieAdapter:
    @pytest.mark.parametrize(
        "pname, expected", [("Bradley Beal", 37), ("bradley beal", 37)]
    )
    def test_player_by_name(self, balldontlie, pname, expected):
        assert balldontlie.player_by_name(pname)["id"] == expected

    @pytest.mark.parametrize(
        "pin",
        [(pytest.lazy_fixture("pinnaclegame")), (pytest.lazy_fixture("pinnaclegame2"))],
    )
    def test_season_game_log_by_name(self, pin, balldontlie):
        # get unique players
        players = list(set([p.name for p in pin.prop_bets()]))

        for pname in players:
            glg = balldontlie.season_game_log_by_name(pname, "2020-21")
            if not glg.empty:
                glg.to_csv(f"tests/csv/balldontlie/game-logs/{pname}.csv")


class TestBetRanges:
    @pytest.mark.parametrize(
        "pin, gamelogs",
        [
            (pytest.lazy_fixture("pinnaclegame"), pytest.lazy_fixture("nba_gamelogs")),
            (pytest.lazy_fixture("pinnaclegame2"), pytest.lazy_fixture("nba_gamelogs")),
            (
                pytest.lazy_fixture("pinnaclegame"),
                pytest.lazy_fixture("balldontlie_gamelogs"),
            ),
            (
                pytest.lazy_fixture("pinnaclegame2"),
                pytest.lazy_fixture("balldontlie_gamelogs"),
            ),
        ],
    )
    def test_calc_values(self, pin, gamelogs, last3, last5, last10, season):
        bets = pin.prop_bets()
        bet_values = []
        for b in bets:
            if "washington" in b.name.lower():
                continue
            br = BetRanges(b, gamelogs[b.name], last3, last5, last10, season)
            br.calc_values()
            bet_values.append(br)
        assert len(bet_values) > 0

    @pytest.mark.parametrize(
        "pin, gamelogs",
        [
            (pytest.lazy_fixture("pinnaclegame"), pytest.lazy_fixture("nba_gamelogs")),
            (pytest.lazy_fixture("pinnaclegame2"), pytest.lazy_fixture("nba_gamelogs")),
            (
                pytest.lazy_fixture("pinnaclegame"),
                pytest.lazy_fixture("balldontlie_gamelogs"),
            ),
            (
                pytest.lazy_fixture("pinnaclegame2"),
                pytest.lazy_fixture("balldontlie_gamelogs"),
            ),
        ],
    )
    def test_to_list(self, pin, gamelogs, last3, last5, last10, season):
        bets = pin.prop_bets()
        bet_values = []
        for b in bets:
            try:
                br = BetRanges(b, gamelogs[b.name], last3, last5, last10, season)
                br.calc_values()
                bet_values.append(br)
            except KeyError:
                continue

        bv_list = []
        for br in bet_values:
            bv_list.extend(br.to_list())

        df = pd.DataFrame(bv_list)
        assert len(df) > 0


class TestStorage:
    def test_s3storage_write(self, localstorage, s3storage):
        df = localstorage.csv_to_dataframe(
            f"{localstorage.game_log_dir}/Andre Drummond.csv"
        )

        s3storage.dataframe_to_csv(df, "Andre Drummond.csv")

    def test_s3storage_read(self, s3storage):
        df = s3storage.csv_to_dataframe("game-logs/Andre Drummond.csv")
        assert len(df) > 0

    def test_s3storage_player_names(self, s3storage):
        s3storage.player_names()
        pass

    def test_s3storage_find_files(self, s3storage):
        keys = s3storage.find_files("bets/")
        assert keys
        pass

    def test_s3storage_find_file(self, s3storage):
        key = s3storage.find_file("bets/2021-03-04T16:51:52.csv")
        assert key

    def test_s3storage_move_file(self, s3storage):
        source = "tests/test_sub/foo.csv"
        dest = "tests/foo.csv"
        s3storage.move_file(source, dest)
        assert not s3storage.find_file(source)
        s3storage.move_file(dest, source)
        assert s3storage.find_file(source)

    @pytest.mark.parametrize(
        "bdl_store",
        [
            (pytest.lazy_fixture("balldontliestorage_local")),
            (pytest.lazy_fixture("balldontliestorage_s3")),
        ],
    )
    def test_balldontliestorage_players(self, bdl_store):
        assert len(bdl_store.players()) > 0
