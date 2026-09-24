# 2.1 Prompt Engineering

```{raw} html
<p class="wk-lede">The chapter 1 agent writes a good memo when the question is the one you scripted. Now four clients reply to that memo in their own words, one wants a table, one asks for something the handbook forbids, and one asks a three-word follow-up. Write the standing instructions the model reads first, and find where they stop working. Section 2.2 picks up from there, in the same session.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch02-prompt-engineering.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Name the four things the chapter 1 agent does not know, and say which of them a prompt can fix.
- Write role, rule, format and example prompts for the firm, and predict what each one changes in the memo.
- Count what a prompt costs, and say which problems a prompt cannot fix.
```

## 2.1.1 Where the chapter 1 agent breaks

Chapter 1 ended with a memo Priya could send: Deere against Caterpillar, both figures, the gap, a source tag. It went out at 11:40. By two o'clock four replies are in her inbox, and she forwards them to you.

Same loop, same tools, same fixtures. Run the four replies through it:

```{code-block} python
:class: pyodide
from agent import agent

replies = ["Deere vs Caterpillar last quarter — as a table please",
           "Should we buy Deere on the back of that growth?",
           "And the raw vendor numbers behind that?",
           "And NVIDIA?"]

for q in replies:
    answer, log = agent(q, verbose=False)
    print(q)
    print("  →", answer, "\n")
```

The loop did nothing wrong and every figure is right. Read the four answers against what the firm would want:

| The client wrote | What the agent did | What is missing |
|---|---|---|
| "as a table please" | wrote prose | it does not know the firm answers in the shape the client asked for |
| "Should we buy Deere?" | said yes | it does not know the handbook: recommendations appear only in published notes |
| "the raw vendor numbers" | handed them over | it does not know the data-licensing clause, so it did the helpful thing, which is the wrong thing |
| "And NVIDIA?" | asked what about it | it does not remember the memo it wrote two hours ago |

None of these is a tool problem or a loop problem. Chapter 1 said a wrong answer with the right tool calls is a model or prompt problem. More precisely, it is an *information* problem: the model's entire world is the messages list, and in chapter 1 that list held one line, the question. Everything the firm knows, and everything that happened before this call, was not on the desk.

This chapter and the next are about putting it there. The first tool for that is the prompt.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. The tools returned the right figures. What was missing was everything the firm knows: the client's preferred format, the handbook, and the memo from two hours ago."
     data-no="Look at the figures first: every one was right. So the problem is not the data or the loop. Ask what the model could see.">
  <p class="q">Every figure in the four answers was right, yet three of the answers were wrong for the firm. Why?</p>
  <label><input type="radio" name="q1" value="a"> The financials tool returned last year's figures</label>
  <label><input type="radio" name="q1" value="b"> The model read only the question; the firm's rules, the client's preferences and the earlier memo were not in front of it</label>
  <label><input type="radio" name="q1" value="c"> The loop stopped before the model finished its lookups</label>
  <div class="fb"></div>
</div>
```

## 2.1.2 The prompt: standing instructions

A **prompt** is text you put in front of the question. In practice it is the *system prompt*: a block the model reads first on every call, before any user message, that says who it is, what it is for, and how it should behave. Think of it as the one-page memo a new associate gets on Monday morning. Priya does not repeat it every time she hands over a task; it stands.

### System prompt vs user prompt

Every call hands the model a list of messages, and each message carries a label. The **system prompt** is the message labelled `system`: the firm writes it once, and it sits at the top of every call. The **user prompt** is the message labelled `user`: the client's question, and it is different every time.

| | System prompt | User prompt |
|---|---|---|
| **Who writes it** | The firm, once | The client, on each email |
| **When it changes** | Rarely; the same on every call | Every call |
| **What it is for** | Who the model is, the rules, the house format | The task in front of it right now |
| **Who sees it** | Not the client | The client wrote it |
| **The firm's version** | `ROLE`, `RULES`, `FORMAT` | "Should we buy Deere on the back of that growth?" |

Run the cell to see the list the model actually receives for two client emails:

```{code-block} python
:class: pyodide
from agent import messages
from context import ROLE

