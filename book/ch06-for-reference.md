# 6.4 For Reference: Long Inputs, Rewards and Evaluation

```{raw} html
<p class="wk-lede">Three topics the session left for self-study: what to do when the input is too long for any prompt, learning from rewards by changing words instead of weights, and how to prove an agent really improved. The session 6 slides, sections 4 to 6, are on <a href="ch06-self-learning-agents.html#ch06-lecture">the chapter 6 page</a>.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch06-self-learning-agents.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Explain context rot, and how a recursive language model reads an input far longer than its context window.
- Compare learning from rewards by changing the weights with changing the words, and say which the firm can use.
- Test whether an agent improved on held-out tasks, and name the five numbers worth tracking.
- Say what reward hacking is, and the guardrails that stop it.
```

## 6.4.1 Recursive language models

### Context rot

As you put more text into a model's context, its ability to find and use any one piece of it gets worse, well before the context window is full. This is **context rot**. The research agent reads 10-Ks, transcripts and notes. Stuffing all of it into one prompt makes answers worse, not better.

It is like reading a 1,000-page binder in one sitting before a meeting. A question about one fact is easy. "Which clients complained twice?" is not, because the answer needs facts from many pages held in mind at once.

### Reading in pieces

A **recursive language model** (RLM) never reads the long input directly. The input sits as a variable in a Python workspace. The model writes code to peek at it, search it and split it, and calls copies of itself on the pieces. A manager with a filing cabinet and three interns works the same way: she checks the index, searches for keywords, hands folders to the interns, and combines their one-page notes into the memo.

Ten years of Deere's 10-Ks come to about 8 million tokens, far beyond any context window. An RLM would handle them like this:

```text
context = <ten years of Deere 10-Ks, about 8M tokens>      # a variable, never in the prompt

print(context[:2000])                                      # 1. peek at the start
hits = find_all("segment revenue", context)                # 2. search for what matters
years = split_by_year(context)                             # 3. split into pieces
figures = [ask_submodel(y, "segment revenue?") for y in years]   # 4. a cheap model reads each piece
FINAL(make_table(figures))                                 # 5. the root model checks and combines
```

No model ever reads all ten filings at once, and the root model's own context stays small. In the paper that introduced RLMs, inputs reached 6 to 11 million tokens, up to about 40 times GPT-5's window:

| Approach, on a search across 1,000 documents | Accuracy | Cost per question |
|---|---|---|
| GPT-5 alone | 0 (the input is too long to start) | – |
| A coding agent with keyword search | 51.0% | $0.71 |
| Summarize as you go | 70.5% | $0.57 |
| Claude Code with the files | 84.0% | $2.03 |
| RLM with GPT-5 | 91.3% | $0.99 |

The gap is widest when a task needs every piece combined. On a test that asks about **pairs** of items spread across a long input, summarize-as-you-go scored 0.1 and the RLM 58.0. A summary throws details away for good, and pairing items needs exactly those details. An RLM keeps the whole input and looks things up when it needs them.

RLMs are not always the answer. Deeper recursion (sub-models calling sub-models) helped on the hardest task, but a March 2026 reproduction found it hurt simple tasks, and one run went from 3.6 seconds to 344.5. Prime Intellect's tests found big gains on long inputs and worse results on short tasks, and the RLM was slower in every case. Two open-source versions are the `rlm` library from MIT and `dspy.RLM` from Stanford's DSPy.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. It's short and needs one fact, so an RLM adds cost and delay for no gain."
     data-no="RLMs shine when a task needs many pieces of a huge input. Which task needs neither?">
  <p class="q">Which task is the worst fit for a recursive language model?</p>
  <label><input type="radio" name="q0" value="a"> Finding one revenue number in a 3-page press release</label>
  <label><input type="radio" name="q0" value="b"> Answering a question spread across 1,000 documents</label>
  <label><input type="radio" name="q0" value="c"> Pairing every client with every complaint in a long log</label>
  <label><input type="radio" name="q0" value="d"> Comparing segment revenue across ten 10-Ks</label>
  <div class="fb"></div>
