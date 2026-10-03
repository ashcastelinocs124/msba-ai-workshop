# F1 Prices and Returns

```{raw} html
<p class="wk-lede">A model never sees a price. It sees a return: how much a holding grew or shrank over a period. Every table in the machine-learning chapters is a column of returns, so the first thing to get right is which return, and how to add them up. This page is pre-reading, with no session of its own.</p>
```

```{admonition} Learning objectives
:class: note
- Turn a list of prices into simple returns and log returns, and say when each is the right one.
- Explain why simple returns do not add up across months, and why log returns do.
- Compound monthly returns into a total return, and see why +50% then −50% is a loss.
- Subtract the risk-free rate to get an excess return, the number the later pages predict.
```

All the numbers on this page are **illustrative**: 24 months of made-up returns for Deere (DE), Caterpillar (CAT) and a market index, from Oct 2024 to Sep 2026, ending at the prices in the firm's records. They are not market data. They sit in a small module, `finance_basics`, that the cells below import.

## F1.1 A price is not a return

A price of $512.40 tells you nothing about whether the stock was a good buy. The same price is a triumph for someone who paid $400 and a disaster for someone who paid $600. What carries information is the *change*, measured against what you started with.

The **simple return** over one period is the price change divided by the old price:

> simple return = (new price − old price) ÷ old price = new price ÷ old price − 1

A stock that goes from $100 to $110 returned +10%. One that goes from $110 back to $100 returned −9.1%, not −10%, because the loss is measured against the higher starting price. That small asymmetry is the whole subject of this page.

Models use returns, not prices, for a practical reason too. Prices drift upward for decades, so a model fitted to prices learns "higher numbers come later". Returns hover around a steady level, which is what a model can learn something from.

```{code-block} python
:class: pyodide
from finance_basics import prices, simple_returns, MONTHS

p = prices("DE")                       # 25 month-end prices, Sep 24 to Sep 26
r = simple_returns(p)                  # 24 monthly returns
print(f"Deere: first price {p[0]:.2f}, last price {p[-1]:.2f}")
for month, price, ret in list(zip(MONTHS, p[1:], r))[:4]:
    print(f"  {month}: price {price:7.2f}   return {ret:+.2%}")
print("  ...")
```

## F1.2 Log returns, and why they add

The **log return** is the natural logarithm of the price ratio: ln(new price ÷ old price). For small moves it is almost the same as the simple return (+1% simple is +0.995% log). It differs on big moves, and it has one property the simple return lacks: **log returns add up across periods.** The log return for a whole year is the sum of the twelve monthly log returns. Simple returns have to be multiplied, month by month.

That is why log returns are popular in models: a sum is easier to work with than a product, and a statistic such as an average of monthly log returns means what it says. Simple returns are the better choice when you want to report what an investor earned, because they are the number on the statement. Try both on the 24 months:

```{raw} html
:file: widgets/mlf-compounding.html
```

Pick Deere and add up its 24 simple returns: you get +1.4%. Yet someone who held Deere from Sep 2024 to Sep 2026 lost 2.9%, because its prices went from $527.71 to $512.40. Adding is the wrong operation for simple returns. Switch to log returns and the sum comes out exactly right once you turn it back with e<sup>x</sup> − 1.

## F1.3 Compounding

Holding for several months means each month's return applies to whatever you had at the end of the last one. To get the total, multiply the growth factors (1 + return) and subtract 1. This is **compounding**, and it is why a 50% gain followed by a 50% loss leaves you down 25%: $100 becomes $150, and half of $150 is $75. The widget's slider shows the same trap at other sizes.

```{code-block} python
:class: pyodide
from finance_basics import prices, simple_returns, log_returns, compound
import math

for ticker in ["DE", "CAT"]:
    p = prices(ticker)
    simple, log = simple_returns(p), log_returns(p)
    print(ticker)
    print(f"  sum of simple returns : {sum(simple):+.1%}   (not what you earned)")
    print(f"  sum of log returns    : {sum(log):+.1%}   (a log, not a percentage)")
    print(f"  compounded simple     : {compound(simple):+.1%}")
    print(f"  from the log sum      : {math.exp(sum(log)) - 1:+.1%}   (e^x - 1; identical)")
    print(f"  straight from prices  : {p[-1] / p[0] - 1:+.1%}")
```

Both routes land on the same answer, and both differ from the plain sum of simple returns. Caterpillar ends the two years up 20.3%, Deere down 2.9%, which is the comparison the client asked for in chapter 1, now stated as returns rather than revenue.

## F1.4 Excess returns

A stock return of 1% in a month sounds fine until cash paid 0.35%. What a model is usually asked to predict, and what an investor is paid for taking risk, is the **excess return**: the stock's return minus the **risk-free rate**, the return on something with no risk, such as a short-term Treasury bill.

> excess return = stock return − risk-free return

In the module the risk-free rate is a flat 0.35% a month, about 4.3% a year. Excess returns are also what the market and factor benchmarks on page F3 are measured in, so the two can be compared directly.

```{code-block} python
:class: pyodide
from finance_basics import RETURNS, RISK_FREE, excess, compound

for ticker in ["DE", "CAT", "MKT"]:
    e = excess(RETURNS[ticker])
    print(f"{ticker}: total return {compound(RETURNS[ticker]):+.1%}, "
          f"total excess return {compound(e):+.1%}, "
          f"average month {sum(e) / len(e):+.2%} above cash")
print(f"\ncash paid {RISK_FREE[0]:.2%} a month, the same every month")
```

Two things to keep from this page. First, which return a column holds is a choice, and the later chapters name it each time: "simple" or "log", "raw" or "excess". Second, anything you want to sum, average or compare over time is safest in log returns, and anything you report to a client is safest in compounded simple returns.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. A 20% gain takes $100 to $120, and a 20% loss on $120 is $24, leaving $96. The loss is taken from a bigger base, so the two do not cancel."
     data-no="Work it in dollars. Start with $100, add 20%, then take 20% off the new amount. What is left?">
  <p class="q">A stock rises 20% one month and falls 20% the next. Compared with where it started, you are:</p>
  <label><input type="radio" name="mlf-r-q1" value="a"> Exactly even, because +20% and −20% cancel</label>
  <label><input type="radio" name="mlf-r-q1" value="b"> Down 4%, because the fall is measured from the higher price</label>
  <label><input type="radio" name="mlf-r-q1" value="c"> Up 4%, because the gain came first</label>
  <div class="fb"></div>
</div>
```

## Further reading

- Wikipedia, [*Rate of return*](https://en.wikipedia.org/wiki/Rate_of_return) — simple and logarithmic returns side by side, with the formulas and the rule for combining periods.
- Wikipedia, [*Compound interest*](https://en.wikipedia.org/wiki/Compound_interest) — the same multiplication of growth factors, in the setting of savings.
- Kenneth French, [*Data Library*](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) — the monthly market, size, value and momentum returns and the risk-free rate that academics use, the real versions of the series used here.
