"""Agent memory (section 3.2): what the desk gets back from earlier conversations.

A model call starts blank every time. "Memory" is whatever the code around the model puts back
on the desk: a summary of the conversation so far (short-term), or notes saved after a session
and recalled in the next one (long-term). Two ways to write those notes:

- end_session: the harness writes them after the session, from the transcript. The agent only reads.
- remember_note: a tool the agent calls itself, to save what it thinks matters.

ponytail: MEMORY is a dict in this browser tab, so it empties when the page reloads. Real systems
keep it in a database or a file (section 3.2.7), keyed by client or user.
"""
import re

from tools import TOOLS, TOOL_SCHEMAS, FINANCIALS
from context import CLIENTS

MEMORY = {}

_FIG = re.compile(r"[A-Z][A-Za-z]+ grew revenue [\d.]+% YoY to \$[\d.]+B")
_PREF = re.compile(r"\b(prefer|keep it under|always|never)\b", re.I)


def _notes(client):
    return MEMORY.setdefault(client, [])


def remember_note(note: str, client: str = "meridian") -> dict:
    """The agent's own memory tool: save one note about a client for next time. Writes only to the
    agent's notebook, never to a firm record (handbook clause records-3)."""
    _notes(client).append({"text": note, "source": "the agent's own summary", "by": "agent"})
    return {"saved": note}


# The chapter 1 tools plus remember_note. The default TOOLS stay read-only; a caller opts in to this.
MEMORY_TOOLS = {**TOOLS, "remember_note": remember_note}
MEMORY_TOOL_SCHEMAS = TOOL_SCHEMAS + [
    {"name": "remember_note",
     "description": "Save one short note about a client for future sessions: a preference, or a figure with its source. Only for things worth knowing next time.",
     "input_schema": {"type": "object",
                      "properties": {"note": {"type": "string", "minLength": 4}, "client": {"type": "string", "enum": ["meridian"]}},
                      "required": ["note"], "additionalProperties": False}},
]


def azure_memory_model(msgs):
    """The campus copy's real model (llm.azure_model), shown the remember_note tool as well (section 3.2.8)."""
    from llm import azure_model
    return azure_model(msgs, tools=MEMORY_TOOL_SCHEMAS)


def end_session(client, history, verbose=True):
    """The harness remembers: after a session, save each figure the memo stated and each preference
    the client gave, with where it came from. The agent never writes these."""
    saved = []
    for role, text in history:
        if role == "assistant":
            saved += [{"text": f, "source": "get_financials, Q2-2026", "by": "harness"} for f in _FIG.findall(text)]
        elif role == "user" and _PREF.search(text):
            saved.append({"text": f"Preference, in the client's words: {text.strip()}", "source": "the client, in session", "by": "harness"})
    _notes(client).extend(saved)
    if verbose:
        for n in saved:
            print(f"Saved: {n['text']}  [{n['source']}]")
    return saved


def recall(client):
    """The notes about a client, as a block for the system prompt of the next session. Empty if none."""
    notes = MEMORY.get(client) or []
    if not notes:
        return ""
    name = CLIENTS.get(client, {}).get("name", client)
    return f"What we remember about {name}:\n" + "\n".join(f"- {n['text']} [{n['source']}]" for n in notes)


def summarize(history, keep=2):
    """Short-term memory when the desk is full: keep the last `keep` turns word for word, and replace
    everything before them with one summary turn. What the summary leaves out is gone."""
    old, recent = history[:-keep], history[-keep:]
    if not old:
        return list(history)
    points = [t.split(". ")[0].rstrip(".") + "." for r, t in old if r == "assistant"]
    points += [f"The client said: {t.strip()}" for r, t in old if r == "user" and _PREF.search(t)]
    return [("assistant", "Summary of the earlier conversation: " + " ".join(points))] + list(recent)


def _wrong(n):
    """The figures in one note that disagree with the firm's data, as (company, noted %, actual %)."""
    out = []
    for name, yoy, _rev in re.findall(r"(\w+) grew revenue ([\d.]+)% YoY to \$([\d.]+)B", n["text"]):
        row = next((r for r in FINANCIALS.values() if r["name"] == name), None)
        if row and abs(row["yoy"] * 100 - float(yoy)) > 0.05:
            out.append((name, yoy, row["yoy"] * 100))
    return out


def check_notes(client):
    """Re-check every figure in a client's notes against the firm's data (handbook clause records-5).
    Returns one plain sentence per note that disagrees."""
    return [f"Note {i} says {name} grew revenue {yoy}%, but the firm's data says {actual:.1f}%. "
            f"It was written by {'the agent' if n['by'] == 'agent' else 'the harness'} ({n['source']})."
            for i, n in enumerate(MEMORY.get(client) or [], 1) for name, yoy, actual in _wrong(n)]


def forget(client, number):
    """Delete one note, by the number show_notes printed: what a person does when a note is wrong (records-4)."""
    notes = MEMORY.get(client) or []
    if not 1 <= number <= len(notes):
        print(f"There is no note {number} about {client}; nothing was deleted.")
        return
    print(f"Deleted note {number}: {notes.pop(number - 1)['text']}")


