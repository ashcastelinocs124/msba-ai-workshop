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

An agent is a language model that decides what to do next, does it through a tool, looks at what came back, and repeats until the job is done or a limit stops it.

Every word in that sentence is doing work. *Decides*: the model, not your code, picks the next step. *Through a tool*: the model never touches data or systems directly; it asks for a named tool with arguments, and your code runs it. *Looks at what came back*: the tool's result goes into the conversation, so the next decision is made with more information than the last. *Until a limit stops it*: an agent without a budget is a bug, not a feature.

It helps to put the agent next to the two things it is most often confused with.

| | Who decides the steps | What the model does | Example |
|---|---|---|---|
| **Single model call** | nobody; there is one step | reads the input, writes the output | "Summarize this earnings call transcript." |
| **Workflow** | your code, in advance | fills in a slot at each fixed step | Extract the vendor, then classify the invoice, then draft an email. Three calls, fixed order. |
| **Agent** | the model, as it goes | chooses which tool to call, reads the result, chooses again | "Should we refund order #4488?" The model decides it needs the order first, then the policy, then answers. |

A workflow is a recipe. An agent is a cook. Most business problems are recipes, and a recipe is cheaper, faster, and easier to test. You reach for an agent when you cannot write the recipe in advance because the steps depend on what the data turns out to say.

Here is the smallest possible demonstration. Ask the model a question it cannot answer from the question alone, and look at what it returns:

```{code-block} python
:class: pyodide
from mock_model import model

reply = model([{"role": "user", "content": "What was Deere's revenue growth last quarter?"}])
print(reply)
```

That is not an answer. It is a request: "run `get_financials` with these arguments and show me the result." A single model call stops here. An agent is what happens when something picks that request up, runs it, and asks the model again. That something is the loop, and you will write it in section 1.4.

## 1.2 The three ingredients

Every agent, from a forty-line script to a commercial product, is made of the same three parts.

**The model.** It reads the conversation so far and produces either a tool request or a final answer. It has no memory between calls and no access to anything outside the text it is given. In this book the model is a mock for the in-page cells and a real one in Colab and on the campus copy of this site; the other two ingredients do not change.

**The tools.** Named functions with a typed contract: a name, a description of when to use them, and a schema for their arguments. The model sees only the contract. Your code owns the implementation, and with it every decision about what the agent is allowed to reach. A read-only `get_order` is a very different risk from an `issue_refund`, and the difference lives entirely in this layer.

**The loop.** The code that carries messages to the model, executes the tool it asks for, appends the result, and goes again. It is also where the guardrails live: the step budget, the timeout, the log, and the human approval gate for anything that writes.

The split matters because it tells you where to look when something goes wrong. A wrong answer with the right tool calls is a model or prompt problem. A tool called with nonsense arguments is a contract problem. A run that never ends is a loop problem. Chapters 2, 6, and this one map onto those three.

```{code-block} python
:class: pyodide
from tools import TOOLS, TOOL_SCHEMAS

print("tools the agent can call:", list(TOOLS))
print()
print("what the model sees for one of them:")
print(TOOL_SCHEMAS[2]["name"], "-", TOOL_SCHEMAS[2]["description"])
print("arguments:", list(TOOL_SCHEMAS[2]["input_schema"]["properties"]))
```

Notice what is *not* in the list: nothing that sends an email, moves money, or changes a record. That is a design choice you will make on purpose in 1.9, and chapter 6 is about how to relax it safely.

## 1.3 When an agent is the right tool

Because an agent decides its own steps, it costs more per task than a workflow, it is slower, and it is harder to test. Those are real costs, so an agent has to earn its place. Four questions settle it:

1. **Can you write the steps down in advance?** If yes, write a workflow. Invoice matching, monthly report generation, and document classification are recipes.
2. **Do the steps depend on what the data says?** A support request that might need an order lookup, a policy check, a warranty check, or none of them, depending on what the customer wrote, is agent territory.
3. **What does a mistake cost, and will anyone see it?** An agent that recommends and a human who approves is a cheap mistake. An agent that acts on a live system is not. Start with the first.
4. **Is the task worth the latency and the tokens?** Three model calls to triage a $59 refund is fine. Three model calls per row of a million-row table is not.

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
import json