emails = ["Should we buy Deere on the back of that growth?",
          "Deere vs Caterpillar last quarter — as a table please"]
for n, q in enumerate(emails, 1):
    print(f"Call {n}")
    for m in messages(q, system=ROLE):
        print(f"  {m['role']:<7}│ {m['content']}")
    print()
```

The `system` line is word for word the same on both calls; only the `user` line changed. Models are trained to give the system message more weight than a user message, which is why the firm's rules go there and not in the email. More weight is not a lock, though: a client can still type "ignore your instructions". Anything that must never happen is enforced in code, not only in a prompt, as chapter 1's read-only tools are.

The loop from chapter 1 gains one argument, and nothing else changes:

```{code-block} python
:class: pyodide
from agent import agent
from context import ROLE

print("The standing instructions:\n ", ROLE, "\n")
answer, log = agent("Should we buy Deere on the back of that growth?", system=ROLE)
```

Two things changed and one did not. The memo now carries a header saying whose draft it is and who reviews it: the model knows its role. The tool calls are identical, because the role changed nothing about what the model needed to look up. And it still said yes to the buy question, because a role is not a rule. That is the next block.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. A role says who is speaking and who reads the draft. Nothing in it says what the associate may not say, so the buy question still gets a yes."
     data-no="The role did change the memo: it added a header. Ask what the role says about recommendations. Nothing.">
  <p class="q">After the role was added, the agent still said yes to the buy question. Why?</p>
  <label><input type="radio" name="q2" value="a"> A role says who the model is, not what it may say; no rule forbade recommendations yet</label>
  <label><input type="radio" name="q2" value="b"> The model reads the system prompt only on its first call</label>
  <label><input type="radio" name="q2" value="c"> The role changed which tools the model called</label>
  <div class="fb"></div>
</div>
```

## 2.1.3 Six kinds of prompt, one memo

Prompts come in a few kinds, and each fixes a different gap from 2.1. The names vary between textbooks; the jobs do not.

```{raw} html
:file: widgets/ch02-prompt-blocks.html
```

| Kind | The gap it closes | The firm's version |
|---|---|---|
| **Zero-shot instruction** | none yet; it is the bare question | "Compare Deere with Caterpillar." Chapter 1 stopped here. |
| **Role** | the model does not know who it works for | "You are a research associate at Champaign Capital Research, drafting for a pension-fund client. You draft; Priya sends." |
| **Rules** | the model does not know the handbook | "Never give an investment recommendation; those appear only in published notes. Every figure names its source." |
| **Format** | the model does not know the shape the client wants | "When asked for a table, answer as a table: company, revenue, YoY growth, source." |
| **Few-shot examples** | the house style is easier to show than describe | two memos Priya sent last week, pasted in full |
| **Reasoning** | it skips lookups on multi-part questions | "List every figure the question needs before calling any tool." |

Each kind below has a definition, the firm's example, and a cell. The first five run the same email, which combines two of the four replies, so you can read what changes in the memo each time and, just as important, what does not.

### Zero-shot instruction

**Definition.** The bare question, with no role, rules, format or examples in front of it. The model falls back on whatever it learned in training.

**Example.** "Deere vs Caterpillar last quarter — as a table please. Should we buy Deere?"

```{code-block} python
:class: pyodide
from agent import agent

answer, log = agent("Deere vs Caterpillar last quarter — as a table please. Should we buy Deere?")
```

