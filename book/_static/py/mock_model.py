"""A deterministic stand-in for an LLM so chapters run in the browser with no API key.

It looks at the last user question, the tool results seen so far, and (since chapter 2) the
system prompt and any earlier turns, and returns either a tool call or a final text answer, in
the same shape the real loop expects:
  {"type": "tool_call", "tool": name, "args": {...}}   or   {"type": "text", "text": "..."}
Colab notebooks swap this for a real model on Lumen (glm-5.3-flash).

What the mock honours in a system prompt (chapter 2, §2.3): a role (adds a draft header), a rule
against investment recommendations, a table format, few-shot memo examples (copies their header
and sign-off), a client card that "prefers tables", a retrieved data-licensing clause, and a
planning instruction. The planning branch is scripted: on a "fastest" question naming three or more
companies, the mock without a plan stops one lookup short, every time. A real model does this only
sometimes, and §2.5 measures it. The mock does not imitate long-prompt attention decay.
"""
import re


def _last_user(msgs):
    for m in reversed(msgs):
        if m["role"] == "user":
            return m["content"].lower()
    return ""


def _earlier_turns(msgs):
    """User/assistant messages before the current question: the history the caller put on the desk."""
    last = max(i for i, m in enumerate(msgs) if m["role"] == "user")
    return [m for m in msgs[:last] if m["role"] in ("user", "assistant") and "tool_call" not in m]


def _tool_results(msgs):
    return [m for m in msgs if m["role"] == "tool"]


def _style(msgs):
    """Which instructions are on the desk. Each flag is one thing a prompt block changes in the answer."""
    s = " ".join(m["content"] for m in msgs if m["role"] == "system").lower()
    return {
        "role": "champaign capital" in s,
        "no_reco": "investment recommendation" in s,
        "table": "as a table" in s or "prefers tables" in s,
        "fewshot": "memo ·" in s,
        "no_raw": "may not be redistributed" in s,
        "plan": "before calling any tool" in s,
    }


# Company names and symbols the mock recognises. Tesla is on purpose: the firm has no data for it,
# so asking about it exercises the tool's error path (chapter 1, §1.9).
_NAMES = {"deere": "DE", "caterpillar": "CAT", "nvidia": "NVDA", "apple": "AAPL", "microsoft": "MSFT", "tesla": "TSLA"}
_DISPLAY = {"DE": "Deere", "CAT": "Caterpillar", "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", "TSLA": "Tesla"}
_TOPIC = ("revenue", "growth", "financial", "compar", "grew", " vs", "versus", "doing", "against")


def _tickers(text):
    """Every company the text names, in the order named."""
    found = []
    for m in re.finditer(r"\b(deere|caterpillar|nvidia|apple|microsoft|tesla|de|cat|nvda|aapl|msft|tsla)\b", text.lower()):
        t = _NAMES.get(m.group(1), m.group(1).upper())
        if t not in found:
            found.append(t)
    return found


def _figures_in(text):
    """Figures an earlier memo already stated, so a follow-up need not look them up again."""
    rows = []
    for name, yoy, rev in re.findall(r"(\w+) grew revenue ([\d.]+)% YoY to \$([\d.]+)B", text):
        rows.append({"name": name, "yoy": float(yoy) / 100, "revenue": float(rev) * 1e9, "period": "Q2-2026"})
    return rows


def _table(rows):
    lines = ["company      revenue   YoY growth   source"]
    for r in rows:
        lines.append(f"{r['name']:<12} ${r['revenue']/1e9:.1f}B    {r['yoy']*100:.1f}%         {r['period']} filing")
    return "\n".join(lines)


def _compare(rows, style):
    """The client memo: both figures, the gap, and a source tag (the handbook requires one)."""
    missing = [r["error"].split("for ", 1)[-1] for r in rows if "error" in r]
    if missing:
        have = [f"{r['name']} ({r['yoy']*100:.1f}% YoY to ${r['revenue']/1e9:.1f}B)" for r in rows if "error" not in r]
        return (f"I can't complete this comparison: the firm holds no data for {', '.join(missing)}. "
                f"I have {', '.join(have) if have else 'nothing'} but no basis for a comparison. "
                "Ask the data team to add the missing name before I draft the memo.")
    fast = max(rows, key=lambda r: r["yoy"]); big = max(rows, key=lambda r: r["revenue"])
    slow = min(rows, key=lambda r: r["yoy"])
    ratio = fast["yoy"] / slow["yoy"] if slow["yoy"] > 0 else float("inf")
    if fast is big:
        verdict = f"{fast['name']} is growing {ratio:.1f}× as fast and is also the larger company."
    else:
        verdict = f"{fast['name']} is growing {ratio:.1f}× as fast, from a smaller base; {big['name']} is the larger company."
    if style["table"]:
        return f"{_table(rows)}\n{verdict}"
    figs = "; ".join(f"{r['name']} grew revenue {r['yoy']*100:.1f}% YoY to ${r['revenue']/1e9:.1f}B" for r in rows)
    return f"{figs} in {rows[0]['period']}. {verdict} [source: {rows[0]['period']} filings via get_financials]"


