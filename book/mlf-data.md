# F4 Financial and Macro Data

```{raw} html
<p class="wk-lede">A model is only as good as the table it is fed, and in finance the hard question is rarely "what is the number?" It is "when could we have known it?" This page lists the data the firm's models use (prices, company accounts, and the big economic series) and the one habit that keeps a back-test honest: use only what was published by the day you are standing on. This page is pre-reading, with no session of its own.</p>
```

```{admonition} Learning objectives
:class: note
- Name the three kinds of data behind a stock model: prices, fundamentals and macro series.
- Compute price-to-earnings, price-to-book and dividend yield from a company's figures.
- Explain data frequency, release date, revision and publication lag, and say why each one matters to a model.
- Spot look-ahead bias in a data table.
```

## F4.1 Three kinds of data

**Prices** are the easy part: a closing price every trading day, or the month-end prices used on page F1. They are public, they arrive the moment the market closes, and they are never revised.

**Fundamentals** come from a company's accounts: revenue, earnings, the value of its assets, what it pays out. They arrive four times a year, weeks after the quarter ends, and companies sometimes restate them later.

**Macro series** describe the whole economy: inflation, interest rates, jobs, output. They come from government agencies and central banks, on a fixed calendar, and the big ones are revised.

| | Frequency | Arrives | Revised? |
|---|---|---|---|
| Stock prices | Every trading day | When the market closes | No |
| Fundamentals | Quarterly | Weeks after quarter-end | Sometimes (restatements) |
| Inflation, jobs | Monthly | One to three weeks after month-end | Jobs often; inflation rarely |
| GDP | Quarterly | About a month after quarter-end, then twice more | Yes, repeatedly |
| Interest-rate decisions | Eight meetings a year | The day of the meeting | No |

The mismatch in the middle column is the whole difficulty. A model that predicts monthly returns from a quarterly series has to say which quarter's number it used, and whether anyone could have read it yet.

## F4.2 Fundamentals and valuation ratios

A price on its own tells an analyst little: is $512 a lot for Deere? Dividing the price by something the company earns or owns makes two firms comparable.

- **Price-to-earnings (P/E)** is the price divided by the last twelve months of earnings per share. It says how many dollars investors pay for one dollar of a year's profit.
- **Price-to-book (P/B)** is the price divided by the accounting value of the company's assets, per share, after debts.
- **Dividend yield** is the yearly dividend per share divided by the price: the cash return before any change in the price.

These are the raw material of the "value" benchmark on page F3, and in chapters 4 and 5 they become the inputs a model is given. Here they are for the two companies the firm follows:

```{code-block} python
:class: pyodide
from finance_basics import FUNDAMENTALS, valuation

for ticker in FUNDAMENTALS:
    f = FUNDAMENTALS[ticker]
    v = valuation(ticker)
    print(f"{ticker}: price ${f['price']:.2f}, earnings per share ${f['eps_ttm']:.2f}, book value per share ${f['book_per_share']:.2f}")
    print(f"    P/E {v['pe']:.1f}   P/B {v['pb']:.1f}   dividend yield {v['yield']:.1%}")
```

Deere costs 20 times a year's earnings; Caterpillar costs 18. That looks cheaper, but a ratio only compares like with like. It says nothing about why. Caterpillar may be cheaper because its profits are expected to fall, which is exactly the kind of question a model is for. The illustrative figures here are made up; the shape of the calculation is not.

## F4.3 Macro series and their calendars

Four families of macro series do most of the work in stock and market models:

- **Inflation**: how fast prices are rising, usually the year-on-year change in a consumer price index. It matters because it drives interest rates, and interest rates change what every future profit is worth today.
- **Interest rates**: the central bank's target rate, and the yields on government bonds of different lengths. Page F5 returns to the gap between long and short yields.
- **Employment**: the unemployment rate and the monthly change in jobs. A fast read on the economy's health.
- **Output**: GDP growth, the broadest and slowest measure.

Each has a calendar. The agencies publish the dates a year ahead, so a model can be built to ask "what had been released by this date?"

