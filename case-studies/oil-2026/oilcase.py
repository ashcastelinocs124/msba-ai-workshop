"""What moves oil, and what can we predict? Case study code for MSBA Workshop 5 (ML Foundations II).

Every model is tested walk-forward: it is refit using only data that existed at the time,
then scored on the period it had not seen. Nothing here is investment advice.
"""
from __future__ import annotations

import csv
import html
import itertools
import json
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, IsolationForest, RandomForestRegressor
from sklearn.linear_model import LassoCV, Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
HERE = Path(__file__).parent
DATA = HERE / "data"
RESULTS = HERE / "results"


# --------------------------------------------------------------------------- data
def _daily(name: str) -> pd.Series:
    d = pd.read_csv(DATA / name, parse_dates=["Date"]).dropna()
    d = d[d.Price > 0]
    return d.set_index("Date").Price


def load_prices() -> dict:
    """Brent/WTI/natural gas daily (EIA), VIX daily (Cboe), gold monthly, S&P 500 monthly (Shiller),
    US 10-yr yield monthly, and a 5-currency dollar index. All from github.com/datasets."""
    p = {"brent": _daily("brent_daily.csv"), "wti": _daily("wti_daily.csv"), "natgas": _daily("natgas_daily.csv")}
    p["vix"] = pd.read_csv(DATA / "vix_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE
    g = pd.read_csv(DATA / "gold_monthly.csv"); g.index = pd.PeriodIndex(g.Date, freq="M").to_timestamp("M"); p["gold"] = g.Price
    s = pd.read_csv(DATA / "shiller.csv", parse_dates=["Date"]).set_index("Date").SP500
    s.index = s.index.to_period("M").to_timestamp("M"); p["sp500"] = s
    y = pd.read_csv(DATA / "us10y_monthly.csv", parse_dates=["Date"]).set_index("Date").Rate
    y.index = y.index.to_period("M").to_timestamp("M"); p["us10y"] = y
    fx = pd.read_csv(DATA / "fx_daily_5ccy.csv", parse_dates=["Date"]).pivot_table(index="Date", columns="Country", values="Exchange rate")
    p["usd"] = np.log(fx[["Japan", "Canada", "Switzerland", "Sweden", "Norway"]]).mean(axis=1)   # higher = stronger dollar
    p["cad"] = np.log(fx["Canada"])
    return p


# --------------------------------------------------------------------------- step 1: anomalies
def anomaly_scores(brent: pd.Series, first_year: int = 1993, contamination_q: float = 0.98) -> pd.DataFrame:
    """Isolation Forest on 3 numbers per day (today's change, 20-day change, 20-day volatility).
    Refit each year on prior years only; flag days above the training set's 98th-percentile score."""
    r = np.log(brent).diff()
    F = pd.DataFrame({"r1": r, "r20": np.log(brent).diff(20), "vol20": r.rolling(20).std() * np.sqrt(252)}).dropna()
    F["score"] = np.nan; F["flag"] = np.nan
    for y in range(first_year, F.index.year.max() + 1):
        tr = F[F.index.year < y][["r1", "r20", "vol20"]]; te = F[F.index.year == y][["r1", "r20", "vol20"]]
        if te.empty: continue
        sc = StandardScaler().fit(tr)
        iso = IsolationForest(n_estimators=300, random_state=0).fit(sc.transform(tr))
        trs = -iso.score_samples(sc.transform(tr)); thr = np.quantile(trs, contamination_q)
        s_ = -iso.score_samples(sc.transform(te))
        F.loc[te.index, "score"] = (s_ - np.median(trs)) / trs.std()
        F.loc[te.index, "flag"] = (s_ > thr).astype(float)
    F["fwd20"] = (np.log(brent).shift(-20) - np.log(brent)).reindex(F.index) * 100
    F["fwdvol20"] = (r[::-1].rolling(20).std()[::-1].shift(-1) * np.sqrt(252) * 100).reindex(F.index)
    return F


def event_study(F: pd.DataFrame, start: str = "1995") -> dict:
    """What happened over the next 20 trading days after flagged vs normal days?"""
    G = F[start:].dropna(subset=["flag", "fwd20"])
    out = {}
    for f, g in G.groupby("flag"):
        out["flagged" if f else "normal"] = {"days": int(len(g)), "pct_up_20d_later": round((g.fwd20 > 0).mean() * 100, 1),
                                            "median_abs_20d_move": round(g.fwd20.abs().median(), 1),
                                            "avg_next20_volatility": round(g.fwdvol20.mean(), 1)}
    return out


# --------------------------------------------------------------------------- step 2: monthly features
def monthly_features(p: dict, F: pd.DataFrame) -> pd.DataFrame:
    me = lambda x: x.resample("ME").last()
    b, w, ng = p["brent"], p["wti"], p["natgas"]; r = np.log(b).diff(); lm = np.log(me(b)); lng = np.log(me(ng))
    v = p["vix"]; g = p["gold"]; s = p["sp500"]; usd = p["usd"].resample("ME").last(); cad = p["cad"].resample("ME").last()
    X = pd.DataFrame({
        "Brent mom 1m": lm.diff(1) * 100, "Brent mom 3m": lm.diff(3) * 100, "Brent mom 12m": lm.diff(12) * 100,
        "Brent vs 5y avg": (lm - np.log(me(b).rolling(60).mean())) * 100,
        "Brent vol last month": r.resample("ME").std() * np.sqrt(252) * 100,
        "Brent vol 3m": r.resample("ME").std().rolling(3).mean() * np.sqrt(252) * 100,
        "Brent-WTI spread": (lm - np.log(me(w))) * 100,
        "Anomaly score": F.score.resample("ME").mean(), "Anomaly days": F.flag.resample("ME").sum(),
        "VIX avg": v.resample("ME").mean(), "VIX change 1m": v.resample("ME").mean().diff(),
        "Nat gas mom 1m": lng.diff() * 100, "Nat gas mom 12m": lng.diff(12) * 100,
        "Gas/oil ratio vs 5y": (lng - lm) * 100 - ((lng - lm) * 100).rolling(60).mean(),
        "Gold mom 1m": np.log(g).diff() * 100, "Gold mom 12m": np.log(g).diff(12) * 100,
        "Oil/gold ratio vs 5y": (lm - np.log(g)) * 100 - ((lm - np.log(g)) * 100).rolling(60).mean(),
        "S&P 500 mom 3m": np.log(s).diff(3) * 100, "S&P 500 mom 12m": np.log(s).diff(12) * 100,
        "Dollar mom 1m": usd.diff() * 100, "Dollar mom 3m": usd.diff(3) * 100, "CAD per USD mom 1m": cad.diff() * 100,
        "10y yield chg 3m": p["us10y"].diff(3), "10y yield level": p["us10y"],
    })
    X["y_ret"] = (lm.shift(-1) - lm) * 100                                      # next month's Brent return, %
    X["y_vol"] = (r.resample("ME").std() * np.sqrt(252) * 100).shift(-1)        # next month's realized volatility, %
    return X[X.index >= "1994-01-31"]


FEATURES_CORE = ["Anomaly score", "Anomaly days", "Brent mom 1m", "VIX avg", "VIX change 1m", "Brent-WTI spread"]
FEATURES_DECK = ["Brent mom 1m", "Brent mom 12m", "Brent vs 5y avg", "Brent-WTI spread", "Anomaly score", "Anomaly days"]


def walk_forward(X, cols, target, start, end=None, model="ridge", refit="monthly"):
    """Fit on everything before each test month, predict it, score vs the historical-average forecast.
    Returns out-of-sample R² (%), and for returns the share of months with the right sign."""
    d = X.dropna(subset=list(cols) + [target])
    if end: d = d[d.index <= end]
    test = d.index[d.index >= start]
    P, B, A = [], [], []; m = sc = None
    for t in test:
        if m is None or refit == "monthly" or t.month == 1:
            tr = d[d.index < t]
            sc = StandardScaler().fit(tr[cols]); Z = sc.transform(tr[cols])
            m = {"ridge": lambda: Ridge(alpha=5.0),
                 "lasso": lambda: LassoCV(cv=TimeSeriesSplit(5), alphas=30, max_iter=20000),
                 "gbm": lambda: HistGradientBoostingRegressor(max_depth=3, learning_rate=0.05, max_iter=150, min_samples_leaf=20, random_state=0),
                 "rf": lambda: RandomForestRegressor(n_estimators=200, min_samples_leaf=10, max_features=0.5, random_state=0)}[model]().fit(Z, tr[target])
            bench = tr[target].mean()
        P.append(float(m.predict(sc.transform(d.loc[[t], cols]))[0])); B.append(bench); A.append(float(d.loc[t, target]))
    P, B, A = map(np.array, (P, B, A))
    out = {"oos_r2_pct": round((1 - ((A - P) ** 2).sum() / ((A - B) ** 2).sum()) * 100, 1), "months": int(len(A))}
    if target == "y_ret":
        out["sign_right_pct"] = round(((P > 0) == (A > 0)).mean() * 100, 1); out["always_up_pct"] = round((A > 0).mean() * 100, 1)
    return out


def holdout_2026(X, cols=FEATURES_CORE, target="y_vol"):
    """Freeze the model at the end of 2025 and forecast each month of 2026 (the Iran-war year)."""
    d = X.dropna(subset=list(cols) + [target])
    tr, te = d[d.index <= "2025-11-30"], d[d.index >= "2025-12-31"]
    sc = StandardScaler().fit(tr[cols]); m = Ridge(alpha=5.0).fit(sc.transform(tr[cols]), tr[target])
    p = m.predict(sc.transform(te[cols])); a = te[target].values; bench = tr[target].mean()
    return {"oos_r2_pct": round((1 - ((a - p) ** 2).sum() / ((a - bench) ** 2).sum()) * 100, 1),
            "rows": [[(t + pd.offsets.MonthEnd(1)).strftime("%b %Y"), round(float(pp), 1), round(float(aa), 1)] for t, pp, aa in zip(te.index, p, a)]}


# --------------------------------------------------------------------------- step 3: variable search
def variable_search(X, target, max_k=3, select=("2005-01-31", "2018-12-31"), hold=("2019-01-31", "2026-08-31"), top=5):
    """Try every 1..max_k combination; choose on the select period, report the winners on the untouched holdout."""
    feats = [c for c in X.columns if not c.startswith("y_")]
    rows = []
    for k in range(1, max_k + 1):
        for combo in itertools.combinations(feats, k):
            try:
                o = walk_forward(X, list(combo), target, *select, refit="yearly")
                rows.append((o["oos_r2_pct"], list(combo)))
            except ValueError:
                continue
    rows.sort(key=lambda x: -x[0])
    return {"tried": len(rows), "share_beating_average_pct": round(np.mean([r[0] > 0 for r in rows]) * 100, 1),
            "winners": [{"vars": c, "select_r2": s, "holdout": walk_forward(X, c, target, *hold, refit="yearly")} for s, c in rows[:top]]}


# --------------------------------------------------------------------------- step 4: Trump posts
def load_posts() -> pd.DataFrame:
    """In-office posts: Twitter 2017-01-20..2021-01-08 and Truth Social from 2025-01-20 (run fetch_data.py first)."""
    rows = []
    tw = DATA / "posts" / "tw_office.csv"
    if tw.exists():
        with open(tw, newline="", encoding="utf-8", errors="ignore") as f:
            rd = csv.reader(f, skipinitialspace=True); next(rd)
            for r in rd:
                m = re.search(r"status/(\d+)", r[2]) if len(r) >= 4 else None
                if m:   # tweet ID encodes its exact UTC timestamp
                    rows.append((pd.Timestamp((int(m.group(1)) >> 22) + 1288834974657, unit="ms", tz="UTC"), ",".join(r[3:])))
    tr = DATA / "posts" / "truth.csv"
    if tr.exists():
        t = pd.read_csv(tr)
        for ts, c in zip(pd.to_datetime(t.created_at, utc=True, errors="coerce"), t.content.fillna("")):
            rows.append((ts, html.unescape(re.sub(r"<[^>]+>", " ", c))))
    P = pd.DataFrame(rows, columns=["ts", "text"]).dropna()
    P = P[((P.ts >= "2017-01-20") & (P.ts < "2021-01-09")) | (P.ts >= "2025-01-20")]
    P = P[~P.text.str.startswith("RT ")]
    P["et"] = P.ts.dt.tz_convert("America/New_York")
    return P


def posts_event_study(brent: pd.Series, P: pd.DataFrame) -> dict:
    """Same-day Brent move on days with each kind of post vs other days, controlling for already-volatile markets."""
    import statsmodels.api as sm
    flags = {
        "pressure_on_opec": P.text.str.contains(r"\bopec\b|\bsaudi", case=False) & P.text.str.contains(r"too high|artificially|very high|increase (the )?(flow|output|production)|keep (oil |gas |gasoline )?prices down|relax|lower|not be cutting|pump more|prices down", case=False)
                            | P.text.str.contains("KEEP OIL PRICES DOWN", case=True),
        "cheap_gas_brag": P.text.str.contains(r"(prices?|gasoline|gas|oil)( prices?)? (are|is|getting|coming|way)? ?(down|low|lower|cheap)", case=False),
        "iran_escalation": P.text.str.contains(r"\biran", case=False) & P.text.str.contains(r"strike|attack|bomb|\bwar\b|destroy|obliterat|military|missile", case=False),
        "hormuz": P.text.str.contains(r"hormuz|strait of", case=False),
    }
    ret = np.log(brent).diff() * 100; days = ret.index
    def tday(et):   # EIA Brent spot ~ London close (11:30 ET): later posts count toward the next session
        d = pd.Timestamp(et.date()) + pd.Timedelta(days=int(et.hour * 60 + et.minute >= 690)); i = days.searchsorted(d)
        return days[i] if i < len(days) else pd.NaT
    P = P.assign(tday=P.et.map(tday))
    D = pd.DataFrame({"ret": ret}); D["absret"] = D.ret.abs(); D["prev5"] = ret.rolling(5).sum().shift(1); D["absret_prev"] = D.absret.shift(1)
    inoff = (((D.index >= "2017-01-20") & (D.index < "2021-01-09")) | (D.index >= "2025-01-20")) & ~((D.index >= "2020-03-01") & (D.index <= "2020-05-31"))
    out = {}
    for k, mask in flags.items():
        D[k] = D.index.isin(P.loc[mask, "tday"].dropna()).astype(int)
        S = D[inoff].dropna()
        m = sm.OLS(S.ret, sm.add_constant(S[[k, "prev5", "absret_prev"]])).fit(cov_type="HC1")
        out[k] = {"days": int(S[k].sum()), "avg_move_on_post_days": round(S[S[k] == 1].ret.mean(), 2),
                  "effect_after_controls": round(m.params[k], 2), "p_value": round(m.pvalues[k], 3)}
    return out


# --------------------------------------------------------------------------- step 5: war attribution
WAR_EVENTS = {   # +1 supply threat (closures, strikes), -1 supply relief (ceasefires, reopening); from data/posts/war_timeline_2026.csv
    "2026-02-28": 1, "2026-03-04": 1, "2026-03-18": 1, "2026-03-28": 1, "2026-04-08": -1, "2026-04-13": 1, "2026-04-17": -1, "2026-04-18": 1,
    "2026-06-17": -1, "2026-07-08": 1, "2026-07-12": 1, "2026-08-30": 1, "2026-09-05": 1, "2026-09-14": 1, "2026-10-14": 1, "2026-10-21": 1}


def war_attribution(p: dict, start="2026-03-02", end="2026-09-22") -> dict:
    """Share of daily Brent moves (R²) explained by market variables, Hormuz/policy events and Trump's war posts."""
    import statsmodels.api as sm
    D = pd.DataFrame({"brent": np.log(p["brent"]).diff() * 100})
    D["natgas"] = (np.log(p["natgas"]).diff() * 100).reindex(D.index)
    D["dollar"] = (p["usd"].diff() * 100).reindex(D.index)
    D["vix_chg"] = p["vix"].diff().reindex(D.index)
    days = D.index; D["event"] = 0.0
    for d, s in WAR_EVENTS.items():
        if pd.Timestamp(d) <= days[-1]: D.loc[days[days.searchsorted(pd.Timestamp(d))], "event"] += s
    posts = pd.read_csv(DATA / "posts" / "war_posts_2026.csv")
    posts = posts[~posts.source.str.contains("headline", case=False, na=False)]
    def tday(dt, date):
        if isinstance(dt, str) and len(dt) >= 16:
            t = pd.Timestamp(dt[:16]); d = pd.Timestamp(t.date()) + pd.Timedelta(days=int(t.hour * 60 + t.minute >= 690))
        else: d = pd.Timestamp(date)
        i = days.searchsorted(d); return days[i] if i < len(days) else pd.NaT
    posts["td"] = [tday(a, c) for a, c in zip(posts.datetime_et, posts.date)]
    posts["s"] = posts.category.map({"escalation": 1, "de-escalation": -1}).fillna(0)
    posts.loc[posts.text.str.contains("OPEN", na=False) & (posts.category == "Hormuz"), "s"] = -1
    D["posts"] = posts.groupby("td").s.sum().reindex(D.index).fillna(0).clip(-1, 1)
    S = D[start:end].dropna()
    r2 = lambda cols: round(sm.OLS(S.brent, sm.add_constant(S[cols])).fit().rsquared * 100, 1)
    mk = ["natgas", "dollar", "vix_chg"]
    return {"days": int(len(S)), "r2_pct": {"market variables": r2(mk), "Hormuz/policy events": r2(["event"]), "Trump posts": r2(["posts"]),
                                            "events + market": r2(["event"] + mk), "events + market + posts": r2(["event"] + mk + ["posts"])}}
