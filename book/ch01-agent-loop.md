# 1. Agent Loop and Tool API Design

```{raw} html
<p class="wk-lede">Build a transparent tool-using agent loop. By the end you can read every step an agent took and explain why it called each tool.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch01-agent-loop.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Trace the model → tool → model cycle and name exactly what enters each call.
- Design a tool schema that a model cannot misuse.
- Log every step so a reviewer can audit the run without re-running it.
```

## 1.1 The loop, in four lines

Strip away the frameworks and an agent is a loop. You send the conversation to the model. If the reply contains a tool call, you run the tool, append the result to the conversation, and send it again. You stop when the model answers in plain text, or when a step budget runs out.

That is the whole thing. Every agent product you will see this year is this loop plus opinions about what goes into the conversation and which tools exist. Step through one run:

```{raw} html
:file: widgets/ch01-loop-stepper.html
```

Three things to notice. The model never runs code; it only *asks* for a tool by name. The loop is the only place with access to real data. And the conversation grows on every step, so whatever the model sees on step three includes everything from steps one and two.

## 1.2 Try it: a minimal loop

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

## 1.3 What enters each call

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

## 1.4 Designing the tool API

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

fin = TOOL_SCHEMAS[0]; search = TOOL_SCHEMAS[2]
print(validate(fin, {"ticker": "DE", "period": "Q2-2026"}))
print(validate(fin, {"ticker": "Deere"}))
print(validate(fin, {"ticker": "DE", "period": "Q2-2026", "currency": "EUR"}))
print(validate(search, {"query": ""}))
```

## 1.5 Two failure modes and their guards

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

## 1.6 A live business example: refund triage

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

## 1.7 Exercise

Open the Colab notebook. It contains the same loop, wired to the real Anthropic API with `strict: true` schemas.

1. Run the refund-triage scenario for all four orders against the real model and compare its tool sequence and recommendations with the mock's.
2. Add a second data tool, `get_price(ticker)`, with a closed schema, and run *"Is Deere's revenue growth better than Caterpillar's, and what are both trading at?"* It should show four tool calls and one text answer.
3. Extend the step log with the total elapsed time of the whole run.
4. In three sentences, explain one tool call the model made that you would not have made, and what schema change would prevent it.

## Further reading

- Anthropic, *Building effective agents* — the "augmented LLM" and the argument for simple loops over frameworks.
- The Anthropic tool-use documentation on `strict` schemas and `additionalProperties`.