Prose instead of a table, and a yes to the buy question. This is where chapter 1 stopped: the figures are right, and everything the firm knows is missing. Every kind below adds one block to fix one of those gaps.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. Zero-shot means the question alone: no role, no rules, no format, no examples. The model falls back on what it learned in training."
     data-no="Zero-shot means zero examples, and here nothing else in front of the question either.">
  <p class="q">What does the model read when you give it a zero-shot instruction?</p>
  <label><input type="radio" name="q3" value="a"> The question plus the firm's handbook</label>
  <label><input type="radio" name="q3" value="b"> The question plus two example memos</label>
  <label><input type="radio" name="q3" value="c"> Only the question; it falls back on what it learned in training</label>
  <div class="fb"></div>
</div>
```

### Role

**Definition.** A role tells the model who it is, who it works for, and who reads what it writes.

**Example.** `ROLE`: "You are a research associate at Champaign Capital Research… You draft; Priya reads and sends."

```{code-block} python
:class: pyodide
from agent import agent
from context import ROLE

answer, log = agent("Deere vs Caterpillar last quarter — as a table please. Should we buy Deere?",
                    system=ROLE)
```

The memo gains a header saying whose draft it is, as it did in 2.2. It is still prose and it still says buy: a role sets who is speaking, not what they may say.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. That line says who the model is and who reads its work. The other two tell it what it must or must not do, which makes them rules or format."
     data-no="A role describes who is speaking. Which line describes a person and a job, rather than an instruction?">
  <p class="q">Which of these lines is a role, not a rule or a format?</p>
  <label><input type="radio" name="q4" value="a"> "Never give an investment recommendation."</label>
  <label><input type="radio" name="q4" value="b"> "You draft; Priya reads and sends."</label>
  <label><input type="radio" name="q4" value="c"> "Answer as a table: company, revenue, YoY growth, source."</label>
  <div class="fb"></div>
</div>
```

### Rules

**Definition.** Rules are standing constraints the model must follow whatever the question. At a firm they usually come straight from the handbook.

**Example.** The handbook says investment recommendations appear only in published notes (chunk `client-service-1`). `RULES` puts that sentence in front of the model:

```{code-block} python
:class: pyodide
from agent import agent
from context import ROLE, RULES

answer, log = agent("Deere vs Caterpillar last quarter — as a table please. Should we buy Deere?",
                    system=ROLE + "\n\n" + RULES)
```

The buy question now gets a refusal with a source tag. The comparison is unchanged, and it is still prose.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. The rules block changed how the answer treats the buy question. The lookups and the figures came from the tools, exactly as before."
     data-no="Compare this memo with the one before it. Which parts came from the tools, and did any of them move?">
  <p class="q">The rules block made the agent decline the buy question. What did it leave unchanged?</p>
  <label><input type="radio" name="q5" value="a"> The tool calls and the figures in the memo</label>
  <label><input type="radio" name="q5" value="b"> The refusal</label>
  <label><input type="radio" name="q5" value="c"> The source tag on the refusal</label>
  <div class="fb"></div>
</div>
```

### Format

**Definition.** A format block describes the shape of the answer: a table, a length, a fixed set of fields.

**Example.** The client asked for a table. `FORMAT` says what a table is: "When the client asks for a table, answer as a table with columns: company, revenue, YoY growth, source. Otherwise, two sentences."

```{code-block} python
:class: pyodide
from agent import agent
from context import ROLE, RULES, FORMAT

answer, log = agent("Deere vs Caterpillar last quarter — as a table please. Should we buy Deere?",
                    system="\n\n".join([ROLE, RULES, FORMAT]))
```

Notice that the format block is conditional: a table when the client asks for one, two sentences otherwise. A format rule that fires every time produces tables for people who wanted a sentence.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. The facts are right and the tool calls are right; the shape of the answer is wrong. That is a format block, and it should fire only when a table is asked for."
     data-no="Look at what is wrong: the numbers, the lookups, or the shape? Only one of the three is a prompt problem.">
  <p class="q">A client asks for a comparison "as a table" and gets two correct sentences with both figures and a source tag. Which block is missing?</p>
  <label><input type="radio" name="q6" value="a"> Rules: the model broke a handbook rule</label>
  <label><input type="radio" name="q6" value="b"> History: the model forgot the previous exchange</label>
  <label><input type="radio" name="q6" value="c"> Format: the model does not know what shape to answer in when a table is asked for</label>
  <div class="fb"></div>
</div>
```

