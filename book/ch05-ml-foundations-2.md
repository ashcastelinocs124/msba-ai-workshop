# 5. ML Foundations II

```{raw} html
<p class="wk-lede">Find structure when no one has given you the answer. Three parts, taught in the same session: grouping similar months with clustering, describing a wide table with fewer numbers, and flagging the months that do not look like the rest.</p>
```

```{raw} html
:file: widgets/goal-map.html
```

Chapter 4 was supervised learning: every month came with a label (Deere's return) and the model learned to predict it. Here there is **no label**. The model gets the table and is asked what it sees. That makes the results harder to judge, because there is no right answer to score against, and the sections come back to that point each time.

- **[5.1 Clustering](ch05-clustering.md).** Sort the 24 months into groups that look alike, with k-means, and decide how many groups are worth having.
- **[5.2 Dimensionality Reduction](ch05-dimensionality-reduction.md).** Replace six numbers per month with two or three that keep most of the variation, with principal components.
- **[5.3 Anomaly Detection](ch05-anomaly-detection.md).** Score how unusual each month is, flag the top few, and see why the list depends on what you measure.

All three use the firm's illustrative monthly returns (made up, not market data) and need no API key. One Colab notebook covers the whole chapter, and it also shows the same three methods in scikit-learn.

(ch05-lecture)=
## Watch the lecture

The session 5 slides cover all three parts. The recording will be added here after the session; watch it alongside 5.1 to 5.3.

```{raw} html
<p><a href="https://github.com/ashcastelinocs124/Workshop-Slides/blob/main/AI/education/quantitative-analyst-course/workshop-5-ml-foundations-2.pdf">Session 5 slides (PDF, 81 pages)</a></p>
```

## Learning from rewards

The third kind of learning from section 4.1 is **reinforcement learning**: no table of answers and no table of unlabeled data, but an agent that acts, gets a reward, and adjusts. It is not part of the three sections above. The simulator in [chapter 0's section on post-training](ch00-post-training.md) lets you run one, and chapter 6 returns to how stronger models are trained.