msgs = [{"role": "user", "content": "What was Deere's revenue growth last quarter?"}]
reply = model(msgs)
print("model asked for:", reply)

result = TOOLS[reply["tool"]](**reply["args"])
msgs.append({"role": "assistant", "content": f"<tool_call>{reply['tool']}({json.dumps(reply['args'])})"})
msgs.append({"role": "tool", "name": reply["tool"], "content": result})

print("\nwhat the model sees on the NEXT call:")
for m in msgs:
    print(" ", m["role"].ljust(9), str(m["content"])[:90])
```

This is what "transparent" means in this chapter. A transparent agent is one where you can print the messages list at any step and every line is something a human put there or a tool returned. Nothing is hidden inside a framework object.

The `agent()` function in this book returns a **log** alongside the answer: one dict per step with the tool name, arguments, result, and elapsed time. In a business setting that log is the audit trail. When a stakeholder asks "why did it say that?", you open the log, not the model.

```{code-block} python
:class: pyodide
from agent import agent
import json

answer, log = agent("What is the refund policy?", verbose=False)
print(answer)
print()
for entry in log:
    print(json.dumps(entry)[:140])
```

## 1.7 Designing the tool API

The loop is simple. The hard part is the contract the model sees: the tool's name, description, and input schema. That contract is the only thing that stands between a well-behaved model and one that calls `search_docs("")` forty times.

Open the schemas this book ships with:

```{code-block} python
:class: pyodide
from tools import TOOL_SCHEMAS
import json
print(json.dumps(TOOL_SCHEMAS[0], indent=2))
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
print(validate(fin, {"ticker": "DE", "period": "Q2-2026"}))
print(validate(fin, {"ticker": "Deere"}))
print(validate(fin, {"ticker": "DE", "period": "Q2-2026", "currency": "EUR"}))
print(validate(search, {"query": ""}))
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

answer, log = agent("anything", TOOLS, model=stubborn, max_steps=3, verbose=False)
print(answer)
print([e["kind"] for e in log])
```

## 1.9 A live business example: refund triage

Everything so far used a finance question because the numbers are easy to check. Here is the same loop doing a job a business actually pays for: deciding what to do with a refund request.

The scenario. An office-furniture retailer gets forty refund requests a day. The policy is short (14 days, unused, receipt required, store credit after that), but applying it means looking up the order, reading the policy, and writing a consistent answer. Today a support rep does all three by hand, and two reps reading the same policy reach different decisions.

The agent gets two tools: `get_order`, which returns the order record, and `search_docs`, which returns the relevant policy chunks. It does not get a `issue_refund` tool. It recommends; a human approves. That split is the single most important design decision in the example, and it is a tool-API decision, not a prompt decision.

```{code-block} python
:class: pyodide
from agent import agent

question = "Customer Priya Natarajan is asking for a refund on order #4471. What should we do?"
answer, log = agent(question)
print()
print(answer)
```

Read the steps. The model asked for the order first, then the policy, then decided. It could not have decided from the question alone, and it could not have skipped the order lookup, because the policy hinges on the number of days since purchase.

Now change the order number. Each order in the fixture data trips a different clause of the policy:

| Order | Customer | What is different | Expected recommendation |
|---|---|---|---|
| 4471 | Priya Natarajan | 9 days, unused, receipt | Approve full refund |
| 4488 | Marcus Bell | 21 days | Store credit, needs manager sign-off |
| 4502 | Elena Ruiz | No receipt on file | Hold and ask for proof of purchase |
| 4519 | Tom Okafor | Item was used | Decline full refund, offer exchange |

```{code-block} python
:class: pyodide
from agent import agent

for order_id in ["4471", "4488", "4502", "4519"]:
    answer, log = agent(f"Customer is asking for a refund on order #{order_id}. What should we do?", verbose=False)
    print(f"#{order_id}: {answer}\n")