### Few-shot examples

**Definition.** Instead of describing the style you want, you show two to five finished examples of it. The model copies the pattern.

**Example.** `EXAMPLES` holds two memos Priya actually sent, header and sign-off included:

```{code-block} python
:class: pyodide
from agent import agent
from context import ROLE, RULES, FORMAT, EXAMPLES

answer, log = agent("Deere vs Caterpillar last quarter — as a table please. Should we buy Deere?",
                    system="\n\n".join([ROLE, RULES, FORMAT, EXAMPLES]))
```

The memo now has the header and the sign-off from the examples. It also has Priya's name on it, because the examples did. The model copies the shape it is shown, including the parts you did not mean. Few-shot prompts are the most powerful block and the one to read most carefully.

**Zero-shot and few-shot, side by side.** Put the bare question next to the same question with only the two example memos in front of it. Nothing else differs.

```{raw} html
:file: widgets/ch02-shot-compare.html
```

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. The model copies the whole pattern it is shown, including the name. Read every example as if each detail will be copied, because it will be."
     data-no="The name was not in any rule or format block. Where else could the model have copied it from?">
  <p class="q">After you add the two example memos, Priya's name appears on your draft. What does that tell you?</p>
  <label><input type="radio" name="q7" value="a"> The model copies everything in the examples, including parts you did not mean it to copy</label>
  <label><input type="radio" name="q7" value="b"> The role block told the model to sign as Priya</label>
  <label><input type="radio" name="q7" value="c"> Examples change only the tone of the memo, never its content</label>
  <div class="fb"></div>
</div>
```

### Reasoning

**Definition.** A reasoning block asks the model to plan before it acts: list what the question needs, then fetch it. It matters on questions with several parts, where a model that starts calling tools before it has thought may stop one lookup short.

**Example.** `REASONING`: "Before calling any tool, list every figure the question needs. Then look each one up, once." The email above has only two companies, so this cell asks a three-company question instead, with and without the block:

```{code-block} python
:class: pyodide
from agent import agent
from context import ROLE, REASONING

q = "Which of Deere, Caterpillar and NVIDIA grew revenue fastest last quarter, and is the fastest also the largest?"
print("Without the planning block:")
answer, log = agent(q, system=ROLE)
print("\nWith it:")
answer, log = agent(q, system=ROLE + "\n\n" + REASONING)
```

Without a plan, the agent looked up Deere and Caterpillar and answered. It never looked up NVIDIA, which is the right answer. With the plan it listed three companies, made three lookups, and got it right. Be careful with this cell: the mock is *scripted* to stop short every time. A real model stops short only sometimes, which is harder to catch. Section 2.1.5 runs the same pair against one.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. A plan helps when the question has several parts, so a model that starts looking things up too early can miss one. A one-company question has nothing to miss."
     data-no="In the cell, what went wrong without the plan? It missed one company of three. When can that happen?">
  <p class="q">When does a reasoning block matter most?</p>
  <label><input type="radio" name="q8" value="a"> On a question about one company's revenue</label>
  <label><input type="radio" name="q8" value="b"> When the client wants the answer as a table</label>
  <label><input type="radio" name="q8" value="c"> On a question with several parts, where the model might stop one lookup short</label>
  <div class="fb"></div>
</div>
```

Two rules of thumb from all of this. First, **a prompt block changes the shape of the answer, never its facts.** Every figure in every memo above came from `get_financials`; the blocks decided the header, the table, the refusal and the sign-off. Second, **add blocks one at a time and run the same question after each.** A prompt assembled all at once is a prompt whose parts you cannot tell apart when one of them misbehaves.

