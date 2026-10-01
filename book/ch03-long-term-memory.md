# 3.3 Long-Term Memory

```{raw} html
<p class="wk-lede">A week after Monday, Dana writes "And NVIDIA?" in a new session, and the agent has no idea what she means: the conversation from page 3.2 is gone. Decide what to save between sessions, who writes it down, what kind of memory each note is, and how to stop a wrong note from being repeated with confidence. The session 3 recording will be on <a href="ch03-memory-rag.html#ch03-lecture">the chapter 3 page</a>.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch03-agent-memory.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Save notes between sessions two ways, written by the harness or by the agent, and weigh the trade-off.
- Sort a note into episodic, semantic or procedural memory, and say how each kind is found and corrected.
- Spot a wrong remembered figure, and name three guards against it.
- Use a System One model (chapter 0's page 0H) as a fast typed gate that decides what gets saved.
- Map short-term and long-term memory onto the OpenAI Agents SDK and LangGraph.
```

Page 3.2 kept one conversation going; this page keeps what matters after it ends.

## 3.3.1 Long-term memory, written by the harness

Long-term memory is a set of **notes** kept after a session ends and put back on the desk when the next one starts. The first way to write them keeps the agent out of it. When a session ends, a separate step, part of the **harness** (the code around the model, as in chapter 1), reads the transcript and saves what should be kept: here, every figure the memo stated and every preference the client gave, each with where it came from. Next session, the harness recalls the notes into the system prompt. The agent only ever reads them.

```{raw} html
:file: widgets/ch03-memory-card.html
```

```{code-block} python
:class: pyodide
from agent import agent
from memory import end_session, recall

monday = "Compare Deere's revenue growth with Caterpillar's last quarter"
memo, log = agent(monday, verbose=False)
session = [("user", monday), ("assistant", memo),
           ("user", "I prefer tables, and keep it under 150 words."), ("assistant", "Understood.")]

print("Monday, when the session ends:")
notes = end_session("meridian", session)

print("\nNext Monday, what the harness puts on the desk:")
print(recall("meridian"))

print("\nThe follow-up, in a brand-new session:")
answer, log = agent("And NVIDIA?", system=recall("meridian"))
```

The follow-up works in a session with no history at all, and it arrives as a table because a note says so. Nothing in the agent changed; it read a longer system prompt. This is the firm's client card from chapter 2, kept up to date by code instead of by hand.

The rules the harness uses are the decision here. These ones save figures and preferences, and nothing else. They cannot save what they were not written to look for, and a person has to change the code to change what is kept.

## 3.3.2 Three kinds of long-term memory

So far every note has been treated alike. They are not. Psychologists split human long-term memory three ways, and people who build agents borrow the split because each kind is written, found and fixed differently.

| | Episodic | Semantic | Procedural |
|---|---|---|---|
| **It is** | What happened, and when | What is true about the client | How the firm does the task |
| **At the firm** | "Monday's memo told Dana that Deere grew 6.4%" | "Dana prefers tables, under 150 words" | "For a comparison, look up both companies, say who grew faster, cite each source" |
| **Found by** | Recency, or how close it is to today's question | The client's name | The task, loaded when it is needed |
| **Goes stale when** | It does not, but an old figure can mislead | The fact changes, so the old note should be replaced | The firm changes its method, so a person edits it |

The harness in section 3.3.1 saves two of the three. The figures a memo stated are **episodic**: a record of what the firm told the client. The preference Dana gave is **semantic**: a standing fact that stays true until she says otherwise. **Procedural** memory is different in kind. It is not something the agent learns from a client; it is the firm's own method, which is already in this book as the system prompt's rules (chapter 2) and as an agent skill (page 0G). A person writes it and a person edits it.

The boundary is a judgement call: a sourced figure could be filed as a fact about the world. What matters is that the choice changes how you handle the note. This cell tags the same Monday notes by kind and puts them on the desk grouped under three headings:

```{code-block} python
:class: pyodide
from agent import agent
from memory import MEMORY, end_session, kind_of, recall_by_kind

MEMORY.clear()
monday = "Compare Deere's revenue growth with Caterpillar's last quarter"
memo, log = agent(monday, verbose=False)
session = [("user", monday), ("assistant", memo),
           ("user", "I prefer tables, and keep it under 150 words."), ("assistant", "Understood.")]

notes = end_session("meridian", session, verbose=False)
for n in notes:
    print(f"{kind_of(n):9} {n['text']}")

print("\nWhat goes on the desk next Monday:")
print(recall_by_kind("meridian"))

print("\nThe follow-up:")
answer, log = agent("And NVIDIA?", system=recall_by_kind("meridian"))
```

