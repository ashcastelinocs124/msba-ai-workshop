"""Campus copy of the book: serves the built site and a same-origin /api/chat proxy to Azure AI Foundry.

The Foundry key lives in App Service settings (Key Vault reference), never in the page.
Entra Easy Auth in front of the app supplies X-MS-CLIENT-PRINCIPAL-NAME; requests without it are refused.
"""
import base64
import csv
import html
import io
import json
import os
from datetime import date

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

ENDPOINT = os.environ.get("FOUNDRY_ENDPOINT", "").rstrip("/")
API_KEY = os.environ.get("FOUNDRY_API_KEY", "")
DEPLOYMENT = os.environ.get("MODEL_DEPLOYMENT", "gpt-5-mini")
DAILY_CAP = int(os.environ.get("DAILY_TOKEN_CAP", "20000"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1024"))
HTML_DIR = os.environ.get("HTML_DIR", os.path.join(os.path.dirname(__file__), "..", "html"))
# Who signed in, one row per person per day. /home persists across restarts and deploys on App Service.
SIGNIN_LOG = os.environ.get("SIGNIN_LOG", "/home/data/signins.csv")
# Only these accounts may read the list; set ADMIN_USERS in App Service settings, never in the repo.
ADMIN_USERS = {u.strip().lower() for u in os.environ.get("ADMIN_USERS", "").split(",") if u.strip()}

app = FastAPI()
_usage: dict[tuple[str, str], int] = {}  # ponytail: in-memory per-user daily counter; Table Storage if restarts matter
_seen: set[tuple[str, str]] = set()  # (day, user) already written today; the reader dedupes anyway, this just saves writes


def _user(request: Request) -> str:
    user = request.headers.get("x-ms-client-principal-name")
    if not user:
        raise HTTPException(401, "sign in required")
    return user.lower()


def _display_name(request: Request) -> str | None:
    """The signed-in user's real name from Easy Auth's claims header, so the page can greet
    them by name instead of their email. Falls back to None (caller uses the email) if the
    header is missing or the identity provider didn't send a name claim."""
    raw = request.headers.get("x-ms-client-principal")
    if not raw:
        return None
    try:
        claims = json.loads(base64.b64decode(raw)).get("claims", [])
    except Exception:
        return None
    name_types = {"name", "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"}
    return next((c.get("val") for c in claims if c.get("typ") in name_types), None)


def _used(user: str) -> int:
    return _usage.get((user, date.today().isoformat()), 0)


def _record_signin(user: str, name: str | None) -> None:
    """Append 'day,user,name' the first time we see this person today. Never lets a logging
    problem break the page: a full disk or a read-only filesystem just means no row."""
    key = (date.today().isoformat(), user)
    if key in _seen:
        return
    _seen.add(key)
    try:
        os.makedirs(os.path.dirname(SIGNIN_LOG), exist_ok=True)
        with open(SIGNIN_LOG, "a", newline="") as f:
            csv.writer(f).writerow([key[0], user, name or ""])
    except OSError:
        pass


def _signins() -> list[tuple[str, str, str]]:
    """Every (day, user, name) row, deduplicated (a restart empties _seen, so a day can repeat), newest first."""
    rows: dict[tuple[str, str], str] = {}
    try:
        with open(SIGNIN_LOG, newline="") as f:
            for day, user, name in csv.reader(f):
                rows.setdefault((day, user), name)
    except OSError:
        pass
    return sorted(((d, u, n) for (d, u), n in rows.items()), reverse=True)


@app.get("/api/whoami")
def whoami(request: Request):
    user = _user(request)
    name = _display_name(request)
    _record_signin(user, name)
    return {"name": name or user, "user": user, "used": _used(user), "cap": DAILY_CAP, "model": DEPLOYMENT}


@app.get("/admin/signins")
def signins(request: Request, format: str = "html"):
    """Who signed in, for the instructor. Not linked from the site; open it directly."""
    if _user(request) not in ADMIN_USERS:
        raise HTTPException(403, "admins only")
    rows = _signins()
    if format == "csv":
        out = io.StringIO()
        csv.writer(out, lineterminator="\n").writerows([("day", "user", "name"), *rows])
        return PlainTextResponse(out.getvalue(), media_type="text/csv")
    people = len({u for _, u, _ in rows})
    body = "".join(f"<tr><td>{html.escape(d)}</td><td>{html.escape(u)}</td><td>{html.escape(n)}</td></tr>" for d, u, n in rows)
    return HTMLResponse(f"""<!doctype html><meta charset="utf-8"><title>Sign-ins</title>
<style>body{{font:15px/1.5 system-ui,sans-serif;margin:2rem;color:#1f2430}}h1{{color:#13294b}}table{{border-collapse:collapse}}td,th{{border-bottom:1px solid #e6e8ee;padding:6px 14px;text-align:left}}th{{color:#5a6478;font-size:12px;text-transform:uppercase;letter-spacing:.08em}}</style>
<h1>Sign-ins</h1><p>{people} people, {len(rows)} person-days. One row per person per day, recorded on their first page load. <a href="?format=csv">Download CSV</a></p>
<table><tr><th>Day</th><th>Account</th><th>Name</th></tr>{body}</table>""")


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
