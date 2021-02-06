import numpy as np

from bbprop.bet_utils import norm_dist, american_to_implied_prob, bet_prob, edge


class BetRanges:
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


class Last3:
    def __str__(self):
        return "last 3"

    def slice(self, df):
        return df
        pass


class Last10:
    def __str__(self):
        return "last 10"

    def slice(self, df):
        return df
        pass


class Last5:
    def __str__(self):
        return "last 5"

    def slice(self, df):
        return df
        pass


class Season:
    def __str__(self):
        return "season"

    def slice(self, df):
        return df
        pass