def forget_wrong(client):
    """Delete every note whose figures fail check_notes, and only those. Returns how many were deleted."""
    notes = MEMORY.get(client) or []
    bad = [n for n in notes if _wrong(n)]
    for n in bad:
        notes.remove(n)
        print(f"Deleted: {n['text']}")
    if not bad:
        print(f"No notes about {client} disagree with the firm's data; nothing was deleted.")
    return len(bad)


_WANTS = re.compile(r"\b(wants?|prefers?|keep it under|always|never)\b", re.I)
_CHAT = re.compile(r"\b(thanks|thank you|that's all|bye|got it)\b", re.I)


def gate(text, source=""):
    """A scripted stand-in for a System One model (section 3.2.6): it cannot write text, only fill in
    a fixed form {decision: save | ask | skip, kind, confidence}. A real one, such as TypeSafe AI's
    Jev, would compute the confidence; here the numbers are hand-set so the cell always prints the same."""
    if _CHAT.search(text):
        return {"decision": "skip", "kind": "small talk", "confidence": 0.93, "text": text}
    if _FIG.search(text):
        if _wrong({"text": text}):                       # disagrees with the firm's data (records-5)
            return {"decision": "ask", "kind": "figure", "confidence": 0.58, "text": text}
        sourced = "get_financials" in source
        return {"decision": "save" if sourced else "ask", "kind": "figure",
                "confidence": 0.91 if sourced else 0.62, "text": text}
    if _WANTS.search(text):
        return {"decision": "save", "kind": "preference", "confidence": 0.97, "text": text}
    return {"decision": "ask", "kind": "other", "confidence": 0.40, "text": text}


def gated_save(text, source="", client="meridian", bar=0.80):
    """Save a note only if the gate says save at or above the bar; otherwise say who has to look at it."""
    g = gate(text, source)
    print(f"{g['decision']:<5} {g['confidence']:.2f}  {g['kind']:<11} \"{text}\"")
    if g["decision"] == "save" and g["confidence"] >= bar:
        _notes(client).append({"text": text, "source": source or "the gate", "by": "harness"})
    return g


def show_notes(client):
    """Print a client's notes, numbered, with who wrote each one and where it came from."""
    notes = MEMORY.get(client) or []
    if not notes:
        print(f"No notes about {client}.")
    for i, n in enumerate(notes, 1):
        print(f"{i}. {n['text']}\n   written by {'the agent' if n['by'] == 'agent' else 'the harness'}, from {n['source']}")


if __name__ == "__main__":
    # ponytail: self-check; run `python memory.py` from _static/py
    from agent import agent
    MEMORY.clear()
    q1 = "Compare Deere's revenue growth with Caterpillar's last quarter"
    memo, _ = agent(q1, verbose=False)
    hist = [("user", q1), ("assistant", memo), ("user", "I prefer tables, and keep it under 150 words."), ("assistant", "Understood.")]
    notes = end_session("meridian", hist)
    assert any("6.4%" in n["text"] for n in notes) and any("tables" in n["text"] for n in notes), notes
    ans, log = agent("And NVIDIA?", system=recall("meridian"), verbose=False)
    assert "58.0%" in ans and "6.4%" in ans and "company" in ans, ans
    assert len(summarize(hist, keep=2)) == 3
    ans, _ = agent("And NVIDIA?", history=summarize(hist, keep=2), verbose=False)     # the summary kept the figures
    assert "58.0%" in ans and "6.4%" in ans, ans
    ans, _ = agent("And NVIDIA?", history=hist[-2:], verbose=False)                   # trimming dropped them
    assert ans.startswith("NVIDIA what?"), ans
    MEMORY.clear()
    ans, log = agent("Remember these figures for next week.", tools=MEMORY_TOOLS, history=hist[:2], verbose=False)
    assert log[0]["tool"] == "remember_note" and "64.0%" in MEMORY["meridian"][0]["text"], MEMORY
    assert check_notes("meridian") and "6.4%" in check_notes("meridian")[0]
    ans, _ = agent("And NVIDIA?", system=recall("meridian"), verbose=False)
    assert "64.0%" in ans, ans
    show_notes("meridian")
    remember_note("Dana wants tables")                                           # a good note that must survive
    assert forget_wrong("meridian") == 1 and [n["text"] for n in MEMORY["meridian"]] == ["Dana wants tables"]
    assert forget_wrong("meridian") == 0                                         # running it twice is harmless
    forget("meridian", 5)                                                        # no such note: a sentence, not a crash
    forget("nobody", 1)
    forget("meridian", 1)                                                        # the number show_notes printed
    assert MEMORY["meridian"] == []
    ans, log = agent("Remember that Dana wants tables.", history=hist[:2], verbose=False)
    assert "error" in log[0]["result"], log
    assert [t["name"] for t in MEMORY_TOOL_SCHEMAS][-1] == "remember_note" and callable(azure_memory_model)
    MEMORY.clear()                                                               # the typed gate (section 3.2.6)
    assert gate("Dana wants tables, under 150 words")["decision"] == "save"
    assert gate("Deere grew revenue 64.0% YoY to $12.0B", "the agent's summary")["decision"] == "ask"
    assert gate("Deere grew revenue 6.4% YoY to $13.8B", "get_financials, Q2-2026")["decision"] == "save"
    assert gate("Thanks, that's all for today")["decision"] == "skip"
    gated_save("Deere grew revenue 64.0% YoY to $12.0B", "the agent's summary")
    assert not MEMORY.get("meridian")                                            # the wrong figure was not saved
    print("ok")
