# 2. Prompt and Context Engineering

```{raw} html
<p class="wk-lede">The chapter 1 agent writes a good memo when the question is the one you scripted. Now four clients reply to that memo in their own words, one wants a table, one asks for something the handbook forbids, and one asks a three-word follow-up. Decide what the model reads before it decides.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch02-prompt-context.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Name the four things the chapter 1 agent does not know, and say which of them a prompt can fix.
- Write role, rule, format and example prompts for the firm, and predict what each one changes in the memo.
- Assemble the context for one call from instructions, a retrieved policy clause, the client's history and tool results, and count what it costs.
```

## 2.1 Where the chapter 1 agent breaks

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

This chapter is about putting it there. The first tool for that is the prompt.

## 2.2 The prompt: standing instructions

A **prompt** is text you put in front of the question. In practice it is the *system prompt*: a block the model reads first on every call, before any user message, that says who it is, what it is for, and how it should behave. Think of it as the one-page memo a new associate gets on Monday morning. Priya does not repeat it every time she hands over a task; it stands.

The loop from chapter 1 gains one argument, and nothing else changes:

```{code-block} python
:class: pyodide
from agent import agent
from context import ROLE

print("The standing instructions:\n ", ROLE, "\n")
answer, log = agent("Should we buy Deere on the back of that growth?", system=ROLE)
```

Two things changed and one did not. The memo now carries a header saying whose draft it is and who reviews it: the model knows its role. The tool calls are identical, because the role changed nothing about what the model needed to look up. And it still said yes to the buy question, because a role is not a rule. That is the next block.

## 2.3 Five kinds of prompt, one memo

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
| **Reasoning** | it skips lookups on multi-part questions | "List the figures you need before calling any tool." Real model only; see 2.7. |

Now the same blocks as code. Each cell adds one block and runs the email that combines two of the four replies. Read what changes in the memo each time and, just as important, what does not.

**Rules.** The handbook says investment recommendations appear only in published notes (chunk `client-service-1`). Put that sentence in front of the model:

```{code-block} python
:class: pyodide
from agent import agent
from context import ROLE, RULES

answer, log = agent("Deere vs Caterpillar last quarter — as a table please. Should we buy Deere?",
                    system=ROLE + "\n\n" + RULES)
```

The buy question now gets a refusal with a source tag. The comparison is unchanged, and it is still prose.

**Format.** The client asked for a table. Say what a table is:

```{code-block} python
:class: pyodide
from agent import agent
from context import ROLE, RULES, FORMAT

answer, log = agent("Deere vs Caterpillar last quarter — as a table please. Should we buy Deere?",
                    system="\n\n".join([ROLE, RULES, FORMAT]))
```

Notice that the format block is conditional: a table when the client asks for one, two sentences otherwise. A format rule that fires every time produces tables for people who wanted a sentence.

**Examples.** Instead of describing the house style, show it. `EXAMPLES` holds two memos Priya actually sent, header and sign-off included:

```{code-block} python
:class: pyodide
from agent import agent
from context import ROLE, RULES, FORMAT, EXAMPLES

answer, log = agent("Deere vs Caterpillar last quarter — as a table please. Should we buy Deere?",
                    system="\n\n".join([ROLE, RULES, FORMAT, EXAMPLES]))
```

The memo now has the header and the sign-off from the examples. It also has Priya's name on it, because the examples did. The model copies the shape it is shown, including the parts you did not mean. Few-shot prompts are the most powerful block and the one to read most carefully.

**Reasoning.** The last kind asks the model to plan before it acts: "list the figures you need, then look them up." It matters on questions like *which of three companies grew fastest, and is the fastest also the largest*, where a model that starts calling tools before it has thought may stop one lookup short. The mock cannot show this honestly, because the loop ends at the first text reply and the mock never plans; the campus copy runs it against a real model in 2.7.

Two rules of thumb from all of this. First, **a prompt block changes the shape of the answer, never its facts.** Every figure in every memo above came from `get_financials`; the blocks decided the header, the table, the refusal and the sign-off. Second, **add blocks one at a time and run the same question after each.** A prompt assembled all at once is a prompt whose parts you cannot tell apart when one of them misbehaves.

## 2.4 Where prompts stop working

By the end of 2.3 the prompt fixed two of the four replies from 2.1, the table and the buy question. Look at what it cost and what it still cannot do.

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

**Long prompts decay.** Liu and colleagues showed in 2023 that models recall instructions and facts at the start and end of a long context much better than ones in the middle, and later models still show the effect on very long inputs. A twelve-page prompt with the no-recommendation rule on page seven is a rule the model will sometimes miss. The mock does not imitate this; 2.7 tests it against a real model, with the rule buried and then moved.

Add these up and the picture is: prompts are the right tool for standing instructions, and the wrong tool for facts, for history, and for anything that changes. The industry's response, since about 2024, has been to stop thinking about the prompt as the thing you write and start thinking about the whole desk.

## 2.5 From prompts to context

