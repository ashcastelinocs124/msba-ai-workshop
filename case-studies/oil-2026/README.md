# Case study: what moves oil, and what can we predict? (2026)

Companion code and data for **Workshop 5 · ML Foundations II (unsupervised learning)**, section 5 of the deck.
Everything from the session applied to one live problem: Brent crude through the 2026 Iran war.

> Teaching example, not investment advice. Every model is tested **walk-forward**: refit using only data that existed at the time, then scored on months it had not seen.

## Run it

**Colab (no install):** open [`notebooks/oil_case_study_colab.ipynb`](notebooks/oil_case_study_colab.ipynb) in Colab and run all cells.

**Locally:**

```bash
git clone --depth 1 https://github.com/ashcastelinocs124/msba-ai-workshop
cd msba-ai-workshop/case-studies/oil-2026
pip install -r requirements.txt
python fetch_data.py          # downloads the two Trump post archives (~17 MB, not stored here)
python run.py                 # all steps, ~1 minute; writes results/summary.md
python run.py --search        # adds the full 2,047-combination variable search (~25 minutes)
python run.py --step holdout  # one step: anomalies | forecast | holdout | search | posts | war
```

**With a coding agent (Claude Code, Codex, Cursor…):** give it [`skill/oil-case-study/SKILL.md`](skill/oil-case-study/SKILL.md). In Claude Code, copy the `skill/oil-case-study` folder into your project's `.claude/skills/` (or `~/.claude/skills/`) and ask, for example, *"use the oil-case-study skill to test whether natural gas improves the volatility forecast"*.

## The five experiments

| # | Step | Method | Headline result |
|---|---|---|---|
| 1 | **Flag** abnormal oil days | Isolation Forest on 3 numbers/day (today's change, 20-day change, 20-day volatility), refit yearly | 2026 has the 2nd-highest share of flagged days since 1987 (after 2020). After a flag, oil is **no more likely to rise** (55% vs 55%) but the next month's volatility is ~3× normal |
| 2 | **Forecast** next month | Ridge regression on momentum, valuation, Brent–WTI spread, VIX, anomaly score | Volatility: ~30% explained out of sample. Return/direction: ~0%, no better than "always up" |
| 3 | **Search** 2,047 combinations | Every 1–3 variable mix of 23 candidates + Lasso, random forest, gradient boosting; chosen on 2005–18, judged on 2019–26 | The search winner fell from 64% to 31%; random forest from 61% to 19%. Simple models held up best |
| 4 | **Stress-test** on 2026 | Train to 2025, forecast each month of 2026 | With the anomaly score: R² +26%; without it: −24%. Neither saw March coming |
| 5 | **Explain** the war | Daily Brent vs Hormuz/policy events, market variables, Trump's posts | Events 14%, markets 22%, posts ~1% of daily moves; posts mostly narrate events |

Pre-computed numbers are in [`results/summary.md`](results/summary.md).

## Files

```
oilcase.py            all the logic (features, Isolation Forest, walk-forward, search, posts, war attribution)
run.py                runs the steps, writes results/summary.{json,md}
fetch_data.py         downloads post archives; --refresh re-downloads the latest prices
data/                 price snapshots (through Oct 2026) and the 2026 war posts/timeline
skill/oil-case-study/ SKILL.md for coding agents
notebooks/            Colab notebook
```

## Data sources

| File | What | Source |
|---|---|---|
| `brent_daily.csv`, `wti_daily.csv` | Brent and WTI spot, daily (EIA) | [datasets/oil-prices](https://github.com/datasets/oil-prices) |
| `natgas_daily.csv` | Henry Hub natural gas, daily (EIA) | [datasets/natural-gas](https://github.com/datasets/natural-gas) |
| `vix_daily.csv` | Cboe VIX, daily | [datasets/finance-vix](https://github.com/datasets/finance-vix) |
| `gold_monthly.csv` | Gold, monthly | [datasets/gold-prices](https://github.com/datasets/gold-prices) |
| `shiller.csv` | S&P 500 monthly (Robert Shiller) | [datasets/s-and-p-500](https://github.com/datasets/s-and-p-500) |
| `us10y_monthly.csv` | US 10-year yield, monthly | [datasets/bond-yields-us-10y](https://github.com/datasets/bond-yields-us-10y) |
| `fx_daily_5ccy.csv` | JPY, CAD, CHF, SEK, NOK per USD (Fed H.10), used as a dollar index | [datasets/exchange-rates](https://github.com/datasets/exchange-rates) |
| `sp500_fin.csv` | S&P 500 constituent ratios (Yahoo Finance snapshot) | [datasets/s-and-p-500-companies-financials](https://github.com/datasets/s-and-p-500-companies-financials) |
| `posts/war_posts_2026.csv` | 93 war-related Truth Social posts, Feb 28–Oct 22, 2026 (mostly excerpts; a sample, not complete) | [trumpstruth.org](https://trumpstruth.org) |
| `posts/war_timeline_2026.csv` | 18 sourced war milestones | Wikipedia war/ceasefire/Hormuz pages, Al Jazeera, news live-blogs |
| `posts/tw_office.csv`, `posts/truth.csv` | Full post archives (downloaded by `fetch_data.py`) | [Complete Trump Tweets Archive](https://github.com/MarkHershey/CompleteTrumpTweetsArchive), [Trump Truth Social archive](https://github.com/stiles/trump-truth-social-archive) |

## Caveats

- Brent here is EIA **spot**, which ran well above futures during the 2026 supply crunch.
- The Truth Social archive has a gap (Nov 2025–Mar 2026); the 2026 war posts are a hand-collected sample.
- War-event dates come from secondary sources; some are approximate. Lists of "major events" are partly chosen because markets moved, which can flatter that variable.
- The anomaly share for 2026 is 17.2% here (refit yearly, no look-ahead) vs 16.3% on the deck slide (fit once on all years).
- Results depend on the period tested; quote holdout numbers, not in-sample ones.
