"""Campus copy of the book: serves the built site and a same-origin /api/chat proxy to Azure AI Foundry.

The Foundry key lives in App Service settings (Key Vault reference), never in the page.
Entra Easy Auth in front of the app supplies X-MS-CLIENT-PRINCIPAL-NAME; requests without it are refused.
"""
import os
from datetime import date

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

ENDPOINT = os.environ.get("FOUNDRY_ENDPOINT", "").rstrip("/")
API_KEY = os.environ.get("FOUNDRY_API_KEY", "")
DEPLOYMENT = os.environ.get("MODEL_DEPLOYMENT", "gpt-5-mini")
DAILY_CAP = int(os.environ.get("DAILY_TOKEN_CAP", "20000"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1024"))
HTML_DIR = os.environ.get("HTML_DIR", os.path.join(os.path.dirname(__file__), "..", "html"))

app = FastAPI()
_usage: dict[tuple[str, str], int] = {}  # ponytail: in-memory per-user daily counter; Table Storage if restarts matter


def _user(request: Request) -> str:
    user = request.headers.get("x-ms-client-principal-name")
    if not user:
        raise HTTPException(401, "sign in required")
    return user.lower()


def _used(user: str) -> int:
    return _usage.get((user, date.today().isoformat()), 0)


@app.get("/api/whoami")
def whoami(request: Request):
    user = _user(request)
    return {"user": user, "used": _used(user), "cap": DAILY_CAP, "model": DEPLOYMENT}


@app.post("/api/chat")
async def chat(request: Request):
    user = _user(request)
    if _used(user) >= DAILY_CAP:
        raise HTTPException(429, "daily token budget used up")
    body = await request.json()
    if not isinstance(body.get("messages"), list):
        raise HTTPException(400, "messages required")
    # gpt-5.x deployments reject max_tokens; max_completion_tokens is the accepted name
    payload = {"model": DEPLOYMENT, "messages": body["messages"],
               "max_completion_tokens": min(int(body.get("max_tokens", MAX_TOKENS)), MAX_TOKENS)}
    if body.get("tools"):
        payload["tools"] = body["tools"]
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{ENDPOINT}/openai/v1/chat/completions", json=payload,
                              headers={"Authorization": f"Bearer {API_KEY}"})
    if r.status_code != 200:
        raise HTTPException(502, f"model call failed: {r.text[:300]}")
    data = r.json()
    key = (user, date.today().isoformat())
    _usage[key] = _usage.get(key, 0) + int((data.get("usage") or {}).get("total_tokens", 0))
    return data


if os.path.isdir(HTML_DIR):
    app.mount("/", StaticFiles(directory=HTML_DIR, html=True), name="site")
