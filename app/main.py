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
import re
import sqlite3
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

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
# Pages only admins may open (matched by file stem, so the page and its _sources copy are both covered).
# Set LOCKED_PAGES to an empty string in App Service settings to open them to everyone.
LOCKED_PAGES = {p.strip() for p in os.environ.get("LOCKED_PAGES", "").split(",") if p.strip()}  # e.g. "ch03-memory-rag"
LOCKED_HTML = open(os.path.join(os.path.dirname(__file__), "locked.html")).read()
ADMIN_HTML = open(os.path.join(os.path.dirname(__file__), "admin.html")).read()
# Usage events and Lecture checkpoints. Like the sign-in list, this never leaves the App Service disk.
APP_DB = os.environ.get("APP_DB", "/home/data/app.db")
EVENT_KINDS = {"page_view", "cell_run"}  # what the browser may send; signin and model_call are written here
SCHEMA = """
CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, ts TEXT NOT NULL, user TEXT NOT NULL,
    kind TEXT NOT NULL, page TEXT, tokens INTEGER);
CREATE INDEX IF NOT EXISTS events_user_ts ON events(user, ts);
CREATE TABLE IF NOT EXISTS lecture_checkpoints (id INTEGER PRIMARY KEY, spot TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'closed', questions TEXT NOT NULL,
    opened_at TEXT, closed_at TEXT, live INTEGER);
CREATE TABLE IF NOT EXISTS answers (checkpoint_id INTEGER NOT NULL REFERENCES lecture_checkpoints(id),
    user TEXT NOT NULL, q INTEGER NOT NULL, value TEXT NOT NULL, correct INTEGER, ts TEXT NOT NULL,
    PRIMARY KEY (checkpoint_id, user, q));
"""

app = FastAPI()


@app.middleware("http")
async def lock_pages(request: Request, call_next):
    stem = request.url.path.rsplit("/", 1)[-1].split(".", 1)[0]
    user = (request.headers.get("x-ms-client-principal-name") or "").lower()
    if stem in LOCKED_PAGES and user not in ADMIN_USERS:
        return HTMLResponse(LOCKED_HTML, status_code=403)
    return await call_next(request)
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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _today() -> date:
    return datetime.now(timezone.utc).date()  # event timestamps are UTC, so "today" is too


_schema_ready: set[str] = set()


def _q(sql: str, args: tuple = ()) -> list[sqlite3.Row]:
    """Run one statement in its own connection and commit.
    ponytail: one SQLite file on the /home disk, fine while the web app runs on one instance;
    scaling out to several instances needs Postgres or Table Storage instead."""
    os.makedirs(os.path.dirname(APP_DB) or ".", exist_ok=True)
    con = sqlite3.connect(APP_DB, timeout=10)
    con.row_factory = sqlite3.Row
    try:
        if APP_DB not in _schema_ready:
            con.executescript(SCHEMA)
            try:  # databases created before one-question-at-a-time lack this column
                con.execute("ALTER TABLE lecture_checkpoints ADD COLUMN live INTEGER")
            except sqlite3.OperationalError:
                pass  # already there
            _schema_ready.add(APP_DB)
        with con:
            return con.execute(sql, args).fetchall()
    finally:
        con.close()


def _log(user: str, kind: str, page: str | None = None, tokens: int | None = None) -> None:
    """Append one usage event. A logging failure never breaks the page or the model call."""
    try:
        _q("INSERT INTO events (ts, user, kind, page, tokens) VALUES (?, ?, ?, ?, ?)", (_now(), user, kind, page, tokens))
    except sqlite3.Error:
        pass


def _used(user: str) -> int:
    """Tokens this user spent today (UTC day), read from the event log so the cap survives restarts."""
    try:
        return _q("SELECT COALESCE(SUM(tokens), 0) FROM events WHERE user = ? AND kind = 'model_call' AND ts >= ?",
                  (user, _today().isoformat()))[0][0]
    except sqlite3.Error:
        return 0


def _record_signin(user: str, name: str | None) -> None:
    """Append 'day,user,name' the first time we see this person today. Never lets a logging
    problem break the page: a full disk or a read-only filesystem just means no row."""
    key = (date.today().isoformat(), user)
    if key in _seen:
        return
    _seen.add(key)
    _log(user, "signin")
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
    _log(user, "model_call", tokens=int((data.get("usage") or {}).get("total_tokens", 0)))
    return data


