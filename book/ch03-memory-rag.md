# 3. Memory Retrieval and RAG

```{raw} html
<p class="wk-lede">Build cited retrieval over a small knowledge base.</p>
```

```{raw} html
:file: widgets/goal-map.html
```

```{admonition} Coming soon
:class: tip
This chapter is being written. Chapter 1 shows the format every chapter will follow: objectives, concepts, runnable cells, an interactive explainer, a checkpoint quiz, and a Colab exercise.
```

## Preview: trade pre-clearance

This example moved here from chapter 1 because its lesson is retrieval: the agent's answer depends on finding the right clause in the handbook and citing it. The loop is the one from chapter 1, unchanged.

The scenario. Everyone at Champaign Capital must ask compliance before trading a stock in a sector the firm covers. Elena Ruiz's team gets about thirty requests a week by email. Each one means opening the request, checking the restricted list, checking when the firm last published on that name, checking how long the position has been held, and writing back a decision with the policy clause that supports it. The rules fit on one page. Applying them the same way at 4:55 on a Friday is the hard part.

The agent gets two read-only tools, `get_trade_request` and `search_docs`, and no `clear_trade` tool. It recommends; a compliance officer approves.

| Request | Employee | What is different | Expected recommendation |
|---|---|---|---|
| 7101 | Priya Natarajan, buy 50 DE | firm last published on Deere 41 days ago | Approve |
| 7102 | Marcus Bell, sell 200 CAT | position held 12 days | Decline, 30-day minimum holding period |
| 7103 | Jordan Lee, buy 30 NVDA | NVIDIA is on the restricted list | Decline |
| 7104 | Tom Okafor, sell 80 DE | firm published on Deere 6 days ago | Hold until the 14-day blackout ends |

```{code-block} python
:class: pyodide
from agent import agent

answer, log = agent("Can compliance clear trade request #7104?")
print()
print(answer)
```

Every recommendation ends with a `[source: …]` tag naming the handbook chunk it relied on. This chapter is about making that tag reliable: how the chunks are built, how the search finds the right one, and what to do when it does not.

```{raw} html
<div class="wk-lcp" data-spot="ch03-retrieval" data-label="Chapter 3 · after the pre-clearance preview"></div>
```
