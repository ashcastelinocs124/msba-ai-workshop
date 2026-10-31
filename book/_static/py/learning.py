"""Self-learning (chapter 6): the harness grades the agent's work, turns a failure into a lesson,
and puts the lessons in front of the next task.

The agent is chapter 1's agent(), unchanged. What is new sits around it:

- grade: an automatic test. The memo's revenue figure must equal the fiscal-year figure in the 10-K.
- reflect: the grader's feedback, written as one plain-English rule.
- save: the rule goes into LESSONS (the lessons.md file), only after a graded failure, only once,
  and only with a person's approval.
- lessons_block: the lessons, on the desk (in the system prompt) for every later memo.

ponytail: LESSONS is a list in this browser tab, so it empties when the page reloads. Real systems
keep lessons.md as a file or a database row, with every change logged (section 6.4.3).
"""
import re

from agent import agent
from mock_model import model as _mock
from tools import TOOLS, TOOL_SCHEMAS

# Annual revenue as the firm's records hold it: the fiscal year in each company's 10-K, and the same
# twelve months added up from four quarterly reports on a calendar-year basis. Illustrative figures,
# not market data. Caterpillar's fiscal year is the calendar year, so its two figures are the same.
FILINGS = {
    "DE":   {"name": "Deere",       "fy": "FY2025 (ended Nov 2, 2025)",  "fiscal": 45.7e9,  "calendar": 44.9e9,  "page": 31},
    "AAPL": {"name": "Apple",       "fy": "FY2025 (ended Sep 27, 2025)", "fiscal": 416.2e9, "calendar": 425.4e9, "page": 28},
    "CAT":  {"name": "Caterpillar", "fy": "FY2025 (ended Dec 31, 2025)", "fiscal": 64.8e9,  "calendar": 64.8e9,  "page": 46},
    "NVDA": {"name": "NVIDIA",      "fy": "FY2026 (ended Jan 25, 2026)", "fiscal": 187.1e9, "calendar": 179.5e9, "page": 52},
    "MSFT": {"name": "Microsoft",   "fy": "FY2025 (ended Jun 30, 2025)", "fiscal": 281.7e9, "calendar": 296.3e9, "page": 37},
}
WEEK = [("Mon", "DE"), ("Tue", "AAPL"), ("Wed", "CAT"), ("Thu", "NVDA")]   # the practice tasks
HELD_OUT = ["MSFT"]                                                          # locked: never learned from (section 6.4.3)
PRIYA = "Firm uses fiscal year. Cite the 10-K."                              # her correction, by email
DESK = "You write revenue memos for Champaign Capital Research. Look up every figure with a tool before you write it."

LESSONS = []


def get_annual_revenue(ticker: str, basis: str = "calendar") -> dict:
    """Annual revenue for a ticker, on a calendar-year or a fiscal-year basis, with where the figure comes from."""
    row = FILINGS.get(ticker.upper())
    if row is None:
        return {"error": f"no annual figures for {ticker}"}
    if basis == "fiscal":
        return {"name": row["name"], "period": row["fy"], "revenue": row["fiscal"], "source": f"10-K, page {row['page']}"}
    return {"name": row["name"], "period": "calendar 2025", "revenue": row["calendar"], "source": "four quarterly reports, added up"}


LEARNING_TOOLS = {**TOOLS, "get_annual_revenue": get_annual_revenue}
LEARNING_TOOL_SCHEMAS = TOOL_SCHEMAS + [
    {"name": "get_annual_revenue",
     "description": "Annual revenue for one company, on a calendar-year or a fiscal-year basis, with its source.",
     "input_schema": {"type": "object",
                      "properties": {"ticker": {"type": "string", "enum": list(FILINGS)},
                                     "basis": {"type": "string", "enum": ["calendar", "fiscal"]}},
                      "required": ["ticker", "basis"], "additionalProperties": False}},
]


def azure_learning_model(msgs):
    """The campus copy's real model (llm.azure_model), shown the annual-revenue tool as well (section 6.2.6)."""
    from llm import azure_model
    return azure_model(msgs, tools=LEARNING_TOOL_SCHEMAS, verbose=False)


def lessons_block(lessons=None):
    """The system prompt for a memo: the desk's standing instruction, then lessons.md if it has anything in it."""
    lessons = LESSONS if lessons is None else lessons
    texts = [l["text"] if isinstance(l, dict) else l for l in lessons]
    if not texts:
        return DESK
    return DESK + "\n\nLessons from past work (lessons.md):\n" + "\n".join(f"- {t}" for t in texts)


def write_memo(ticker, model=None, lessons=None, verbose=False):
    """Steps 1 and 2: chapter 1's agent writes the annual revenue memo, with lessons.md on the desk."""
    name = FILINGS[ticker]["name"]
    answer, _ = agent(f"Write the annual revenue memo for {name}.", tools=LEARNING_TOOLS, model=model or _mock,
                      system=lessons_block(lessons), verbose=verbose)
    return answer


