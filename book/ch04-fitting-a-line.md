# 4.2 Fitting a Line

```{raw} html
<p class="wk-lede">The simplest model that predicts a number is a straight line. Fitting one means choosing two numbers, and judging a choice means turning "how wrong" into one score. That score is the loss. This section is taught in the same session as 4.1 and 4.3.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch04-ml-foundations-1.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Read a fitted line: what the slope and the intercept say, in the firm's terms.
- Compute a loss for a guess, and say why squared and absolute error behave differently.
- Fit the best straight line in one step with the closed-form solution, and say what it cannot do.
```

## 4.2.1 A line as a model

A **regression** predicts a number. With one feature, the model is a line: `prediction = slope × feature + intercept`. The **slope** says how far the prediction moves when the feature moves by one unit. The **intercept** is the prediction when the feature is zero.

Take the question from [page F3](mlf-benchmarks.md): when the market moves, how much does Deere move in the same month? Each dot below is one month. Drag the line, and notice that every position of it is a guess with a score.

```{raw} html
:file: widgets/ch04-line-fit.html
```

The score under the chart is the **loss**, introduced next. The reading of the line is the useful part: a slope of 1.3 says that, in this data, Deere has moved about 1.3 points for each point the market moved. That is a **beta**, as on page F3 (which uses returns in excess of cash); this is where the number comes from.

## 4.2.2 Loss: scoring a guess

To compare two lines you need one number per line. Take each month's **miss** (the actual return minus the line's prediction) and combine them. Two common ways:

- **Mean absolute error (MAE).** Average the sizes of the misses.
- **Mean squared error (MSE).** Square each miss, then average. A 4-point miss counts four times as much as a 2-point miss, not twice.

The average of the squares is what the widget above shows, and it is the default for regression for a practical reason as much as a principled one: it has a smooth bottom, which makes it easy to walk down (section 4.3). Its cost is that one very bad month can dominate it.

```{raw} html
:file: widgets/ch04-mse-mae.html
```

A **loss function** is any such score, chosen to match what a miss costs. If a 10-point miss is ten times as bad as a 1-point miss, MAE matches. If it is a hundred times as bad, MSE does. A model never "knows" what you care about; the loss is where you tell it.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. Squaring makes the one 10-point month count 100 against 1 for a 1-point month, so a model trained on squared error will work hardest to fix it."
     data-no="Compare the two ways of counting a 10-point miss: its size, or its size squared.">
  <p class="q">Nine months are missed by 1 point and one month by 10. Which loss is dominated by the 10-point month?</p>
  <label><input type="radio" name="q0" value="a"> Mean squared error</label>
  <label><input type="radio" name="q0" value="b"> Mean absolute error</label>
  <label><input type="radio" name="q0" value="c"> Neither: both treat the months equally</label>
  <div class="fb"></div>
</div>
```


## 4.2.3 Finding the best line

For one feature the best line, the one with the smallest mean squared error, has a closed-form answer. No searching is needed: the slope is how the feature and the label vary together, divided by how much the feature varies on its own, and the intercept then makes the line pass through the averages. That is **least squares**, and `fit_line` does it.

```{code-block} python
:class: pyodide
from ml_basics import table, column, fit_line, predict, mse, mae

X, y = table()
x = column(X, 0)                       # the market's return, same month
slope, intercept = fit_line(x, y)
pred = [slope * a + intercept for a in x]

print(f"best line: Deere = {slope:.2f} x market + ({intercept:.2f})")
print("mean squared error:", round(mse(y, pred), 1))
print("mean absolute error:", round(mae(y, pred), 1), "points")
print("guessing the average every month, squared error:", round(mse(y, [sum(y) / len(y)] * len(y)), 1))
```

The line cuts the squared error from about 36 (guess the average) to under 10: it explains roughly three quarters of the month-to-month movement in Deere, which is the R squared from [page F5](mlf-statistics.md). The best a straight line can do is still a miss of about 2.5 points a month, because Deere also moves on news the market does not carry.

Now use all four features, one weight each. The model is a dot product, and the best weights are still a minimisation, though no longer a one-line formula. The next section finds them by walking:

```{code-block} python
:class: pyodide
from ml_basics import table, predict, mse, descend

X, y = table()
w = [1.4, -0.4, 0.2, -0.5]; b = -0.9           # roughly where the walk below ends up
print("four-feature loss:", round(mse(y, [predict(w, b, r) for r in X]), 1))
print("one-feature loss was 9.7")
```

More features lowered the score on these 24 months. Whether that is a better model or just a more flexible one is the question section 4.3 ends on.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. It is the prediction when the market's return is zero. The beta, the response to the market, is the slope."
     data-no="The intercept is where the line crosses the vertical axis, where the feature is zero.">
  <p class="q">In Deere = 1.31 x market - 1.13, what does the -1.13 say?</p>
  <label><input type="radio" name="q1" value="a"> Deere falls 1.13 points for every market point</label>
  <label><input type="radio" name="q1" value="b"> The predicted Deere return in a month when the market is flat</label>
  <label><input type="radio" name="q1" value="c"> The share of Deere's movement the market explains</label>
  <div class="fb"></div>
</div>
```


## 4.2.4 Exercise

Open the Colab notebook and run section 2.

1. Fit the line for Caterpillar instead of Deere. Is the slope above or below Deere's? Which stock moves more with the market in this data?
2. Delete the worst month (the last one, the market's -7.2 and Deere's -13.7) and refit. How far does the slope move? What does that say about how much a single month steers the line?
3. Switch the loss from squared to absolute error in your head: which of the two fits would you expect to move more when one month is removed, and why?

## Further reading

- Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani, [*An Introduction to Statistical Learning*](https://www.statlearning.com/), chapter 3 (2021) — linear regression, free to read.
- 3Blue1Brown, [*Neural networks*](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi), chapter 2 (2017) — what a "cost function" is, drawn well.
