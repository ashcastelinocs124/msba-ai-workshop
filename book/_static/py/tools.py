"""Tiny, read-only tools over bundled fixture data. Every tool is a plain function
plus a JSON schema, exactly as you would hand to the real API."""
from docs import DOCS

FINANCIALS = {
    ("DE", "Q2-2026"):   {"name": "Deere", "revenue": 13.8e9, "yoy": 0.064},
    ("CAT", "Q2-2026"):  {"name": "Caterpillar", "revenue": 16.9e9, "yoy": 0.031},
    ("NVDA", "Q2-2026"): {"name": "NVIDIA", "revenue": 52.4e9, "yoy": 0.58},
    ("AAPL", "Q2-2026"): {"name": "Apple", "revenue": 96.1e9, "yoy": 0.05},
    ("MSFT", "Q2-2026"): {"name": "Microsoft", "revenue": 76.3e9, "yoy": 0.17},
}
PRICES = {"DE": 512.40, "CAT": 398.15, "NVDA": 181.22, "AAPL": 232.90, "MSFT": 512.06}

# Orders for the refund-triage example. days_since_purchase is what the policy hinges on.
ORDERS = {
    "4471": {"customer": "Priya Natarajan", "item": "Standing desk", "amount": 449.00, "days_since_purchase": 9,  "used": False, "receipt": True},
    "4488": {"customer": "Marcus Bell",     "item": "Office chair",  "amount": 289.00, "days_since_purchase": 21, "used": False, "receipt": True},
    "4502": {"customer": "Elena Ruiz",      "item": "Monitor arm",   "amount": 79.00,  "days_since_purchase": 4,  "used": False, "receipt": False},
    "4519": {"customer": "Tom Okafor",      "item": "Desk lamp",     "amount": 59.00,  "days_since_purchase": 6,  "used": True,  "receipt": True},
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


def get_order(order_id: str) -> dict:
    """Order details: customer, item, amount, days since purchase, used, receipt on file."""
    row = ORDERS.get(str(order_id).lstrip("#"))
    return {**row, "order_id": str(order_id).lstrip("#")} if row else {"error": f"no order {order_id}"}


def search_docs(query: str, k: int = 3) -> list:
    """Keyword search over the bundled policy documents. Returns top-k chunks with ids."""
    words = set(query.lower().split())
    scored = []
    for d in DOCS:
        score = sum(1 for w in words if w in d["text"].lower())
        if score:
            scored.append((score, d))
    scored.sort(key=lambda s: -s[0])
    return [d for _, d in scored[:k]]


TOOLS = {"get_financials": get_financials, "get_price": get_price, "get_order": get_order, "search_docs": search_docs}

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
    {"name": "get_order",
     "description": "Look up one customer order by id. Use when a question names an order number.",
     "input_schema": {"type": "object",
                      "properties": {"order_id": {"type": "string", "pattern": "^[0-9]{4}$"}},
                      "required": ["order_id"], "additionalProperties": False}},
    {"name": "search_docs",
     "description": "Keyword search over company policy documents. Do not call with an empty or one-word query.",
     "input_schema": {"type": "object",
                      "properties": {"query": {"type": "string", "minLength": 4}, "k": {"type": "integer", "minimum": 1, "maximum": 5}},
                      "required": ["query"], "additionalProperties": False}},
]