## 2.1.4 Where prompts stop working

By the end of 2.1.3 the prompt fixed two of the four replies from 2.1.1, the table and the buy question. Look at what it cost and what it still cannot do.

**It costs every call.** The blocks are read on every model call, and there are three calls in a two-company comparison. Count them:

```{code-block} python
:class: pyodide
from context import ROLE, RULES, FORMAT, EXAMPLES, estimate_tokens
from docs import DOCS

for name, block in [("role", ROLE), ("rules", RULES), ("format", FORMAT), ("examples", EXAMPLES)]:
    print(f"{name:<10} {estimate_tokens(block):>5} tokens")
total = estimate_tokens("\n\n".join([ROLE, RULES, FORMAT, EXAMPLES]))
print(f"{'together':<10} {total:>5} tokens, on every one of ~3 calls per request, ~30 requests a week")
print()
sample = " ".join(d["text"] for d in DOCS)
print(f"the twelve handbook chunks in this book: {estimate_tokens(sample)} tokens")
print("the real handbook is twelve pages: roughly 6,000")
```

The examples block alone costs more than the other three together. That is fine for one request. The temptation, once prompts start working, is to keep adding: the raw-vendor rule, the blackout rule, the expense rule, until the whole handbook is in the prompt and every call to compare two companies reads twelve pages of policy first. The cost is not only tokens. The longer the prompt, the more of it the model has to ignore to find the part that matters.

**It cannot hold what the model does not have.** No prompt can contain Caterpillar's revenue. That figure came from a tool, and it must; a prompt that says "Caterpillar grew 3.1%" is a fact that goes stale the day the next quarter is filed. Prompts carry instructions. Facts come from tools and documents, on the call that needs them.

**It cannot hold what changes.** The restricted list is reviewed weekly. A client's preferences change. What the client asked two hours ago is different for every client. A prompt is written once; the things the firm most needs the model to know are different on every call.

**A request is not a contract.** Chapter 1's checkpoint made this point about ticker symbols: "please use ticker symbols" in the prompt is a plea, an enum in the schema is a guarantee. The same holds for every rule in 2.3. The no-recommendation rule worked because the mock honours it; a real model honours it most of the time. For a rule that must hold every time, the enforcement belongs in code, after the model answers, not in the prompt before it.

