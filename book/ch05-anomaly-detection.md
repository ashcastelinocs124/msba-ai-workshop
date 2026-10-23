# 5.3 Anomaly Detection

```{raw} html
<p class="wk-lede">An anomaly is a row that does not look like the rest. Anomaly detection scores how unusual each row is so a person can look at the top few. This section is taught in the same session as 5. The session 5 slides are on <a href="ch05-ml-foundations-2.html#ch05-lecture">the chapter 5 page</a>.1 and 5.2.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch05-ml-foundations-2.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Score how unusual a row is as its distance from a normal row, and read the score.
- Choose a threshold, and say what too many or too few flags cost.
- Explain why a flag is a question for a person and not a finding, and why the list depends on what is measured.
```

## 5.3.1 Finding what does not fit

Clustering (5.1) asks which rows are alike. **Anomaly detection** asks the reverse: which row is unlike all the others? It is unsupervised again, because the model is not shown examples of "odd". It learns what normal looks like from the table and scores each row by how far it is from that.

At a research firm this is a screen, not an answer. A month that looks nothing like the others might be a data error, a one-off event, or the start of a new regime. All three deserve a person's attention before any analysis is trusted, and none of them can be told apart by the score.

## 5.3.2 A score for "unusual"

The simplest score uses what 5.1 set up. Standardize every column so each is in typical swings. A normal month is then the average month, which is zero in every column. A month's **score** is its distance from that point. `odd_scores` computes it, and `most_odd` picks the top few.

```{code-block} python
:class: pyodide
from ml_unsup import months, standardize, odd_scores, most_odd
from finance_basics import MONTHS

X = months()                                   # the four benchmarks
scores = odd_scores(X)
print("average score:", round(sum(scores) / len(scores), 1))
print("most unusual months:")
for i in most_odd(scores, 5):
    print("  ", MONTHS[i], round(scores[i], 2), [round(v, 1) for v in X[i]])
```

With four columns a typical month scores about 2. The five highest are Sep 25 (3.1), Jun 25 (3.0), Aug 25 (2.9), Dec 24 (2.8) and Sep 26 (2.6). Look at Sep 25: the market down 6.2, value down 5.6, momentum down 3.4. No one column is wildly out, but several are moderately out at once, and that is what the distance adds up.

## 5.3.3 Where to draw the line

The model returns a score for every month. Turning that into a list means choosing a **threshold**, and the choice is about workload and cost, not statistics. Set it too high and a real problem slips past. Set it too low and the list is so long that no one reads it, and a list that is ignored finds nothing.

```{raw} html
:file: widgets/ch05-anomaly.html
```

A usual way to set it is by capacity: how many items can a person review? If an analyst can look at three months a quarter, the threshold is whatever gives three. That also forces the question of what a missed anomaly costs against a wasted review.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. Flags are only useful if someone reviews them, so the threshold is set by what a person can review and what a miss would cost."
     data-no="Think about what happens to a list of flags that is too long for anyone to read.">
  <p class="q">An analyst lowers the threshold until a third of the months are flagged. What is the main problem?</p>
  <label><input type="radio" name="q0" value="a"> The score is no longer a distance</label>
  <label><input type="radio" name="q0" value="b"> The list is too long to review, so the real anomalies get lost among the flags</label>
  <label><input type="radio" name="q0" value="c"> The model must be retrained</label>
  <div class="fb"></div>
</div>
```

## 5.3.4 What you measure changes the answer

The score depends on which columns you give it. Add Deere's and Caterpillar's own returns to the four benchmarks:

```{code-block} python
:class: pyodide
from ml_unsup import months, standardize, odd_scores, most_odd, NAMES
from finance_basics import MONTHS

X = months(NAMES)
z, _, _ = standardize(X)
scores = odd_scores(X)
for i in most_odd(scores, 3):
    big = max(range(len(NAMES)), key=lambda j: abs(z[i][j]))
    print(MONTHS[i], round(scores[i], 2), "| raw:", [round(v, 1) for v in X[i]])
    print("    largest single column:", NAMES[big], round(z[i][big], 1), "typical swings from average")
```

Now Sep 26 is the most unusual month (the market down 7.2, Deere down 13.7 and Caterpillar down 13.9 together) and Feb 25 enters the top three because Deere rose 14.3. On the four benchmarks alone, Sep 26 ranked fifth.

Neither list is wrong. They answer different questions: which months were strange for the *market*, and which were strange for *Deere and Caterpillar*. Part of the work is deciding which question you are asking, before the model runs.

A second limit: this score measures distance from one average month. A month can be far from the average and still be typical of its own group from 5.1: a sell-off month is unusual against all months, but ordinary among sell-offs. If the data has groups, measure each month's distance to the centre of its own group instead.

## 5.3.5 A flag is a question

Take the top flag. Sep 26 might be:

- **A data error.** A wrong price or a misplaced decimal. Check the source.
- **A real, one-off event.** A shock the firm already knows about. Note it, and decide whether it belongs in the training data for any model.
- **The start of something new.** The thing a monitoring system exists to catch. Whatever tells it from the previous case is outside the table.

The score cannot say which. It can only say *look here first*. That is why, at the firm, the output of an anomaly detector is a list handed to a person with the reason attached (above, the columns that were furthest out), and why a person signs off before anything is changed or sent.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. The detector only measures distance from normal. Whether the month is an error, an event or a new regime is for a person to find out."
     data-no="The score says how far a month is from normal, not why. Which of the answers goes beyond what a distance can tell you?">
  <p class="q">Sep 26 has the highest score. What can you conclude?</p>
  <label><input type="radio" name="q1" value="a"> It is a data error and should be deleted</label>
  <label><input type="radio" name="q1" value="b"> The market will keep falling</label>
  <label><input type="radio" name="q1" value="c"> It is the most unusual month on these columns and deserves a person's review; the score does not say why</label>
  <div class="fb"></div>
</div>
```

## 5.3.6 Exercise

Open the Colab notebook and run section 3.

1. Score the months on market and momentum only. Is Sep 26 still in the top three? Which month rises most, and why?
2. Set the threshold so that exactly three months are flagged on the six series. Write one sentence for each flag saying what you would check before using that month in a model.
3. Compare the score with scikit-learn's `IsolationForest` (the notebook sets it up). Do the two methods flag the same months? Where they disagree, which would you trust, and why?

## Further reading

- scikit-learn, [*Novelty and outlier detection*](https://scikit-learn.org/stable/modules/outlier_detection.html) — the main methods, with plots of what each one flags.
- Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani, [*An Introduction to Statistical Learning*](https://www.statlearning.com/), chapter 12 (2021) — unsupervised learning, free to read.
