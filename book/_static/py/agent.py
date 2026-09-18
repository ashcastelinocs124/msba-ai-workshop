"""The transparent agent loop from chapter 1. Every step is printed so a reviewer can audit the run.

Everything printed here is written in plain English on purpose: this book is for people who are
not going to read code, so a tool call reads as "looked up ... " rather than as a JSON object.
"""
import time

from mock_model import model as _mock_model
from tools import TOOLS

# "get_x" -> looks up / looked up x. "search_x" -> searches / searched x. Add a verb pair here
# if a future chapter's tools use a different prefix; anything unlisted falls back to its own name.
_VERBS = {"get": ("look up", "looked up"), "search": ("search", "searched")}


def _fmt_value(v):
    """A number formatted the way a person would say it, not the way Python prints it."""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if not isinstance(v, (int, float)):
        return v
    if isinstance(v, float) and 0 <= v < 1:
        return f"{v:.1%}"
    if isinstance(v, (int, float)) and abs(v) >= 1000:
        return f"{v:,.0f}"
    return v


def _describe_call(name, args, past=True):
    """A tool call in plain English: 'looked up financials (DE, Q2-2026)', not a JSON blob."""
    verb, _, rest = name.partition("_")
    subject = rest.replace("_", " ") or name
    base, done = _VERBS.get(verb, (name, name))
    action = done if past else base
    detail = ", ".join(str(_fmt_value(v)) for v in args.values())
    return f"{action} {subject}" + (f" ({detail})" if detail else "")


def _describe_result(result):
    """What a tool handed back, in a sentence instead of a dict or a list."""
    if isinstance(result, dict) and "error" in result:
        return f"nothing found — {result['error']}"
    if isinstance(result, list):
        n = len(result)
        if n == 0:
            return "no matches"
        # Name the matched handbook sections so the reader (and the Watch view) can see which.
        ids = ", ".join(str(m["id"]) for m in result if isinstance(m, dict) and "id" in m)
        return f"{n} match{'es' if n != 1 else ''} found" + (f" ({ids})" if ids else "")
    if isinstance(result, dict):
        # "field: value" pairs — the Watch view splits on this to draw the record.
        return ", ".join(f"{k.replace('_', ' ')}: {_fmt_value(v)}" for k, v in result.items())
    return str(result)


def explain_reply(reply):
    """One plain-English line describing a raw model reply, before any tool has run."""
    if reply["type"] == "text":
        return f"answered directly: {reply['text']}"
    return f"wants to {_describe_call(reply['tool'], reply['args'], past=False)}"


def narrate(log):
    """Turn a run's log into plain-English sentences, one per step — the audit trail a
    non-technical reviewer can actually read."""
    lines = []
    for i, e in enumerate(log, 1):
        if e["kind"] == "tool_call":
            lines.append(f"Step {i}: {_describe_call(e['tool'], e['args'])} → {_describe_result(e['result'])}")
        elif e["kind"] == "text":
            lines.append(f"Step {i}: answered — {e['text']}")
        else:
            lines.append(f"Step {i}: stopped — the step budget ran out")
    return lines


def agent(question, tools=TOOLS, model=_mock_model, max_steps=6, verbose=True):
    """Run a tool-using loop until the model answers in text or the step budget runs out.

    Returns (answer, log). The log is a list of dicts, one per step, so it can be
    inspected, tested, or written to disk.
    """
    msgs = [{"role": "user", "content": question}]
    log = []
    for step in range(max_steps):
        reply = model(msgs)
        if reply["type"] == "text":
            log.append({"step": step, "kind": "text", "text": reply["text"]})
            if verbose:
                print(f"Step {step + 1}: answered — {reply['text']}")
            return reply["text"], log

        name, args = reply["tool"], reply["args"]
        t0 = time.time()
        try:
            result = tools[name](**args)
        except Exception as e:  # a bad tool call is data, not a crash
            result = {"error": f"{type(e).__name__}: {e}"}
        ms = (time.time() - t0) * 1000
        log.append({"step": step, "kind": "tool_call", "tool": name, "args": args, "result": result, "ms": round(ms, 2)})
        if verbose:
            print(f"Step {step + 1}: {_describe_call(name, args)} → {_describe_result(result)}")
        msgs.append({"role": "assistant", "content": f"[{_describe_call(name, args)}]", "tool_call": {"name": name, "args": args}})
        msgs.append({"role": "tool", "name": name, "content": result})

    log.append({"step": max_steps, "kind": "budget_exhausted"})
    return "Stopped: step budget exhausted.", log


if __name__ == "__main__":
    # ponytail: self-check; run `python agent.py` from _static/py
    ans, log = agent("What was Deere's revenue growth last quarter?", verbose=False)
    assert "6.4%" in ans, ans
    assert log[0]["kind"] == "tool_call" and log[0]["tool"] == "get_financials"
    ans, log = agent("Compare Deere's revenue growth with Caterpillar's last quarter", verbose=False)
    assert "6.4%" in ans and "3.1%" in ans and "[source:" in ans, ans
    assert [e.get("tool") for e in log[:2]] == ["get_financials", "get_financials"] and log[2]["kind"] == "text", log
    ans, log = agent("Compare Deere with Tesla", verbose=False)
    assert "no data for TSLA" in ans and len(log) == 3, (ans, log)
    ans, _ = agent("What does the handbook say about the blackout window?", verbose=False)
    assert "[source: personal-trading" in ans, ans
    for rid, expect in [("7101", "APPROVE"), ("7102", "DECLINE"), ("7103", "DECLINE"), ("7104", "HOLD")]:
        ans, log = agent(f"Can compliance clear trade request #{rid}?", verbose=False)
        assert expect in ans, (rid, ans)
        assert [e.get("tool") for e in log[:2]] == ["get_trade_request", "search_docs"], log
    print("ok")
