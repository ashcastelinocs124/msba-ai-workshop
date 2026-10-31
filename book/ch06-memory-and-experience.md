# 6.3 Memory and Experience

```{raw} html
<p class="wk-lede">The cheapest way for an agent to learn is to write the lesson down where it will read it next time. This page covers four ways to keep lessons, from a single note to a playbook, and the cleanup that stops them piling up. The session 6 slides and lecture are on <a href="ch06-self-learning-agents.html#ch06-lecture">the chapter 6 page</a>.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch06-self-learning-agents.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Explain reflection memory, and why a lesson is only as good as the feedback behind it.
- Say what a skill library and an evolving playbook add over single notes.
- Explain why small edits keep detail that full rewrites lose.
- Say what "dreaming" does to a memory store, and why it writes a new one instead of editing the old.
```

All four work in the first of the four layers from section 6.1.3: the context. Nothing is retrained. Chapter 3's memory held **facts** about clients and documents. These hold **lessons** about the agent's own work. Chapter 3 called that kind **procedural** memory (§3.3.2), but there the procedures were written by a person; here the agent writes them from its failures, and a person approves them.

## 6.3.1 Reflection

**Reflection memory** works like this: after a failed attempt, the model writes a short note in plain English on what went wrong, and the note is fed into its next attempt. No retraining is needed. The lesson is just text in the context: cheap, readable, and easy to delete if it's wrong. It is the sticky note on your monitor that says "check the units first" after you lost points twice for mixing up millions and thousands.

Steps 4 and 5 of section 6.2's loop do exactly this. Here is the reflection the mock writes from the grader's feedback, and the desk it lands on:

```{code-block} python
:class: pyodide
from learning import reflect, lessons_block

feedback = "the memo says $44.9B; the 10-K says $45.7B for FY2025 (ended Nov 2, 2025)"
lesson = reflect(feedback)
print("lesson:", lesson)
print()
print(lessons_block([lesson]))
```

The idea comes from **Reflexion** (2023), where a model writing down its mistakes did markedly better on coding tests:

| Coding test (tests passed on the first try) | Model alone | With reflection |
|---|---|---|
| HumanEval, Python | 80% | 91% |
| HumanEval, Rust | 60% | 68% |
| MBPP, Python | 80.1% | 77.1% |

The last row went the wrong way. On that test the model's feedback came from unit tests it wrote for itself, and some of those tests were wrong. Wrong feedback produced wrong lessons. This is why the firm's lessons come from a grader the agent can't edit (§6.4.3), and why Priya approves each one.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. A lesson is only as good as the grader behind it. Bad tests taught bad lessons."
     data-no="On that test, the feedback came from unit tests the model wrote for itself, and some were wrong. What would wrong feedback do to a lesson?">
  <p class="q">Why did writing down lessons make Reflexion worse on one coding test?</p>
  <label><input type="radio" name="q0" value="a"> The lessons were too long to read</label>
  <label><input type="radio" name="q0" value="b"> Wrong feedback produced wrong lessons</label>
  <label><input type="radio" name="q0" value="c"> The model forgot its lessons</label>
  <label><input type="radio" name="q0" value="d"> That test had no time limit</label>
  <div class="fb"></div>
</div>
```

## 6.3.2 Skill library

A note says what to avoid. A **skill** says how to do something. With a **skill library**, an agent that solves something new saves the working procedure, often as code, under a name, and reuses it instead of solving it again. The first lasagna takes three hours and a video. You write a recipe card, and the next one takes twenty minutes.

**Voyager** (2023) did this in Minecraft, where goals build on each other: wood, then stone, then iron, then diamond tools. It counted how many attempts each agent needed to reach iron tools (fewer is better):

| Agent | Attempts to reach iron tools |
|---|---|
| Voyager, with its skill library | 21 |
| Voyager, skill library removed | 29 |
| AutoGPT, an earlier agent | 135 |

Only Voyager with its library ever reached diamond tools, in one of three runs. Each saved skill became a building block for a harder one, so the gain grew with each step.

Skill libraries now ship in products. An **Agent Skill** is a folder with a `SKILL.md` file and optional scripts. The agent reads each skill's one-line description and loads the full skill only when it needs it ([page 0G](ch00-skills-mcp.md) covers them). It is now an open standard, used on more than 70 platforms, with about a million skills published. Today people review the skills; the hope is that agents will write and test their own.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. The easier goals were reachable either way. Only the agent with its library reached diamond: skills compound."
     data-no="With the library: iron in 21 attempts, and diamond in one run of three. Without it: iron in 29, and diamond never.">
  <p class="q">What did Voyager's saved skills help with most?</p>
  <label><input type="radio" name="q1" value="a"> Every goal equally</label>
  <label><input type="radio" name="q1" value="b"> Only the first, easiest goal</label>
  <label><input type="radio" name="q1" value="c"> The hardest goals, which build on many earlier skills</label>
  <label><input type="radio" name="q1" value="d"> Nothing; the difference is noise</label>
  <div class="fb"></div>
</div>
```

## 6.3.3 Evolving playbook

An **evolving playbook** is a structured set of rules the agent edits after each task: it adds a bullet, sharpens one, or removes one. It never rewrites the whole thing. In **ACE** (2025) the same model, with only its playbook changing, gained 13 to 17 points:

| Task | Model alone | With the playbook |
|---|---|---|
| AppWorld: agent tasks across email, music and file apps | 42.4 | 59.5 |
| Finance: tagging and calculating figures in financial filings | 69.1 | 81.9 |

Why insist on small edits? Because a summary keeps the gist and drops the detail, and a summary of a summary drops more. Here is the firm's playbook rewritten as a fresh summary three times, next to the same playbook with one small edit:

```{code-block} python
:class: pyodide
from learning import PLAYBOOK, rewrite_all, edit

print("Rewritten whole, three times:")
for rule in rewrite_all(times=3):
    print("-", rule)
print()
print("One small edit:")
for rule in edit(add="Charts: label both axes, with units."):
    print("-", rule)
```

The rewrites kept every rule's first half and lost what made it useful: which page to cite, which handbook clause covers recommendations, where the source goes in a table. The small edit kept every word and added one rule. The mock's summary is scripted, so it loses the same words every run. A real model loses different words each time, which is harder to spot. The notebook's section 2 lets you watch it happen.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. A summary of a summary of a summary loses detail. Small edits keep it."
     data-no="Look at what the three rewrites above kept, and what they dropped.">
  <p class="q">An agent rewrites its whole playbook as a fresh summary after every task. What goes wrong after 50 tasks?</p>
  <label><input type="radio" name="q2" value="a"> The agent stops reading it</label>
  <label><input type="radio" name="q2" value="b"> The playbook grows too long</label>
  <label><input type="radio" name="q2" value="c"> Specific, hard-won details get squeezed out</label>
  <label><input type="radio" name="q2" value="d"> It becomes too expensive to read</label>
  <div class="fb"></div>
</div>
```

## 6.3.4 Dreaming

Notes written in the middle of a task pile up. They repeat each other, contradict each other, and go out of date. **Dreaming**, or memory consolidation, is a background job that runs between tasks. It rereads past sessions and the notes, merges the duplicates, settles the contradictions, drops what is stale, and writes down patterns it finds across sessions. It is you on a Sunday, rereading the week's scribbled class notes, crossing out what was wrong and writing a one-page summary.

The shape is work by day and consolidate by night:

| Daytime, on the task | Night, the dreaming job | Morning |
|---|---|---|
| sessions write quick, messy notes: the Deere memo, the Caterpillar memo, a client email | reads the memory and the recent sessions; merges, settles, prunes, finds patterns | a cleaned memory, reviewed by a person if you want, which the next task starts from |

Anthropic's version (in Claude Managed Agents, a research preview from May 2026) reads up to 100 past sessions and writes a **new** memory store. The original is never changed. You review the new one, or have it applied automatically. OpenAI, Letta and LangChain ship similar features, each running when the agent is idle. Doing this thinking ahead pays: a Letta and UC Berkeley study found that thinking about the material before the question arrived cut the computing needed at answer time about five-fold, at the same accuracy.

At the firm, the agent dreams every Friday night over the week's notes, and Priya approves the new file on Monday morning before the agent uses it:

```{raw} html
:file: widgets/ch06-dreaming.html
```

The same consolidation in code. `dream` returns a new list and leaves the week's notes as they were:

```{code-block} python
:class: pyodide
from learning import WEEK_NOTES, dream

new = dream()
print()
print("lessons-new.md:", new)
print("the Friday notes still have", len(WEEK_NOTES), "lines")
```

The rules here are fixed: notes about the fiscal year merge into one, the newer of two table rules wins, and old guidance is dropped. Deciding that "Tables only for institutional clients" is wrong, rather than a narrower rule, is a judgment. That is why the result goes to Priya instead of straight to the agent.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. Keeping the original untouched means a bad cleanup can be thrown away, and a person stays in the loop."
     data-no="Think about what happens on the day the cleanup goes wrong.">
  <p class="q">Why does Anthropic's dreaming write a new memory store instead of editing the original?</p>
  <label><input type="radio" name="q3" value="a"> So someone can review the result, and discard it if the cleanup went wrong</label>
  <label><input type="radio" name="q3" value="b"> So it can run without any model</label>
  <label><input type="radio" name="q3" value="c"> So dreaming runs faster</label>
  <label><input type="radio" name="q3" value="d"> So it uses less storage</label>
  <div class="fb"></div>
</div>
```

## 6.3.5 Exercise

Open the Colab notebook and run section 2. A real model on Lumen consolidates the week's notes, and rewrites the playbook five times.

1. Read the model's `lessons-new.md`. Did it merge the three fiscal-year notes into one rule? Which table rule did it keep, and did it say why?
2. Add a seventh note that contradicts the fiscal-year rule ("Use calendar year for Caterpillar"). Dream again. Is the result right, and how would Priya catch it if it weren't?
3. After five full rewrites of the playbook, which details survived? Count the words each round.

## Further reading

- Noah Shinn et al., [*Reflexion: Language Agents with Verbal Reinforcement Learning*](https://arxiv.org/abs/2303.11366) (2023) — reflection memory, and the coding results above.
- Guanzhi Wang et al., [*Voyager: An Open-Ended Embodied Agent with Large Language Models*](https://arxiv.org/abs/2305.16291) (2023) — the skill library in Minecraft.
- Anthropic, [*Equipping agents for the real world with Agent Skills*](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills) — skills as folders an agent loads when needed.
- Qizheng Zhang et al., [*Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models*](https://arxiv.org/abs/2510.04618) (2025) — ACE, the evolving playbook.
- Claude, [*New in Claude Managed Agents: dreaming, outcomes, and multiagent orchestration*](https://claude.com/resources/articles/new-in-claude-managed-agents) (2026), and the [*Dreams* documentation](https://platform.claude.com/docs/en/managed-agents/dreams) — how the new memory store is written and reviewed.
- Kevin Lin, Charlie Snell et al., [*Sleep-time Compute: Beyond Inference Scaling at Test-time*](https://arxiv.org/abs/2504.13171) (2025), with Letta's [summary](https://www.letta.com/blog/sleep-time-compute/) — thinking while the agent is idle.