The answer is the same as in 3.3.1, because the notes are the same. Only the layout changed, and the layout is the point: an agent that can tell "what we told her" from "what she wants" from "how we work" can update one without touching the others. Sort five of the firm's notes yourself:

```{raw} html
:file: widgets/ch03-memory-kinds.html
```

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. Dana's preference is a standing fact, so the old note should be replaced. Adding a second note would leave two that disagree, and the agent could follow either one."
     data-no="Ask which kind of memory a preference is, and what should happen to the old note when the fact changes.">
  <p class="q">Dana now wants bullet points instead of tables. What should happen to the note that says she prefers tables?</p>
  <label><input type="radio" name="ch32-q5" value="a"> Keep it, and add a new note beside it</label>
  <label><input type="radio" name="ch32-q5" value="b"> Replace it: it is a standing fact, and the old one is now wrong</label>
  <label><input type="radio" name="ch32-q5" value="c"> Leave it; the agent will work out which is newer</label>
  <div class="fb"></div>
</div>
```

## 3.3.3 Long-term memory, written by the agent

The second way hands the decision to the agent. It gets one more tool, `remember_note`, and chooses for itself when something is worth keeping. This is how the memory features in ChatGPT and Claude work, and it catches things no rule anticipated.

It is also the first time in this book an agent writes anything. Chapter 1 §1.9 gave the agent read-only tools on purpose. `remember_note` is a fenced exception: it writes only to the agent's own notebook, never to a firm record (handbook clause `records-3`), and every note is visible to a person who can delete it (`records-4`). The default tool list stays read-only; a cell has to pass `MEMORY_TOOLS` to get the new tool.

```{code-block} python
:class: pyodide
from agent import agent
from memory import MEMORY_TOOLS, show_notes

answer, log = agent("Remember that Dana wants tables, and nothing longer than 150 words.", tools=MEMORY_TOOLS)
print()
show_notes("meridian")

print("\nThe same request, to an agent without the tool:")
answer, log = agent("Remember that Dana wants tables.")
```

Press **Watch** on the first run to see the note being written. The second agent has no `remember_note` tool, so it says it cannot save anything, and nothing is saved.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. The harness saves only what its rules look for, and nothing the rules miss. The agent can save anything it judges worth keeping, which also means it can save something wrong."
     data-no="Compare who decides what is saved. What can each one miss, and what can each one get wrong?">
  <p class="q">What is the main trade-off between notes written by the harness and notes written by the agent?</p>
  <label><input type="radio" name="ch32-q2" value="a"> Harness notes cost more tokens</label>
  <label><input type="radio" name="ch32-q2" value="b"> Agent notes cannot be deleted</label>
  <label><input type="radio" name="ch32-q2" value="c"> The harness saves only what its rules look for; the agent saves what it judges worth keeping, including mistakes</label>
  <div class="fb"></div>
</div>
```

## 3.3.4 When memory goes wrong

A note is only as good as whoever wrote it. After Monday's memo, Priya asks the agent to remember the figures for next week, and it writes Deere's growth as 64.0% instead of 6.4%. The slip is scripted in this book's mock model, and it happens every time; a real model makes this kind of slip only sometimes, which is harder to catch.

```{code-block} python
:class: pyodide
from agent import agent
from memory import MEMORY, MEMORY_TOOLS, recall, show_notes

MEMORY.clear()
monday = "Compare Deere's revenue growth with Caterpillar's last quarter"
memo, log = agent(monday, verbose=False)

print("Monday:")
answer, log = agent("Remember these figures for next week.", tools=MEMORY_TOOLS,
                    history=[("user", monday), ("assistant", memo)])

print("\nNext Monday:")
answer, log = agent("And NVIDIA?", system=recall("meridian"))
```

Next Monday's memo tells a client that Deere is growing twenty times as fast as Caterpillar. Worse, it cites `get_financials` as its source: the figure came from a note, the note came from the agent, and nothing was looked up. A remembered figure arrives on the desk looking exactly like a checked one. This is chapter 0's section 0.6 again, a fluent answer that is wrong, except that now the mistake persists and repeats every week until someone finds it.

Three guards, all from the handbook's section on AI assistants:

1. **Keep the source with every note** (`records-4`). A note that says *the agent's own summary* is worth less than one that says *get_financials, Q2-2026*, and anyone reading it can tell which is which.
2. **Check a remembered figure again before it goes to a client** (`records-5`). A note is a reminder of where to look, not evidence.
3. **Let a person see and delete notes** (`records-4`). Memory the firm cannot inspect is memory it cannot correct.

The second and third guards, in code:

```{code-block} python
:class: pyodide
from agent import agent
from memory import check_notes, forget_wrong, recall, show_notes

show_notes("meridian")
print()
for problem in check_notes("meridian"):
    print("Check failed:", problem)

print()
forget_wrong("meridian")
print("\nAfter deleting the notes that failed the check:")
show_notes("meridian")
answer, log = agent("And NVIDIA?", system=recall("meridian"))
```

With the wrong note gone, and no other notes left in this example, the agent is back to asking what the client means. That is the correct answer: better to ask than to repeat a wrong figure. The note inspector below puts the same three guards in front of a person:

```{raw} html
:file: widgets/ch03-note-inspector.html
```

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. The note looks like any other context on the desk. Re-checking the figure against the firm's data before it reaches a client catches the slip, whoever wrote the note."
     data-no="The model cannot tell a checked figure from a remembered one. What step would catch the slip before a client sees it?">
  <p class="q">An agent's note says Deere grew 64.0%. Which guard would have stopped the wrong figure reaching Dana?</p>
  <label><input type="radio" name="ch32-q3" value="a"> Re-checking every remembered figure against the firm's data before it goes into a memo</label>
  <label><input type="radio" name="ch32-q3" value="b"> Telling the agent to be more careful in its system prompt</label>
  <label><input type="radio" name="ch32-q3" value="c"> Keeping notes for a shorter time</label>
  <div class="fb"></div>
</div>
```

```{raw} html
<div class="wk-lcp" data-spot="ch03-memory" data-label="3.3 Long-Term Memory · after §3.3.4 when memory goes wrong"></div>
```

## 3.3.5 A fast gate for memory writes

Section 3.3.3's `remember_note` accepts any string, which is why "Deere grew 64.0%" got in. A different kind of model suggests a third way: a **System One model**, which returns a decision in a fixed form with a confidence, not a sentence (chapter 0's page 0H). Ask one whether a note should be saved and the only possible answers are `save`, `ask` (a person should look) or `skip`. It cannot answer with a paragraph, and it cannot make up a fourth option. It is also cheap and fast enough to run on every candidate note, before anything is saved.

The cell below uses a **scripted stand-in**, not a real System One model such as Jev. `gate` fills in the same three fields with hand-set confidences, the way this book's mock model stands in for a real one. It does use the figure check from section 3.3.3, so a wrong figure scores low.

```{code-block} python
:class: pyodide
from memory import MEMORY, gated_save, show_notes

MEMORY.clear()
gated_save("Dana wants tables, under 150 words")
gated_save("Deere grew revenue 64.0% YoY to $12.0B", source="the agent's summary")
gated_save("Thanks, that's all for today")
gated_save("Deere grew revenue 6.4% YoY to $13.8B", source="get_financials, Q2-2026")
print()
show_notes("meridian")
```

Three of the four are decided without a person: the preference is saved, the small talk is dropped, and the sourced figure is saved. The 64.0% note is not saved. Its confidence is too low, so it goes to a person, who sees it with its source before it can ever reach a memo. Move the bar in the widget and watch which notes change side:

```{raw} html
:file: widgets/ch03-memory-gate.html
```

Two limits. A gate is only as good as its confidence: a real model can be confidently wrong, so the check against the firm's data in section 3.3.4 (`records-5`) still runs before a figure goes to a client. And this idea is the book's own; TypeSafe AI's post describes the model (page 0H), not a memory design.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. Because the output is a fixed form, nothing free-form can slip into memory, and a low confidence sends the note to a person. It still needs the re-check, because a confident score can be wrong."
     data-no="Think about what the gate is allowed to return, and what happens to a note it is unsure about.">
  <p class="q">Why is a System One gate safer than letting the agent call <code>remember_note</code> with any text?</p>
  <label><input type="radio" name="ch32-q4" value="a"> It is always right, so notes never need re-checking</label>
  <label><input type="radio" name="ch32-q4" value="b"> It can only answer save, ask or skip, and low-confidence notes go to a person</label>
  <label><input type="radio" name="ch32-q4" value="c"> It writes longer, more careful notes</label>
  <div class="fb"></div>
</div>
```

## 3.3.6 Memory in real frameworks

Everything above is a Python dictionary in this browser tab, and it empties when you reload the page. Real agent frameworks keep memory in a database, and they draw the same line between short-term and long-term:

| | Short-term (this conversation) | Long-term (across conversations) |
|---|---|---|
| **OpenAI Agents SDK** | a **session**: `SQLiteSession("dana-monday", "memory.db")` stores every turn, and `await Runner.run(agent, question, session=session)` puts them back on the desk | nothing built in; you add it, for example as a `remember` tool that writes a file, read into the agent's instructions |
| **LangGraph** | a **checkpointer**: `InMemorySaver()` saves the conversation's state under a `thread_id`; call again with the same id and it continues | a **store**: `InMemoryStore()` holds notes in **namespaces** such as `("meridian", "notes")`, shared across every thread, with `put`, `get` and `search` |

The same Monday-and-next-Monday task, written in each:

```{raw} html
:file: widgets/ch03-sdk-tabs.html
```

In both frameworks the ideas are the ones from this page: a conversation is replayed from storage, notes are kept under a client's name, and a tool lets the agent write them. What the frameworks add is persistence, many users at once, and search over large numbers of notes. What they do not add is judgment about what to keep, or a check that a note is right. Those are still yours.

## 3.3.7 Run it against a real model

On the campus copy, these cells send the same memory to the GPT deployment on Illinois Azure through `/api/chat`. A real model decides for itself whether a note is worth using, and whether to call `remember_note` at all.

```{raw} html
<div class="wk-banner wk-pages-only">Model cells need the campus copy of this book: <a data-campus="/ch03-agent-memory.html#run-it-against-a-real-model" href="#">open it there</a> and sign in with your @illinois.edu account. Everything else on this page works here.</div>
```

First, recalled notes. Does the real model answer the follow-up from the notes, and does it use a table?

```{code-block} python
:class: pyodide
from agent import agent
from llm import azure_model
from memory import MEMORY, end_session, recall

MEMORY.clear()
monday = "Compare Deere's revenue growth with Caterpillar's last quarter"
memo, log = agent(monday, model=azure_model, verbose=False)
end_session("meridian", [("user", monday), ("assistant", memo),
                         ("user", "I prefer tables, and keep it under 150 words.")])
answer, log = agent("And NVIDIA?", model=azure_model, system=recall("meridian"))
```

Then the agent's own notes. Ask it to remember something, and read what it chose to write:

```{code-block} python
:class: pyodide
from agent import agent
from memory import MEMORY_TOOLS, azure_memory_model, show_notes

answer, log = agent("Dana says she only wants US-listed companies in future comparisons. Remember that.",
                    model=azure_memory_model, tools=MEMORY_TOOLS)
print()
show_notes("meridian")
```

Did it call `remember_note`? Is the note in your words or its own, and does it say where it came from?

## 3.3.8 Exercise

Open the Colab notebook. It runs the Monday and next-Monday task twice on `glm-5.3-flash` via Lumen, once with the OpenAI Agents SDK and once with LangGraph (see [Setup](setup.md) for the key).

1. In the OpenAI Agents SDK version, take the `remember` tool out of the agent's `tools=` list, delete `meridian_notes.json`, and run Monday's session, then next Monday's with its *new* `SQLiteSession` id. What does the agent remember, and why? Put the tool back and run both sessions again.
2. In the LangGraph version, look inside the store after Monday (`store.search(("meridian", "notes"))`). Change the `remember` tool so every note must include a source, and refuse to save one without it.
3. In three sentences: one thing you would let an agent remember about a client, one you would only let the harness save, and one you would never keep at all, with a reason for each.

## Further reading

- OpenAI, [*Sessions*](https://openai.github.io/openai-agents-python/sessions/) — short-term memory in the OpenAI Agents SDK, with the SQLite, Redis and SQLAlchemy stores.
- LangChain, [*Memory overview*](https://docs.langchain.com/oss/python/concepts/memory) — LangGraph's short-term (checkpointer) and long-term (store) memory, and the kinds of things worth remembering.
- LangChain, [*Long-term memory*](https://docs.langchain.com/oss/python/langchain/long-term-memory) — tools that read and write the store, as in this chapter's notebook.
- Charles Packer and others, [*MemGPT: Towards LLMs as Operating Systems*](https://arxiv.org/abs/2310.08560) (2023) — an agent that manages its own memory, moving facts between the desk and storage.
- Lilian Weng, [*LLM Powered Autonomous Agents*](https://lilianweng.github.io/posts/2023-06-23-agent/) (2023) — the memory section sets out short-term and long-term memory for agents.
