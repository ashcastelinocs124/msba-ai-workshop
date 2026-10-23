---
name: oil-case-study
description: Reproduce and extend the MSBA Workshop 5 oil case study (Brent 2026) — anomaly detection, walk-forward forecasts of next-month oil volatility and returns, variable search with a holdout, and war-event attribution. Use when asked to run, explain, or extend the oil case study, or to test whether a new variable predicts oil.
---

# Oil case study skill

You are helping a student work with the oil case study in `case-studies/oil-2026/` of the
`ashcastelinocs124/msba-ai-workshop` repository. It asks: **what moves oil, and what can we predict?**

## Setup: do it for the student, one step at a time

Many students have no coding background. Run each command yourself, check it worked, and explain in one plain sentence what it did before moving on. If a step fails, fix it (see Troubleshooting) instead of handing the error back.

1. **Check Python.** Run `python3 --version` (on Windows: `python --version` or `py --version`). Need 3.9 or newer. If it's missing, tell the student the simplest option for their machine: macOS `brew install python` (or the installer from python.org); Windows the python.org installer with "Add python.exe to PATH" ticked. If they'd rather not install anything, use the **Colab route** below.
2. **Check git.** `git --version`. If missing and not easy to install, download the repo as a ZIP from GitHub (Code → Download ZIP) and unzip it instead.
3. **Get the code.** `git clone --depth 1 https://github.com/ashcastelinocs124/msba-ai-workshop` then `cd msba-ai-workshop/case-studies/oil-2026`. If the folder already exists, `cd` into it and run `git pull`.
4. **Make a virtual environment** so nothing clashes with other projects:
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows (PowerShell): `py -m venv .venv; .venv\Scripts\Activate.ps1`
5. **Install the libraries.** `pip install -r requirements.txt` (numpy, pandas, scikit-learn, statsmodels, matplotlib).
6. **Smoke test** (a few seconds): `python -c "import oilcase as oc; p = oc.load_prices(); print(p['brent'].index[-1], round(p['brent'].iloc[-1], 2))"` should print the last date and Brent price.
7. **Get the post archives** (only needed for the `posts` step): `python fetch_data.py`. Add `--refresh` to pull the latest prices too.
8. **Run it.** `python run.py` runs everything except the slow search (~1 min). `python run.py --search` adds the full 2,047-combination search (~25 min). `python run.py --step <anomalies|forecast|holdout|search|posts|war>` runs one step.
9. **Explain the results.** Open `results/summary.md` and walk the student through it in plain language, step by step, using the numbers in the file.

**Colab route (no install):** open `notebooks/oil_case_study_colab.ipynb` from the GitHub folder in Google Colab (File → Open notebook → GitHub, paste the repo URL) and Runtime → Run all. The notebook clones the repo, installs, runs and shows the results.

### Troubleshooting

- `pip: command not found` → use `python3 -m pip install -r requirements.txt` (Windows: `py -m pip …`).
- `externally-managed-environment` → you skipped the virtual environment; do step 4 first.
- PowerShell refuses to run `Activate.ps1` → `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then retry, or use Command Prompt: `.venv\Scripts\activate.bat`.
- `ModuleNotFoundError: oilcase` → you're not in `case-studies/oil-2026`; `cd` there.
- `FileNotFoundError … posts/truth.csv` → run `python fetch_data.py` (only the posts step needs it).
- Download blocked (school network, proxy) → use the Colab route; all price data already ships in `data/`.
- Apple Silicon build errors for scikit-learn/statsmodels → `pip install --upgrade pip` first, then reinstall.

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
