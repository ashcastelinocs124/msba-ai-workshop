# 1. Introduction to AI Agents

```{raw} html
<p class="wk-lede">What an agent is, what it is made of, and when to use one. Then build the loop yourself, design the tools it is allowed to call, and read every step it took.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch01-agent-loop.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Say what an agent is and tell it apart from a single model call and from a workflow.
- Trace the model → tool → model cycle and name exactly what enters each call.
- Design a tool schema that a model cannot misuse, and log every step so a reviewer can audit the run.
```

## 1.1 What an agent is

It is Monday morning at Champaign Capital Research and the first item in your inbox is a client asking for Deere's revenue growth last quarter. If you have not read [the firm page](the-firm.md), do that first; this chapter, and every chapter after it, is one task from that firm's plan.

An agent is a language model that decides what to do next, does it through a tool, looks at what came back, and repeats until the job is done or a limit stops it.

Every word in that sentence is doing work. *Decides*: the model, not your code, picks the next step. *Through a tool*: the model never touches data or systems directly; it asks for a named tool with arguments, and your code runs it. *Looks at what came back*: the tool's result goes into the conversation, so the next decision is made with more information than the last. *Until a limit stops it*: an agent without a budget is a bug, not a feature.

It helps to put the agent next to the two things it is most often confused with.

| | Who decides the steps | What the model does | Example |
|---|---|---|---|
| **Single model call** | nobody; there is one step | reads the input, writes the output | "Summarize this earnings call transcript." |
| **Workflow** | your code, in advance | fills in a slot at each fixed step | Extract the vendor, then classify the invoice, then draft an email. Three calls, fixed order. |
| **Agent** | the model, as it goes | chooses which tool to call, reads the result, chooses again | "Can Marcus sell his Caterpillar shares today?" The model decides it needs the request first, then the trading policy, then answers. |

A workflow is a recipe. An agent is a cook. Most business problems are recipes, and a recipe is cheaper, faster, and easier to test. You reach for an agent when you cannot write the recipe in advance because the steps depend on what the data turns out to say.

Here is the smallest possible demonstration. Ask the model a question it cannot answer from the question alone, and look at what it returns:

```{code-block} python
:class: pyodide
from mock_model import model
from agent import explain_reply

reply = model([{"role": "user", "content": "What was Deere's revenue growth last quarter?"}])
print(explain_reply(reply))
```

That is not an answer. It is a request to run a tool and hand back the result. A single model call stops here. An agent is what happens when something picks that request up, runs it, and asks the model again. That something is the loop, and you will write it in section 1.4.

## 1.2 The three ingredients

Every agent, from a forty-line script to a commercial product, is made of the same three parts.

**The model.** It reads the conversation so far and produces either a tool request or a final answer. It has no memory between calls and no access to anything outside the text it is given. In this book the model is a mock for the in-page cells and a real one in Colab and on the campus copy of this site; the other two ingredients do not change.

**The tools.** Named functions with a typed contract: a name, a description of when to use them, and a schema for their arguments. The model sees only the contract. Your code owns the implementation, and with it every decision about what the agent is allowed to reach. A read-only `get_trade_request` is a very different risk from a `clear_trade`, and the difference lives entirely in this layer.

**The loop.** The code that carries messages to the model, executes the tool it asks for, appends the result, and goes again. It is also where the guardrails live: the step budget, the timeout, the log, and the human approval gate for anything that writes.

You already own a version of all three. Hover a part on either figure:

```{raw} html
:file: widgets/ch01-agent-vs-human.html
```

The split matters because it tells you where to look when something goes wrong. A wrong answer with the right tool calls is a model or prompt problem. A tool called with nonsense arguments is a contract problem. A run that never ends is a loop problem. Chapters 2, 6, and this one map onto those three.

```{code-block} python
:class: pyodide
from tools import TOOLS, TOOL_SCHEMAS

print("tools the agent can call:", list(TOOLS))
print()
print("what the model sees for one of them:")
print(TOOL_SCHEMAS[2]["name"], "-", TOOL_SCHEMAS[2]["description"])
print("arguments:", ", ".join(TOOL_SCHEMAS[2]["input_schema"]["properties"]))
```

Notice what is *not* in the list: nothing that sends an email, clears a trade, publishes a note, or changes a record. That is a design choice you will make on purpose in 1.9, and chapter 6 is about how to relax it safely.

## 1.3 When an agent is the right tool

Because an agent decides its own steps, it costs more per task than a workflow, it is slower, and it is harder to test. Those are real costs, so an agent has to earn its place. Four questions settle it:

