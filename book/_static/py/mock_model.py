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

    order = re.search(r"#\s?(\d{4})", q)
    if order and ("refund" in q or "return" in q):
        if not seen:
            return {"type": "tool_call", "tool": "get_order", "args": {"order_id": order.group(1)}}
        if len(seen) == 1:
            return {"type": "tool_call", "tool": "search_docs", "args": {"query": "refund days receipt store credit"}}
        o = seen[0]["content"]
        if "error" in o:
            return {"type": "text", "text": f"I could not find order #{order.group(1)}. Ask the customer to confirm the order number."}
        who = f"{o['customer']} (order #{o['order_id']}, {o['item']}, ${o['amount']:.2f}, {o['days_since_purchase']} days ago)"
        if not o["receipt"]:
            return {"type": "text", "text": f"RECOMMEND: HOLD. {who}: no receipt on file, and a receipt is required for any refund. Ask for proof of purchase before deciding. [source: refund-policy-1]"}
        if o["used"]:
            return {"type": "text", "text": f"RECOMMEND: DECLINE full refund. {who}: the item has been used; the 14-day refund covers unused items only. Offer an exchange or store credit at manager discretion. [source: refund-policy-1] [source: refund-policy-2]"}
        if o["days_since_purchase"] <= 14:
            return {"type": "text", "text": f"RECOMMEND: APPROVE full refund of ${o['amount']:.2f}. {who}: within 14 days, unused, receipt on file. [source: refund-policy-1]"}
        return {"type": "text", "text": f"RECOMMEND: STORE CREDIT of ${o['amount']:.2f}, not cash. {who}: past the 14-day window, so a refund is store credit only and needs manager sign-off. [source: refund-policy-2]"}

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

    if "policy" in q or "doc" in q or "refund" in q or "search" in q:
        if not seen:
            words = [w for w in re.findall(r"[a-z]+", q) if len(w) > 3][:3]
            return {"type": "tool_call", "tool": "search_docs", "args": {"query": " ".join(words)}}
        hits = seen[-1]["content"]
        if not hits:
            return {"type": "text", "text": "I couldn't find that in the documents."}
        top = hits[0]
        return {"type": "text", "text": f"{top['text']} [source: {top['id']}]"}

    return {"type": "text", "text": "I can answer questions about revenue, prices, or company policy documents."}
