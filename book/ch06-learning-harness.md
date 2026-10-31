# 6.2 The Learning Harness

```{raw} html
<p class="wk-lede">The model is the engine; the harness is the car you build around it: the loop, the tools, the checks, and the place lessons are kept. This page adds three steps to chapter 1's agent (grade, reflect, save), so a correction Priya makes on Monday is still there on Tuesday. The session 6 slides and lecture are on <a href="ch06-self-learning-agents.html#ch06-lecture">the chapter 6 page</a>.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch06-self-learning-agents.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Say what an agent harness is, and why the same model scores differently in two harnesses.
- Name the five steps of the learning loop, and the three that make an agent learn.
- Pick a grader for a task, and say what it can and can't catch.
- Explain the three trends in harnesses: harnesses that improve themselves, models that make parts of them unnecessary, and harnesses built for one industry.
```

## 6.2.1 The agent harness

An **agent harness** is all the software around a model that turns it into an agent: the loop, the tools, the context, the memory, the permissions, and how it checks its own work. You have built most of it already:

| Harness part | Where you built it |
|---|---|
| The loop and the tools | chapter 1 |
| The context: instructions, examples, the desk | chapter 2 |
| Memory of clients and documents | chapter 3 |
| Feedback and lessons | this page |
| Permissions: what it may never do | chapter 1's read-only tools, and §6.4.3 |

Think of two equally smart analysts. One gets a checklist, the right files and a manager who reviews drafts. The other gets nothing. The first writes the better memo, and not because of raw ability. The analyst is the model; the checklist, files and review are the harness.

This matters because you can't retrain Claude or GPT. You can change the harness, and that is where most practical improvement comes from. On one coding benchmark (Terminal-Bench 2.1, rows dated April to June 2026), each lab's own harness beat a generic harness running the same model:

| Model | Generic harness | The lab's own harness |
|---|---|---|
| Claude Fable 5 | 80.4% | 83.8% (Claude Code) |
| GPT-5.5 | 78.0% | 83.1% (Codex CLI) |
| Claude Opus 4.7 | 66.1% | 68.9% (Claude Code) |
| Gemini 3.1 Pro | 65.6% | 65.8% (Gemini CLI) |

The gaps are 0 to 5 points. The harness matters, but the model matters more: a weaker model in a better harness doesn't catch up with a stronger one.

## 6.2.2 Harness engineering

The job has moved twice. From 2022 to 2024 it was **prompt engineering**: write better instructions (section 2.1). By mid-2025 it was **context engineering**: choose what the model sees on each call (section 2.2). In 2026 it is **harness engineering**: design everything around the model (instructions, tools, checks and feedback) so the agent does the job right without a person fixing each output. Each layer contains the one before. A harness still needs good prompts and good context.

House rules on a fridge grow the same way. Someone forgets to lock the door, so "Lock the door" goes on the list. The milk goes bad, so "Label your leftovers" joins it. The list grows; the roommates stay the same. Each rule is a small piece of harness engineering.

A good harness has two kinds of controls:

| | Guides, before it acts | Checks, after it acts |
|---|---|---|
| What they are | an instructions file, templates, examples, a map of the documents | tests, a second model's review, error messages that say how to fix the problem |
| At the firm | "Always use fiscal-year revenue." | "Every figure must match the 10-K." |

The checks are where self-learning starts: each failed check is feedback worth saving.

Two results show how far harness work alone can go. LangChain kept its model fixed and raised its coding agent on Terminal-Bench 2.0 from 52.8% to 66.5%. Turning up the model's reasoning effort alone reached only 53.9%. The rest came from a checklist that forced a verification pass, detection of loops where the agent repeated itself, a map of the files at the start, and warnings as time ran out. And an OpenAI team of three to seven engineers shipped about a million lines of code in five months with none written by hand: the engineers built the harness, and agents wrote the code.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. A check (a sensor) lives in the harness. Fine-tuning, waiting for a release and vendor retraining all change the model itself."
     data-no="The harness is everything around the model. Which option leaves the model's weights alone?">
  <p class="q">Which change is harness engineering rather than model training?</p>
  <label><input type="radio" name="q0" value="a"> Adding a check that rejects any memo whose figures don't match the 10-K</label>
  <label><input type="radio" name="q0" value="b"> Waiting for the next model release</label>
  <label><input type="radio" name="q0" value="c"> Asking the vendor to retrain on finance data</label>
  <label><input type="radio" name="q0" value="d"> Fine-tuning the model on 10,000 corrected memos</label>
  <div class="fb"></div>
