"""Foundations for ML: the finance every model in Part II is built on.

Prices, returns, risk, benchmarks, data timing and a first regression, all in plain Python
(no numpy: Pyodide loads packages only from a cell's own imports). The numbers are ILLUSTRATIVE,
made up for teaching: 24 months of returns for Deere (DE), Caterpillar (CAT), a market index and
three factor benchmarks. They are not market data. Month 0 is Oct 2024; month 23 is Sep 2026.
"""
import math

MONTHS = ["Oct 24", "Nov 24", "Dec 24", "Jan 25", "Feb 25", "Mar 25", "Apr 25", "May 25", "Jun 25", "Jul 25", "Aug 25", "Sep 25",
          "Oct 25", "Nov 25", "Dec 25", "Jan 26", "Feb 26", "Mar 26", "Apr 26", "May 26", "Jun 26", "Jul 26", "Aug 26", "Sep 26"]

# Monthly returns, as fractions (0.0086 = +0.86%).
MARKET = [0.0086, -0.0166, 0.0233, 0.0585, 0.0706, 0.032, 0.01, -0.0021, -0.0093, -0.032, -0.0531, -0.0618, 0.0478, 0.0058, 0.0462, -0.0464, 0.018, 0.0074, 0.0339, -0.0012, 0.0442, 0.0462, 0.0594, -0.0718]
SIZE = [-0.0237, 0.0292, 0.0526, 0.0111, -0.0058, 0.0251, 0.0053, 0.0052, 0.028, 0.0023, -0.0331, -0.0128, 0.0135, -0.0159, 0.0087, -0.01, 0.0121, -0.0093, 0.0193, -0.0063, -0.0207, 0.0116, 0.0084, 0.0039]
VALUE = [-0.036, -0.009, 0.0265, 0.0091, -0.0278, 0.0338, 0.0129, 0.0013, -0.0093, -0.0012, 0.0146, -0.0564, -0.0069, -0.0298, 0.0129, 0.0048, 0.0027, 0.0123, 0.0442, 0.0491, -0.0294, 0.0465, 0.0049, -0.0411]
MOMENTUM = [0.0436, -0.0202, -0.0155, 0.0316, -0.0019, 0.0089, 0.0414, 0.0146, -0.0756, -0.0074, -0.0363, -0.0341, -0.0352, 0.0098, 0.0072, -0.0032, 0.0356, 0.0078, -0.0043, 0.0346, 0.0208, 0.0111, 0.0375, 0.0278]
RISK_FREE = [0.0035] * 24   # about 4.3% a year, paid monthly

RETURNS = {
    "DE": [0.0002, -0.0156, 0.0303, 0.0429, 0.143, 0.0623, -0.0545, 0.0035, -0.0284, -0.0655, -0.0669, -0.0805, 0.0887, -0.0112, 0.0538, -0.0353, -0.0482, -0.0356, 0.0137, 0.0464, 0.0277, 0.0372, 0.0427, -0.1365],
    "CAT": [0.0086, -0.0313, 0.0492, 0.0959, 0.1035, 0.0601, -0.0025, 0.0047, -0.0242, -0.0444, -0.0278, -0.1255, 0.0728, 0.0096, 0.063, -0.0777, 0.0231, 0.0034, 0.0224, -0.0186, -0.004, 0.0588, 0.1594, -0.1386],
    "MKT": MARKET,
}
# Month-end price before the first return, so that the last price is today's price in tools.PRICES (DE 512.40, CAT 398.15).
START = {"DE": 527.71, "CAT": 331.01, "MKT": 100.0}


def prices(ticker):
    """The 25 month-end prices (Sep 24 to Sep 26) built from START and the monthly returns."""
    p = [START[ticker]]
    for r in RETURNS[ticker]:
        p.append(round(p[-1] * (1 + r), 2))
    return p


def simple_returns(p):
    """Simple return: the price change as a fraction of the old price."""
    return [p[i + 1] / p[i] - 1 for i in range(len(p) - 1)]


def log_returns(p):
    """Log return: ln(new price / old price). Adds up across months; simple returns do not."""
    return [math.log(p[i + 1] / p[i]) for i in range(len(p) - 1)]


def compound(returns):
    """Total return over the whole period: multiply (1 + r) across months, then subtract 1."""
    t = 1.0
    for r in returns:
        t *= 1 + r
    return t - 1


def excess(returns, rf=RISK_FREE):
    """Excess return: what you earned over what cash would have paid."""
    return [r - f for r, f in zip(returns, rf)]


def mean(x):
    return sum(x) / len(x)


def stdev(x):
    """Sample standard deviation (divides by n - 1)."""
    m = mean(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))


def annual_return(returns):
    """Compounded return scaled to a year, from monthly returns."""
    return (1 + compound(returns)) ** (12 / len(returns)) - 1


def annual_vol(returns):
    """Volatility: the monthly standard deviation scaled to a year by the square root of 12."""
    return stdev(returns) * math.sqrt(12)


def drawdowns(p):
    """At each date, how far the price is below its highest earlier price (0 at a new high, else negative)."""
    peak, out = p[0], []
    for v in p:
        peak = max(peak, v)
        out.append(v / peak - 1)
    return out


