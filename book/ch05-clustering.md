# 5.1 Clustering

```{raw} html
<p class="wk-lede">Clustering sorts rows into groups of similar rows without being told what the groups are. This section is taught in the same session as 5.2 and 5.3. Each month of the firm's data is one row, and the question is which months look alike.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch05-ml-foundations-2.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Say what unsupervised learning is, and why the output has no score against a right answer.
- Run k-means by hand: assign each row to its nearest centre, move each centre to the middle of its rows, repeat.
- Say why columns are put on one scale first, and why the number of groups is a judgement.
```

## 5.1.1 Learning without a label

In chapter 4 each month had four features (the market's, size's, value's and momentum's returns) and a label, Deere's return. Delete the label. What is left is a table of 24 rows and four columns, and a different kind of question: **do some of these months resemble each other?** Answering it is **clustering**: the model proposes groups, and every month goes in exactly one.

This is the first kind of **unsupervised learning** from section 4.1. Nothing marks a grouping as correct. You judge it by whether the groups are tight, whether they are stable, and above all whether they mean something to the person who will use them.

## 5.1.2 One scale for every column

Distance is the idea underneath clustering: two months are alike when their rows are close. But a distance adds up the columns, so a column with big numbers dominates. Look at how much each column moves:

```{code-block} python
:class: pyodide
from ml_unsup import months, standardize
from finance_basics import MONTHS

X = months()                                  # market, size, value, momentum, in percent
z, means, spreads = standardize(X)
print("typical swing of each column (its spread):", [round(s, 1) for s in spreads])
print("first month before:", [round(v, 1) for v in X[0]])
print("first month after: ", [round(v, 1) for v in z[0]])
```

The market swings about 4 points a month and size about 2. Left alone, a size difference would count for half as much as a market difference just because of the units. **Standardizing** subtracts each column's average and divides by its spread, so every column is measured in "typical swings" and counts equally. Nearly every method in this chapter starts here.

## 5.1.3 k-means

**k-means** needs one choice from you, the number of groups, k. Then it repeats two steps:

1. **Assign.** Give each month to the nearest group centre.
2. **Move.** Put each centre at the average of the months now assigned to it.

It starts with some centres, and stops when no month changes group. `kmeans` does it:

```{code-block} python
:class: pyodide
from ml_unsup import months, standardize, kmeans, inertia
from finance_basics import MONTHS

X = months()
z, _, _ = standardize(X)
centers, labels = kmeans(z, 3)

for g in range(3):
    mine = [i for i in range(24) if labels[i] == g]
    avg = [sum(X[i][j] for i in mine) / len(mine) for j in range(4)]
    print(f"group {g + 1}: {len(mine)} months, average market/size/value/momentum:", [round(v, 1) for v in avg])
    print("   ", ", ".join(MONTHS[i] for i in mine))
print("tightness (lower is tighter):", round(inertia(z, centers, labels), 1))
```

Read the averages and name the groups yourself: the model returns only "group 1, 2, 3". One group is a steady rally with strong momentum (the market up about 2.7 points, momentum up 2.4). One is a rally led by small and value stocks, with momentum falling. One is five months of sell-off, the market down about 5 points on average. Try it:

```{raw} html
:file: widgets/ch05-kmeans.html
```

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. The market's numbers are the biggest, so without a common scale it would decide almost every grouping by itself."
     data-no="Think about which column has the largest numbers, and what that does to a distance that adds the columns up.">
  <p class="q">Why are the columns standardized before k-means?</p>
  <label><input type="radio" name="q0" value="a"> So the groups come out the same size</label>
  <label><input type="radio" name="q0" value="b"> So the model can use Deere's return as a label</label>
  <label><input type="radio" name="q0" value="c"> So a column with large numbers does not outweigh the others in every distance</label>
  <div class="fb"></div>
</div>
```

## 5.1.4 How many groups?

k-means will give you whatever k you ask for, and the tightness score (the **inertia**: each month's squared distance to its group centre, added up) always falls as k grows. At k equal to the number of months it is zero. So the score cannot choose k.

```{code-block} python
:class: pyodide
from ml_unsup import months, standardize, kmeans, inertia

z, _, _ = standardize(months())
for k in range(1, 6):
    c, l = kmeans(z, k)
    print(k, "groups: inertia", round(inertia(z, c, l), 1), " sizes", sorted([l.count(g) for g in range(k)], reverse=True))
```

The drop is 92 to 69, then to 49, 35 and 30. A textbook "elbow", a sharp bend after which extra groups barely help, would show here as a clear change of slope, and there is only a mild one around 3 to 4. With 24 months that is the honest result. Choose k by asking whether you can **name** each group and whether it holds up: at 5 groups three of them have three or four months, which is too few to say anything about.

Two more cautions. The result depends on where k-means starts: shuffle the order of the months and the tightness moves (about 48 to 49) and a month or two changes group. And the groups describe these 24 months. They are not a forecast of the 25th.

Now check the groups against something the model never saw. Deere's average return in each group:

```{code-block} python
:class: pyodide
from ml_unsup import months, standardize, kmeans

X = months()
de = months(("DE",))
z, _, _ = standardize(X)
_, labels = kmeans(z, 3)
for g in range(3):
    mine = [i for i in range(24) if labels[i] == g]
    print("group", g + 1, ": Deere averaged", round(sum(de[i][0] for i in mine) / len(mine), 1), "% over", len(mine), "months")
```

Deere averaged about +1.8, +2.7 and -7.7 across the three groups, though its return was never given to the model. That is the use of clustering at the firm: a **regime** label ("sell-off month") you can attach to each month and then study. It is also why the next section asks how to describe these months with fewer numbers.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. Squared distances only shrink as groups are added, so a lower score alone always points to more groups. You choose k by what the groups mean."
     data-no="Look at the five numbers: the tightness falls every time k goes up, so it cannot also tell you when to stop.">
  <p class="q">The inertia is lower at k = 5 than at k = 3. What does that tell you?</p>
  <label><input type="radio" name="q1" value="a"> Five groups are the right number</label>
  <label><input type="radio" name="q1" value="b"> Nothing by itself: it falls whenever k grows, so k has to be judged another way</label>
  <label><input type="radio" name="q1" value="c"> The model is overfitting and must be stopped</label>
  <div class="fb"></div>
</div>
```

## 5.1.5 Exercise

Open the Colab notebook and run section 1.

1. Cluster the months using only market and momentum. Do the same five sell-off months stay together? Which month moves?
2. Add Deere and Caterpillar as two more columns (`months(NAMES)`) and cluster again at k = 3. Does the sell-off group grow or shrink, and why would it?
3. Run k = 3 from three different row orders (the notebook shows how). Which months change group? What would you tell a client about those months?

## Further reading

- Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani, [*An Introduction to Statistical Learning*](https://www.statlearning.com/), chapter 12 (2021) — clustering and principal components, free to read.
- scikit-learn, [*Clustering*](https://scikit-learn.org/stable/modules/clustering.html) — the methods beyond k-means, and when each fits.
