"""The transparent agent loop from chapter 1. Every step is printed so a reviewer can audit the run."""
import json
import time

from mock_model import model as _mock_model
from tools import TOOLS


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
                print(f"step {step}: text -> {reply['text']}")
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
            print(f"step {step}: tool_call {name}({json.dumps(args)}) -> {json.dumps(result)[:120]}")
        msgs.append({"role": "assistant", "content": f"<tool_call>{name}({json.dumps(args)})", "tool_call": {"name": name, "args": args}})
        msgs.append({"role": "tool", "name": name, "content": result})

    log.append({"step": max_steps, "kind": "budget_exhausted"})
    return "Stopped: step budget exhausted.", log


if __name__ == "__main__":
    # ponytail: self-check; run `python agent.py` from _static/py
    ans, log = agent("What was Deere's revenue growth last quarter?", verbose=False)
    assert "6.4%" in ans, ans
    assert log[0]["kind"] == "tool_call" and log[0]["tool"] == "get_financials"
    ans, _ = agent("What does the handbook say about the blackout window?", verbose=False)
    assert "[source: personal-trading" in ans, ans
    for rid, expect in [("7101", "APPROVE"), ("7102", "DECLINE"), ("7103", "DECLINE"), ("7104", "HOLD")]:
        ans, log = agent(f"Can compliance clear trade request #{rid}?", verbose=False)
        assert expect in ans, (rid, ans)
        assert [e.get("tool") for e in log[:2]] == ["get_trade_request", "search_docs"], log
    print("ok")
