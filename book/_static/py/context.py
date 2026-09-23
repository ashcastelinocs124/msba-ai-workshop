"""Prompt blocks (chapter 2) and context engineering (chapter 3): code decides what the model reads on each call.

A prompt is one block a person typed. The context is everything on the desk for one call:
the standing instructions, a handbook clause retrieved because this question needs it, the
client's card, the previous exchange, and (inside the loop) the tool results. build_context
assembles the first three and trims the fourth; the loop in agent.py adds the last.
"""
from tools import search_docs

ROLE = ("You are a research associate at Champaign Capital Research, an independent equity research firm. "
        "You are drafting a reply for a portfolio manager at a pension-fund client. You draft; Priya reads and sends.")
RULES = ("Rules. Never give an investment recommendation; those appear only in published notes [client-service-1]. "
         "Every figure must name its source [research-process-1]. If the firm holds no data for a company, say so instead of guessing.")
FORMAT = ("Format. When the client asks for a table, answer as a table with columns: company, revenue, YoY growth, source. "
          "Otherwise, two sentences.")
EXAMPLES = ("Example 1.\nMEMO · Deere vs Caterpillar · Q2-2026\nDeere grew revenue 6.4% YoY to $13.8B; Caterpillar grew revenue 3.1% YoY to $16.9B. "
            "Deere is growing 2.1× as fast, from a smaller base. [source: Q2-2026 filings]\n— Priya Natarajan, Industrials\n\n"
            "Example 2.\nMEMO · NVIDIA vs Apple · Q2-2026\nNVIDIA grew revenue 58.0% YoY to $52.4B; Apple grew revenue 5.0% YoY to $96.1B. "
            "NVIDIA is growing 11.6× as fast, from a smaller base. [source: Q2-2026 filings]\n— Priya Natarajan, Industrials")
REASONING = "Before calling any tool, list every figure the question needs. Then look each one up, once."

# The client card. About 120 institutions subscribe; this is the one from the firm page's "first Monday".
CLIENTS = {
    "meridian": {"name": "Meridian Pension Trust", "contact": "Dana Whitfield, portfolio manager",
                 "prefers": "tables", "covers": "industrials and agricultural equipment"},
}

_STOP = {"and", "the", "that", "this", "what", "does", "about", "behind", "have", "with", "from", "please", "those", "them"}


def estimate_tokens(text):
    """Roughly how many tokens a block costs. ponytail: words × 1.3; a real system would call the tokenizer."""
    return int(len(str(text).split()) * 1.3) + 1


def build_context(question, client=None, history=None, examples=False):
    """Assemble what the model reads for one call. Returns (system, history) for agent().

    - the standing instructions (role, rules, format; examples only if asked, they are expensive)
    - the client's card, if we know who is asking
    - one handbook clause, retrieved only when the question sounds like it needs one
    - the last exchange from history, and nothing older
    """
    blocks = [ROLE, RULES, FORMAT] + ([EXAMPLES] if examples else [])
    if client:
        c = CLIENTS[client]
        blocks.append(f"Client. {c['name']} ({c['contact']}); covers {c['covers']}; prefers {c['prefers']}.")
    q = question.lower()
    if any(w in q for w in ("vendor", "raw", "policy", "handbook", "allowed", "can we", "may we")):
        query = " ".join(w for w in q.replace("?", "").split() if len(w) > 2 and w not in _STOP)
        hit = search_docs(query, k=1)
        if hit:
            blocks.append(f"Relevant policy [{hit[0]['id']}]: {hit[0]['text']}")
    system = "\n\n".join(blocks)
    # ponytail: keep only the last exchange; a real system would summarise older turns into a few lines.
    history = list(history or [])[-2:]
    return system, history


def describe_context(system, history, question):
    """Print what is on the desk for this call, one line per block, with a token estimate each."""
    rows = [(b.split(".")[0].split("\n")[0][:34], estimate_tokens(b)) for b in system.split("\n\n")]
    rows += [(f"history · {r}", estimate_tokens(c)) for r, c in history]
    rows.append(("the question", estimate_tokens(question)))
    for label, n in rows:
        print(f"  {label:<36} {n:>5} tokens")
    print(f"  {'total on the desk':<36} {sum(n for _, n in rows):>5} tokens")


if __name__ == "__main__":
    # ponytail: self-check; run `python context.py` from _static/py
    s, h = build_context("Deere vs Caterpillar as a table")
    assert "Champaign Capital" in s and "investment recommendation" in s and "Relevant policy" not in s and h == []
    s, h = build_context("And the raw vendor numbers behind that?", client="meridian", history=[("user", "a"), ("assistant", "b"), ("user", "c"), ("assistant", "d")])
    assert "[data-licensing-1]" in s and "prefers tables" in s and h == [("user", "c"), ("assistant", "d")], s
    assert 60 < estimate_tokens(ROLE + RULES) < 120
    print("ok")
