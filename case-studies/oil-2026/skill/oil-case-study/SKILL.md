---
name: oil-case-study
description: Reproduce and extend the MSBA Workshop 5 oil case study (Brent 2026) — anomaly detection, walk-forward forecasts of next-month oil volatility and returns, variable search with a holdout, and war-event attribution. Use when asked to run, explain, or extend the oil case study, or to test whether a new variable predicts oil.
---

# Oil case study skill

You are helping a student work with the oil case study in `case-studies/oil-2026/` of the
`ashcastelinocs124/msba-ai-workshop` repository. It asks: **what moves oil, and what can we predict?**

## Setup

1. If the folder isn't present: `git clone --depth 1 https://github.com/ashcastelinocs124/msba-ai-workshop` and `cd msba-ai-workshop/case-studies/oil-2026`.
2. `pip install -r requirements.txt` (numpy, pandas, scikit-learn, statsmodels, matplotlib).
3. `python fetch_data.py` for the Trump post archives (needed only for the `posts` step). Add `--refresh` to pull the latest prices.
4. `python run.py` runs everything except the slow search (~1 min). `python run.py --search` adds the full 2,047-combination search (~25 min). `python run.py --step <anomalies|forecast|holdout|search|posts|war>` runs one step.
5. Read `results/summary.md` and explain it in plain language.

## How the code is organised (`oilcase.py`)

- `load_prices()` – Brent, WTI, natural gas, VIX, gold, S&P 500, 10-yr yield, dollar index.
- `anomaly_scores(brent)` – Isolation Forest on today's change, 20-day change, 20-day volatility; refit each year on prior years only. Columns: `score`, `flag`.
- `monthly_features(p, F)` – one row per month: 24 candidate predictors plus targets `y_ret` (next month's Brent return, %) and `y_vol` (next month's realized volatility, %).
- `walk_forward(X, cols, target, start, end=None, model="ridge"|"lasso"|"gbm"|"rf")` – the honest test. Returns out-of-sample R² (%) vs the historical average; for returns also `sign_right_pct` and the `always_up_pct` baseline.
- `holdout_2026(X, cols)` – train through 2025, forecast each 2026 month.
- `variable_search(X, target, max_k)` – choose on 2005–2018, report winners on 2019–2026.
- `posts_event_study(...)`, `war_attribution(p)` – Trump posts and Hormuz/policy events vs daily Brent.

## Extending it (typical student requests)

- **"Does variable Z help?"** Add a column to `monthly_features` built only from data available at month-end (no future values), then compare `walk_forward(X, base + ["Z"], "y_vol", "2005-01-31")` with the same call without Z. Report both, plus the 2019–2026 holdout.
- **New target** (e.g., WTI, natural gas): add the target column the same way; reuse `walk_forward`.
- **New model**: add it to the dictionary in `walk_forward`; keep the same refit schedule and benchmark.
- **Update to today**: `python fetch_data.py --refresh`, rerun, and say which dates the data now covers.

## Rules — follow these every time

1. **No look-ahead.** Features at month t may use only data up to month t. Anything fit on data (scalers, models, anomaly thresholds) is refit on past data only.
2. **Quote out-of-sample numbers.** If you try many variants, choose on 2005–2018 and report 2019–2026. Say how many variants you tried.
3. **Compare to the baseline.** For direction, compare the hit rate to "always guess up" (`always_up_pct`), not to 50%.
4. **Real data only.** Never invent, interpolate or "fill in" numbers. If data is missing, say so.
5. **Explain plainly.** R² = share of the benchmark's squared error the model removed; 0 = no better than the average, negative = worse.
6. **Not investment advice.** Present forecasts with their uncertainty and their track record.

## What the original study found (to sanity-check reruns)

- After flagged days, oil is no more likely to rise, but next-month volatility is ~3× normal.
- Next-month volatility: ~30% explained out of sample; next-month return: ~0%.
- The best of 2,047 combinations lost about half its score on unseen years; random forest and gradient boosting overfit.
- 2026 holdout: with the anomaly score R² ≈ +26%; without it ≈ −24%.
- During the war: market variables ≈ 22%, Hormuz/policy events ≈ 14%, Trump's posts ≈ 1% of daily moves.