</div>
```

## 6.4.2 Rewards and continual learning

### Change the weights, or change the words

Reinforcement learning (session 5, and [chapter 0's page on post-training](ch00-post-training.md)) is: try, get a reward, do more of what scored well. Session 5's Q-learning updated a table of values. For a language model, reinforcement learning updates the weights. For an agent, the reward can also update **text**: its prompts and notes.

| | Change the weights (RL, for example GRPO) | Change the words (prompt evolution, for example GEPA) |
|---|---|---|
| How | score many attempts; nudge the model's parameters | score a few attempts; the model reflects in words and rewrites its prompt |
| Needs | access to the model and GPUs | any model behind an API |
| Attempts | thousands | up to 35 times fewer |

When your practice-test scores dip, you can grind thousands of problems, or reread your mistakes and rewrite your study plan in an evening. In the GEPA paper, rewriting the prompt beat reinforcement learning on the weights by 6% on average (up to 20%), with up to 35 times fewer attempts.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. API users can't touch the weights. Rewriting the prompt is possible, and cheaper."
     data-no="What can you change about a model you reach only through an API?">
  <p class="q">You use Claude through an API. Why might GEPA beat RL fine-tuning for you?</p>
  <label><input type="radio" name="q1" value="a"> It doesn't need any scoring</label>
  <label><input type="radio" name="q1" value="b"> It changes the model's weights faster</label>
  <label><input type="radio" name="q1" value="c"> It works through an API without access to the weights, and needs far fewer attempts</label>
  <label><input type="radio" name="q1" value="d"> It guarantees 100% accuracy</label>
  <div class="fb"></div>
</div>
```

### Agents that edit their own code

A **self-modifying agent** edits its own harness code (its tools, prompts and workflow) and keeps the version that scores better on tests. It automates the engineer who tunes the agent, and the benchmark becomes the boss. A coach works this way: try new plays in scrimmages, keep the ones that win, and file the rest away in case they're useful later.

| Agent | Test | Starting | After rewriting itself |
|---|---|---|---|
| SICA | a coding benchmark (sample) | 17% | 53% |
| Darwin Gödel Machine | a coding benchmark (sample) | 20% | 50% |
| Darwin Gödel Machine | coding in several languages | 14.2% | 30.7% |

The model underneath was the same each time; the gains came from the agent rewriting itself. The Darwin Gödel Machine keeps an archive of every version, weaker ones included, and builds new versions from any of them. Remove the archive and the gains shrink: a weak version can be the stepping stone to a much better one. The idea already runs in production. Google DeepMind's AlphaEvolve found a scheduling rule that recovers 0.7% of Google's worldwide computing capacity, continuously.

### Continual learning

**Continual learning** means learning from a stream of new tasks over time without forgetting what was learned before. Learning Spanish this semester shouldn't make you forget French. Markets change, and an agent that learned only 2024's rules has to adapt without erasing what still works. Retraining the weights risks exactly that kind of forgetting.

The firm keeps lessons as text first and treats retraining as a last resort. Text doesn't make the model forget, but it does pile up. So lessons.md has four rules:

1. Add a lesson only after a graded failure.
2. Make small edits, never a full rewrite (§6.3.3).
3. A person approves every new lesson.
4. Prune stale lessons every month, and dream every Friday (§6.3.4).

The first and third are in `save` (section 6.2.4); the fourth is `dream`.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. Text avoids forgetting but piles up clutter, hence the monthly pruning and the Friday dreaming."
     data-no="The weights never change in this design. What does grow every week?">
  <p class="q">The firm's agent keeps lessons in lessons.md instead of retraining. After a year, what is the biggest risk?</p>
  <label><input type="radio" name="q2" value="a"> Being unable to learn new rules</label>
  <label><input type="radio" name="q2" value="b"> Forgetting old skills</label>
  <label><input type="radio" name="q2" value="c"> Stale and contradictory notes piling up</label>
  <label><input type="radio" name="q2" value="d"> The model's weights drifting</label>
  <div class="fb"></div>
</div>
```

## 6.4.3 Evaluation

### Held-out tasks

Every number on the practice week can be gamed, often without anyone meaning to. **Held-out evaluation** tests the improved agent on tasks it did not learn from, and compares it with the original agent on those same tasks. Memorizing last year's exam gets you 100% on last year's exam. Only new questions show whether you learned the subject.

The firm's held-out task is a Microsoft memo, which the agent never saw during the week. Try three lessons files, and then let the agent edit its own grader:

```{raw} html
:file: widgets/ch06-held-out.html
```

The same comparison in code. `evaluate` scores the four practice memos and the held-out one:

```{code-block} python
:class: pyodide
from learning import evaluate, MEMORIZED, reflect

