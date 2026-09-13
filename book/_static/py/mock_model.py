"""A deterministic stand-in for an LLM so chapters run in the browser with no API key.

It looks at the last user question and the tool results seen so far, and returns
either a tool call or a final text answer, in the same shape the real loop expects:
  {"type": "tool_call", "tool": name, "args": {...}}   or   {"type": "text", "text": "..."}
Colab notebooks swap this for the real Anthropic API.
"""
import re


def _last_user(msgs):
    for m in reversed(msgs):
        if m["role"] == "user":
            return m["content"].lower()
    return ""


def _tool_results(msgs):
    return [m for m in msgs if m["role"] == "tool"]


def _ticker(text):
    m = re.search(r"\b(DE|AAPL|MSFT|NVDA|CAT)\b", text.upper())
    return m.group(1) if m else "DE"


def model(msgs, tools=None):
    """Return the mock model's reply for the current message list."""
    q = _last_user(msgs)
    seen = _tool_results(msgs)
    t = _ticker(q)

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

    if "revenue" in q or "growth" in q or "financial" in q:
        if not seen:
            return {"type": "tool_call", "tool": "get_financials", "args": {"ticker": t, "period": "Q2-2026"}}
        r = seen[-1]["content"]
        return {"type": "text", "text": f"{r['name']} revenue grew {r['yoy']*100:.1f}% YoY to ${r['revenue']/1e9:.1f}B in {r['period']}."}

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

    return {"type": "text", "text": "I can answer questions about revenue, prices, trade pre-clearance requests, or the firm policy handbook."}
