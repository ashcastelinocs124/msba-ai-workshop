"""Chapter 5's toy unsupervised learning, in plain Python so every step can be read.

No labels here: the model gets the table of months and has to find structure in it
(groups, a shorter description, odd rows). Data are the firm's illustrative monthly
returns from finance_basics (made up, not market data), in percent.
"""
import math
from finance_basics import RETURNS, MARKET, SIZE, VALUE, MOMENTUM, MONTHS

NAMES = ["market", "size", "value", "momentum", "DE", "CAT"]
_SERIES = {"market": MARKET, "size": SIZE, "value": VALUE, "momentum": MOMENTUM, "DE": RETURNS["DE"], "CAT": RETURNS["CAT"]}


def months(names=("market", "size", "value", "momentum")):
    """One row per month, one number per name, in percent."""
    return [[100 * _SERIES[n][i] for n in names] for i in range(len(MONTHS))]


def standardize(rows):
    """Put every column on the same scale: subtract its average, divide by its spread. Returns (z, means, spreads)."""
    d = len(rows[0])
    means = [sum(r[j] for r in rows) / len(rows) for j in range(d)]
    sds = [math.sqrt(sum((r[j] - means[j]) ** 2 for r in rows) / (len(rows) - 1)) for j in range(d)]
    return [[(r[j] - means[j]) / sds[j] for j in range(d)] for r in rows], means, sds


def dist(a, b):
    """Straight-line distance between two rows."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def kmeans(rows, k, steps=50):
    """Group rows into k clusters. Returns (centers, labels).
    Start: the first row, then repeatedly the row farthest from every centre so far (so a run is repeatable).
    Then repeat: give each row to its nearest centre, move each centre to the average of its rows."""
    centers = [list(rows[0])]
    while len(centers) < k:
        far = max(rows, key=lambda r: min(dist(r, c) for c in centers))
        centers.append(list(far))
    labels = [0] * len(rows)
    for _ in range(steps):
        new = [min(range(k), key=lambda j: dist(r, centers[j])) for r in rows]
        if new == labels and _ > 0:
            break
        labels = new
        for j in range(k):
            mine = [r for r, l in zip(rows, labels) if l == j]
            if mine:
                centers[j] = [sum(r[c] for r in mine) / len(mine) for c in range(len(rows[0]))]
    return centers, labels


def inertia(rows, centers, labels):
    """How tight the groups are: the sum of squared distances from each row to its own centre. Lower is tighter."""
    return sum(dist(r, centers[l]) ** 2 for r, l in zip(rows, labels))


def pca(rows, n=2):
    """Principal components of standardized rows: the n directions along which the months vary most.
    Returns (components, shares): each component is a list of weights, one per column;
    each share is the fraction of all the variation that direction carries."""
    z, _, _ = standardize(rows)
    d, m = len(z[0]), len(z)
    cov = [[sum(r[a] * r[b] for r in z) / (m - 1) for b in range(d)] for a in range(d)]
    total = sum(cov[i][i] for i in range(d))
    comps, shares = [], []
    for _ in range(n):
        v = [1.0 / math.sqrt(d) + 0.01 * i for i in range(d)]
        for _ in range(500):                                   # power iteration: multiply by cov until the direction settles
            w = [sum(cov[a][b] * v[b] for b in range(d)) for a in range(d)]
            norm = math.sqrt(sum(x * x for x in w))
            v = [x / norm for x in w]
        lam = sum(v[a] * sum(cov[a][b] * v[b] for b in range(d)) for a in range(d))
        big = max(range(d), key=lambda i: abs(v[i]))
        if v[big] < 0:                                         # fix the sign so the biggest weight is positive
            v = [-x for x in v]
        comps.append(v)
        shares.append(lam / total)
        cov = [[cov[a][b] - lam * v[a] * v[b] for b in range(d)] for a in range(d)]   # remove it, find the next
    return comps, shares


def project(rows, comps):
    """Each month's coordinates on the chosen components (its short description)."""
    z, _, _ = standardize(rows)
    return [[sum(w * x for w, x in zip(c, r)) for c in comps] for r in z]


def odd_scores(rows):
    """How unusual each row is: its distance from the average row, with every column on the same scale."""
    z, _, _ = standardize(rows)
    return [dist(r, [0.0] * len(r)) for r in z]


def most_odd(scores, top=3):
    """Indexes of the `top` highest scores, highest first."""
    return sorted(range(len(scores)), key=lambda i: -scores[i])[:top]


if __name__ == "__main__":
    X = months()
    z, _, _ = standardize(X)
    for k in (1, 2, 3, 4, 5):
        c, l = kmeans(z, k)
        print(k, round(inertia(z, c, l), 1), [l.count(j) for j in range(k)])
    c, l = kmeans(z, 3)
    for j in range(3):
        print(j, [MONTHS[i] for i in range(24) if l[i] == j], [round(v, 2) for v in c[j]])
    comps, shares = pca(months(NAMES), 4)
    print([round(s, 3) for s in shares])
    for c_ in comps[:2]:
        print([round(v, 2) for v in c_])
    s = odd_scores(X)
    print([(MONTHS[i], round(s[i], 2)) for i in most_odd(s, 5)])
    s6 = odd_scores(months(NAMES))
    print([(MONTHS[i], round(s6[i], 2)) for i in most_odd(s6, 5)])
