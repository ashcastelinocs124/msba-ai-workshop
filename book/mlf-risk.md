# F2 Risk: Volatility and Drawdowns

```{raw} html
<p class="wk-lede">Two stocks can earn the same return and feel nothing alike to hold. One drifts upward; the other falls a quarter of its value on the way. Page F1 measured what a stock earned. This page measures what it took to earn it: how much the price bounces, how far it falls from a high, and how much return you got for each unit of that risk. Every model in Part II is judged on these numbers, so they are worth learning before the models. This page is pre-reading, with no session of its own.</p>
```

```{admonition} Learning objectives
:class: note
- Compute volatility from monthly returns and scale it to a year.
- Find a drawdown, the fall from the highest price so far, and say what it takes to recover from one.
- Compare two investments by return per unit of risk (the Sharpe ratio), not by return alone.
```

The numbers on this page are **illustrative**: 24 made-up monthly returns for Deere (DE), Caterpillar (CAT) and a market index, October 2024 to September 2026. They are not market data, but their last prices match the ones in the firm's records (Deere $512.40, Caterpillar $398.15).

## F2.1 Volatility: how much the price bounces

A stock's average return says nothing about the ride. **Volatility** is the standard deviation of its returns: roughly, how far a typical month lands from the average month. A stock that earns 1% every month has zero volatility. One that earns +10% and −8% in turn can have the same average and a very different life.

Monthly volatility is hard to compare with the yearly figures people quote, so it is scaled up. Returns in different months are treated as independent draws, and independent variation adds in squares, so twelve months of it grows by the *square root* of 12 (about 3.46), not by 12:

> annual volatility = monthly standard deviation × √12

Run it for the three series:

```{code-block} python
:class: pyodide
from finance_basics import RETURNS, stdev, annual_vol, compound

for name in ["DE", "CAT", "MKT"]:
    r = RETURNS[name]
    print(f"{name:>3}: monthly stdev {stdev(r):.1%}, annual volatility {annual_vol(r):.1%}, total return over 24 months {compound(r):+.1%}")
```

The market index has an annual volatility of about 14%. Deere and Caterpillar are both well above it, around 21% and 24%. Neither is unusual: single stocks bounce more than an index of many stocks, because one company's bad quarter is diluted when it is a small part of the index.

## F2.2 Drawdown: how far it falls, and what it takes to get back

Volatility treats a surprise gain and a surprise loss alike. Investors do not. What hurts is a **drawdown**: at any date, how far the price is below the highest price it has reached so far. The **maximum drawdown** is the worst of them, the biggest fall from a peak to the trough that followed.

Recovery is harder than the fall. A stock that drops 20% needs a 25% gain to get back, because the gain is measured from a smaller base. A 50% drop needs a 100% gain. The deeper the hole, the more lopsided the climb.

Drag the window and switch series to see the price path above and its drawdown below:

```{raw} html
:file: widgets/mlf-drawdown.html
```

On the full 24 months, Deere's price fell 26% from its March 2025 peak to September 2025, and was still 24% below that peak a year later. The same period shows why the average return misleads: Deere's average month was a gain of 0.06%, which sounds harmless, and its worst stretch took a quarter of the money.

## F2.3 Return per unit of risk: the Sharpe ratio

Neither number alone says which investment is better. Caterpillar returned more than Deere, but with more volatility. How do you compare them? Ask what each earned **above cash**, per unit of volatility. That is the **Sharpe ratio**:

> Sharpe ratio = average monthly excess return ÷ standard deviation of monthly excess return × √12

*Excess* means the return minus what cash would have paid (page F1). In this data cash pays 0.35% a month. A Sharpe ratio of 0 means the investment paid no more than cash; higher is better; negative means cash won.

```{code-block} python
:class: pyodide
from finance_basics import RETURNS, prices, max_drawdown, sharpe, MONTHS

for name in ["DE", "CAT", "MKT"]:
    depth, peak, trough = max_drawdown(prices(name))
    # prices() has one more entry than there are monthly returns: index 0 is Sep 24
    month = lambda i: "Sep 24" if i == 0 else MONTHS[i - 1]
    print(f"{name:>3}: worst fall {depth:.1%} ({month(peak)} to {month(trough)}), Sharpe ratio {sharpe(RETURNS[name]):.2f}")
```

The market index wins on both counts: a Sharpe ratio of about 0.5, against 0.3 for Caterpillar and a negative number for Deere. That is the lesson to carry into Part II. A model whose forecasts beat the market's return but not its Sharpe ratio has only taken more risk. And a Sharpe ratio from 24 months of data is itself a noisy estimate, so a difference this small should be treated as a hint, not proof.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. Caterpillar's Sharpe ratio is about 0.33 and the market's is about 0.48: the index earned slightly more, with far less volatility (14% against 24%). Caterpillar's total return was a little lower, and it took much more risk to get it."
     data-no="Compare the Sharpe ratios in the second cell, not the total returns. Which series has the higher number?">
  <p class="q">Over the 24 months, Caterpillar returned +20% and the market index +22%. Caterpillar's annual volatility was about 24% and the index's about 14%. Which earned more per unit of risk?</p>
  <label><input type="radio" name="mlf-risk-q1" value="a"> Caterpillar, because it is the more volatile stock</label>
  <label><input type="radio" name="mlf-risk-q1" value="b"> They are equal, because both returned about 20%</label>
  <label><input type="radio" name="mlf-risk-q1" value="c"> The market index: similar return, much less volatility</label>
  <div class="fb"></div>
</div>
```

## Further reading

- William F. Sharpe, [*The Sharpe Ratio*](https://web.stanford.edu/~wfsharpe/art/sr/sr.htm) (1994) — the ratio's author on what it measures and how to use it.
- Wikipedia, [*Volatility (finance)*](https://en.wikipedia.org/wiki/Volatility_(finance)) — the standard deviation, annualising, and why the √12 rule is an approximation.
- Wikipedia, [*Drawdown (economics)*](https://en.wikipedia.org/wiki/Drawdown_(economics)) — maximum drawdown and how it is used to judge funds.
