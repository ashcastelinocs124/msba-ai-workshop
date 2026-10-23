"""Download the large Trump post archives (not stored in this repo) and, optionally, refresh the price data.

    python fetch_data.py             # post archives only
    python fetch_data.py --refresh   # also re-download the latest price files from github.com/datasets
"""
import argparse
import urllib.request
from pathlib import Path

DATA = Path(__file__).parent / "data"
POSTS = {
    "posts/tw_office.csv": "https://raw.githubusercontent.com/MarkHershey/CompleteTrumpTweetsArchive/master/data/realDonaldTrump_in_office.csv",
    "posts/truth.csv": "https://raw.githubusercontent.com/stiles/trump-truth-social-archive/main/data/truth_archive.csv",
}
PRICES = {
    "brent_daily.csv": "https://raw.githubusercontent.com/datasets/oil-prices/main/data/brent-daily.csv",
    "wti_daily.csv": "https://raw.githubusercontent.com/datasets/oil-prices/main/data/wti-daily.csv",
    "natgas_daily.csv": "https://raw.githubusercontent.com/datasets/natural-gas/main/data/daily.csv",
    "vix_daily.csv": "https://raw.githubusercontent.com/datasets/finance-vix/main/data/vix-daily.csv",
    "gold_monthly.csv": "https://raw.githubusercontent.com/datasets/gold-prices/main/data/monthly.csv",
    "us10y_monthly.csv": "https://raw.githubusercontent.com/datasets/bond-yields-us-10y/main/data/monthly.csv",
    "shiller.csv": "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv",
}

ap = argparse.ArgumentParser(); ap.add_argument("--refresh", action="store_true"); args = ap.parse_args()
todo = dict(POSTS, **(PRICES if args.refresh else {}))
for rel, url in todo.items():
    dest = DATA / rel; dest.parent.mkdir(parents=True, exist_ok=True)
    print("downloading", rel); urllib.request.urlretrieve(url, dest)
if args.refresh:
    import pandas as pd
    fx = pd.read_csv("https://raw.githubusercontent.com/datasets/exchange-rates/main/data/daily.csv", parse_dates=["Date"])
    fx[fx.Country.isin(["Japan", "Canada", "Switzerland", "Sweden", "Norway"]) & (fx.Date >= "1985-01-01")].to_csv(DATA / "fx_daily_5ccy.csv", index=False)
print("done")
