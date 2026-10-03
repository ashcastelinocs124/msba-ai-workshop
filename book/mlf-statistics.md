# F5 The Statistics You Need

```{raw} html
<p class="wk-lede">Machine learning on returns is statistics with a bigger toolbox, and the toolbox only makes sense once five ideas are solid: an average, a spread, how two things move together, a line drawn through a cloud of dots, and the habit of testing on months the model has not seen. This page is the bridge into chapters 4 and 5. It is pre-reading, with no session of its own.</p>
```

```{admonition} Learning objectives
:class: note
- Read a mean, a variance and a correlation off a column of returns, and say what each one does not tell you.
- Fit a line by least squares and explain what its slope and its R squared mean.
- Say why a small R squared is normal for returns, and why a high one should make you suspicious.
- Split data by date into a training part and a test part, and explain what goes wrong if you shuffle it.
```

## F5.1 Average and spread

The **mean** is the typical value: add the months up and divide by how many there are. The **variance** measures how far the months stray from the mean, on average, as a squared distance; its square root, the **standard deviation**, is back in the units of the data and is what page F2 called volatility. Two stocks can have the same mean and very different spreads, and the spread is usually the thing that decides how a position feels.

```{code-block} python
:class: pyodide
from finance_basics import mean, stdev, RETURNS

for ticker in ["DE", "CAT", "MKT"]:
    r = RETURNS[ticker]
    print(f"{ticker}: average month {mean(r):+.2%}, typical swing around it {stdev(r):.2%}")
```

Notice how large the swing is next to the average. A typical month moves Deere several times further than its average month earns. That ratio, a small signal under a lot of noise, is the central fact of this whole course.

## F5.2 How two things move together

**Correlation** is a number between -1 and 1. At +1 two series rise and fall in perfect step; at 0 knowing one tells you nothing about the other; at -1 they move opposite. It is the building block of benchmarks (page F3) and of portfolio risk, because two stocks that move together protect you less than two that do not.

Two cautions. Correlation is about a *straight-line* pattern, so a strong curved relationship can show a correlation near 0. And **correlation is not causation**: two series that both trend, or both react to the same third thing, will correlate with no link between them. Deere and Caterpillar rise together mostly because both respond to the same economy, not because one moves the other.

```{code-block} python
:class: pyodide
from finance_basics import corr, RETURNS, MARKET, SIZE, VALUE, MOMENTUM

print("Deere and the market, same month:", round(corr(RETURNS["DE"], MARKET), 2))
print("Deere and Caterpillar, same month:", round(corr(RETURNS["DE"], RETURNS["CAT"]), 2))
print("Value and size benchmarks:", round(corr(VALUE, SIZE), 2))
print("Momentum and the market:", round(corr(MOMENTUM, MARKET), 2))
print()
print("Market this month and Deere NEXT month:", round(corr(MARKET[:-1], RETURNS["DE"][1:]), 2))
```

The first four are high or moderate: things that move *together*. The last one is the question a forecaster actually asks, whether this month tells you anything about next month, and the answer is far weaker. Same-month correlations describe the past; prediction needs the next-month kind.

## F5.3 The simplest prediction model: a line

Plot next month's Deere return against this month's market return and you get a cloud of dots. **Least squares** draws the one straight line that sits closest to the dots, in the sense that the squared vertical misses add up to the smallest total. The line has two numbers: an **intercept** (where it starts) and a **slope** (how much the prediction moves when the input moves one unit). That is a model: give it this month's market return and it hands back a forecast for next month's Deere return. Every regression in chapter 4 is this idea with more inputs.

**R squared** is the share of the dots' up-and-down that the line explains, from 0 (none) to 1 (all). Deere against the market *in the same month* explains most of the variation (page F3 uses this), because that is a benchmark, not a forecast. For *predicting* a return, the honest number is tiny. Monthly stock returns are mostly news nobody could have known beforehand, so an R squared of a few percent is normal, and it can still be worth money when it is real and repeatable. An R squared of 40% on next-month returns is far more likely a bug, such as a number that quietly included the future, than a discovery.

## F5.4 Overfitting, and why we split by date

A line has two numbers to tune. A curve with eight bends has nine, and with enough bends it can pass through almost every past dot. Its past looks superb and its future is useless, because it has memorised the noise. That is **overfitting**, and the more flexible the model, the easier it is. Drag the slider and watch the two errors part ways:

```{raw} html
:file: widgets/mlf-overfit.html
```

The remedy is to judge a model only on data it has never seen. Hold some back, fit on the rest, and score on what was held back. For returns, hold back the **latest months**, not a random sample. A random split lets the model learn from March 2026 and then be "tested" on February 2026, a peek into the future that a real forecaster never gets. This has a name, look-ahead bias, and it is the most common way a promising model turns out to be worthless.

```{code-block} python
:class: pyodide
from finance_basics import ols, mean, split_by_time, MARKET, RETURNS

x, y = MARKET[:-1], RETURNS["DE"][1:]        # this month's market, next month's Deere
x_old, x_new = split_by_time(x)               # first 17 months to learn from, last 6 to test on
y_old, y_new = split_by_time(y)

intercept, slope, r2 = ols(x_old, y_old)
print(f"learned on the past: next month = {intercept:+.3f} + {slope:.2f} x this month's market   (R squared {r2:.2f})")

miss_line = (sum((intercept + slope * a - b) ** 2 for a, b in zip(x_new, y_new)) / len(y_new)) ** 0.5
miss_avg = (sum((mean(y_old) - b) ** 2 for b in y_new) / len(y_new)) ** 0.5
print(f"typical miss on the 6 unseen months: line {miss_line:.1%}, just the old average {miss_avg:.1%}")
```

On the months it learned from, the line explains about a tenth of the movement. On the six months it never saw, it does *no better* than guessing the old average. That is not a failure of the method; it is the method telling you the truth. The first thing chapter 4 asks of every model is to beat that boring baseline on held-out months.

## F5.5 Where this goes next

- **Chapter 4** turns the line into regressions and classifiers for market returns and for recessions, scored out of sample.
- **Chapter 5** adds the brakes, regularization, which holds a flexible model back from chasing noise.
- The time-ordered split you just used becomes the rolling and expanding windows of the validation chapter.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. A few percent of next-month variation is normal for returns. What matters is whether it holds on months the model has not seen."
     data-no="Re-read F5.3. Returns are mostly unpredictable news, so what does a small R squared on next month's return mean, and what would a very large one suggest?">
  <p class="q">A model that predicts next month's Deere return has an R squared of 0.04 on months it was not fitted to. What is the fair reading?</p>
  <label><input type="radio" name="stat-q1" value="a"> It is broken: a useful model must explain at least half the movement</label>
  <label><input type="radio" name="stat-q1" value="b"> It is in the normal range for monthly returns, and worth keeping only if it stays positive on later unseen months</label>
  <label><input type="radio" name="stat-q1" value="c"> It proves that this month's market return causes next month's Deere return</label>
  <div class="fb"></div>
</div>
```

## Further reading

- Wikipedia, [*Coefficient of determination*](https://en.wikipedia.org/wiki/Coefficient_of_determination) — R squared defined, with the cases where it misleads.
- scikit-learn, [*Cross-validation: evaluating estimator performance*](https://scikit-learn.org/stable/modules/cross_validation.html) — held-out scoring in practice, including `TimeSeriesSplit` for ordered data.
- Tyler Vigen, [*Spurious correlations*](https://www.tylervigen.com/spurious-correlations) — a gallery of series that move together for no reason, a useful antidote to reading too much into a correlation.