</div>
```

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. Reasoning effort alone added 1.1 points (52.8% to 53.9%). The other 12.6 came from harness changes that check and steer the work."
     data-no="Turning up reasoning effort alone gave 53.9%. Where did the rest of the gain to 66.5% come from?">
  <p class="q">LangChain's score rose from 52.8% to 66.5% with the same model. What drove most of the gain?</p>
  <label><input type="radio" name="q1" value="a"> Harness changes, mostly verification and loop detection</label>
  <label><input type="radio" name="q1" value="b"> Luck: benchmarks are noisy</label>
  <label><input type="radio" name="q1" value="c"> Extra reasoning effort</label>
  <label><input type="radio" name="q1" value="d"> A bigger model</label>
  <div class="fb"></div>
</div>
```

## 6.2.3 The learning loop

Chapter 1's agent does two steps: it **acts** (looks things up) and hands over an **output** (the memo). Self-learning adds three steps after the task:

1. **Act.** Run the task.
2. **Output.** The memo, code or answer.
3. **Grade.** Check it: a test, a score, or a person.
4. **Reflect.** Ask what went wrong, and write it as a rule.
5. **Save.** Put the rule where the next task will read it.

The next task then starts with the lesson already in its context. Turn the learning steps on and run the week again:

```{raw} html
:file: widgets/ch06-learning-loop.html
```

Now the same steps in code. First, one memo with an empty lessons file. The agent is chapter 1's `agent()` with one extra read-only tool, `get_annual_revenue`, which can return either basis. Switch to Watch to see it at the desk:

```{code-block} python
:class: pyodide
from learning import write_memo, grade

memo = write_memo("DE", lessons=[], verbose=True)
print()
print(grade(memo, "DE"))
```

It asked for the calendar year, and the grader says what is wrong. Now the whole week with the learning steps on. `run_week` empties lessons.md first, then grades each memo, and on a failure reflects and saves:

```{code-block} python
:class: pyodide
from learning import run_week, show_lessons

run_week(learn=True)
print()
show_lessons()
```

One memo sent back instead of three. The saved lesson records its rule, the failure behind it and who approved it. That is the audit trail a reviewer needs (section 6.4.3). Here `approved_by="Priya"` is passed in for her; at the firm she would click Approve.

On Friday the agent writes a memo it has never written before, on Microsoft. Here is what it reads first, and what it writes. lessons.md lives in this page's memory, so run the cell above first; reloading the page empties it.

```{code-block} python
:class: pyodide
from learning import lessons_block, write_memo

print(lessons_block())
print()
memo = write_memo("MSFT", verbose=True)
```

The lesson is plain text in the system prompt, the same desk as chapter 2. The mock model reads "fiscal year" there and asks for the fiscal figure, and the memo cites the 10-K page. Microsoft wasn't in the week at all: the rule carried over to a company the agent never wrote about. Section 6.4.3 calls that **transfer**.

```{admonition} The mock is scripted
:class: tip
The mock model asks for the calendar year whenever no lesson says "fiscal year", every time. A real model might choose the fiscal year on its own, or might not. Section 6.2.6 runs the same week against one.
```

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. It graded and reflected, but never saved the lesson where the next task reads it, so nothing carried over."
     data-no="It graded its memo and wrote 'I used calendar-year revenue', then finished. What did the next week's task never see?">
  <p class="q">The agent noticed its mistake, yet repeated it the next week. Which step is missing?</p>
  <label><input type="radio" name="q2" value="a"> Step 4: Reflect</label>
  <label><input type="radio" name="q2" value="b"> Step 5: Save</label>
  <label><input type="radio" name="q2" value="c"> Step 1: Act</label>
  <label><input type="radio" name="q2" value="d"> Step 3: Grade</label>
  <div class="fb"></div>
