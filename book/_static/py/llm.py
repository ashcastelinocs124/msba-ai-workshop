"""A real model for the agent loop, reached through this site's /api/chat proxy.

    from agent import agent
    from llm import azure_model
    answer, log = agent("…", model=azure_model)

The browser never holds a key: the proxy on the campus (Azure) copy of the book adds it.
On a copy with no proxy (GitHub Pages) every call raises LLMUnavailable with the campus URL.
"""
import json

from tools import TOOL_SCHEMAS

SYSTEM = ("You are a research and compliance assistant at Champaign Capital Research, an equity research firm. "
          "Use the tools to look up facts before answering. For trade pre-clearance requests: look up the request, "
          "then the personal-trading policy, then give ONE recommendation in the form "
          "'RECOMMEND: <APPROVE|HOLD|DECLINE>. <reason>' and cite policy chunk ids like [source: personal-trading-2]. "
          "You cannot clear trades; a compliance officer approves.")


class LLMUnavailable(Exception):
    pass


def _campus_url():
    try:
        from js import window
        return str(window.WK_CAMPUS_URL)
    except Exception:
        return "the campus copy of this book"


def _post(path, body):
    """Synchronous POST from Pyodide (sync XHR keeps agent() a plain loop)."""
    from js import XMLHttpRequest
    xhr = XMLHttpRequest.new()
    xhr.open("POST", path, False)
    xhr.setRequestHeader("Content-Type", "application/json")
    xhr.send(json.dumps(body))
    status = int(xhr.status)
    if status in (404, 405):  # no proxy on this copy (GitHub Pages answers 405 to POST)
        raise LLMUnavailable(f"this copy of the book has no {path}. Open the campus site to run model cells:\n{_campus_url()}")
    if status in (401, 403):
        raise LLMUnavailable("sign in with your @illinois.edu account, then run the cell again.")
    if status == 429:
        raise LLMUnavailable("daily token budget used up; it resets at midnight.")
    if status != 200:
        raise LLMUnavailable(f"proxy returned {status}: {xhr.responseText[:200]}")
    return json.loads(xhr.responseText)


def _openai_messages(msgs, system):
    # A system message the caller put in msgs (chapter 2's agent(system=…)) wins over the default.
    given = [m["content"] for m in msgs if m["role"] == "system"]
    out = [{"role": "system", "content": given[0] if given else system}]
    i = 0
    for m in msgs:
        if m["role"] == "user":
            out.append({"role": "user", "content": m["content"]})
        elif m["role"] == "assistant" and "tool_call" not in m:
            out.append({"role": "assistant", "content": m["content"]})   # an earlier turn from history
        elif m["role"] == "assistant" and "tool_call" in m:
            i += 1
            tc = m["tool_call"]
            out.append({"role": "assistant", "content": None,
                        "tool_calls": [{"id": f"call_{i}", "type": "function",
                                        "function": {"name": tc["name"], "arguments": json.dumps(tc["args"])}}]})
        elif m["role"] == "tool":
            out.append({"role": "tool", "tool_call_id": f"call_{i}", "content": json.dumps(m["content"])})
    return out


def _openai_tools(schemas):
    return [{"type": "function", "function": {"name": s["name"], "description": s["description"], "parameters": s["input_schema"]}}
            for s in schemas]


def azure_model(msgs, tools=None, system=SYSTEM, verbose=True):
    """Drop-in replacement for mock_model.model: same input, same {type: tool_call|text} output."""
    data = _post("/api/chat", {"messages": _openai_messages(msgs, system),
                               "tools": _openai_tools(tools or TOOL_SCHEMAS)})
    msg = data["choices"][0]["message"]
    u = data.get("usage") or {}
    if verbose:
        print(f"   ── {u.get('prompt_tokens', '?')} prompt + {u.get('completion_tokens', '?')} completion tokens · {data.get('model', '')}")
    calls = msg.get("tool_calls") or []
    if calls:
        fn = calls[0]["function"]
        return {"type": "tool_call", "tool": fn["name"], "args": json.loads(fn["arguments"] or "{}")}
    return {"type": "text", "text": (msg.get("content") or "").strip()}


if __name__ == "__main__":
    # ponytail: self-check of the format conversion only (no network)
    msgs = [{"role": "user", "content": "refund on order #4488?"},
            {"role": "assistant", "content": "<tool_call>get_order({...})", "tool_call": {"name": "get_order", "args": {"order_id": "4488"}}},
            {"role": "tool", "name": "get_order", "content": {"order_id": "4488"}}]
    om = _openai_messages(msgs, "sys")
    assert om[0]["role"] == "system" and om[2]["tool_calls"][0]["id"] == "call_1" and om[3]["tool_call_id"] == "call_1", om
    assert _openai_tools(TOOL_SCHEMAS)[0]["function"]["name"] == "get_financials"
    print("ok")