1. **Can you write the steps down in advance?** If yes, write a workflow. Invoice matching, monthly report generation, and document classification are recipes.
2. **Do the steps depend on what the data says?** A client question that might need a filing lookup, a data-vendor pull, a policy check, or none of them, depending on what the client wrote, is agent territory.
3. **What does a mistake cost, and will anyone see it?** An agent that recommends and a human who approves is a cheap mistake. An agent that acts on a live system is not. Start with the first.
4. **Is the task worth the latency and the tokens?** Three model calls to pre-clear one trade request is fine. Three model calls per row of a million-row price table is not.

Chapter 7 turns these four questions into a full decision framework, with the "neither" answer treated seriously. For now the rule of thumb is: workflow by default, agent when the recipe cannot be written, and never let an agent hold a pen until its log has earned your trust.

## 1.4 The loop, in four lines

Now the third ingredient. Strip away the frameworks and an agent is a loop. You send the conversation to the model. If the reply contains a tool call, you run the tool, append the result to the conversation, and send it again. You stop when the model answers in plain text, or when a step budget runs out.

That is the whole thing. Every agent product you will see this year is this loop plus opinions about what goes into the conversation and which tools exist. Step through one run:

```{raw} html
:file: widgets/ch01-loop-stepper.html
```

Three things to notice. The model never runs code; it only *asks* for a tool by name. The loop is the only place with access to real data. And the conversation grows on every step, so whatever the model sees on step three includes everything from steps one and two.

## 1.5 Try it: a minimal loop

This cell runs in your browser against a **mock model**: a small function that behaves like an LLM for the questions in this book, so no API key is needed. The Colab notebook swaps in the real Anthropic API with the same loop.

```{code-block} python
:class: pyodide
from agent import agent
from tools import TOOLS

answer, log = agent("What was Deere's revenue growth last quarter?", TOOLS)
print()
print("ANSWER:", answer)
print("STEPS :", len(log))
```

Now change the question to `"What is the current price of NVDA?"` and run again. The model picks a different tool, and the loop does not care; it only checks whether the reply is a tool call or text.

Here is the loop itself, shortened. Read it once slowly; the rest of Part I builds on it.

```python
def agent(question, tools, model, max_steps=6):
    msgs = [{"role": "user", "content": question}]
    for step in range(max_steps):
        reply = model(msgs)                       # 1. ask the model
        if reply["type"] == "text":
            return reply["text"]                  # 2. plain text → done
        result = tools[reply["tool"]](**reply["args"])   # 3. run the tool
        msgs.append({"role": "tool", "content": result}) # 4. append, go again
    return "Stopped: step budget exhausted."
```

## 1.6 What enters each call

The model is stateless. It has no memory of the previous step except what you put in `msgs`. That makes the messages list the single most important object in the system: it is the model's entire world.

Print it and look:

```{code-block} python
:class: pyodide
from mock_model import model
from tools import TOOLS
from agent import explain_reply, _describe_result

msgs = [{"role": "user", "content": "What was Deere's revenue growth last quarter?"}]
reply = model(msgs)
print("The model's first move:", explain_reply(reply))

result = TOOLS[reply["tool"]](**reply["args"])
msgs.append({"role": "assistant", "content": f"[{reply['tool']}]"})
msgs.append({"role": "tool", "name": reply["tool"], "content": result})

print("\nWhat the model sees on the NEXT call, one line per message:")
for m in msgs:
    text = _describe_result(m["content"]) if m["role"] == "tool" else str(m["content"])
    print(" ", m["role"].ljust(9), text)
```

This is what "transparent" means in this chapter. A transparent agent is one where you can print the messages list at any step and every line is something a human put there or a tool returned. Nothing is hidden inside a framework object.

The `agent()` function in this book returns a **log** alongside the answer: one dict per step with the tool name, arguments, result, and elapsed time. In a business setting that log is the audit trail. When a stakeholder asks "why did it say that?", you open the log, not the model.

```{code-block} python
:class: pyodide
from agent import agent, narrate

answer, log = agent("What does the handbook say about the blackout window?", verbose=False)
print(answer)
print()
for line in narrate(log):
    print(line)
```

## 1.7 Designing the tool API

The loop is simple. The hard part is the contract the model sees: the tool's name, description, and input schema. That contract is the only thing that stands between a well-behaved model and one that calls `search_docs("")` forty times.

Open the schemas this book ships with:

```{code-block} python
:class: pyodide
from tools import TOOL_SCHEMAS, describe_schema
describe_schema(TOOL_SCHEMAS[0])
```

Four rules, each of which fixes a failure you will otherwise see in week one:

**Enums over free text.** `ticker` is an enum of five symbols, not a string. A string invites `"Deere"`, `"DE Corp"`, and `"deere.com"`. An enum makes the invalid call impossible instead of merely unlikely.

**Required means required.** `period` is required even though it has one value today. The day a second quarter is added, the model must choose rather than default silently.

