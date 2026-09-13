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
        msgs.append({"role": "assistant", "content": f"<tool_call>{name}({json.dumps(args)})"})
        msgs.append({"role": "tool", "name": name, "content": result})

    log.append({"step": max_steps, "kind": "budget_exhausted"})
    return "Stopped: step budget exhausted.", log


if __name__ == "__main__":
    # ponytail: self-check; run `python agent.py` from _static/py
    ans, log = agent("What was Deere's revenue growth last quarter?", verbose=False)
    assert "6.4%" in ans, ans
    assert log[0]["kind"] == "tool_call" and log[0]["tool"] == "get_financials"
    ans, _ = agent("What is the refund policy?", verbose=False)
    assert "[source: refund-policy" in ans, ans
    for oid, expect in [("4471", "APPROVE"), ("4488", "STORE CREDIT"), ("4502", "HOLD"), ("4519", "DECLINE")]:
        ans, log = agent(f"Customer is asking for a refund on order #{oid}. What should we do?", verbose=False)
        assert expect in ans, (oid, ans)
        assert [e.get("tool") for e in log[:2]] == ["get_order", "search_docs"], log
    print("ok")