</div>
```

## 6.2.4 Choosing a grader

The grader decides what the agent learns, so pick it carefully:

| Feedback source | Example at the firm | Strength | Weakness |
|---|---|---|---|
| Automatic test | figures match the 10-K | cheap, objective | only checks what you test |
| Reward or score | a client's rating from 1 to 5 | scales to many tasks | can be gamed |
| A second model as judge | another model grades the tone | flexible | shares the model's blind spots |
| A person | Priya's corrections | most trusted | slow and costly |

This chapter's grader is an automatic test, and it checks one thing. Anything else gets through:

```{code-block} python
:class: pyodide
from learning import grade

print(grade("Deere annual revenue was $45.7B. Buy it now, it can only go up.", "DE"))
```

The figure is right, so the memo passes, recommendation and all. Chapter 2's rules forbid that recommendation, and this grader never looks. Most good harnesses combine an automatic check with a person on the decisions that matter. The firm's `save` follows that rule: a lesson needs a graded failure behind it and a person's approval, and a duplicate is refused:

```{code-block} python
:class: pyodide
from learning import save, LESSONS

print(save("Always use tables."))                                       # no failure behind it
print(save("Always use tables.", failure="client asked for a table"))   # nobody approved it
print("lessons in lessons.md:", len(LESSONS))
```

Anthropic describes a harness for agents that work over many sessions, and it runs on the same pieces. A first agent writes a progress file and a feature list, every feature marked failing. Each later session reads the progress file, picks one failing feature, and tests it end to end, as a user would, before marking it passing. Then it saves its work and updates the notes for the next session. **The model forgets between sessions. The harness doesn't.** In Anthropic's own tests, giving an agent a memory file and pruning old context lifted results by 39% and cut the tokens used on a 100-turn task by 84%. Those are harness features, not a new model.

At the firm, the change from chapter 3 to now:

| The chapter 3 agent | The chapter 6 agent |
|---|---|
| loop, tools, memory of clients | the same, plus a grader: figures must match the 10-K |
| Priya corrects the memo by email | Priya's correction is captured as feedback |
| the correction is lost after the task | the lesson is saved to lessons.md |
| | lessons.md is loaded into every new memo |

## 6.2.5 Where harnesses are heading

Three trends will decide what harnesses look like next.

### Harnesses that improve themselves

A **self-improving harness** reads its own failure logs, proposes a small change to its prompts, tools or workflow code, and keeps the change only if the old tasks still pass. Think of a new hire who rewrites their own how-to guide after every mistake, but checks first that the old tasks still work. The model stays frozen. The loop is:

1. **Run** the benchmark tasks.
2. **Mine** the failure logs.
3. **Propose** one small edit to the harness.
4. **Test**: do the old tasks still pass?
5. **Keep** the edit, or revert it.

Most of the gains came from tools, middleware and memory, not from the system prompt. In one study (Self-Harness, June 2026) harnesses that rewrote themselves lifted every model tested on Terminal-Bench 2.0: GLM-5 from 46.1% to 57.0%, MiniMax M2.5 from 42.2% to 53.9%, and a small Qwen model from 18.0% to 36.7%. The smallest model gained the most. And harnesses designed this way now beat ones written by experts: one automatically improved harness reached 77.0%, ahead of OpenAI's hand-built Codex CLI harness at 71.9% on the same test.

There is a catch. Left unchecked, a self-improving harness grows. In one study (RRSI, September 2026) unchecked self-improvement bloated a harness from 1.56 million tokens per trial to 3.80 million. A version with limits on its edits stopped at 2.42 million. The unchecked version also scored higher on the tasks it evolved on (92.8 against 90.5) and lower on tasks it had never seen (88.9 against 89.2). That is chapter 4's overfitting again.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. Gains that appear only on the tasks it trained on are overfitting: the train/test gap from chapter 4."
     data-no="Overfitting means doing better on what you learned from and worse on what you didn't. Which option has that shape?">
  <p class="q">Which result shows that a self-improving harness is overfitting?</p>
  <label><input type="radio" name="q3" value="a"> It scores higher on practice tasks but lower on new tasks than a constrained version</label>
  <label><input type="radio" name="q3" value="b"> It uses fewer tokens per task</label>
  <label><input type="radio" name="q3" value="c"> It makes fewer edits each round</label>
  <label><input type="radio" name="q3" value="d"> It scores higher on both practice and new tasks</label>
  <div class="fb"></div>
</div>
```

