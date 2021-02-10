import numpy as np

from bbprop.bet_utils import norm_dist, american_to_implied_prob, bet_prob, edge

"""Classes for calculating a bet's value over different time ranges.

The classes following BetRanges all implement the slice method which returns the game
logs matching the time range's criteria.
"""


class BetRanges:
    """Given a bet and a list of time-oriented ranges, calculate bet values."""

    def __init__(self, bet, game_logs, *ranges):
        self.bet = bet
        self.game_logs = game_logs
        self.ranges = ranges

        self.values = []

    def calc_values(self):
        for r in self.ranges:
            dist, mean, var = norm_dist(r.slice(self.game_logs), self.bet.market)
            true_prob = bet_prob(dist, self.bet.points, self.bet.option)
            implied_prob = american_to_implied_prob(self.bet.line)
            edge_ = edge(true_prob, implied_prob)
            self.values.append(
                {
                    "range": str(r),
                    "avg": mean,
                    "std": np.sqrt(var),
                    "true": true_prob,
                    "implied": implied_prob,
                    "edge": edge_,
                }
            )

    def to_list(self):
        bets = []
        for v in self.values:
            bets.append({**vars(self.bet), **v})
        return bets


def slice_last_n(df, n):
    return df.sort_values(
        by="GAME_DATE",
        ascending=False,
    )[:n]


def slice_season(df, season):
    return df[df["SEASON_YEAR"] == season]


class Last3:
    def __str__(self):
        return "last 3"

    def slice(self, df):
        return slice_last_n(df, 3)


class Last10:
    def __str__(self):
        return "last 10"

    def slice(self, df):
        return slice_last_n(df, 10)


class Last5:
    def __str__(self):
        return "last 5"

    def slice(self, df):
        return slice_last_n(df, 5)


class Season:
    def __str__(self):
        return "season"

    def slice(self, df):
        return slice_season(df, "2020-21")