@app.post("/api/events")
async def events(request: Request):
    """A page view or a cell run, sent by site.js / pyodide-cell.js on the campus copy."""
    user = _user(request)
    body = await request.json()
    kind, page = body.get("kind"), body.get("page")
    if kind not in EVENT_KINDS or not isinstance(page, str) or not re.fullmatch(r"[\w.-]{1,80}", page):
        raise HTTPException(400, "bad event")
    _log(user, kind, page)
    return {"ok": True}


# ---- Lecture checkpoints: the instructor opens them in class, students answer in the chapter ----

def _checkpoint(spot: str) -> sqlite3.Row | None:
    rows = _q("SELECT * FROM lecture_checkpoints WHERE spot = ?", (spot,))
    return rows[0] if rows else None


def _student_view(cp: sqlite3.Row | None, spot: str, user: str) -> dict:
    """What a student's page shows. While a checkpoint is open, only the questions released so far
    (up to `live`, the one being asked now) are sent, so nobody can read ahead. Correct answers only
    after the checkpoint has been opened and closed again, so one closed *before* class gives nothing away."""
    if cp is None:
        return {"spot": spot, "status": "none"}
    revealed = cp["status"] == "closed" and cp["opened_at"] is not None
    qs = json.loads(cp["questions"])
    shown = qs if revealed else qs[:(cp["live"] or 0) + 1] if cp["status"] == "open" else []
    mine = {r["q"]: r["value"] for r in _q("SELECT q, value FROM answers WHERE checkpoint_id = ? AND user = ?", (cp["id"], user))}
    questions = [{"prompt": q["prompt"], "kind": q["kind"], "choices": q.get("choices", []),
                  **({"correct": q.get("correct"), "explain": q.get("explain", "")} if revealed else {})} for q in shown]
    return {"spot": spot, "title": cp["title"], "status": cp["status"], "revealed": revealed, "total": len(qs),
            "live": cp["live"] if cp["status"] == "open" else None, "questions": questions, "mine": mine}


@app.get("/api/checkpoints/{spot}")
def checkpoint_get(spot: str, request: Request):
    return _student_view(_checkpoint(spot), spot, _user(request))


@app.post("/api/checkpoints/{spot}")
async def checkpoint_answer(spot: str, request: Request):
    """Save a student's answers. Resubmitting overwrites, so each student counts once per question."""
    user = _user(request)
    cp = _checkpoint(spot)
    if cp is None or cp["status"] != "open":
        raise HTTPException(409, "this checkpoint is closed")
    questions = json.loads(cp["questions"])
    answers = (await request.json()).get("answers")
    if not isinstance(answers, dict) or not answers:
        raise HTTPException(400, "answers required")
    rows = []
    for k, v in answers.items():
        i = int(k) if str(k).isdigit() else -1
        if not 0 <= i < len(questions):
            raise HTTPException(400, f"no question {k}")
        if i != (cp["live"] or 0):
            raise HTTPException(409, f"question {i + 1} is not open right now")
        q = questions[i]
        if q["kind"] == "mc":
            if not isinstance(v, int) or not 0 <= v < len(q["choices"]):
                raise HTTPException(400, f"question {i + 1}: pick one of the choices")
            rows.append((i, str(v), int(v == q["correct"])))
        else:
            if not isinstance(v, str) or not v.strip():
                raise HTTPException(400, f"question {i + 1}: write an answer")
            rows.append((i, v.strip()[:1000], None))
    for i, value, correct in rows:
        _q("""INSERT INTO answers (checkpoint_id, user, q, value, correct, ts) VALUES (?, ?, ?, ?, ?, ?)
              ON CONFLICT (checkpoint_id, user, q) DO UPDATE SET value = excluded.value, correct = excluded.correct, ts = excluded.ts""",
           (cp["id"], user, i, value, correct, _now()))
    return _student_view(_checkpoint(spot), spot, user)


# ---- Admin: usage dashboard and the checkpoint builder (ADMIN_USERS only) ----

def _admin(request: Request) -> str:
    user = _user(request)
    if user not in ADMIN_USERS:
        raise HTTPException(403, "admins only")
    return user


