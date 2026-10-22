# 5.2 Dimensionality Reduction

```{raw} html
<p class="wk-lede">A table with many columns is hard to look at, hard to cluster and easy to overfit. Dimensionality reduction replaces many columns with a few new ones that keep most of what varies. This section is taught in the same session as 5.1 and 5.3.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch05-ml-foundations-2.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Say why columns that move together can be replaced by fewer numbers, and what is lost.
- Read the output of principal component analysis: the share of variation each component carries, and the weights that make it up.
- Pick how many components to keep, and use them to see or to cluster the data.
```

## 5.2.1 Columns that say the same thing

Each month now has six numbers: the market, size, value, momentum, Deere and Caterpillar. Many of them are not independent. Deere and the market move together (correlation 0.86; [page F5](mlf-statistics.md) explains correlation), Caterpillar and the market even more (0.92), and Deere and Caterpillar with each other (0.81). Three columns that tell nearly the same story are close to one column said three times.

**Dimensionality reduction** uses that overlap. It builds a few new columns, each a weighted mix of the old ones, so that the new columns keep as much of the variation as possible. Fewer columns are easier to plot, quicker to cluster, and give a model less room to fit noise (the overfitting from section 4.3).

## 5.2.2 Principal components

**Principal component analysis (PCA)** builds the new columns one at a time:

1. The **first component** is the direction along which the months vary the most.
2. The **second** is the direction of the most variation left over, at right angles to the first.
3. And so on, each one capturing less than the last.

As in 5.1, the columns are standardized first. Each component has a **share**: the fraction of all the variation it carries. The shares add to 100%.

```{code-block} python
:class: pyodide
from ml_unsup import months, pca, NAMES

X = months(NAMES)                              # six series per month, in percent
components, shares = pca(X, 3)

print("columns:", NAMES)
for i, (c, s) in enumerate(zip(components, shares), 1):
    print(f"component {i}: carries {100 * s:.0f}% of the variation, weights", [round(w, 2) for w in c])
```

Read the weights like a recipe. Component 1 puts weight of about 0.5 on the market, on Deere and on Caterpillar and little on the rest: it is **the market tide**, one number for "was this a good month for stocks in general". It carries 52% of everything in the table. Component 2 is size against momentum (+0.66 and -0.65), which is a different story, and carries another 21%. The names are ours; the model returns only weights.

```{raw} html
:file: widgets/ch05-pca.html
```

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. The component is a mix of the original columns. Its weights are how much each one counts, and the share is how much of the table's variation it carries."
     data-no="The component is built from the old columns; its weights tell you how much each contributes.">
  <p class="q">Component 1 has weights of about 0.5 on the market, Deere and Caterpillar. What does it measure?</p>
  <label><input type="radio" name="q0" value="a"> How good the month was for stocks in general: the part the three columns share</label>
  <label><input type="radio" name="q0" value="b"> Deere's return, predicted from the other columns</label>
  <label><input type="radio" name="q0" value="c"> The one column that matters and the others can be deleted</label>
  <div class="fb"></div>
</div>
```

## 5.2.3 How many components to keep

Keeping the first two components keeps 73% of the variation, and three keep 88%. The last two carry about 4% between them, which is mostly noise. There is no rule for where to stop: keep enough that what you lose does not matter for the job, and few enough that the picture is simple. Two is convenient because two numbers can be drawn.

The cost is that the new columns are harder to explain than the old ones. "Deere's return" means something to a client; "component 2" has to be explained each time. For the firm's research that matters, so reduction is used to see the data or to feed another method, and rarely to report a result.

## 5.2.4 Using the short description

`project` gives each month's coordinates on the components, its short description. Two uses follow.

```{code-block} python
:class: pyodide
from ml_unsup import months, pca, project, kmeans, NAMES
from finance_basics import MONTHS

X = months(NAMES)
components, shares = pca(X, 2)
P = project(X, components)                     # 24 rows, two numbers each

order = sorted(range(24), key=lambda i: P[i][0])
print("lowest on component 1 (the weakest months for stocks):")
for i in order[:3]:
    print("  ", MONTHS[i], [round(v, 1) for v in P[i]])

centers, labels = kmeans(P, 3)                 # cluster on two numbers instead of six
print("groups of months:", sorted(labels.count(g) for g in range(3)))
```

First, **look**. Sep 25 and Sep 26 both land at -3.7 on component 1, further out than any other month: the two worst months for stocks in the data. Second, **cluster on the short description**. The groups found from two components agree with the groups in 5.1 for 23 of the 24 months (only Dec 25 moves), so almost nothing was lost for this purpose.

Two cautions. PCA only finds straight-line patterns: a relationship that bends is invisible to it. And as in 5.1, the components describe these 24 months; a different set of months gives somewhat different weights.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. Reduction trades detail for simplicity, and how much detail you can lose depends on what the result is for."
     data-no="Look at the shares: each extra component adds less, and the cost of fewer columns is that you lose some of what varies.">
  <p class="q">Two components keep 73% of the variation and three keep 88%. Which is the right number to keep?</p>
  <label><input type="radio" name="q1" value="a"> Three, because more is always better</label>
  <label><input type="radio" name="q1" value="b"> Two, because the rule is to keep at least 70%</label>
  <label><input type="radio" name="q1" value="c"> It depends on the job: how much detail it needs against how simple you want the picture</label>
  <div class="fb"></div>
</div>
```

## 5.2.5 Exercise

Open the Colab notebook and run section 2.

1. Run PCA on only the four benchmarks (`months()` instead of `months(NAMES)`). How much does the first component carry now, and what do its weights look like? Why did adding Deere and Caterpillar raise it?
2. Plot the months on components 1 and 2 and colour them by the 5.1 groups. Where does each group sit?
3. Keep one component instead of two and re-cluster. Which months change group, and what does that tell you about what component 2 was carrying?

## Further reading

- Victor Powell and Lewis Lehe, [*Principal Component Analysis explained visually*](https://setosa.io/ev/principal-component-analysis/) — drag the data and watch the components move.
- Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani, [*An Introduction to Statistical Learning*](https://www.statlearning.com/), chapter 12 (2021) — PCA and what it can and cannot do, free to read.
