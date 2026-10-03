# Foundations for ML

```{raw} html
<p class="wk-lede">Part II teaches machine learning on stocks and macro data. Before it starts, this part covers the finance and the statistics every model there is built on: what a return is, how risk is measured, what a benchmark is, when a number was actually known, and what it means for a line to fit data. It is self-paced, with no session of its own.</p>
```

Chapters 4 and 5 ask a model to predict returns. A model can only be as sound as the quantities it is fed, and most of the ways these models go wrong are finance mistakes, not code mistakes: a return that does not add up, a risk number that hides a crash, a benchmark that explains the whole result, a figure that was not yet published on the day the model "used" it. This part removes those traps first.

Do it on your own time, before session 4 (Fri, Oct 16). It needs no key and no background beyond the earlier chapters. Five pages, each with a widget to play with and a few runnable cells:

- **[F1 Prices and Returns](mlf-returns.md).** Simple, log and excess returns, and why a 50% gain followed by a 50% loss is not break-even.
- **[F2 Risk: Volatility and Drawdowns](mlf-risk.md).** How much a return moves, how far it fell from its peak, and return per unit of risk.
- **[F3 Benchmarks and Factors](mlf-benchmarks.md).** Beta to the market, the size, value and momentum benchmarks, and what is left over as alpha.
- **[F4 Financial and Macro Data](mlf-data.md).** Prices, fundamentals, valuation ratios, inflation, rates, jobs and GDP, and the release dates, revisions and publication lags that decide what a model could have known.
- **[F5 The Statistics You Need](mlf-statistics.md).** Mean, variance, correlation, a line fitted by least squares, overfitting, and splitting by time instead of at random.

The pages share one Colab notebook, [`mlf-foundations.ipynb`](https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch0f-ml-foundations.ipynb). It uses numpy, pandas and matplotlib only.

```{admonition} About the numbers
:class: note
Every price, return and macro figure in this part is **illustrative**: made up for teaching, in the style of the firm's other fixtures (Deere and Caterpillar, with prices that match the rest of the book). They are not market data, and nothing here is a forecast.
```
