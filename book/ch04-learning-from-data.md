# 4.1 Learning From Data

```{raw} html
<p class="wk-lede">Until now the agent followed instructions. A model learns its rule from examples instead. First decide what kind of learning the task needs, then turn the firm's data into the numbers a model can read. This section is taught in the same session as 4.2 and 4.3. The session 4 lecture recording is on <a href="ch04-ml-foundations-1.html#ch04-lecture">the chapter 4 page</a>.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch04-ml-foundations-1.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Tell supervised, unsupervised and reinforcement learning apart by what the data contains.
- Turn a table of months into features, a label, a vector and a matrix.
- Say what a parameter is, and count the parameters of a small model.
```

## 4.1.1 What machine learning is

The agent in chapters 1 to 3 works from rules a person wrote: a prompt, a tool list, a policy clause. **Machine learning** replaces some of those rules with a rule the computer finds itself, from examples. Show it enough past months and it works out how Deere's return tends to move with the market's, without anyone writing "multiply by 1.3".

What the examples look like decides the kind of learning. There are three.

- **Supervised learning.** Every example comes with the right answer, called the **label**. The model learns to predict the label for new cases. Predicting next month's return, or whether a trade request will be flagged, are supervised tasks.
- **Unsupervised learning.** The examples have no answers. The model looks for structure: groups of similar clients, months that look unlike the rest.
- **Reinforcement learning.** There are no examples to copy. The model takes actions and receives a reward, and it adjusts to earn more of it. Chapter 0's [section 0C](ch00-post-training.md) has a simulator for this one.

Sort five of the firm's tasks:

```{raw} html
:file: widgets/ch04-kinds.html
```

Most of the models in this book, and most that finance teams ship, are supervised. They are also the easiest to check, because the right answer is known afterwards. The rest of this chapter is supervised learning.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. Past emails already carry a right answer (urgent or not), so this is supervised. Grouping clients with no labels is unsupervised, and learning from a reward is reinforcement."
     data-no="Ask what the data contains. If every example already has the right answer attached, it is supervised.">
  <p class="q">The compliance team has 5,000 old trade requests, each marked approved or escalated. They want a model that marks new ones. Which kind of learning is it?</p>
  <label><input type="radio" name="q0" value="a"> Unsupervised, because the model works on its own</label>
  <label><input type="radio" name="q0" value="b"> Supervised, because each example has its label</label>
  <label><input type="radio" name="q0" value="c"> Reinforcement, because a person checks the result</label>
  <div class="fb"></div>
</div>
```


## 4.1.2 Data as numbers

A model cannot read a table of months. It reads numbers in a fixed order. Each row of the table is one case; the numbers describing the case are its **features**, and the thing to predict is the **label**.

Take the firm's data from [page F1](mlf-returns.md). For each month we know four benchmark returns: the market, the size factor, the value factor and momentum. The label is what Deere did the following month. One row:

| month | market | size | value | momentum | **label: Deere next month** |
|---|---|---|---|---|---|
| Jan 25 | +5.85 | +1.11 | +0.91 | +3.16 | **+14.30** |

The four features, in order, are a **vector**: `[5.85, 1.11, 0.91, 3.16]`. Stack every month's vector and you get a **matrix**, written `X`, with one row per month and one column per feature. The labels stack into a vector `y`. Everything a supervised model does is arithmetic on `X` and `y`.

```{raw} html
:file: widgets/ch04-matrix.html
```

The last month has no "next month", so 24 months of returns give 23 rows. Losing a row to line up features and label is normal, and getting the alignment wrong, so that a feature secretly contains the future, is the commonest way to build a model that looks brilliant and is useless (see [page F5](mlf-statistics.md)).

```{code-block} python
:class: pyodide
from ml_basics import table, column, FEATURES

X, y = table()
print("features:", FEATURES)
print("rows in X:", len(X), "   columns:", len(X[0]))
print("one vector:", [round(v, 2) for v in X[3]])
print("its label :", round(y[4], 2), "  (Deere the following month)")
print("market column:", [round(v, 1) for v in column(X, 0)][:6], "...")
```

`table()` here lines each month up with the same month's Deere return; for the next-month version, the cell shifts the labels by one, as the widget does. Section 4.3 uses that version.

## 4.1.3 Parameters: what the model keeps

A model is a rule with adjustable numbers inside. Here is the simplest: multiply each feature by a number, add them up, and add a starting number.

`prediction = w1 × market + w2 × size + w3 × value + w4 × momentum + b`

The multipliers `w1` to `w4` are the **weights** and `b` is the **bias**, the prediction when every feature is zero. Together they are the model's **parameters**: five numbers. Learning means finding good values for them. The features and labels come from the world; the parameters belong to the model.

```{code-block} python
:class: pyodide
from ml_basics import table, predict

X, y = table()
w = [1.0, 0.0, 0.0, 0.0]     # a guess: Deere moves one-for-one with the market
b = 0.0
for k in (0, 3, 11):
    print("month", k, " predicted", round(predict(w, b, X[k]), 2), " actual", round(y[k], 2))
```

The guess is not good, and it should not be: nothing has taught it yet. Chapter 0's [section 0.4](ch00-how-llms-work.md) said a large language model has billions of these numbers; the line we fit has two. The idea is the same.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. Four weights and one bias make five parameters. The 23 rows are data, not parameters, and the label is what the model predicts."
     data-no="Count the numbers the model itself keeps: one multiplier per feature, plus the starting number.">
  <p class="q">A model predicts Deere's next-month return from the market, size, value and momentum returns, one weight each, plus a bias. How many parameters does it have?</p>
  <label><input type="radio" name="q1" value="a"> 23, one per month of data</label>
  <label><input type="radio" name="q1" value="b"> 1, the prediction</label>
  <label><input type="radio" name="q1" value="c"> 5, four weights and a bias</label>
  <div class="fb"></div>
</div>
```


## 4.1.4 Exercise

Open the Colab notebook and run section 1.

1. Change `table("DE")` to `table("CAT")`. Which of the four columns of `X` moves most like the labels? Check by eye, then with `corr` from [page F5](mlf-statistics.md).
2. Write the vector for the month of your choice by hand, then check it against `X`.
3. In two sentences: name one task at the firm that would be supervised, one unsupervised, and what would be the label in the first.

## Further reading

- Andrew Ng, [*Machine Learning Specialization*](https://www.coursera.org/specializations/machine-learning-introduction), course 1 (2022) — supervised and unsupervised learning, features and labels, built up the same way.
- Google, [*Machine Learning Crash Course*](https://developers.google.com/machine-learning/crash-course) — free, short, with exercises; its Framing and Data modules cover this section.