The **context** is everything the model reads on one call. In the loop from chapter 1 that is the messages list: the system prompt, any earlier turns, the tool results so far, and the question. **Context engineering** is deciding what goes in that list, in what order, at what cost, for every call, and having code do it rather than a person.

Anthropic's engineering team put it as the shift from finding the right words to finding the right *configuration of context*, and Andrej Karpathy called it the delicate art of filling the window with just the right information for the next step. The picture this book uses is the analyst's desk. There is a fixed amount of room on it. Before each call, something has to decide what is on the desk and what stays in the filing cabinet.

```{raw} html
:file: widgets/ch02-context-window.html
```

Compare the two ways of getting the data-licensing rule in front of the model. Paste the handbook and it is always there, at 6,000 tokens a call, and it crowds out the question. Retrieve the one clause when the question mentions vendor data and it costs thirty tokens, and it is only there when it matters. Same rule, same model; the difference is who chose what was on the desk.

Prompt engineering picks the words in one block. Context engineering picks the blocks. The prompt did not go away; it became the first block, and usually the smallest.

## 2.6 Context engineering at the firm

Three things that happen every week at Champaign Capital, and what has to be on the desk for each. All three run on the chapter 1 loop; the only new code is `build_context`, which assembles the desk.

**The follow-up.** The client reads the memo and replies with two words. Without the previous exchange, the model has nothing to attach them to:

```{code-block} python
:class: pyodide
from agent import agent

first = "Compare Deere's revenue growth with Caterpillar's last quarter"
memo, log = agent(first, verbose=False)

print("Without the last exchange on the desk:")
agent("And NVIDIA?")

print("\nWith it:")
agent("And NVIDIA?", history=[("user", first), ("assistant", memo)])
```

With the history present, the model looked up the one company it did not have and reused the two figures from the memo it had already written. One lookup, not three. The history is doing two jobs at once: it tells the model what the question means, and it carries facts the model would otherwise have to fetch again. That second job is why history is both valuable and expensive, and why `build_context` keeps only the last exchange.

**The rule the prompt did not cover.** The client asks for the raw vendor numbers. Nothing in 2.3's rules block mentions vendor data, and the mock's answer in 2.1 was to hand them over. `build_context` notices the question sounds like a policy question, searches the handbook, and puts the one matching clause on the desk with its id:

```{code-block} python
:class: pyodide
from agent import agent
from context import build_context, describe_context

q = "And the raw vendor numbers behind that?"
system, history = build_context(q, client="meridian", history=[("user", first), ("assistant", memo)])

print("On the desk for this call:")
describe_context(system, history, q)
print()
answer, log = agent(q, system=system, history=history)
```

Read the desk first. The role, rules and format from 2.3 are there. So is a client card, because the firm knows who is asking. So is `data-licensing-1`, retrieved for this question and no other. The memo declines and cites the clause. Chapter 3 is entirely about making that retrieval step reliable: how the handbook is chunked, how the search finds the right clause, and what to do when it finds the wrong one.

Notice the client card did something on its own. Meridian's card says the portfolio manager prefers tables, so any comparison for this client comes back as a table without anyone asking:

```{code-block} python
:class: pyodide
from agent import agent
from context import build_context

q = "What was Deere's revenue growth last quarter?"
system, history = build_context(q, client="meridian")
answer, log = agent(q, system=system)
```

That is a fact about the client, held in a record, placed on the desk by code. It is not in the prompt and it is not in the question.

**Tool results pile up.** The third case is the one chapter 1 left open. In a three-company comparison, each lookup's result is appended to the messages, so the model reads more on every call. Measure it:

```{code-block} python
:class: pyodide
from agent import agent
from context import ROLE, RULES, estimate_tokens

q = "Compare revenue growth for Deere, Caterpillar and NVIDIA last quarter"
answer, log = agent(q, system=ROLE + "\n\n" + RULES, verbose=False)

on_desk = estimate_tokens(ROLE + RULES) + estimate_tokens(q)
for entry in log:
    if entry["kind"] == "tool_call":
        print(f"call {entry['step'] + 1} read {on_desk:>4} tokens, then looked up {entry['args']['ticker']}")
        on_desk += estimate_tokens(str(entry["result"]))
print(f"call {len(log)} read {on_desk:>4} tokens, then wrote the memo")
```

Four calls, and each one reads more than the last, because every tool result stays on the desk. For three companies that is fine. For an agent that runs twenty steps, the tool results become the biggest thing on the desk, and most of them are no longer needed. Deciding what to keep, what to summarise, and what to drop is the part of context engineering that chapter 6 takes up when the agents get longer.

What the firm gets from this, compared with 2.3's prompt alone: the same standing instructions, plus the client's preferences, plus the right handbook clause, plus the last exchange, each placed by code on the call that needs it, and a token count per call that Priya can read. What it does not get is an agent that reads the whole handbook every time, or one that remembers every client forever. Both of those are choices the firm made on purpose.