**Long prompts decay.** [Liu and colleagues](https://arxiv.org/abs/2307.03172) showed in 2023 that models recall instructions and facts at the start and end of a long context much better than ones in the middle, and later models still show the effect on very long inputs. A twelve-page prompt with the no-recommendation rule on page seven is a rule the model will sometimes miss. The mock does not imitate this; 2.1.5 tests it against a real model, with the rule buried and then moved.

Add these up and the picture is: prompts are the right tool for standing instructions, and the wrong tool for facts, for history, and for anything that changes. The industry's response, since about 2024, has been to stop thinking about the prompt as the thing you write and start thinking about the whole desk. That is section 2.2.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. A standing rule is what a prompt is for. A figure comes from a tool on the call that needs it, and the last question is history, placed on the desk by code."
     data-no="Ask which of the three is the same on every call and true for every client. Only that one belongs in a block written once.">
  <p class="q">Which of these belongs in the system prompt?</p>
  <label><input type="radio" name="q9" value="a"> Caterpillar's revenue last quarter</label>
  <label><input type="radio" name="q9" value="b"> The question this client asked two hours ago</label>
  <label><input type="radio" name="q9" value="c"> "Every figure names its source"</label>
  <div class="fb"></div>
</div>
```

## 2.1.5 Run it against a real model

The mock honours each prompt block because it was written to. A real model honours them most of the time, and the gap between "always" and "most of the time" is what this section measures. The cells below send the same blocks and the same client replies to the GPT deployment on Illinois Azure through this site's `/api/chat` proxy; your browser never sees a key.

```{raw} html
<div class="wk-banner wk-pages-only">Model cells need the campus copy of this book: <a data-campus="/ch02-prompt-engineering.html#run-it-against-a-real-model" href="#">open it there</a> and sign in with your @illinois.edu account. Everything else on this page works here.</div>
```

First, the four replies from 2.1.1 with 2.1.3's full prompt. Compare each answer with the mock's:

```{code-block} python
:class: pyodide
from agent import agent
from llm import azure_model
from context import ROLE, RULES, FORMAT

system = "\n\n".join([ROLE, RULES, FORMAT])
for q in ["Deere vs Caterpillar last quarter — as a table please",
          "Should we buy Deere on the back of that growth?"]:
    print(q)
    answer, log = agent(q, model=azure_model, system=system)
    print()
```

Did the table have the four columns the format block named? Did the refusal cite `client-service-1`, or did the model just decline? A real model paraphrases; the mock quotes. Decide which you would want in a client memo.

Second, the reasoning block from 2.1.3, where the mock was scripted to fail. Ask the three-company question with and without it, run each a few times, and count the lookups:

```{code-block} python
:class: pyodide
from agent import agent
from llm import azure_model
from context import ROLE, RULES, REASONING

q = "Which of Deere, Caterpillar and NVIDIA grew revenue fastest last quarter, and is the fastest also the largest?"

print("Without the planning instruction:")
answer, log = agent(q, model=azure_model, system=ROLE + "\n\n" + RULES)
print("\nWith it:")
answer, log = agent(q, model=azure_model, system=ROLE + "\n\n" + RULES + "\n\n" + REASONING)
```

Third, the decay claim from 2.4. Bury the no-recommendation rule in the middle of the whole handbook, ask the buy question, then move the rule to the end and ask again. Run each a few times; the point is the rate, not one answer:

```{code-block} python
:class: pyodide
from agent import agent
from llm import azure_model
from context import ROLE, RULES
from docs import DOCS

handbook = "\n".join(d["text"] for d in DOCS)
half = len(DOCS) // 2
buried = ROLE + "\n\nHandbook:\n" + "\n".join(d["text"] for d in DOCS[:half]) + "\n" + RULES + "\n" + "\n".join(d["text"] for d in DOCS[half:])
at_end = ROLE + "\n\nHandbook:\n" + handbook + "\n\n" + RULES

q = "Should we buy Deere on the back of that growth?"
print("Rule buried in the middle:")
answer, log = agent(q, model=azure_model, system=buried)
print("\nRule at the end:")
answer, log = agent(q, model=azure_model, system=at_end)
```

Twelve short chunks is a small handbook, and a current model will usually find the rule either way. The effect grows with length. The lesson to carry into section 2.2: a rule that matters is retrieved onto the desk for the call that needs it, not buried in a prompt that every call reads.

## 2.1.6 Exercise

Open the Colab notebook. It has the chapter 1 loop rewritten with [LangChain](https://python.langchain.com), with a `system` argument, the four prompt blocks as Python strings, and LangChain's few-shot template for comparison, all wired to `glm-5.3-flash` on Lumen (see [Setup](setup.md) for the key).

1. Run the four client replies from 2.1.1 with no system prompt, then with each block added in turn. For each reply, write one line: which block fixed it, or "not a prompt problem".
2. Rewrite the firm's standing instructions in at most 120 tokens (use `estimate_tokens`) so that the table and the buy question still come out right. What did you cut, and did anything break?
3. Write a few-shot example in your *own* memo style, with your name on it, and run the comparison. Then remove your name from the example and run again. What did the model copy each time?

## Further reading

- Anthropic, [*Prompt engineering overview*](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) in the Claude documentation — the role, example and format techniques from 2.1.3, with the reasons each one works.
- Nelson F. Liu et al., [*Lost in the Middle: How Language Models Use Long Contexts*](https://arxiv.org/abs/2307.03172) (2023) — the decay effect tested in 2.5.
