# 0C Pre-, Mid- and Post-Training

```{raw} html
<p class="wk-lede">The training loop from page 0B runs in three stages, each on different material: a vast read of everything, a focused course, and then learning the job from examples and scored attempts. People learn a profession the same way. The last stage, reinforcement learning, is where a model learns to be helpful, and also where it can learn to sound sure without being right. This page is pre-reading, with no session of its own.</p>
```

```{raw} html
:file: widgets/goal-map.html
```

```{admonition} Learning objectives
:class: note
- Name the three stages of training (pre-training, mid-training and post-training) and what each one adds.
- Explain reinforcement learning in one sentence, and why it can teach a model to sound sure rather than be right.
```

## 0C.1 Pre-training, mid-training and post-training

Training happens in three stages. Each one starts from the model the stage before produced.

| Stage | What it reads | What it learns |
|---|---|---|
| **Pre-training** | Trillions of tokens of public text: web pages, books, code, filings | To predict the next token in any kind of text. Almost all of its knowledge comes from here. After this it can continue a document, but it does not yet act like an assistant. |
| **Mid-training** | A smaller, carefully chosen set: high-quality writing, maths, code, long documents, sometimes a specialist field | To be better at what its makers care most about, and to read much longer inputs. It is still next-token prediction, only on better text. |
| **Post-training** | Examples of requests with good answers, then scores for the answers it writes itself | To act like an assistant: follow instructions, answer in a useful shape, reason step by step, call tools, and decline some requests. |

People learn a profession in the same three stages. Step through them for the model, a person, and Marcus Bell, the associate on Priya's industrials team. In the third stage, you are the reviewer:

```{raw} html
:file: widgets/ch00-training-stages.html
```

## 0C.2 Reinforcement learning

Post-training has two parts. First the model studies thousands of example conversations written by people, and learns to answer the way they do. Then comes **reinforcement learning**: the model writes several answers to the same request, each answer is scored, and the weights are nudged so that high-scoring answers become more likely. It learns from its own attempts, the way an analyst improves from a reviewer's marks rather than from reading more.

The score comes from one of two places:

- **People's preferences.** Reviewers compare two answers and pick the better one, and a second model learns to predict their choice. This is often called RLHF, reinforcement learning from human feedback. It is what makes a model polite, clear and helpful.
- **A check that can be run.** For a maths problem the final number is right or wrong; for code the tests pass or fail. Rewarding correct results over many attempts is how "reasoning" models learned to work through a problem step by step before answering.

Run it. Pick who scores the answers, then train: each round the model writes four answers, each is scored, and the styles that beat the round's average become more likely. Try all three scorers, starting over each time:

```{raw} html
:file: widgets/ch00-rl.html
```

Reinforcement learning teaches the model what gets rewarded, not what is true. Reviewers tend to prefer answers that are confident and agreeable, so a model can learn to sound sure of itself even when it is not (chapter 0's section 0.6).

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. Reinforcement learning makes whatever scores well more likely. If reviewers score confident, agreeable answers higher, the model learns to sound confident, whether or not it is right."
     data-no="Reinforcement learning rewards whatever gets a high score. What do reviewers tend to score highly?">
  <p class="q">After post-training, a model states a wrong revenue figure in a calm, certain tone. Which stage best explains the tone?</p>
  <label><input type="radio" name="inside-q2" value="a"> Pre-training, because the web is full of wrong figures</label>
  <label><input type="radio" name="inside-q2" value="b"> Mid-training, because it read too much maths</label>
  <label><input type="radio" name="inside-q2" value="c"> Reinforcement learning, because reviewers tend to reward confident, agreeable answers</label>
  <div class="fb"></div>
</div>
```

## Further reading

- Hugging Face, [*Illustrating Reinforcement Learning from Human Feedback*](https://huggingface.co/blog/rlhf) — how post-training turns people's preferences into a score the model learns from.

**Watch: Nathan Lambert's post-training course.** Lambert wrote *[The RLHF Book](https://rlhfbook.com)* and records a free lecture series alongside it. These five follow this page:

- [*Post-Training and RLHF Overview*](https://www.youtube.com/watch?v=o6l6tJQgUg4) (46 min) — what post-training is and why every assistant goes through it (section 0C.1).
- [*Preference Data: The Most Opaque Part of Post-Training*](https://www.youtube.com/watch?v=Y2tv5vuaxFs) (36 min) — where the reviewers' choices in 0C.2 come from, and why labs keep them secret.
- [*Over-Optimization and RLHF's Bad Reputation*](https://www.youtube.com/watch?v=y04JhXpiI4s) (24 min) — what happens when a model chases the reward too hard: the "sounds sure" problem from 0C.2.
- [*The Rise of Reasoning Models*](https://www.youtube.com/watch?v=o4AB5xHIDdM) (45 min) — reinforcement learning on checkable answers, the second source of scores in 0C.2.
- [*How Language Models Use Tools and the Path to Agents*](https://www.youtube.com/watch?v=GMry2DzC304) (38 min) — how post-training teaches a model to call tools, the bridge to chapter 1.