def _billions(x):
    return f"${x / 1e9:.1f}B"


def grade(memo, ticker):
    """Step 3, an automatic test: the memo's figure must be the fiscal-year figure in the 10-K.
    Returns (passed, feedback). It checks the figure and nothing else, which is a grader's limit."""
    row = FILINGS[ticker]
    want = _billions(row["fiscal"])
    if want in memo:
        return True, f"{want} matches the 10-K"
    found = re.findall(r"\$[\d.]+B", memo)
    said = f"the memo says {found[0]}" if found else "the memo gives no figure"
    return False, f"{said}; the 10-K says {want} for {row['fy']}"


def reflect(feedback, model=None):
    """Step 4: turn the grader's feedback into one short rule for next time. The mock writes it
    from a template; a real model writes it in its own words."""
    if model is not None:
        msgs = [{"role": "system", "content": "You keep the research desk's lessons file. Reply with one rule of at most 20 words."},
                {"role": "user", "content": f"A revenue memo failed this check: {feedback}. Priya's note: {PRIYA} Write the rule that would have prevented it."}]
        reply = model(msgs)
        if reply["type"] == "text" and reply["text"]:
            return reply["text"].strip().splitlines()[0]
    # ponytail: scripted reflection; every failure this grader can find is the same one.
    return "Revenue: use the fiscal year in the company's 10-K, and cite the 10-K page."


def save(lesson, failure=None, approved_by=None):
    """Step 5, with the rules for the lessons file: only after a graded failure, never twice, and only
    when a person has approved it. Returns what happened, in a sentence."""
    if not failure:
        return "not saved: no graded failure behind it"
    if not approved_by:
        return "not saved: waiting for a person to approve it"
    if any(l["text"] == lesson for l in LESSONS):
        return "not saved: already in lessons.md"
    LESSONS.append({"text": lesson, "because": failure, "approved_by": approved_by})
    return f"saved to lessons.md (approved by {approved_by})"


def show_lessons(lessons=None):
    """Print lessons.md: each rule, the failure that caused it, and who approved it."""
    lessons = LESSONS if lessons is None else lessons
    if not lessons:
        print("lessons.md is empty.")
    for i, l in enumerate(lessons, 1):
        print(f"{i}. {l['text']}\n   because: {l['because']} · approved by {l['approved_by']}")


def _line(label, *parts):
    print(f"{label:<24}{parts[0]}")
    for p in parts[1:]:
        print(" " * 24 + p)


def run_week(learn=True, model=None, approver="Priya", fresh=True):
    """Four memos, Monday to Thursday. With learn=False this is chapter 1's agent: act and hand over,
    and Priya corrects by email. With learn=True each memo is graded, and a failure becomes a lesson.
    lessons.md starts empty unless fresh=False. Returns the week's counts."""
    if fresh:
        LESSONS.clear()
    corrections = right = 0
    for day, t in WEEK:
        label = f"{day} · {FILINGS[t]['name']} memo"
        ok, feedback = grade(write_memo(t, model), t)
        if ok:
            right += 1
            _line(label, f"✓ graded: {feedback}" if learn else "✓ right figure, nothing to correct")
            continue
        corrections += 1
        if not learn:
            _line(label, f"✗ wrong figure: {feedback}", f'Priya corrects it: "{PRIYA}" The correction stays in her email.')
            continue
        lesson = reflect(feedback, model)
        _line(label, f"✗ graded: {feedback}", f'reflected: "{lesson}"', save(lesson, failure=feedback, approved_by=approver))
    print(f"Memos sent back this week: {corrections}. Right first time: {right} of {len(WEEK)}.")
    return {"corrections": corrections, "right": right}


# Section 6.3.4: a week of notes, written in a hurry. Three say the same thing, two disagree, one is stale.
WEEK_NOTES = [
    ("Mon", "Use fiscal year (Deere)"),
    ("Tue", "Fiscal year, not calendar"),
    ("Wed", "FY figures; cite 10-K"),
    ("Wed", "Tables only for institutional clients"),
    ("Thu", "Tables whenever a client asks"),
    ("Thu", "2025 guidance: Deere expects $46-48B revenue"),
]
_TOPICS = {"revenue": ("fiscal", "fy ", "10-k"), "tables": ("table",), "guidance": ("guidance",)}
_MERGED = {"revenue": "Revenue: use the fiscal year in the company's 10-K, and cite the 10-K page."}


def _topic(text):
    t = text.lower() + " "
    return next((k for k, words in _TOPICS.items() if any(w in t for w in words)), None)