```

Every recommendation ends with a `[source: …]` tag naming the policy chunk it relied on. Chapter 3 makes that mandatory. For now, notice what it buys you: a manager who disagrees with a recommendation can open the policy line, not argue with a model.

The log is the audit trail. This is what you would store per request, and what you would show a compliance reviewer six months later:

```{code-block} python
:class: pyodide
from agent import agent
import json

answer, log = agent("Customer is asking for a refund on order #4488. What should we do?", verbose=False)
for entry in log:
    print(json.dumps({k: v for k, v in entry.items() if k != "result"}))
```

What the business gets from this loop, compared with the rep doing it by hand: the same policy applied the same way every time, a written reason with a citation on every decision, a log that can be reviewed, and a rep who now approves forty recommendations instead of researching forty cases. What it does not get is an agent that moves money. That stays behind a human click until the log has earned trust, which is the subject of chapter 6.

The Colab notebook runs this exact scenario against the real model. Compare its tool sequence with the mock's; a well-designed schema should make them match.

## Checkpoint

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. The steps are fixed and known in advance, so code should decide them. A model call fills each slot; no agent is needed."
     data-no="Look at who decides the order of steps. If you can write the recipe before seeing the data, you do not need the model to choose.">
  <p class="q">Every Monday, finance needs each new vendor invoice extracted into fields, matched to a purchase order, and flagged if the amounts differ. Which shape fits?</p>
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

The mock model answered every question so far. This section sends the same loop, the same tool schemas, and the same refund request to a GPT deployment on Illinois Azure.

Your browser never sees a key. The page calls `/api/chat` on this site, a small proxy that holds the key, checks that you are signed in with your campus account, and forwards the request. That is the same "no write tools, a human approves" idea from 1.9 applied to the key itself: the model is reachable, the credential is not.

```{raw} html
<div class="wk-banner wk-pages-only">Model cells need the campus copy of this book: <a data-campus="/ch01-agent-loop.html#run-it-against-a-real-model" href="#">open it there</a> and sign in with your @illinois.edu account. Everything else on this page works here.</div>
```

```{code-block} python
:class: pyodide
from agent import agent
from llm import azure_model      # real model, via /api/chat on this site

answer, log = agent("Customer is asking for a refund on order #4488. What should we do?", model=azure_model)
print()
print(answer)
```

Compare with the mock's run in 1.9. The tool order should match, because the schema made it the only sensible order. The wording will differ; the citation should not.

Now the question the mock could never handle, because it only knows the scripts in this book:

```{code-block} python
:class: pyodide
from agent import agent
from llm import azure_model

answer, log = agent("Tom Okafor (order #4519) says the lamp arrived scratched. Is that a refund or a warranty claim, and what do we need from him?", model=azure_model)
print()
print(answer)
```

Read the log. Did the model look up the order? Did it search the policy for warranty, refund, or both? Every extra tool call costs tokens and time, so a good loop is not the one that calls the most tools, it is the one that calls exactly the ones the question needs. Your token budget for the day is in the header of this page.

## 1.11 Exercise

Open the Colab notebook. It contains the same loop, wired to the real Anthropic API with `strict: true` schemas.

1. Classify three tasks from your own work or internship as single call, workflow, or agent, using the four questions in 1.3. One sentence each.
2. Run the refund-triage scenario for all four orders against the real model and compare its tool sequence and recommendations with the mock's.
3. Add a second data tool, `get_price(ticker)`, with a closed schema, and run *"Is Deere's revenue growth better than Caterpillar's, and what are both trading at?"* It should show four tool calls and one text answer.
4. Extend the step log with the total elapsed time of the whole run.
5. In three sentences, explain one tool call the model made that you would not have made, and what schema change would prevent it.

## Further reading

- Anthropic, *Building effective agents* — the "augmented LLM" and the argument for simple loops over frameworks.
- The Anthropic tool-use documentation on `strict` schemas and `additionalProperties`.