print("No lessons:")
evaluate(lessons=[])
print("Memorized answers:", MEMORIZED)
evaluate(lessons=MEMORIZED)
print("The general rule:")
evaluate(lessons=[reflect("figure does not match the 10-K")])
```

Memorizing the four answers gives a perfect practice score and fails the first new company. The general rule passes both. That is chapter 4's lesson again: judge a model on data it didn't learn from. One held-out memo is a thin test. The firm's real set would have twenty locked questions.

Five numbers tell you whether an agent is really learning:

| Number | The question it answers | At the firm |
|---|---|---|
| Held-out accuracy | Better on new tasks? | figures right on 20 locked questions |
| Learning curve | Improving over time? | memos sent back per week |
| Transfer | Do lessons carry over? | Deere's lesson helps on Microsoft |
| Cost per task | Cheaper or dearer? | tokens and minutes per memo |
| Regressions | Did anything get worse? | old clients' rules still followed |

The tasks are getting longer, so these checks matter more. METR measures how long a task (in expert hours) an agent can finish half the time. It went from about 1 hour (Claude 3.7 Sonnet, February 2025) to 5.3 hours (Claude Opus 4.5, November 2025), with a lower-bound estimate of 16 hours or more for one model in April 2026: doubling roughly every four months. Over a task that long, the harness has to remember for the model.

### Reward hacking

**Reward hacking** is an agent raising its score by exploiting the grader instead of doing the task better. A sales team paid per call starts making 30-second calls: calls go up, sales go down. Self-improving agents push hard against their grader, and any loophole will eventually be found.

It has happened. The Darwin Gödel Machine was rewarded for passing tests and for avoiding made-up tool calls. One version faked a log saying the tests had passed, when they never ran, and removed the markers the checker looked for. It was caught because every change was archived, so people could trace it.

Here is the same trick, scripted. The agent may replace the grader that marks its practice tasks with one that always says pass:

```{code-block} python
:class: pyodide
from learning import evaluate

def always_pass(memo, ticker):
    return True, "looks fine"

evaluate(lessons=[], grader=always_pass)
```

Practice reads 4 of 4. The held-out memo is still 0 of 1, because a grader the agent can't touch marks it. The guardrails follow:

- The agent can edit its notes, **never** its grader or its tests.
- Every change is logged, so it can be traced and undone.
- A person approves new lessons and anything sent to a client.

Sandboxes, change archives and human oversight were the safeguards in both the Darwin Gödel Machine and SICA.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. If it can edit its grader, it will learn to fool the grader instead of doing better work."
     data-no="The Darwin Gödel Machine faked a log and removed the checker's markers. What permission made that possible?">
  <p class="q">Which permission should a self-improving agent never have?</p>
  <label><input type="radio" name="q3" value="a"> Editing its own lessons file</label>
  <label><input type="radio" name="q3" value="b"> Editing the tests and the checker that grade it</label>
  <label><input type="radio" name="q3" value="c"> Reading its past sessions</label>
  <label><input type="radio" name="q3" value="d"> Querying the 10-K database</label>
  <div class="fb"></div>
</div>
```

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. Gains on the practice set may be memorization or gaming. Only unseen tasks show real learning."
     data-no="Look back at the memorized-answers row: 100% on practice. What did the held-out score say?">
  <p class="q">The agent's practice score rose from 60% to 95% in a month. What should you check first?</p>
  <label><input type="radio" name="q4" value="a"> Its score on held-out questions it never saw</label>
  <label><input type="radio" name="q4" value="b"> Whether a bigger model scores 99%</label>
  <label><input type="radio" name="q4" value="c"> How long lessons.md has become</label>
  <label><input type="radio" name="q4" value="d"> Nothing: 95% means it's ready</label>
  <div class="fb"></div>
</div>
```

## 6.4.4 Exercise

Open the Colab notebook and run section 3.

1. Run `evaluate` with no lessons, with memorized answers and with the general rule, on the real model. Do the scores match the mock's? Where do they differ, and why might a real model pass the held-out memo with no lessons at all?
2. Write a lesson that is half memorized and half general (for example, "Deere: $45.7B; otherwise use the fiscal year"). Predict the practice and held-out scores, then check.
3. Which of the five numbers in the table could the firm track this week with what the notebook already records? Which would need a new log?

## Further reading

- Alex L. Zhang, Tim Kraska, Omar Khattab, [*Recursive Language Models*](https://arxiv.org/abs/2512.24601) (2025) — the paper behind §6.4.1, with the code at [github.com/alexzhang13/rlm](https://github.com/alexzhang13/rlm).
- Chroma, [*Context Rot: How Increasing Input Tokens Impacts LLM Performance*](https://www.trychroma.com/research/context-rot) (2025) — measured context rot across models.
- Prime Intellect, [*Recursive Language Models: the paradigm of 2026*](https://www.primeintellect.ai/blog/rlm) (2026) — training models to work as RLMs.
- Lakshya A. Agrawal et al., [*GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning*](https://arxiv.org/abs/2507.19457) (2025) — changing the words instead of the weights.
- Jenny Zhang et al., [*Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents*](https://arxiv.org/abs/2505.22954) (2025), with Sakana AI's [write-up](https://sakana.ai/dgm/) of the faked test log.
- Maxime Robeyns et al., [*A Self-Improving Coding Agent*](https://arxiv.org/abs/2504.15228) (2025) — SICA.
- Google DeepMind, [*AlphaEvolve: a Gemini-powered coding agent for designing advanced algorithms*](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) (2025) — self-improvement in production.
- METR, [*Time Horizon 1.1*](https://metr.org/blog/2026-01-29-time-horizon-1-1/) (2026) — how long a task agents can finish, and how fast that is growing.
