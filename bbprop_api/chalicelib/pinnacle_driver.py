from datetime import datetime
import logging

import pandas as pd

from chalicelib.bbprop.pinnacle import Pinnacle
from chalicelib.bbprop.sportapi import NBA
from chalicelib.bbprop.betrange import Last10, Last3, Last5, Season, BetRanges

logger = logging.getLogger(__name__)


def gen_csvs(store, bets, csvs):
    nba = NBA()
    for bet in bets:
        if bet.name not in csvs:
            player = nba.player_by_name(bet.name)
            try:
                # Raises KeyError if player couldn't be found.
                glg = nba.season_game_log(player["id"], "2020-21")
                store.dataframe_to_csv(glg, f"{store.game_log_dir}/{bet.name}.csv")
                csvs = store.csv_dict()
            except KeyError:
                pass
    return csvs


def driver(store):
    pin = Pinnacle()
    pg = pin.league()

    csvs = gen_csvs(store, pg.props, store.csv_dict())
    # Filter out bets with missing game logs.
    bets = [p for p in pg.props if p.name in csvs]

    bet_values = []
    last3 = Last3()
    last5 = Last5()
    last10 = Last10()
    season = Season()
    for bet in bets:
        glg = store.csv_to_dataframe(csvs[bet.name])
        br = BetRanges(bet, glg, last3, last5, last10, season)
        br.calc_values()
        bet_values.append(br)

    bv_list = []
    for br in bet_values:
        bv_list.extend(br.to_list())

    store.dataframe_to_csv(
        pd.DataFrame(bv_list), f"{store.bets_dir}/{datetime.now().isoformat()}.csv"
    )


if __name__ == "__main__":
    driver()
