"""Tiny, read-only tools over bundled fixture data for Champaign Capital Research. Every tool is a plain
function plus a JSON schema, exactly as you would hand to the real API."""
from docs import DOCS

FINANCIALS = {
    ("DE", "Q2-2026"):   {"name": "Deere", "revenue": 13.8e9, "yoy": 0.064},
    ("CAT", "Q2-2026"):  {"name": "Caterpillar", "revenue": 16.9e9, "yoy": 0.031},
    ("NVDA", "Q2-2026"): {"name": "NVIDIA", "revenue": 52.4e9, "yoy": 0.58},
    ("AAPL", "Q2-2026"): {"name": "Apple", "revenue": 96.1e9, "yoy": 0.05},
    ("MSFT", "Q2-2026"): {"name": "Microsoft", "revenue": 76.3e9, "yoy": 0.17},
}
PRICES = {"DE": 512.40, "CAT": 398.15, "NVDA": 181.22, "AAPL": 232.90, "MSFT": 512.06}

# Personal-trade pre-clearance requests from staff. Compliance decides; the policy hinges on these fields.
TRADE_REQUESTS = {
    "7101": {"employee": "Priya Natarajan", "role": "senior analyst, industrials", "ticker": "DE",   "side": "buy",  "shares": 50,  "days_since_firm_research": 41, "restricted": False, "holding_days": None},
    "7102": {"employee": "Marcus Bell",     "role": "associate, industrials",     "ticker": "CAT",  "side": "sell", "shares": 200, "days_since_firm_research": 60, "restricted": False, "holding_days": 12},
    "7103": {"employee": "Jordan Lee",      "role": "analyst, semiconductors",    "ticker": "NVDA", "side": "buy",  "shares": 30,  "days_since_firm_research": 25, "restricted": True,  "holding_days": None},
    "7104": {"employee": "Tom Okafor",      "role": "data engineer",              "ticker": "DE",   "side": "sell", "shares": 80,  "days_since_firm_research": 6,  "restricted": False, "holding_days": 210},
}


def get_financials(ticker: str, period: str = "Q2-2026") -> dict:
    """Quarterly revenue and YoY growth for a ticker."""
    row = FINANCIALS.get((ticker.upper(), period))
    if row is None:
        return {"error": f"no data for {ticker} {period}"}
    return {**row, "ticker": ticker.upper(), "period": period}


def get_price(ticker: str) -> dict:
    """Last traded price for a ticker."""
    p = PRICES.get(ticker.upper())
    return {"ticker": ticker.upper(), "price": p} if p else {"error": f"unknown ticker {ticker}"}


def get_trade_request(request_id: str) -> dict:
    """One personal-trade pre-clearance request: employee, ticker, side, shares, days since the firm last published on the name, restricted-list flag, holding days."""
    row = TRADE_REQUESTS.get(str(request_id).lstrip("#"))
    return {**row, "request_id": str(request_id).lstrip("#")} if row else {"error": f"no request {request_id}"}


def search_docs(query: str, k: int = 3) -> list:
    """Keyword search over the firm's policy handbook. Returns top-k chunks with ids."""
    words = set(query.lower().split())
    scored = []
    for d in DOCS:
        score = sum(1 for w in words if w in d["text"].lower())
        if score:
            scored.append((score, d))
    scored.sort(key=lambda s: -s[0])
    return [d for _, d in scored[:k]]


TOOLS = {"get_financials": get_financials, "get_price": get_price, "get_trade_request": get_trade_request, "search_docs": search_docs}


def describe_schema(schema):
    """Print a tool's contract in plain, indented English instead of raw JSON."""
    print(f"{schema['name']} — {schema['description']}")
    props, req = schema["input_schema"]["properties"], schema["input_schema"]["required"]
    for field, spec in props.items():
        need = "required" if field in req else "optional"
        note = f", one of: {', '.join(str(v) for v in spec['enum'])}" if "enum" in spec else ""
        print(f"  - {field} ({need}){note}")

# The schemas the model sees. Chapter 1 is about why these matter.
TOOL_SCHEMAS = [
    {"name": "get_financials",
     "description": "Quarterly revenue and YoY growth for one ticker. Use only when the user asks about revenue, growth, or earnings.",
     "input_schema": {"type": "object",
                      "properties": {"ticker": {"type": "string", "enum": list(PRICES)},
                                     "period": {"type": "string", "enum": ["Q2-2026"]}},
                      "required": ["ticker", "period"], "additionalProperties": False}},
    {"name": "get_price",
     "description": "Last traded price for one ticker.",
     "input_schema": {"type": "object",
                      "properties": {"ticker": {"type": "string", "enum": list(PRICES)}},
                      "required": ["ticker"], "additionalProperties": False}},
    {"name": "get_trade_request",
     "description": "Look up one personal-trade pre-clearance request by id. Use when a question names a request number.",
     "input_schema": {"type": "object",
                      "properties": {"request_id": {"type": "string", "pattern": "^[0-9]{4}$"}},
                      "required": ["request_id"], "additionalProperties": False}},
    {"name": "search_docs",
     "description": "Keyword search over the firm's policy handbook. Do not call with an empty or one-word query.",
     "input_schema": {"type": "object",
                      "properties": {"query": {"type": "string", "minLength": 4}, "k": {"type": "integer", "minimum": 1, "maximum": 5}},
                      "required": ["query"], "additionalProperties": False}},
]
