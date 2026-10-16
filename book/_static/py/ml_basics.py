"""Chapter 4's toy machine learning, in plain Python so every step can be read.

A model here is a rule with numbers inside it. The numbers are the parameters;
'learning' is finding good ones. Data are the firm's illustrative monthly
returns from finance_basics (made up, not market data), in percent.
"""
from finance_basics import RETURNS, MARKET, SIZE, VALUE, MOMENTUM, MONTHS

# One row per month. Features are the benchmark returns; the label is Deere's return.
FEATURES = ["market", "size", "value", "momentum"]


def table(label="DE"):
    """(X, y): X is a list of rows [market, size, value, momentum], y the label for that month, all in percent."""
    X = [[100 * m, 100 * s, 100 * v, 100 * mo] for m, s, v, mo in zip(MARKET, SIZE, VALUE, MOMENTUM)]
    y = [100 * r for r in RETURNS[label]]
    return X, y


def column(X, j):
    """One feature as a list: the j-th number of every row."""
    return [row[j] for row in X]


def predict(w, b, row):
    """The model: a weighted sum of the features plus a starting point (a dot product)."""
    return sum(wi * xi for wi, xi in zip(w, row)) + b


def mse(y, pred):
    """Mean squared error: square each miss, then average. Big misses count far more."""
    return sum((a - p) ** 2 for a, p in zip(y, pred)) / len(y)


def mae(y, pred):
    """Mean absolute error: average size of a miss, no squaring."""
    return sum(abs(a - p) for a, p in zip(y, pred)) / len(y)


def fit_line(x, y):
    """Least squares for one feature: the slope and intercept with the smallest mean squared error (closed form)."""
    mx, my = sum(x) / len(x), sum(y) / len(y)
    slope = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    return slope, my - slope * mx


def gradient_step(X, y, w, b, lr):
    """One step of gradient descent: nudge every parameter a little in the direction that lowers the MSE."""
    n = len(y)
    err = [predict(w, b, row) - t for row, t in zip(X, y)]
    gw = [2 / n * sum(e * row[j] for e, row in zip(err, X)) for j in range(len(w))]
    gb = 2 / n * sum(err)
    return [wi - lr * g for wi, g in zip(w, gw)], b - lr * gb


def descend(X, y, lr=0.01, steps=50, w=None, b=0.0):
    """Run gradient descent from a starting guess; returns the history [(step, loss, w, b), ...]."""
    w = list(w) if w is not None else [0.0] * len(X[0])
    hist = [(0, mse(y, [predict(w, b, r) for r in X]), list(w), b)]
    for s in range(1, steps + 1):
        w, b = gradient_step(X, y, w, b, lr)
        hist.append((s, mse(y, [predict(w, b, r) for r in X]), list(w), b))
    return hist


def split_by_date(X, y, test_months=6):
    """Earlier months to learn from, the last few held back. Never shuffled: a model is used on months after the ones it studied."""
    k = len(y) - test_months
    return X[:k], y[:k], X[k:], y[k:]


if __name__ == "__main__":
    X, y = table()
    x = column(X, 0)
    s, i = fit_line(x, y)
    best = mse(y, [s * a + i for a in x])
    assert abs(sum(e for e in [t - (s * a + i) for a, t in zip(x, y)])) < 1e-9      # least squares leaves no average miss
    assert best <= mse(y, [(s + 0.1) * a + i for a in x]) and best <= mse(y, [s * a + i + 0.1 for a in x])
    # gradient descent on one feature walks to the closed-form answer
    h = descend([[a] for a in x], y, lr=0.005, steps=3000)
    assert abs(h[-1][2][0] - s) < 0.01 and abs(h[-1][3] - i) < 0.01, h[-1]
    assert all(h[k + 1][1] <= h[k][1] + 1e-12 for k in range(len(h) - 1))            # the loss never rises at a small step
    assert mae(y, [0] * len(y)) < mse(y, [0] * len(y))                               # percent misses above 1 square upward
    # next-month prediction: more flexible fit looks better on the past than the future
    Xt, yt = [[a] for a in x[:-1]], y[1:]
    Xa, ya, Xb, yb = split_by_date(Xt, yt, 6)
    sl, ic = fit_line(column(Xa, 0), ya)
    tr, te = mse(ya, [sl * r[0] + ic for r in Xa]), mse(yb, [sl * r[0] + ic for r in Xb])
    print("same-month fit: slope %.2f intercept %.2f loss %.2f" % (s, i, best))
    print("next-month: train %.2f test %.2f" % (tr, te))
    print("ml_basics ok")
