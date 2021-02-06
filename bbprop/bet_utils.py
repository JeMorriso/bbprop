import numpy as np

from scipy import stats


def norm_dist(df, cols):
    """Find the normal distribution for cols from avg and std dev."""
    try:
        rv_means = [df[c].mean() for c in cols]
    except KeyError:
        pass

    # Separating cases makes it easier because index error in j loop on single variable.
    if len(cols) == 1:
        mean = df[cols[0]].mean()
        # sample variance
        var = df[cols[0]].var()
    else:
        samples = [df[c] for c in cols]
        # sample covariance
        cov = np.cov(samples)
        rv_vars = [cov[i][i] for i in range(len(cov))]
        term = 0
        for i in range(1, len(cov)):
            for j in range(i, len(cov)):
                term += 2 * cov[i][j]
        mean = sum(rv_means)
        var = sum(rv_vars) + term

    dist = stats.norm(mean, np.sqrt(var))

    return dist, mean, var


def american_to_implied_prob(line):
    if line < 0:
        return -line / (100 - line)
    else:
        return 100 / (line + 100)


def bet_prob(dist, points, option):
    if option == "under":
        return dist.cdf(points)
    else:
        return 1 - dist.cdf(points)


def edge(true_prob, implied_prob):
    return true_prob - implied_prob