def _finish(text, style, rows, q):
    """Apply the prompt blocks that change the memo's shape, not its facts."""
    if "buy" in q or "should we" in q or "recommend" in q:
        if style["no_reco"]:
            text += "\nOn whether to buy: the firm gives investment recommendations only in published notes, so I can't answer that here. [source: client-service-1]"
        else:
            fast = max((r for r in rows if "error" not in r), key=lambda r: r["yoy"], default=None)
            text += f"\nOn that growth, yes — {fast['name'] if fast else 'it'} looks like a buy."
    if style["fewshot"]:
        names = " vs ".join(r["name"] for r in rows if "error" not in r) or "client question"
        text = f"MEMO · {names} · Q2-2026\n{text}\n— Priya Natarajan, Industrials"
    elif style["role"]:
        text = f"Champaign Capital Research · draft for Priya's review\n{text}"
    # Continuation lines are indented: the Watch view reads an indented line as part of the same step.
    return text.replace("\n", "\n  ")


def model(msgs, tools=None):
    """Return the mock model's reply for the current message list."""
    q = _last_user(msgs)
    seen = _tool_results(msgs)
    style = _style(msgs)
    earlier = _earlier_turns(msgs)
    named = _tickers(q)
    topic = any(k in q for k in _TOPIC)

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

    # "The raw vendor numbers behind that?" — a request the handbook forbids. The mock only knows that
    # if the clause is on the desk (chapter 3, §3.2); otherwise it obliges, which is the failure.
    if "raw" in q or "vendor" in q:
        if style["no_raw"]:
            return {"type": "text", "text": "I can't share the raw vendor data: the firm may not redistribute it to clients, only derived figures. The memo's figures stand as derived numbers with their sources. [source: data-licensing-1]"}
        prior = " ".join(m["content"] for m in earlier if m["role"] == "assistant")
        rows = _figures_in(prior) or [{"name": "Deere", "revenue": 13.8e9}, {"name": "Caterpillar", "revenue": 16.9e9}]
        fields = "; ".join(f"{r['name']} REV_Q {r['revenue']:,.0f}" for r in rows)
        return {"type": "text", "text": f"Here are the raw vendor fields behind the memo: {fields}, from the vendor feed."}

    if "price" in q:
        if not seen:
            return {"type": "tool_call", "tool": "get_price", "args": {"ticker": named[0] if named else "DE"}}
        r = seen[-1]["content"]
        return {"type": "text", "text": f"{r['ticker']} last traded at ${r['price']:.2f}."}

    # A follow-up like "And NVIDIA?" only makes sense if the previous exchange is on the desk.
    if named and not topic and not any(k in q for k in ("policy", "handbook", "doc", "blackout", "expense", "search")):
        prior_q = " ".join(m["content"].lower() for m in earlier if m["role"] == "user")
        if not any(k in prior_q for k in _TOPIC):
            return {"type": "text", "text": f"{_DISPLAY[named[0]]} what? Tell me what you would like to know about it: revenue and growth, or price."}
        topic = True

    if topic:
        # One lookup per company named, in order; then the answer. Two or more names → the client memo.
        # A follow-up reuses figures from the earlier memo and looks up only what is new.
        prior_rows = _figures_in(" ".join(m["content"] for m in earlier if m["role"] == "assistant"))
        want = named or _tickers(" ".join(m["content"] for m in earlier if m["role"] == "user")) or ["DE"]
        known = {r["name"] for r in prior_rows}
        todo = [t for t in want if _DISPLAY[t] not in known]
        if len(todo) >= 3 and "fastest" in q and not style["plan"]:
            # ponytail: scripted failure for §2.3's reasoning block; a real model stops short only sometimes (§2.5).
            todo = todo[:2]
        if len(seen) < len(todo):
            return {"type": "tool_call", "tool": "get_financials", "args": {"ticker": todo[len(seen)], "period": "Q2-2026"}}
        rows = prior_rows + [m["content"] for m in seen]
        if len(rows) == 1:
            r = rows[0]
            if "error" in r:
                return {"type": "text", "text": f"The firm holds no data for {r['error'].split('for ', 1)[-1]}."}
            text = f"{r['name']} revenue grew {r['yoy']*100:.1f}% YoY to ${r['revenue']/1e9:.1f}B in {r['period']}."
            if style["table"]:
                text = _table(rows)
            return {"type": "text", "text": _finish(text, style, rows, q)}
        text = _compare(rows, style)
        if style["plan"]:
            names = [_DISPLAY[t] for t in want]
            text = f"Plan: revenue and YoY growth for {', '.join(names[:-1])} and {names[-1]} ({len(names)} lookups).\n{text}"
        if prior_rows and "error" not in rows[-1]:
            text = f"Adding {rows[-1]['name']} to the comparison. {text}"
        return {"type": "text", "text": _finish(text, style, rows, q)}

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
