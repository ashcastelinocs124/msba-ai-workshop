# F3 Benchmarks and Factors

```{raw} html
<p class="wk-lede">Deere gained 14% in one month. Is that good? It depends on what everything else did that month. A return only means something next to a yardstick, and this page builds the three the firm uses: the market, a handful of style benchmarks called factors, and cash. Then it measures how much of any stock's movement they explain, and what is left over. This page is pre-reading, with no session of its own.</p>
```

```{admonition} Learning objectives
:class: note
- Explain why a stock's return is judged against a benchmark, not on its own.
- Read **beta**: how far a stock moves when the market moves.
- Name the size, value and momentum benchmarks and say what each one tries to capture.
- Read **alpha** as what is left after the benchmarks, and **R squared** as how much they explain.
```

All the numbers on this page are **illustrative**: 24 months of made-up returns for Deere, Caterpillar, a market index and three factor benchmarks, kept in `finance_basics.py`. They behave like market data, but they are not market data, so do not quote them.

## F3.1 Why compare to something

Page F1 measured what a stock earned, and page F2 measured how bumpy the ride was. Neither says whether the stock did well. If the whole market rose 6% in a month, a stock that rose 6% did nothing special: anyone who bought an index fund got the same. A stock that rose 3% in a month the market fell 5% did something real.

So an analyst always asks the same question: **compared with what?** The answer is a **benchmark**, a return series that stands for an alternative the client could have chosen instead. Three kinds matter here:

- **Cash.** What a safe deposit paid, the risk-free rate. A return minus cash is the *excess return* from page F1, and it is what a model is usually asked to predict.
- **The market.** A broad index of stocks. It stands for "just own everything".
- **Factors.** Simple recipes for a style of investing, covered in F3.3.

## F3.2 The market and beta

Put the stock's excess return on one axis and the market's excess return on the other, one dot per month. If the stock tends to move with the market, the dots fall along a rising line. The slope of that line is the stock's **beta**.

- Beta of **1.0**: the stock moves about as much as the market.
- Beta of **1.3**: when the market moves 1%, the stock tends to move about 1.3% in the same direction, so it moves about 1.3 times as much as the market, up or down. Beta above 1 means a stock amplifies the market, and below 1 means it dampens it.
- Beta near **0**: the market's moves tell you almost nothing about the stock.

Beta is not a forecast of the stock's return. It is a measure of how exposed the stock is to something the whole market does. A portfolio of industrial stocks with beta 1.4 is, in effect, a leveraged bet on the market, however carefully each name was chosen.

```{code-block} python
:class: pyodide
from finance_basics import alpha_beta, corr, RETURNS, MARKET

for ticker in ["DE", "CAT"]:
    alpha, beta, r2 = alpha_beta(RETURNS[ticker])
    print(f"{ticker}: beta {beta:.2f}, alpha {alpha:+.2%} a month, R squared {r2:.2f}")

print()
print("Correlation of Deere with the market:", round(corr(RETURNS["DE"], MARKET), 2))
```

Both stocks have a beta above 1, and Caterpillar's is the larger: it swung more with the market than Deere did. Try the same thing with the picture:

```{raw} html
:file: widgets/mlf-factors.html
```

## F3.3 Factors: style benchmarks

The market is one yardstick. Researchers found that stocks with certain traits tend to move together beyond what the market explains, and built a benchmark for each trait. Each one is a **long-short** return: buy one group, sell the other, and record the difference. Because the two sides roughly cancel the market's own moves, the benchmark isolates the trait.

| Factor | Buys | Sells | The idea |
|---|---|---|---|
| **Size** | Small companies | Large companies | Small firms behave differently from large ones, and have often (not always) paid more for the extra risk. |
| **Value** | Cheap stocks (low price against earnings or book value, page F4) | Expensive stocks | Cheap stocks are cheap for a reason, and sometimes the market is too pessimistic. |
| **Momentum** | Last year's winners | Last year's losers | Stocks that have been rising tend to keep rising for a while. |

A factor return is a number like any other: "value returned +1.2% this month" means the cheap-minus-expensive portfolio earned 1.2% more than the expensive side. When an analyst says "this stock has a value tilt", they mean its returns line up with that benchmark, in the same way Caterpillar's line up with the market.

```{code-block} python
:class: pyodide
from finance_basics import RETURNS, SIZE, VALUE, MOMENTUM, MARKET, excess, corr

stock = excess(RETURNS["CAT"])
for name, series in [("Market", excess(MARKET)), ("Size", SIZE), ("Value", VALUE), ("Momentum", MOMENTUM)]:
    print(f"{name:<9} correlation with Caterpillar: {corr(stock, series):+.2f}")
```

The market towers over the rest. In this illustrative sample each factor explains only a small share of either stock (a correlation of 0.3 explains under 10%), and that is typical for single stocks: most of what a stock does in a month is the market, and the rest is mostly noise.

## F3.4 Alpha and R squared

Fit the line through the dots from F3.2 and two numbers come out besides beta:

- **Alpha** is the line's height where the benchmark did nothing: the part of the stock's return that the benchmark does *not* explain. Positive alpha means the stock did better than its exposure predicted, negative means worse. It is shown a month at a time here, so multiply by about 12 for a year.
- **R squared** is the share of the stock's ups and downs that the benchmark explains, from 0 (none) to 1 (all). It tells you how far to trust the other two numbers. With an R squared of 0.05, the dots are a cloud, and the beta and alpha describe almost nothing.

In this sample, the market explains about 73% of Deere's monthly swings and about 85% of Caterpillar's. Deere's alpha is negative: even allowing for its exposure to the market, it did worse. That is what "underperformed on a risk-adjusted basis" means in a research note.

Be careful with alpha. It is what is left over, so it is also where every mistake hides: a factor you left out, a lucky stretch, a data error. Twenty-four months is a short sample, and an alpha that looks large can disappear next quarter. Chapter 4 returns to this, because *alpha* is what a prediction model is, in the end, trying to find.

## F3.5 What this sets up

- A model that predicts excess returns is predicting a number next to a benchmark, not a raw price change.
- When a model "beats the market", the first question is whether it simply took more beta.
- A stock's exposures to the market and to the factors are **features**, columns a model can learn from, and chapter 4 builds them.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. A beta of 1.4 means the stock moves about 1.4 times as much as the market, so a 5% fall in the market goes with a fall of about 7%."
     data-no="Beta is the slope of the line: the stock's move for each 1% move in the market. Beta 1.4 means 1.4% for each 1%. Try picking Caterpillar and the Market in the widget above and reading the beta against the dots.">
  <p class="q">A stock has a beta of 1.4. The market falls 5% in a month. About how far does this stock tend to fall, apart from alpha?</p>
  <label><input type="radio" name="mlf3-q1" value="a"> 5%, the same as the market</label>
  <label><input type="radio" name="mlf3-q1" value="b"> 7%, since it moves about 1.4 times as much</label>
  <label><input type="radio" name="mlf3-q1" value="c"> 3.6%, since a beta above 1 protects it</label>
  <div class="fb"></div>
</div>
```

## Further reading

- Kenneth French, [*Data Library*](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) — the market, size and value benchmarks used in academic research, free to download, with monthly returns back to 1926.
- AQR, [*Data Sets*](https://www.aqr.com/Insights/Datasets) — value, momentum and other factor returns, with the papers that describe how each one is built.
- Wikipedia, [*Capital asset pricing model*](https://en.wikipedia.org/wiki/Capital_asset_pricing_model) — where beta and alpha come from, in more detail than this page.
