# 6.1 What Self-Learning Means

```{raw} html
<p class="wk-lede">An agent learns when it changes something about itself because of feedback, and keeps the change. This page says what counts, and the four places the change can live. The session 6 slides and lecture are on <a href="ch06-self-learning-agents.html#ch06-lecture">the chapter 6 page</a>.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch06-self-learning-agents.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Say what makes an agent self-improving, and what looks like learning but is not.
- Name the four places an agent can change, from a note in its prompt to new model weights, and what each costs to undo.
- Say why this chapter keeps lessons as text first.
```

## 6.1.1 The same mistake twice

A company's **fiscal year** is the twelve months its annual report (the **10-K**) covers. It often isn't January to December. Deere's ends in early November, Apple's in late September and NVIDIA's in late January. The firm reports the fiscal-year figure from the 10-K. The research agent doesn't know that. Asked for annual revenue, it adds up four quarterly reports for calendar 2025, which is a different twelve months and a different number.

Run a week of memos with chapter 1's agent: it acts, hands over the memo, and stops.

```{code-block} python
:class: pyodide
from learning import run_week

run_week(learn=False)
```

Three of four memos are sent back, and Priya writes the same correction three times. Caterpillar's memo is right only because its fiscal year is the calendar year. Nothing the agent did made it right.

This isn't a memory problem of the chapter 3 kind. The agent remembers clients and figures. What it lacks is any memory of **its own mistakes**. Nothing in its loop changes because the work went badly.

## 6.1.2 Self-improving agent

A **self-improving agent** uses feedback on its own work to change something it will use next time: its notes, its tools, its code, or its weights. Without that, every correction costs a person the same time again. With it, the tenth memo needs fewer fixes than the first.

A student who keeps an error log works the same way. After each practice exam they write down every mistake and the fix, and they reread the log before the next exam.

| In the example | For the agent |
|---|---|
| The practice exam | the task: a revenue memo |
| The graded answers | feedback: Priya's correction, or an automatic check |
| The error log | what is saved: a lesson in a file |
| A higher score next time | fewer memos sent back |

Two parts have to be there: feedback on **its own** work, and a change that **lasts** to the next task. Some things look like learning but miss one of them:

- **A newer model.** The agent is better, but someone else changed it, and not because of its own mistakes.
- **More documents on the desk.** The input changed. The agent didn't.
- **Draft, critique, rewrite.** Self-critique improves one memo, then the next memo starts from scratch. Researchers call this **self-refine**. It is useful, but it doesn't last.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. Only the rules file carries feedback forward. Self-critique improves one memo and forgets; a new model or more documents changes the inputs, not what the agent learned."
     data-no="Ask of each one: is it feedback on the agent's own work, and does the change last to the next memo?">
  <p class="q">Which of these four research agents is self-improving?</p>
  <label><input type="radio" name="q0" value="a"> It switches to a newer, smarter model every quarter</label>
  <label><input type="radio" name="q0" value="b"> It logs each of Priya's corrections in a rules file that it loads before every new memo</label>
  <label><input type="radio" name="q0" value="c"> It retrieves three times as many documents before writing each memo</label>
  <label><input type="radio" name="q0" value="d"> It drafts a memo, critiques it, rewrites it and sends it; the next memo starts from scratch</label>
  <div class="fb"></div>
</div>
```

## 6.1.3 Four places an agent can change

The change can live in four places, from cheap to expensive:

1. **Context.** The prompt, its memory, a playbook of rules. A lesson is a line of text. It takes minutes, and you undo it by deleting the line.
2. **Tools and skills.** A new tool, or a saved procedure it can reuse. Hours of work, and reusable.
3. **Architecture.** The agent's own code and workflow. Days of work, and safe only with tests.
4. **Model weights.** The parameters, retrained on rewards. Weeks of work, costly, and hard to undo.

A chef whose dish is sent back has the same four options: tape a note to the station, buy a new knife or write a recipe card, reorganize the kitchen, or practise for months until the instinct changes. Click through the layers:

```{raw} html
:file: widgets/ch06-four-layers.html
```

This chapter works mostly in the first layer, for three reasons. The firm reaches its model through an API, so it can't change the weights at all. A lesson in text is cheap, and anyone can read it and check it. A wrong lesson is one deleted line, not a retraining run. Section 6.4.2 comes back to the other layers.

## 6.1.4 Three years of it

In about three years, research agents went from remembering their mistakes to rewriting their own code. The dates are when each paper or announcement first appeared:

| When | System | What it changes | In this chapter |
|---|---|---|---|
| Mar 2023 | Reflexion | writes notes on its mistakes | §6.3.1 |
| May 2023 | Voyager | saves working skills as code | §6.3.2 |
| Apr 2025 | SICA | edits its own code | §6.4.2 |
| May 2025 | Darwin Gödel Machine | evolves a population of agents' code | §6.4.2 |
| May 2025 | AlphaEvolve | evolves algorithms | §6.4.2 |
| Jul 2025 | GEPA | evolves its prompts | §6.4.2 |
| Oct 2025 | ACE | evolves a playbook | §6.3.3 |
| Sep 2026 | RRSI | evolves its harness, with limits | §6.2.5 |

The same idea runs through all of them: **feedback on the agent's own work becomes a change it keeps**. They differ in which of the four layers they change.

## 6.1.5 Exercise

No notebook for this one.

1. Put each change in one of the four layers: a "check the units" line added to the system prompt; a new tool that pulls the 10-K page; the agent rewriting its loop to run a second check; fine-tuning on last year's corrected memos.
2. For each change, say what it would cost to undo if the lesson turned out to be wrong.
3. Name one thing at your own job (or in your studies) that you learned once and now never get wrong. Which layer did it live in?

## Further reading

- Huan-ang Gao et al., [*A Survey of Self-Evolving Agents*](https://arxiv.org/abs/2507.21046) (2025, updated 2026) — the four layers this page uses, and the systems in the table.
- Aman Madaan et al., [*Self-Refine: Iterative Refinement with Self-Feedback*](https://arxiv.org/abs/2303.17651) (2023) — draft, critique, rewrite: better answers that don't carry over.
- Noah Shinn et al., [*Reflexion: Language Agents with Verbal Reinforcement Learning*](https://arxiv.org/abs/2303.11366) (2023) — the first agent in the table, and the subject of §6.3.1.