def max_drawdown(p):
    """The worst peak-to-trough fall: (depth, index of the peak, index of the trough)."""
    peak_i, worst, w_peak, w_trough = 0, 0.0, 0, 0
    for i, v in enumerate(p):
        if v > p[peak_i]:
            peak_i = i
        d = v / p[peak_i] - 1
        if d < worst:
            worst, w_peak, w_trough = d, peak_i, i
    return worst, w_peak, w_trough


def sharpe(returns, rf=RISK_FREE):
    """Sharpe ratio: average excess return per unit of volatility, scaled to a year."""
    e = excess(returns, rf)
    return mean(e) / stdev(e) * math.sqrt(12)


def corr(x, y):
    mx, my = mean(x), mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def ols(x, y):
    """Fit y = intercept + slope * x by least squares: (intercept, slope, r_squared)."""
    mx, my = mean(x), mean(y)
    slope = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    intercept = my - slope * mx
    ss_res = sum((b - intercept - slope * a) ** 2 for a, b in zip(x, y))
    ss_tot = sum((b - my) ** 2 for b in y)
    return intercept, slope, 1 - ss_res / ss_tot


def alpha_beta(stock, market=MARKET, rf=RISK_FREE):
    """Regress the stock's excess return on the market's: alpha (a month), beta, r_squared."""
    return ols(excess(market, rf), excess(stock, rf))


def split_by_time(x, frac=0.75):
    """Train on the early part, test on the later part. Never shuffle a time series."""
    k = int(len(x) * frac)
    return x[:k], x[k:]


# Valuation: price over the last twelve months of earnings per share (tools.PRICES for the price).
FUNDAMENTALS = {
    "DE": {"price": 512.40, "eps_ttm": 25.60, "book_per_share": 71.20, "dividend": 6.40},
    "CAT": {"price": 398.15, "eps_ttm": 21.90, "book_per_share": 44.80, "dividend": 5.80},
}


def valuation(ticker):
    """Price-to-earnings, price-to-book and dividend yield from FUNDAMENTALS."""
    f = FUNDAMENTALS[ticker]
    return {"pe": f["price"] / f["eps_ttm"], "pb": f["price"] / f["book_per_share"], "yield": f["dividend"] / f["price"]}


# Macro releases: what a model could have known on a given day. Each row is one figure, the date it was first
# published, the first value, and (if revised) the date and value of the revision. Illustrative.
MACRO = [
    {"series": "CPI inflation, year on year", "period": "Aug 26", "freq": "monthly", "first": "2026-09-11", "value": 3.1, "revised": None, "revised_value": None},
    {"series": "Unemployment rate", "period": "Aug 26", "freq": "monthly", "first": "2026-09-04", "value": 4.3, "revised": None, "revised_value": None},
    {"series": "Nonfarm payrolls, change (thousands)", "period": "Aug 26", "freq": "monthly", "first": "2026-09-04", "value": 142, "revised": "2026-10-02", "revised_value": 96},
    {"series": "Real GDP growth, annualized", "period": "Q2 26", "freq": "quarterly", "first": "2026-07-30", "value": 2.6, "revised": "2026-08-27", "revised_value": 2.1},
    {"series": "Fed funds target, upper bound", "period": "Sep 26", "freq": "8 meetings a year", "first": "2026-09-16", "value": 4.50, "revised": None, "revised_value": None},
]


def known_on(series, date):
    """The value a model could have used on `date` (YYYY-MM-DD): the revised figure only after its revision date."""
    for m in MACRO:
        if m["series"] == series:
            if date < m["first"]:
                return None
            if m["revised"] and date >= m["revised"]:
                return m["revised_value"]
            return m["value"]
    raise KeyError(series)


if __name__ == "__main__":
    p = prices("DE")
    assert len(p) == 25 and abs(p[-1] - 512.40) < 0.5 and abs(prices("CAT")[-1] - 398.15) < 0.5
    assert abs(sum(log_returns(p)) - math.log(p[-1] / p[0])) < 1e-9          # log returns add up
    assert abs(compound(simple_returns(p)) - (p[-1] / p[0] - 1)) < 1e-9
    d, a, b = max_drawdown(p)
    assert d < 0 and a < b and abs(drawdowns(p)[b] - d) < 1e-9
    assert abs(corr(MARKET, MARKET) - 1) < 1e-9
    i, s, r2 = ols([1, 2, 3, 4], [3, 5, 7, 9]); assert abs(s - 2) < 1e-9 and abs(i - 1) < 1e-9 and abs(r2 - 1) < 1e-9
    al, be, r2 = alpha_beta(RETURNS["DE"]); assert 0.8 < be < 1.5 and 0 < r2 < 1
    assert round(valuation("DE")["pe"], 1) == 20.0
    assert known_on("Nonfarm payrolls, change (thousands)", "2026-09-10") == 142 and known_on("Nonfarm payrolls, change (thousands)", "2026-10-05") == 96
    assert known_on("CPI inflation, year on year", "2026-09-01") is None
    tr, te = split_by_time(MARKET); assert len(tr) == 18 and len(te) == 6
    print("finance_basics ok")
