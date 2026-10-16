# 4.3 Improving and Judging a Model

```{raw} html
<p class="wk-lede">A closed formula only exists for the simplest models. The rest are found by walking: take a step that lowers the loss, then another. Then comes the harder question, whether a model that scores well on the past will score well on next month. This section is taught in the same session as 4.1 and 4.2.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch04-ml-foundations-1.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Describe gradient descent as repeated small steps downhill, and say what too large a step does.
- Split data by date into what a model learns from and what it is tested on.
- Recognise underfitting and overfitting from the gap between the two scores.
```

## 4.3.1 Gradient descent

Imagine standing on a hillside in fog. You cannot see the valley, but you can feel which way the ground slopes under your feet. Step downhill, feel again, step again. That is **gradient descent**. The hillside is the loss; your position is the model's parameters; the slope under your feet is the **gradient**, which tells you, for each parameter, whether nudging it up or down lowers the loss.

One step is `parameter = parameter - step size × gradient`. The **step size** (also called the learning rate) is chosen by a person. Too small and the walk takes forever; too large and each step overshoots the bottom and lands higher on the far side. Try all four sizes on the line from section 4.2:

```{raw} html
:file: widgets/ch04-gradient.html
```

The walk ends where `fit_line` already told us it would, slope 1.31 and intercept -1.13, because this loss has one bottom. For one line, descent is more work than the formula. Its value is that it keeps working when there is no formula: four features, or a model with billions of parameters. Chapter 0's [section 0B](ch00-training.md) shows the same walk on a bumpy surface, with the Adam variant that adapts its step size.

```{code-block} python
:class: pyodide
from ml_basics import table, column, descend

X, y = table()
x = [[a] for a in column(X, 0)]
for lr in (0.001, 0.02, 0.07):
    h = descend(x, y, lr=lr, steps=30)
    print(f"step size {lr}: loss after 0, 1, 5, 30 steps =", [round(h[k][1], 1) for k in (0, 1, 5, 30)])
```

The smallest step size is still on its way after 30 steps. The middle one has arrived. The largest has made the loss grow, not shrink: it overshoots further each time. The 0.07 is not special, only past the point where this loss can be walked in steps that big.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. A step that is too large jumps past the bottom and lands higher up the other side, so the loss rises each time."
     data-no="Think about the foggy hillside: what happens if every step is longer than the valley is wide?">
  <p class="q">Gradient descent on a loss starts well, then the loss gets larger every step. What is the most likely cause?</p>
  <label><input type="radio" name="q0" value="a"> The data have too many months</label>
  <label><input type="radio" name="q0" value="b"> The model has too few features</label>
  <label><input type="radio" name="q0" value="c"> The step size is too large</label>
  <div class="fb"></div>
</div>
```


## 4.3.2 A model is judged on months it never saw

A model with enough parameters can score well on the data it learned from by memorising it. What matters is how it does on cases it has not seen, which is **generalization**. So we hold some data back: the model learns from the **training** months and is scored on the **test** months. Here the split is by date: train on the earlier months, test on the last six, because a real model is always used on months after the ones it learned from. Shuffling would let it peek at the future.

Now predict next month's Deere return, not this month's, which is the question a forecaster asks:

```{code-block} python
:class: pyodide
from ml_basics import table, descend, predict, mse, split_by_date

X, y = table()
Xn, yn = X[:-1], y[1:]                       # this month's features, NEXT month's Deere return

def score(cols):
    rows = [[r[j] for j in cols] for r in Xn]
    Xa, ya, Xb, yb = split_by_date(rows, yn, 6)
    h = descend(Xa, ya, lr=0.002, steps=4000)
    w, b = h[-1][2], h[-1][3]
    return mse(ya, [predict(w, b, r) for r in Xa]), mse(yb, [predict(w, b, r) for r in Xb]), ya, yb

avg = None
for name, cols in (("1 feature (market)", [0]), ("4 features", [0, 1, 2, 3])):
    tr, te, ya, yb = score(cols)
    avg = mse(yb, [sum(ya) / len(ya)] * len(yb))
    print(f"{name}: error on months it learned {tr:5.1f}   on the 6 held back {te:5.1f}")
print("just guessing the training average, on the 6 held back:", round(avg, 1))
```

This is the honest result. Using more features made the score on the learned months *better* (about 22 against 33) and the score on the held-back months *much worse* (about 106 against 50). And even the one-feature model does worse on the held-back months than guessing the average (about 42). This month's market return says almost nothing about next month's Deere return, and the extra features gave the model more room to chase noise.

## 4.3.3 Underfitting, overfitting, generalization

Two ways to fail:

- **Underfitting.** The model is too simple to capture the pattern. It scores badly on the data it learned from *and* on new data. A flat line through the average is the extreme.
- **Overfitting.** The model is flexible enough to bend around the noise in the training data. It scores well on what it learned and badly on what it did not. The gap between the two scores is the warning.

The target is the middle: a model simple enough that what it learned is signal, flexible enough to keep that signal. Drag the slider on the curve below, which is the same picture as page F5's, and watch the two errors part:

```{raw} html
:file: widgets/mlf-overfit.html
```

Three habits come out of this section, and they are the habits that separate a model from a story:

1. Always score on data the model did not learn from, split by date.
2. Compare against the simplest baseline (guess the average). A model that cannot beat it has learned nothing.
3. Be more suspicious of a good score than a bad one. In finance, where next month is mostly news, a very good score on a forecast is far more likely a leak than a discovery.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. A big gap between a low training error and a high test error is the signature of overfitting: the model learned the noise in the months it studied."
     data-no="Look at the gap, not at either number alone. Which score is the model going to be judged on in practice?">
  <p class="q">A model has an error of 2 on the months it learned and 9 on the months held back. What is the likely problem?</p>
  <label><input type="radio" name="q1" value="a"> Underfitting, because the model is too simple</label>
  <label><input type="radio" name="q1" value="b"> Overfitting, because it did far better on what it learned</label>
  <label><input type="radio" name="q1" value="c"> Nothing: the test months are always harder</label>
  <div class="fb"></div>
</div>
```


## 4.3.4 Exercise

Open the Colab notebook and run section 3.

1. In the gradient descent cell, find the largest step size that still reaches the bottom in 30 steps. Is it faster than 0.02?
2. Change `split_by_date(rows, yn, 6)` to hold back 3 months, then 9. Does the verdict on the four-feature model change? What does that say about trusting a result from six months of test data?
3. Write three sentences for a portfolio manager who is excited that a model scored well on the past: what to ask before believing it.

## Further reading

- Trevor Hastie, Robert Tibshirani, Jerome Friedman, [*The Elements of Statistical Learning*](https://hastie.su.domains/ElemStatLearn/), chapter 7 (2009) — model assessment and the train/test idea, free to read.
- Marcos López de Prado, *Advances in Financial Machine Learning* (2018), chapter 7 — why finance needs splits by time, not random shuffles.
- Google, [*Machine Learning Crash Course: Overfitting*](https://developers.google.com/machine-learning/crash-course/overfitting) — a short treatment with generalization curves.