**Describe when *not* to call.** The `get_financials` description says "Use only when the user asks about revenue, growth, or earnings." Models over-call tools that sound useful. The negative instruction is usually more valuable than the positive one.

**Close the schema.** `additionalProperties: false` rejects arguments you did not define. Without it, a model that invents `{"ticker": "DE", "currency": "EUR"}` gets a silent success and a wrong answer.

Try breaking one. The cell below validates a call against the schema with a tiny checker (the real API does this for you when you set `strict: true`, which you will use in the notebook):

```{code-block} python
:class: pyodide
from tools import TOOL_SCHEMAS

def validate(schema, args):
    props, req = schema["input_schema"]["properties"], schema["input_schema"]["required"]
    problems = [f"missing required '{r}'" for r in req if r not in args]
    problems += [f"unexpected '{k}'" for k in args if k not in props]
    for k, v in args.items():
        if k in props and "enum" in props[k] and v not in props[k]["enum"]:
            problems.append(f"'{k}'={v!r} not in {props[k]['enum']}")
        if k in props and "minLength" in props[k] and len(v) < props[k]["minLength"]:
            problems.append(f"'{k}' shorter than {props[k]['minLength']}")
    return problems or ["ok"]

fin = TOOL_SCHEMAS[0]; search = TOOL_SCHEMAS[3]
print(", ".join(validate(fin, {"ticker": "DE", "period": "Q2-2026"})))
print(", ".join(validate(fin, {"ticker": "Deere"})))
print(", ".join(validate(fin, {"ticker": "DE", "period": "Q2-2026", "currency": "EUR"})))
print(", ".join(validate(search, {"query": ""})))
```

## 1.8 Two failure modes and their guards

**The runaway loop.** A model that keeps calling tools never returns text. `max_steps` is the guard. Six is a good default for a single question; set it from the task, not from hope. When the budget is exhausted the loop returns a message that says so, and the log records it. Never let the loop end silently.

**The bad call.** The model asks for a tool with arguments that crash it. The loop in this book catches the exception and returns `{"error": ...}` as the tool result. The model then sees the error on the next step and can correct. A crash tells the model nothing; an error message is data.

```{code-block} python
:class: pyodide
from agent import agent
from tools import TOOLS

# a model that never stops calling tools
def stubborn(msgs):
    return {"type": "tool_call", "tool": "get_price", "args": {"ticker": "DE"}}

answer, log = agent("anything", TOOLS, model=stubborn, max_steps=3)
print()
print(answer)
```

## 1.9 A live business example: trade pre-clearance

Everything so far used a research question because the numbers are easy to check. Here is the same loop doing a job the firm pays two people to do: pre-clearing employees' personal trades.

The scenario. Everyone at Champaign Capital must ask compliance before trading a stock in a sector the firm covers. Elena Ruiz's team gets about thirty requests a week by email. Each one means opening the request, checking the restricted list, checking when the firm last published on that name, checking how long the position has been held, and writing back a decision with the policy clause that supports it. The rules fit on one page. Applying them the same way at 4:55 on a Friday is the hard part, and two officers reading the same handbook have reached different answers on the same request.

The agent gets two tools: `get_trade_request`, which returns the request record, and `search_docs`, which returns the relevant handbook chunks. It does not get a `clear_trade` tool. It recommends; a compliance officer approves. That split is the single most important design decision in the example, and it is a tool-API decision, not a prompt decision.

```{code-block} python
:class: pyodide
from agent import agent

answer, log = agent("Can compliance clear trade request #7102?")
print()
print(answer)
```

Read the steps. The model asked for the request first, then the policy, then decided. It could not have decided from the question alone, and it could not have skipped the lookup, because every rule hinges on a field in the request.

Now change the request number. Each request in the fixture data trips a different clause of the handbook:

| Request | Employee | What is different | Expected recommendation |
|---|---|---|---|
| 7101 | Priya Natarajan, buy 50 DE | firm last published on Deere 41 days ago | Approve |
| 7102 | Marcus Bell, sell 200 CAT | position held 12 days | Decline, 30-day minimum holding period |
| 7103 | Jordan Lee, buy 30 NVDA | NVIDIA is on the restricted list | Decline |
| 7104 | Tom Okafor, sell 80 DE | firm published on Deere 6 days ago | Hold until the 14-day blackout ends |

```{code-block} python
:class: pyodide
from agent import agent

for request_id in ["7101", "7102", "7103", "7104"]:
    answer, log = agent(f"Can compliance clear trade request #{request_id}?", verbose=False)
    print(f"#{request_id}: {answer}\n")
```

Every recommendation ends with a `[source: …]` tag naming the handbook chunk it relied on. Chapter 3 makes that mandatory. For now, notice what it buys you: an employee who disagrees with a decision can read the clause, not argue with a model.

