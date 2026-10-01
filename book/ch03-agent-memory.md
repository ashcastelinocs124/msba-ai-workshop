# 3.2 Short-Term Memory

```{raw} html
<p class="wk-lede">On Monday, Dana Whitfield at Meridian Pension Trust got the Deere and Caterpillar comparison and said she prefers tables. A model keeps nothing between calls, so even inside one long conversation the agent only remembers what the code puts back on the desk. Keep a long conversation going without letting it outgrow the desk, and see what trimming and summarizing each lose. The session 3 recording will be on <a href="ch03-memory-rag.html#ch03-lecture">the chapter 3 page</a>.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch03-agent-memory.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Explain why a model has no memory of its own, and what "memory" means for an agent.
- Keep a long conversation going by trimming or summarizing it, and say what each one loses.
- Say what short-term memory cannot do, and why the next page (long-term memory) is needed.
```

## 3.2.1 Why agents need memory

A model keeps nothing between calls. Every call starts with an empty desk, and the model reads only what is put on it: the system prompt, earlier turns, tool results, the question. What people call an agent's **memory** is whatever the code around the model puts back on the desk from before.

Chapter 2 did this once already, by hand: it passed the Monday exchange as `history`, and "And NVIDIA?" made sense. That only works if the history is still there. Next Monday it is a new session, and the desk is empty:

```{raw} html
:file: widgets/ch03-two-sessions.html
```

The same follow-up in code, with nothing carried over and then with Monday's exchange put back:

```{code-block} python
:class: pyodide
from agent import agent

monday = "Compare Deere's revenue growth with Caterpillar's last quarter"
memo, log = agent(monday, verbose=False)

print("Next Monday, nothing carried over:")
answer, log = agent("And NVIDIA?")

print("\nWith Monday's exchange on the desk:")
answer, log = agent("And NVIDIA?", history=[("user", monday), ("assistant", memo)])
```

There are two kinds of memory to build, and they solve different problems:

| | Short-term memory | Long-term memory |
|---|---|---|
| **Holds** | this conversation, turn by turn | facts worth keeping after it ends |
| **Lasts** | until the session ends | across sessions, weeks, months |
| **Problem** | the conversation outgrows the desk | deciding what to keep, and keeping it right |
| **At the firm** | today's back-and-forth with Dana | Dana prefers tables; last week's figures |

## 3.2.2 Short-term memory

Within one session, short-term memory is the conversation so far, and chapter 1's loop already carries it: every turn and every tool result goes back on the desk for the next call. The trouble starts when the conversation is long. Every turn costs tokens on every later call, and the desk is only so big (chapter 0's section 0.5). Something has to give, and there are two common choices:

- **Trim.** Drop the oldest turns and keep the last few. Cheap, and whatever was said early is simply gone.
- **Summarize.** Replace the older turns with a short summary, and keep the last few word for word. It costs a summary, and anything the summary leaves out is gone just as surely.

Add turns until the desk is full, then try each:

```{raw} html
:file: widgets/ch03-window-fill.html
```

The same choice in code. Monday's session has four turns; keep only the last two, first by trimming and then by summarizing:

```{code-block} python
:class: pyodide
from agent import agent
from memory import summarize

monday = "Compare Deere's revenue growth with Caterpillar's last quarter"
memo, log = agent(monday, verbose=False)
session = [("user", monday), ("assistant", memo),
           ("user", "I prefer tables, and keep it under 150 words."), ("assistant", "Understood.")]

print("Trimmed to the last two turns:")
answer, log = agent("And NVIDIA?", history=session[-2:])

print("\nSummarized, then the last two turns:")
for role, text in summarize(session, keep=2):
    print(f"  {role}: {text}")
answer, log = agent("And NVIDIA?", history=summarize(session, keep=2))
```

Trimming lost the comparison, so the follow-up made no sense. The summary kept the two figures in one sentence, and the follow-up worked. A summary is only as good as what it chose to keep: this one kept figures because it was written to. Real systems summarize with the model itself, which is cheaper than it sounds and fallible in the way you would expect.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. Trimming keeps the latest turns word for word and drops the earliest. Anything said only at the start, such as a preference stated in the first message, is gone."
     data-no="Trimming drops the oldest turns. When did Dana state her preference?">
  <p class="q">Dana said she prefers tables in her first message. Twenty turns later the agent trims the conversation to its last six turns. What happens to the preference?</p>
  <label><input type="radio" name="ch32-q1" value="a"> It is kept, because preferences are always saved</label>
  <label><input type="radio" name="ch32-q1" value="b"> It is dropped, along with everything else from the early turns</label>
  <label><input type="radio" name="ch32-q1" value="c"> It moves to long-term memory automatically</label>
  <div class="fb"></div>
</div>
```

## 3.2.3 What short-term memory cannot do

Everything on this page ends with the session. Trimming and summarizing keep a conversation going, but when Dana closes the window the conversation is gone, and next Monday the desk is empty again. To carry anything across sessions the system has to save it somewhere and put it back, which is long-term memory. [Section 3.3](ch03-long-term-memory.md) builds that: who writes the notes, what kinds there are, and how to stop a wrong note being repeated with confidence.