### Models eating harnesses

Every harness part is a bet on what the model can't do yet, and the models keep winning those bets. Rich Sutton's "Bitter Lesson" makes the general point: methods that scale with computing power beat hand-built cleverness. When GPS arrived, drivers stopped planning routes with paper maps, but they still needed the car, the fuel and the road.

"Think step by step" is one scaffold the models absorbed. A Wharton study found it added 13.5 points for Gemini 2.0 Flash and 11.7 for Claude 3.5 Sonnet, models that don't reason before they answer. For reasoning models it added between −3.3 and +3.1 points, and made answers 20% to 80% slower. Anthropic did the same with its own harness. Sonnet 4.5 rushed to finish as its context filled up, so the harness added context resets. Opus 4.5 largely stopped doing it, and Anthropic removed the resets. The minimal end is mini-SWE-agent: about 100 lines of Python with one tool, a command line, scoring over 74% on a standard coding benchmark with recent models.

What gets absorbed and what survives:

| Getting absorbed | Still needed |
|---|---|
| "think step by step" prompts | access to data and tools (EDGAR, FactSet) |
| hand-written planning steps | tests and graders that check the work |
| context resets and retry tricks | memory across sessions |
| elaborate tool wrappers | permissions, audit logs, a person's approval |

Build the harness around what the model can't reach, and what it can't be trusted to check. Re-test each part when a new model ships, and delete what it no longer needs.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. It made up for a weakness that reasoning models no longer have. Data access, logs and a person's approval cover things the model can't do or can't be trusted with."
     data-no="Look at the two columns above. Which part is scaffolding for thinking rather than plumbing for acting?">
  <p class="q">A new reasoning model ships. Which harness part should you test removing first?</p>
  <label><input type="radio" name="q4" value="a"> Priya's approval before client emails</label>
  <label><input type="radio" name="q4" value="b"> The connector to the 10-K database</label>
  <label><input type="radio" name="q4" value="c"> The "think step by step" line in the prompt</label>
  <label><input type="radio" name="q4" value="d"> The audit log of every tool call</label>
  <div class="fb"></div>
</div>
```

### Harnesses built for one industry

A **domain-specific harness** is the general model plus one industry's data feeds, ready-made skills, review steps and compliance rules. A bank gives a new analyst a market-data login, model templates and a compliance checklist; a hospital gives the same graduate a different kit.

Firms tried the other route first. Bloomberg trained its own 50-billion-parameter finance model, BloombergGPT, in 2023. Months later the general GPT-4 beat it on four of five finance tests in one comparison (for example 76.5 against 43.4 on a financial question-answering test). Domain models were overtaken by general ones. A finance harness wraps whichever general model scores best in:

- **data connectors**: FactSet, S&P Capital IQ, PitchBook, Morningstar, LSEG, Moody's;
- **skills**: comparable-company analysis, discounted cash flow, a three-statement model;
- **workflows**: agent templates such as a pitch builder or an earnings reviewer;
- **controls**: a person's approval, permissions for each tool, an audit log.

On the Vals AI Finance Index (October 2026), which grades models in a finance harness, the top five models scored within two points of each other (66.35% to 64.53%). When models are that close, the data, skills and checks around them decide the result. In law, Harvey reports that adding a graph of case law and each firm's own documents raised pass rates by up to 30% in early tests and cut the cost of a task by up to half. Partners approve each agent step before the next one runs.

The firm's agent is heading the same way: connectors to its filings, house skills, a check that every figure matches the 10-K, lessons.md with a cleanup every Friday (section 6.3.4), and Priya's approval on every step. When a better model comes out next month, the firm swaps it in and keeps everything else.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. A custom model gets overtaken by the next general model. The data, skills and checks around it survive every upgrade."
     data-no="Bloomberg's own model was beaten months later by a general one. What part of a system survives a model upgrade?">
  <p class="q">What is the best lesson for a bank from BloombergGPT?</p>
  <label><input type="radio" name="q5" value="a"> Never use AI for finance</label>
  <label><input type="radio" name="q5" value="b"> Train an even bigger finance model</label>
  <label><input type="radio" name="q5" value="c"> Build the data, skills and checks around the model, and keep the model swappable</label>
  <label><input type="radio" name="q5" value="d"> Only use the cheapest model available</label>
  <div class="fb"></div>
</div>
```