## F4.4 Release dates, revisions and lags

Three things separate a data point's *date* from its *knowability*.

**Period versus release date.** The August jobs figure describes August, but it comes out in the first days of September. The gap between the end of the period and the release is the **publication lag**: a few days for jobs, about eleven days for inflation, about a month for the first estimate of GDP.

**Revisions.** The first number is an estimate from an incomplete survey. As more responses arrive, the agency rewrites it, sometimes by a lot. In the illustrative data below, a first jobs report of +142 thousand becomes +96 thousand a month later, and a first GDP estimate of 2.6% becomes 2.1%.

**Point-in-time data** means keeping, for each date, the numbers as they stood on that date: the first release and every revision with its own release day. A series downloaded today holds only the final values, which nobody could see at the time.

Drag the date and watch what a model can use. Then turn on the cheat:

```{raw} html
:file: widgets/mlf-release-timeline.html
```

```{code-block} python
:class: pyodide
from finance_basics import MACRO, known_on

series = "Nonfarm payrolls, change (thousands)"
for day in ["2026-09-03", "2026-09-10", "2026-10-05"]:
    print(f"{day}: a model could use {known_on(series, day)}")

print()
print("Days from the end of the period to the first release:")
for m in MACRO:
    print(f"  {m['series']:40s} {m['period']:6s} out {m['first']}")
```

On September 3 the August jobs number does not exist, so the function returns nothing. By September 10 it is +142 thousand. After October 2 the same question gets a different answer, +96 thousand, because the figure was revised. A table with one row per month and the final number in it throws that story away.

## F4.5 The look-ahead trap

A back-test asks: if we had used this rule in the past, how would it have done? It is honest only if each decision uses information that existed on that day. Using final, revised numbers, or an August figure on August 31, lets the model see the future. The result is a strategy that looks wonderful in a test and cannot be run live.

There are three common ways it creeps in, and each is a data-table problem rather than a modelling one:

1. **Dating by period, not by release.** The August jobs row is stamped 31 August, but nobody knew it until 4 September.
2. **Using revised values.** The final GDP figure was not the one on the screen that week.
3. **Today's company list.** Fundamentals pulled from a database now describe firms that survived to now, which flatters every test. Chapter 5 returns to this.

The fix is the habit this page began with. For every row, ask *when could we have known this?* and store that date next to the value. Chapters 4 and 5 build the validation scheme around it.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. On 31 August the August jobs report had not been published, so a model that uses it is looking at the future. The row needs a release date next to the period."
     data-no="Look at the timeline widget. On 31 August, is the August jobs figure out yet? Which date should the row be stamped with?">
  <p class="q">An analyst builds a table with one row per month, stamped with the last day of the month, and puts that month's jobs report on the row. Trading rules are tested on the 31st of each month using that row. What is wrong?</p>
  <label><input type="radio" name="mlf-data-q1" value="a"> Nothing; monthly data should be stamped at month-end</label>
  <label><input type="radio" name="mlf-data-q1" value="b"> The jobs report is not published until days after month-end, so the test uses information that did not exist yet</label>
  <label><input type="radio" name="mlf-data-q1" value="c"> Jobs data is too noisy to use in any model</label>
  <div class="fb"></div>
</div>
```

## Further reading

- Federal Reserve Bank of St. Louis, [*ALFRED: Archival Federal Reserve Economic Data*](https://alfred.stlouisfed.org/) — every revision of a macro series, with the date each value was known. The tool for point-in-time data.
- Federal Reserve Bank of St. Louis, [*FRED*](https://fred.stlouisfed.org/) — the free source for most macro series used in this book.
- Federal Reserve Bank of Philadelphia, [*Real-Time Data Research Center*](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research) — datasets of macro series as first reported, and notes on how large revisions are.
- Bureau of Economic Analysis, [*Release schedule*](https://www.bea.gov/news/schedule) — the dates GDP and related figures are published, a year ahead.
- Federal Reserve, [*FOMC calendars*](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) — the eight meeting dates each year, when the policy rate is set.