@lru_cache(maxsize=4)
def _scan(html_dir: str) -> tuple[dict, list]:
    """Page titles and Lecture checkpoint markers, read once from the built book (it doesn't change while running)."""
    titles, spots = {}, []
    if os.path.isdir(html_dir):
        for name in sorted(os.listdir(html_dir)):
            if not name.endswith(".html"):
                continue
            text = open(os.path.join(html_dir, name), encoding="utf-8", errors="ignore").read()
            stem = name[:-5]
            t = re.search(r"<title>(.*?)</title>", text, re.S)
            titles[stem] = html.unescape(t.group(1)).split(" — ")[0].strip() if t else stem
            for spot, label in re.findall(r'data-spot="([\w-]+)"\s+data-label="([^"]*)"', text):
                spots.append({"spot": spot, "label": html.unescape(label), "page": stem})
    return titles, spots


@app.get("/admin")
def admin_page(request: Request):
    _admin(request)
    return HTMLResponse(ADMIN_HTML)


@app.get("/admin/api/data")
def admin_data(request: Request, days: int = 7):
    """Everything the dashboard draws, in one call. Admin accounts are left out of every student number."""
    _admin(request)
    titles, spots = _scan(os.path.abspath(HTML_DIR))
    since = (_today() - timedelta(days=max(days, 1) - 1)).isoformat() if days > 0 else ""
    admins = tuple(sorted(ADMIN_USERS)) or ("",)
    notadmin = f"user NOT IN ({','.join('?' * len(admins))})"
    names = {u: n for _, u, n in _signins() if n}

    def ev(sql: str, args: tuple = ()) -> list[sqlite3.Row]:
        return _q(sql.replace("{NOTADMIN}", notadmin), (*admins, *args))

    total = ev("SELECT COUNT(DISTINCT user) FROM events WHERE {NOTADMIN}")[0][0]
    k = ev("""SELECT COUNT(DISTINCT user), SUM(kind = 'cell_run'), SUM(kind = 'model_call'), COALESCE(SUM(tokens), 0)
              FROM events WHERE {NOTADMIN} AND ts >= ?""", (since,))[0]
    daily = [dict(r) for r in ev("""SELECT substr(ts, 1, 10) AS day, COUNT(DISTINCT user) AS users FROM events
                                    WHERE {NOTADMIN} AND ts >= ? GROUP BY day ORDER BY day""", (since,))]
    chapters = [{**dict(r), "title": titles.get(r["page"], r["page"])} for r in ev(
        """SELECT page, COUNT(DISTINCT CASE WHEN kind = 'page_view' THEN user END) AS readers,
                  SUM(kind = 'page_view') AS views, SUM(kind = 'cell_run') AS cell_runs
           FROM events WHERE {NOTADMIN} AND page IS NOT NULL AND ts >= ? GROUP BY page""", (since,))]
    chapters.sort(key=lambda c: (not c["title"][:1].isdigit(), c["title"]))  # numbered chapters in reading order, then the rest

    cps = []
    for cp in _q("SELECT * FROM lecture_checkpoints ORDER BY COALESCE(opened_at, '') DESC, id DESC"):
        qs = json.loads(cp["questions"])
        ans = [dict(r) for r in _q("SELECT user, q, value, correct, ts FROM answers WHERE checkpoint_id = ? ORDER BY ts",
                                   (cp["id"],)) if r["user"] not in ADMIN_USERS]
        for a in ans:
            a["name"] = names.get(a["user"], "")
        label = next((s["label"] for s in spots if s["spot"] == cp["spot"]), cp["spot"] + " (marker not found in the book)")
        cps.append({**{c: cp[c] for c in ("id", "spot", "title", "status", "opened_at", "closed_at", "live")},
                    "label": label, "questions": qs, "answers": ans, "answered": len({a["user"] for a in ans})})
    last = next((c for c in cps if c["opened_at"]), None)

    opened = [c for c in cps if c["opened_at"]]
    students = []
    for r in ev("""SELECT user, MAX(ts) AS last_seen, COUNT(DISTINCT substr(ts, 1, 10)) AS days,
                          SUM(kind = 'page_view') AS pages, SUM(kind = 'cell_run') AS cell_runs, COALESCE(SUM(tokens), 0) AS tokens
                   FROM events WHERE {NOTADMIN} GROUP BY user ORDER BY last_seen DESC"""):
        mine = [a for c in opened for a in c["answers"] if a["user"] == r["user"]]
        scored = [a["correct"] for a in mine if a["correct"] is not None]
        students.append({**dict(r), "name": names.get(r["user"], ""),
                         "checkpoints": len({c["id"] for c in opened if any(a["user"] == r["user"] for a in c["answers"])}),
                         "score": round(100 * sum(scored) / len(scored)) if scored else None})
    return {"days": days, "since": since, "total_students": total, "active": k[0], "cell_runs": k[1] or 0,
            "model_calls": k[2] or 0, "tokens": k[3], "daily": daily, "chapters": chapters,
            "last_checkpoint": {"title": last["title"], "answered": last["answered"]} if last else None,
            "checkpoints": cps, "checkpoints_opened": len(opened), "students": students, "spots": spots}