## 6.2.6 Run it against a real model

On the campus copy, these cells send the same week to the GPT deployment on Illinois Azure through `/api/chat`. The model sees the same `get_annual_revenue` tool and the same lessons file. It also writes its own lesson in step 4, in place of the mock's template.

```{raw} html
<div class="wk-banner wk-pages-only">Model cells need the campus copy of this book: <a data-campus="/ch06-learning-harness.html#run-it-against-a-real-model" href="#">open it there</a> and sign in with your @illinois.edu account. Everything else on this page works here.</div>
```

First, one memo with an empty lessons file. Which basis does the real model choose?

```{code-block} python
:class: pyodide
from learning import write_memo, grade, azure_learning_model

memo = write_memo("DE", model=azure_learning_model, lessons=[], verbose=True)
print()
print(grade(memo, "DE"))
```

Then the week, with the learning steps on:

```{code-block} python
:class: pyodide
from learning import run_week, show_lessons, azure_learning_model

run_week(learn=True, model=azure_learning_model)
print()
show_lessons()
```

If the model picked the fiscal year on its own, nothing failed and nothing was saved. That is the first rule of the lessons file working: no lesson without a failure behind it. If it failed, read the lesson it wrote. Is it general enough to help on Apple, or does it only mention Deere?

## 6.2.7 Exercise

Open the Colab notebook and run section 1. It builds the same loop on `glm-5.3-flash` via Lumen (see [Setup](setup.md) for the key), and keeps lessons.md as a real file.

1. Run the week with learning off, then on. How many memos were sent back each time? If the model chose the fiscal year without help, change `DESK` to say "Use calendar-year figures" and run it again. What does the grader catch?
2. Read the lesson the model wrote. Rewrite it so it would also help on a company it hasn't seen, and run the held-out Microsoft memo with your version.
3. Add a second check to `grade`: the memo must cite a 10-K page. Which memos fail now, and what lesson does the model write?

## Further reading

- Anthropic, [*Effective harnesses for long-running agents*](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) — the progress file, feature list and end-to-end tests in §6.2.4.
- Anthropic, [*Harness design for long-running apps*](https://www.anthropic.com/research/harness-design-long-running-apps) (2026) — why harness parts are bets on the model's limits, and the context resets it removed.
- OpenAI, [*Harness engineering: leveraging Codex in an agent-first world*](https://openai.com/index/harness-engineering/) (2026) — the team that shipped a million lines with none written by hand.
- LangChain, [*Improving Deep Agents with harness engineering*](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) (2026) — 52.8% to 66.5% with the same model.
- Anthropic, [*Effective context engineering for AI agents*](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) (2025) — the step before harness engineering.
- Claude, [*Managing context on the Claude Developer Platform*](https://claude.com/resources/articles/context-management) (2025) — the memory tool and context editing behind the 39% figure.
- Hangfan Zhang et al., [*Self-Harness: Harnesses That Improve Themselves*](https://arxiv.org/abs/2606.09498) (2026), and Xia et al., [*RRSI: Regularized Recursive Self-Improvement of Agent Harnesses*](https://arxiv.org/abs/2609.24972) (2026) — the gains, and the catch.
- Rich Sutton, [*The Bitter Lesson*](http://www.incompleteideas.net/IncIdeas/BitterLesson.html) (2019) — why general methods keep winning.
- Lennart Meincke, Ethan Mollick et al., [*Prompting Science Report 2: The Decreasing Value of Chain of Thought in Prompting*](https://arxiv.org/abs/2506.07142) (2025) — the "think step by step" numbers.
- Shijie Wu et al., [*BloombergGPT: A Large Language Model for Finance*](https://arxiv.org/abs/2303.17564) (2023), and Xianzhi Li et al., [*Are ChatGPT and GPT-4 General-Purpose Solvers for Financial Text Analytics?*](https://arxiv.org/abs/2305.05862) (2023) — the domain model, and the general model that beat it.
- Harvey, [*Improving agent accuracy with Harvey Graph*](https://www.harvey.ai/blog/improving-agent-accuracy-with-harvey-graph) (2026) — a domain harness in law (company-reported, early results).
