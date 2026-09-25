# 0B How a Model Is Trained

```{raw} html
<p class="wk-lede">A transformer starts out knowing nothing. Three stages of training turn it into an assistant that follows instructions and calls tools, and people learn a profession in the same three stages. This page is pre-reading, with no session of its own.</p>
```

```{raw} html
:file: widgets/goal-map.html
```

```{admonition} Learning objectives
:class: note
- Describe one training step: predict, measure the error, go back through the layers, and let the optimizer adjust the weights.
- Name the three stages of training (pre-training, mid-training and post-training) and what each one adds.
- Explain reinforcement learning in one sentence, and why it can teach a model to sound sure rather than be right.
```

## 0B.1 One training step

Every stage of training repeats the same small loop, billions of times. The model reads some text and **predicts** the next token. Its guess is **compared** with the token that really came next, which gives a number for how wrong it was, the **error** (also called the loss). Then the model **goes back** through its layers to work out how much each weight contributed to that error; this step is called **backpropagation**. Finally the **optimizer** turns every weight a little in the direction that would have made the error smaller. Then the next piece of text.

Run the loop yourself. Each step makes "grew" a little more likely after "Deere's revenue", and the error curve falls. Then try a larger learning rate, the size of each turn:

```{raw} html
:file: widgets/ch00-optimizer.html
```

Nothing in the loop checks whether a sentence is true. The model is nudged towards whatever text it is shown, which is why what it reads in each stage matters so much.

## 0B.2 Pre-training, mid-training and post-training

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

## 0B.3 Reinforcement learning

Post-training has two parts. First the model studies thousands of example conversations written by people, and learns to answer the way they do. Then comes **reinforcement learning**: the model writes several answers to the same request, each answer is scored, and the weights are nudged so that high-scoring answers become more likely. It learns from its own attempts, the way an analyst improves from a reviewer's marks rather than from reading more.

The score comes from one of two places:

- **People's preferences.** Reviewers compare two answers and pick the better one, and a second model learns to predict their choice. This is often called RLHF, reinforcement learning from human feedback. It is what makes a model polite, clear and helpful.
- **A check that can be run.** For a maths problem the final number is right or wrong; for code the tests pass or fail. Rewarding correct results over many attempts is how "reasoning" models learned to work through a problem step by step before answering.

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

- [*Post-Training and RLHF Overview*](https://www.youtube.com/watch?v=o6l6tJQgUg4) (46 min) — what post-training is and why every assistant goes through it (section 0B.2).
- [*Preference Data: The Most Opaque Part of Post-Training*](https://www.youtube.com/watch?v=Y2tv5vuaxFs) (36 min) — where the reviewers' choices in 0B.3 come from, and why labs keep them secret.
- [*Over-Optimization and RLHF's Bad Reputation*](https://www.youtube.com/watch?v=y04JhXpiI4s) (24 min) — what happens when a model chases the reward too hard: the "sounds sure" problem from 0B.3.
- [*The Rise of Reasoning Models*](https://www.youtube.com/watch?v=o4AB5xHIDdM) (45 min) — reinforcement learning on checkable answers, the second source of scores in 0B.3.
- [*How Language Models Use Tools and the Path to Agents*](https://www.youtube.com/watch?v=GMry2DzC304) (38 min) — how post-training teaches a model to call tools, the bridge to chapter 1.