def _clean_questions(raw) -> list[dict]:
    if not isinstance(raw, list) or not 1 <= len(raw) <= 20:
        raise HTTPException(400, "add between 1 and 20 questions")
    out = []
    for n, q in enumerate(raw, 1):
        prompt = str((q or {}).get("prompt", "")).strip()
        if not prompt or len(prompt) > 1000:
            raise HTTPException(400, f"question {n}: write the question")
        explain = str(q.get("explain") or "").strip()[:1000]  # optional; students see it after the checkpoint closes
        if q.get("kind") == "short":
            out.append({"prompt": prompt, "kind": "short", "choices": [], "correct": None, "explain": explain})
            continue
        choices = [str(c).strip() for c in q.get("choices") or [] if str(c).strip()]
        if not 2 <= len(choices) <= 8:
            raise HTTPException(400, f"question {n}: give 2 to 8 choices")
        correct = q.get("correct")
        if not isinstance(correct, int) or not 0 <= correct < len(choices):
            raise HTTPException(400, f"question {n}: mark the correct choice")
        out.append({"prompt": prompt, "kind": "mc", "choices": choices, "correct": correct, "explain": explain})
    return out


@app.post("/admin/api/checkpoints")
async def admin_save(request: Request):
    """Create a checkpoint, or edit one nobody has answered yet (so results always match what was asked)."""
    _admin(request)
    body = await request.json()
    title, spot = str(body.get("title", "")).strip(), str(body.get("spot", ""))
    if not title or len(title) > 200:
        raise HTTPException(400, "give the checkpoint a title")
    if spot not in {s["spot"] for s in _scan(os.path.abspath(HTML_DIR))[1]}:
        raise HTTPException(400, "pick a spot from the book")
    questions = json.dumps(_clean_questions(body.get("questions")))
    try:
        if body.get("id"):
            if _q("SELECT 1 FROM answers WHERE checkpoint_id = ? LIMIT 1", (body["id"],)):
                raise HTTPException(409, "students have already answered; its questions are locked")
            _q("UPDATE lecture_checkpoints SET title = ?, spot = ?, questions = ?, live = NULL WHERE id = ?", (title, spot, questions, body["id"]))
        else:
            _q("INSERT INTO lecture_checkpoints (spot, title, questions) VALUES (?, ?, ?)", (spot, title, questions))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "that spot already has a checkpoint")
    return {"ok": True}


@app.post("/admin/api/checkpoints/{cp_id}/status")
async def admin_status(cp_id: int, request: Request):
    _admin(request)
    """open: start at question 1 (a reopen resumes where it stopped); next: lock the live question and
    release the following one; closed: lock everything and reveal the answers."""
    action = (await request.json()).get("status")
    rows = _q("SELECT status, live, questions FROM lecture_checkpoints WHERE id = ?", (cp_id,))
    if not rows:
        raise HTTPException(404, "no such checkpoint")
    cp = rows[0]
    if action == "open":
        _q("UPDATE lecture_checkpoints SET status = 'open', opened_at = ?, live = COALESCE(live, 0) WHERE id = ?", (_now(), cp_id))
    elif action == "next":
        if cp["status"] != "open" or (cp["live"] or 0) + 1 >= len(json.loads(cp["questions"])):
            raise HTTPException(409, "no next question: close the checkpoint instead")
        _q("UPDATE lecture_checkpoints SET live = live + 1 WHERE id = ?", (cp_id,))
    elif action == "closed":
        _q("UPDATE lecture_checkpoints SET status = 'closed', closed_at = ? WHERE id = ?", (_now(), cp_id))
    else:
        raise HTTPException(400, "status is open, next or closed")
    return {"ok": True}


if os.path.isdir(HTML_DIR):
    app.mount("/", StaticFiles(directory=HTML_DIR, html=True), name="site")