def dream(notes=None):
    """Consolidate a week of notes while the agent is idle: merge notes that agree, keep the newest of
    notes that disagree, drop stale ones. Returns a NEW list and leaves the old one untouched, so a
    person can compare the two and approve or throw away the new one.
    ponytail: scripted rules by topic word; in the Colab notebook a real model does the rereading."""
    notes = WEEK_NOTES if notes is None else notes
    groups = {}
    for day, text in notes:
        groups.setdefault(_topic(text), []).append((day, text))
    new = []
    for topic, items in groups.items():
        if topic == "guidance":
            print(f"removed (stale, FY2025 results are out): {', '.join(t for _, t in items)}")
        elif topic in _MERGED:
            new.append(_MERGED[topic])
            print(f"merged {len(items)} notes that agree → {_MERGED[topic]}")
        elif topic == "tables" and len(items) > 1:
            new.append(items[-1][1])
            print(f"kept the newest of {len(items)} that disagree → {items[-1][1]} (replaces: {', '.join(t for _, t in items[:-1])})")
        else:
            new += [t for _, t in items]
    print(f"{len(notes)} notes in, {len(new)} out. The old list is unchanged until a person approves the new one.")
    return new


# Section 6.3.3: a playbook edited in small steps, or rewritten whole after every task.
PLAYBOOK = [
    "Revenue: use the fiscal year in the company's 10-K, and cite the 10-K page (Deere's year ends in early November).",
    "Recommendations: never give one in a memo, and route the client to an analyst (handbook client-service-1).",
    "Tables: use one whenever a client asks, with the source in the last column.",
]


def rewrite_all(playbook=None, times=1):
    """Rewrite the whole playbook as a fresh summary, `times` times. Each summary keeps every rule's
    first clause and drops the rest. ponytail: scripted summary, so the loss is the same every run."""
    book = list(PLAYBOOK if playbook is None else playbook)
    for _ in range(times):
        book = [re.split(r",|\(", rule)[0].rstrip(" .") + "." for rule in book]
    return book


def edit(playbook=None, add=None):
    """A small edit: add one rule and leave every other rule word for word."""
    book = list(PLAYBOOK if playbook is None else playbook)
    return book + [add] if add else book


def evaluate(lessons=None, grader=None, model=None):
    """Score the agent on the practice week and on the held-out task it never learned from.
    The held-out task is always marked by the real grader; `grader` replaces it on practice only,
    to show what happens when the agent can edit its own grader (section 6.4.3)."""
    lessons = LESSONS if lessons is None else lessons
    practice = grader or grade
    p = sum(practice(write_memo(t, model, lessons), t)[0] for _, t in WEEK)
    h = sum(grade(write_memo(t, model, lessons), t)[0] for t in HELD_OUT)
    print(f"practice: {p} of {len(WEEK)} right ({p / len(WEEK):.0%}) · held-out: {h} of {len(HELD_OUT)} right ({h / len(HELD_OUT):.0%})")
    return p, h


MEMORIZED = [f"{FILINGS[t]['name']}: {_billions(FILINGS[t]['fiscal'])}" for _, t in WEEK]   # answers, not a rule


if __name__ == "__main__":
    # ponytail: self-check; run `python learning.py` from _static/py
    assert get_annual_revenue("DE", "fiscal")["revenue"] == 45.7e9 and "error" in get_annual_revenue("TSLA")
    memo = write_memo("DE", lessons=[])
    assert "$44.9B" in memo and not grade(memo, "DE")[0], memo                # no lesson: calendar year, fails
    assert grade(write_memo("CAT", lessons=[]), "CAT")[0]                      # Caterpillar is right either way
    assert run_week(learn=False) == {"corrections": 3, "right": 1} and LESSONS == []
    assert run_week(learn=True) == {"corrections": 1, "right": 4 - 1} and len(LESSONS) == 1
    memo = write_memo("AAPL")
    assert "$416.2B" in memo and "10-K, page 28" in memo, memo                # the lesson is on the desk
    assert "fiscal year" in lessons_block() and lessons_block([]) == DESK
    assert save("x").startswith("not saved: no graded") and save("x", "f").startswith("not saved: waiting")
    assert save(LESSONS[0]["text"], "f", "Priya").startswith("not saved: already") and len(LESSONS) == 1
    assert run_week(learn=True, approver=None)["corrections"] == 3 and LESSONS == []   # unapproved: nothing kept
    new = dream()
    assert len(new) == 2 and new[0].startswith("Revenue") and new[1] == "Tables whenever a client asks", new
    assert len(WEEK_NOTES) == 6                                                # dreaming never edits the old list
    short = rewrite_all(times=3)
    assert "page" not in short[0] and "client-service-1" not in short[1] and len(short) == 3, short
    assert edit(add="Charts: label both axes.")[:3] == PLAYBOOK
    assert evaluate(lessons=[]) == (1, 0)
    assert evaluate(lessons=MEMORIZED) == (4, 0)                               # memorized answers: practice only
    assert evaluate(lessons=[reflect("x")]) == (4, 1)                          # the general rule carries over
    assert evaluate(lessons=[], grader=lambda memo, t: (True, "looks fine")) == (4, 0)   # a grader the agent rewrote
    assert [s["name"] for s in LEARNING_TOOL_SCHEMAS][-1] == "get_annual_revenue" and callable(azure_learning_model)
    LESSONS.clear()
    print("ok")