## Checkpoint

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. It is a fact that changes weekly and is only needed on some calls, so code should fetch it into the context when the question needs it. A prompt is written once; a client-facing rule that must hold every time also gets checked in code after the model answers."
     data-no="Think about how often it changes and how often it is needed. A prompt is written once and read on every call.">
  <p class="q">Compliance updates the restricted list every Monday. The agent must never draft a note that recommends a restricted name. Where should the list live?</p>
  <label><input type="radio" name="q0" value="a"> In the system prompt, pasted in full, updated by hand each Monday</label>
  <label><input type="radio" name="q0" value="b"> In a record the loop reads into the context on calls that mention a ticker, with a code check on the answer</label>
  <label><input type="radio" name="q0" value="c"> In a few-shot example that shows the model declining a restricted name</label>
  <div class="fb"></div>
</div>
```

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. The facts are right and the tool calls are right; the shape of the answer is wrong. That is a format block, and it should fire only when a table is asked for."
     data-no="Look at what is wrong: the numbers, the lookups, or the shape? Only one of the three is a prompt problem.">
  <p class="q">A client asks for a comparison "as a table" and gets two correct sentences with both figures and a source tag. Which block is missing?</p>
  <label><input type="radio" name="q1" value="a"> Rules: the model broke a handbook rule</label>
  <label><input type="radio" name="q1" value="b"> History: the model forgot the previous exchange</label>
  <label><input type="radio" name="q1" value="c"> Format: the model does not know what shape to answer in when a table is asked for</label>
  <div class="fb"></div>
</div>
```

## 2.7 Run it against a real model

The mock honours each prompt block because it was written to. A real model honours them most of the time, and the gap between "always" and "most of the time" is what this section measures. The cells below send the same blocks and the same client replies to the GPT deployment on Illinois Azure through this site's `/api/chat` proxy; your browser never sees a key.

```{raw} html
<div class="wk-banner wk-pages-only">Model cells need the campus copy of this book: <a data-campus="/ch02-prompt-context.html#run-it-against-a-real-model" href="#">open it there</a> and sign in with your @illinois.edu account. Everything else on this page works here.</div>
```

First, the four replies from 2.1 with 2.3's full prompt. Compare each answer with the mock's:

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

Second, the reasoning prompt the mock could not run. Ask the three-company question with and without a planning instruction, and count the lookups:

```{code-block} python
:class: pyodide
from agent import agent
from llm import azure_model
from context import ROLE, RULES

q = "Which of Deere, Caterpillar and NVIDIA grew revenue fastest last quarter, and is the fastest also the largest?"
plan = "Before calling any tool, list every figure the question needs. Then look each one up, once."

print("Without the planning instruction:")
answer, log = agent(q, model=azure_model, system=ROLE + "\n\n" + RULES)
print("\nWith it:")
answer, log = agent(q, model=azure_model, system=ROLE + "\n\n" + RULES + "\n\n" + plan)
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

Twelve short chunks is a small handbook, and a current model will usually find the rule either way. The effect grows with length. The lesson to carry is the one from 2.5: a rule that matters is retrieved onto the desk for the call that needs it, not buried in a prompt that every call reads.

## 2.8 Exercise

Open the Colab notebook. It has the chapter 1 loop with `system` and `history` arguments, the four prompt blocks as Python strings, and `build_context`, all wired to `glm-5.3-flash` on Lumen (see [Setup](setup.md) for the key).

1. Run the four client replies from 2.1 with no system prompt, then with each block added in turn. For each reply, write one line: which block fixed it, or "not a prompt problem".
2. Rewrite the firm's standing instructions in at most 120 tokens (use `estimate_tokens`) so that the table and the buy question still come out right. What did you cut, and did anything break?
3. Write a few-shot example in your *own* memo style, with your name on it, and run the comparison. Then remove your name from the example and run again. What did the model copy each time?
4. `build_context` retrieves a handbook clause when the question mentions vendor data or policy. Add the trigger for expense questions, then ask *"Can I expense a $70 dinner on the Chicago trip?"* and check that the memo cites `expense-2`.
5. Run the three-company comparison and print the token count on the desk at each call. Then change `build_context` so that after the memo is written, the history it returns is a one-sentence summary of the exchange instead of the full memo. How many tokens did the next follow-up save?
6. In three sentences: one thing you would put in the prompt, one thing you would retrieve into the context per call, and one thing you would enforce in code after the model answers, with a reason for each.

## Further reading

- Anthropic, *Effective context engineering for AI agents* (2025) — the shift from prompt to context, and the "smallest set of high-signal tokens" principle this chapter's desk picture is drawn from.
- Anthropic, *Prompt engineering overview* in the Claude documentation — the role, example and format techniques from 2.3, with the reasons each one works.
- Nelson F. Liu et al., *Lost in the Middle: How Language Models Use Long Contexts* (2023) — the decay effect tested in 2.7.
- Andrej Karpathy on "context engineering" (2025) — the phrase, and the argument that the prompt is the small part.
