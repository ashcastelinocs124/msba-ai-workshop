"""A deterministic stand-in for an LLM so chapters run in the browser with no API key.

It looks at the last user question and the tool results seen so far, and returns
either a tool call or a final text answer, in the same shape the real loop expects:
  {"type": "tool_call", "tool": name, "args": {...}}   or   {"type": "text", "text": "..."}
Colab notebooks swap this for a real model on Lumen (glm-5.3-flash).
"""
import re


def _last_user(msgs):
    for m in reversed(msgs):
        if m["role"] == "user":
            return m["content"].lower()
    return ""


def _tool_results(msgs):
    return [m for m in msgs if m["role"] == "tool"]


# Company names and symbols the mock recognises. Tesla is on purpose: the firm has no data for it,
# so asking about it exercises the tool's error path (chapter 1, §1.9).
_NAMES = {"deere": "DE", "caterpillar": "CAT", "nvidia": "NVDA", "apple": "AAPL", "microsoft": "MSFT", "tesla": "TSLA"}


def _tickers(text):
    """Every company the question names, in the order named; defaults to Deere."""
    found = []
    for m in re.finditer(r"\b(deere|caterpillar|nvidia|apple|microsoft|tesla|de|cat|nvda|aapl|msft|tsla)\b", text.lower()):
        t = _NAMES.get(m.group(1), m.group(1).upper())
        if t not in found:
            found.append(t)
    return found or ["DE"]


def _compare(rows):
    """The client memo: both figures, the gap, and a source tag (the handbook requires one)."""
    missing = [r["error"].split("for ", 1)[-1] for r in rows if "error" in r]
    if missing:
        have = [f"{r['name']} ({r['yoy']*100:.1f}% YoY to ${r['revenue']/1e9:.1f}B)" for r in rows if "error" not in r]
        return (f"I can't complete this comparison: the firm holds no data for {', '.join(missing)}. "
                f"I have {', '.join(have) if have else 'nothing'} but no basis for a comparison. "
                "Ask the data team to add the missing name before I draft the memo.")
    figs = "; ".join(f"{r['name']} grew revenue {r['yoy']*100:.1f}% YoY to ${r['revenue']/1e9:.1f}B" for r in rows)
    fast = max(rows, key=lambda r: r["yoy"]); big = max(rows, key=lambda r: r["revenue"])
    slow = min(rows, key=lambda r: r["yoy"])
    ratio = fast["yoy"] / slow["yoy"] if slow["yoy"] > 0 else float("inf")
    if fast is big:
        verdict = f"{fast['name']} is growing {ratio:.1f}× as fast and is also the larger company."
    else:
        verdict = f"{fast['name']} is growing {ratio:.1f}× as fast, from a smaller base; {big['name']} is the larger company."
    return f"{figs} in {rows[0]['period']}. {verdict} [source: {rows[0]['period']} filings via get_financials]"


def model(msgs, tools=None):
    """Return the mock model's reply for the current message list."""
    q = _last_user(msgs)
    seen = _tool_results(msgs)
    tickers = _tickers(q)
    t = tickers[0]

    req = re.search(r"#\s?(\d{4})", q)
    if req and ("trade" in q or "clear" in q or "sell" in q or "buy" in q or "request" in q):
        if not seen:
            return {"type": "tool_call", "tool": "get_trade_request", "args": {"request_id": req.group(1)}}
        if len(seen) == 1:
            return {"type": "tool_call", "tool": "search_docs", "args": {"query": "trade pre-clearance blackout restricted holding period"}}
        r = seen[0]["content"]
        if "error" in r:
            return {"type": "text", "text": f"I could not find request #{req.group(1)}. Ask the employee to confirm the request number."}
        who = f"{r['employee']} ({r['role']}) asks to {r['side']} {r['shares']} {r['ticker']}, request #{r['request_id']}"
        if r["restricted"]:
            return {"type": "text", "text": f"RECOMMEND: DECLINE. {who}: {r['ticker']} is on the restricted list, so no employee may trade it. [source: restricted-list-1]"}
        if r["days_since_firm_research"] <= 14:
            return {"type": "text", "text": f"RECOMMEND: HOLD. {who}: the firm published on {r['ticker']} {r['days_since_firm_research']} days ago, inside the 14-day blackout window. Re-submit after day 14. [source: personal-trading-2]"}
        if r["side"] == "sell" and r["holding_days"] is not None and r["holding_days"] < 30:
            return {"type": "text", "text": f"RECOMMEND: DECLINE. {who}: the position has been held {r['holding_days']} days, under the 30-day minimum. [source: personal-trading-3]"}
        return {"type": "text", "text": f"RECOMMEND: APPROVE. {who}: not restricted, outside the blackout window, holding period satisfied. Pre-clearance is required and is granted by compliance, not by this assistant. [source: personal-trading-1]"}

    if "revenue" in q or "growth" in q or "financial" in q or "compar" in q or "grew" in q:
        # One lookup per company named, in order; then the answer. Two or more names → the client memo.
        if len(seen) < len(tickers):
            return {"type": "tool_call", "tool": "get_financials", "args": {"ticker": tickers[len(seen)], "period": "Q2-2026"}}
        rows = [m["content"] for m in seen]
        if len(rows) == 1:
            r = rows[0]
            if "error" in r:
                return {"type": "text", "text": f"The firm holds no data for {r['error'].split('for ', 1)[-1]}."}
            return {"type": "text", "text": f"{r['name']} revenue grew {r['yoy']*100:.1f}% YoY to ${r['revenue']/1e9:.1f}B in {r['period']}."}
        return {"type": "text", "text": _compare(rows)}

    if "price" in q:
        if not seen:
            return {"type": "tool_call", "tool": "get_price", "args": {"ticker": t}}
        r = seen[-1]["content"]
        return {"type": "text", "text": f"{r['ticker']} last traded at ${r['price']:.2f}."}

    if "policy" in q or "doc" in q or "handbook" in q or "search" in q or "blackout" in q or "expense" in q:
        if not seen:
            stop = {"what", "does", "about", "this", "that", "have", "with", "from", "says", "handbook", "policy", "search", "docs", "document", "documents"}
            words = [w for w in re.findall(r"[a-z]+", q) if len(w) > 3 and w not in stop][:4]
            return {"type": "tool_call", "tool": "search_docs", "args": {"query": " ".join(words)}}
        hits = seen[-1]["content"]
        if not hits:
            return {"type": "text", "text": "I couldn't find that in the documents."}
        top = hits[0]
        return {"type": "text", "text": f"{top['text']} [source: {top['id']}]"}

    return {"type": "text", "text": "I can answer questions about revenue and growth (one company or a comparison), prices, trade pre-clearance requests, or the firm policy handbook."}