The log is the audit trail. This is what you would store per request, and what you would show the firm's annual compliance review:

```{code-block} python
:class: pyodide
from agent import agent, narrate

answer, log = agent("Can compliance clear trade request #7104?", verbose=False)
for line in narrate(log):
    print(line)
```

What the firm gets from this loop, compared with an officer doing it by hand: the same handbook applied the same way every time, a written reason with a citation on every decision, a log that can be reviewed, and a compliance officer who now approves thirty recommendations instead of researching thirty requests. What it does not get is an agent that clears trades. That stays behind a human click until the log has earned trust, which is the subject of chapter 6.

The Colab notebook runs this exact scenario against the real model. Compare its tool sequence with the mock's; a well-designed schema should make them match.

## Checkpoint

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. The steps are fixed and known in advance, so code should decide them. A model call fills each slot; no agent is needed."
     data-no="Look at who decides the order of steps. If you can write the recipe before seeing the data, you do not need the model to choose.">
  <p class="q">Every month, Champaign Capital's data team needs each data-vendor invoice extracted into fields, matched to the contract, and flagged if the amounts differ. Which shape fits?</p>
  <label><input type="radio" name="q0" value="a"> An agent, because it involves several steps and a model</label>
  <label><input type="radio" name="q0" value="b"> A single model call, because it is one document at a time</label>
  <label><input type="radio" name="q0" value="c"> A workflow: code runs the three fixed steps and the model only extracts fields</label>
  <div class="fb"></div>
</div>
```

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. Constraints belong in the contract the model sees. A retry hides the bug and a plea in the prompt is unenforceable."
     data-no="Not quite. That treats the symptom. Where does the model learn what a valid call looks like, before it decides to make one?">
  <p class="q">The model keeps calling <code>search_docs</code> with an empty query. Where is the fix most likely to live?</p>
  <label><input type="radio" name="q1" value="a"> In the loop: retry the call when the query is empty</label>
  <label><input type="radio" name="q1" value="b"> In the tool schema: make <code>query</code> required with a minimum length, and say in the description when not to search</label>
  <label><input type="radio" name="q1" value="c"> In the system prompt: "please be careful with search"</label>
  <div class="fb"></div>
</div>
```

## 1.10 Run it against a real model

The mock model answered every question so far. This section sends the same loop, the same tool schemas, and the same pre-clearance request to a GPT deployment on Illinois Azure.

Your browser never sees a key. The page calls `/api/chat` on this site, a small proxy that holds the key, checks that you are signed in with your campus account, and forwards the request. That is the same "no write tools, a human approves" idea from 1.9 applied to the key itself: the model is reachable, the credential is not.

```{raw} html
<div class="wk-banner wk-pages-only">Model cells need the campus copy of this book: <a data-campus="/ch01-agent-loop.html#run-it-against-a-real-model" href="#">open it there</a> and sign in with your @illinois.edu account. Everything else on this page works here.</div>
```

```{code-block} python
:class: pyodide
from agent import agent
from llm import azure_model      # real model, via /api/chat on this site

answer, log = agent("Can compliance clear trade request #7102?", model=azure_model)
print()
print(answer)
```

Compare with the mock's run in 1.9. The tool order should match, because the schema made it the only sensible order. The wording will differ; the citation should not.

Now the question the mock could never handle, because it only knows the scripts in this book:

```{code-block} python
:class: pyodide
from agent import agent
from llm import azure_model

answer, log = agent("Priya Natarajan (request #7101) wants to buy Deere, but says she will probably publish a note on Deere within two weeks. Approve now, hold, or decline, and what should compliance tell her?", model=azure_model)
print()
print(answer)
```

Read the log. Did the model look up the request? Did it search the handbook for the blackout rule, the pre-clearance rule, or both? Every extra tool call costs tokens and time, so a good loop is not the one that calls the most tools, it is the one that calls exactly the ones the question needs. Your token budget for the day is in the header of this page.

## 1.11 Exercise

Open the Colab notebook. It contains the same loop, wired to the real Anthropic API with `strict: true` schemas.

1. Classify three tasks from your own work or internship as single call, workflow, or agent, using the four questions in 1.3. One sentence each.
2. Run the pre-clearance scenario for all four requests against the real model and compare its tool sequence and recommendations with the mock's.
3. Add a second data tool, `get_price(ticker)`, with a closed schema, and run *"Is Deere's revenue growth better than Caterpillar's, and what are both trading at?"* It should show four tool calls and one text answer.
4. Extend the step log with the total elapsed time of the whole run.
5. In three sentences, explain one tool call the model made that you would not have made, and what schema change would prevent it.

## Further reading

- Anthropic, *Building effective agents* — the "augmented LLM" and the argument for simple loops over frameworks.
- The Anthropic tool-use documentation on `strict` schemas and `additionalProperties`.
