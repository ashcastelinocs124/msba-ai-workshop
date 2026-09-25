"""ponytail: one runnable check. `uv run --with fastapi --with httpx --with pytest pytest app/test_main.py`"""
import httpx
from fastapi.testclient import TestClient

import app.main as m

import base64
import json

H = {"x-ms-client-principal-name": "Student@illinois.edu"}
CLAIMS = base64.b64encode(json.dumps(
    {"claims": [{"typ": "name", "val": "Priya Natarajan"}, {"typ": "preferred_username", "val": "student@illinois.edu"}]}
).encode()).decode()
H_NAMED = {**H, "x-ms-client-principal": CLAIMS}


def fake_transport(status=200, usage=900):
    def handler(request: httpx.Request):
        assert request.url.path.endswith("/openai/v1/chat/completions")
        assert request.headers["authorization"] == "Bearer k"
        import json
        body = json.loads(request.read())
        assert body["model"] == "gpt-5-mini" and body["max_completion_tokens"] == 1024
        return httpx.Response(status, json={"choices": [{"message": {"role": "assistant", "content": "hi"}}],
                                            "usage": {"total_tokens": usage}, "model": "gpt-5-mini"})
    return httpx.MockTransport(handler)


def test_proxy(monkeypatch, tmp_path):
    m.ENDPOINT, m.API_KEY, m.DAILY_CAP = "https://x.cognitiveservices.azure.com", "k", 1000
    m.APP_DB, m.SIGNIN_LOG = str(tmp_path / "app.db"), str(tmp_path / "signins.csv")   # fresh token log
    real = httpx.AsyncClient
    monkeypatch.setattr(m.httpx, "AsyncClient", lambda **kw: real(transport=fake_transport(), **kw))
    c = TestClient(m.app)
    assert c.get("/api/whoami").status_code == 401                      # no Easy Auth header
    assert c.post("/api/chat", json={"messages": []}, headers=H).status_code == 200
    who = c.get("/api/whoami", headers=H).json()
    assert who == {"name": "student@illinois.edu", "user": "student@illinois.edu", "used": 900, "cap": 1000, "model": "gpt-5-mini"}
    # with the richer Easy Auth claims header, the pill shows the real name instead of the email
    named = c.get("/api/whoami", headers=H_NAMED).json()
    assert named["name"] == "Priya Natarajan" and named["user"] == "student@illinois.edu"
    assert c.post("/api/chat", json={"messages": [], "max_tokens": 99999}, headers=H).status_code == 200
    assert c.post("/api/chat", json={"messages": []}, headers=H).status_code == 429   # cap reached


def test_signins(tmp_path):
    m.SIGNIN_LOG, m.APP_DB = str(tmp_path / "data" / "signins.csv"), str(tmp_path / "app.db")
    m.ADMIN_USERS = {"admin@illinois.edu"}
    m._seen.clear()
    c = TestClient(m.app)
    ADMIN = {"x-ms-client-principal-name": "admin@illinois.edu"}
    assert c.get("/api/whoami", headers=H_NAMED).status_code == 200
    assert c.get("/api/whoami", headers=H_NAMED).status_code == 200      # same person, same day: one row
    assert open(m.SIGNIN_LOG).read().count("\n") == 1
    m._seen.clear()                                                        # a restart forgets; the reader still dedupes
    assert c.get("/api/whoami", headers=H).status_code == 200
    assert c.get("/admin/signins").status_code == 401                      # not signed in
    assert c.get("/admin/signins", headers=H).status_code == 403           # signed in, not an admin
    page = c.get("/admin/signins", headers=ADMIN)
    assert page.status_code == 200 and "1 people, 1 person-days" in page.text and "Priya Natarajan" in page.text
    csv_ = c.get("/admin/signins?format=csv", headers=ADMIN).text
    assert csv_.startswith("day,user,name\n") and csv_.count("student@illinois.edu") == 1


def test_locked_pages(tmp_path):
    (tmp_path / "ch02-prompt-engineering.html").write_text("chapter two")
    m.ADMIN_USERS, m.LOCKED_PAGES = {"admin@illinois.edu"}, {"ch02-prompt-engineering"}
    app = m.FastAPI()
    app.middleware("http")(m.lock_pages)
    app.mount("/", m.StaticFiles(directory=tmp_path, html=True))
    c = TestClient(app)
    locked = c.get("/ch02-prompt-engineering.html", headers=H)
    assert locked.status_code == 403 and "not open yet" in locked.text and "chapter two" not in locked.text
    assert c.get("/_sources/ch02-prompt-engineering.md", headers=H).status_code == 403
    assert c.get("/ch02-prompt-engineering.html", headers={"x-ms-client-principal-name": "Admin@illinois.edu"}).text == "chapter two"
    m.LOCKED_PAGES = set()                                                 # LOCKED_PAGES="" opens it to everyone
    assert c.get("/ch02-prompt-engineering.html", headers=H).text == "chapter two"


ADMIN = {"x-ms-client-principal-name": "admin@illinois.edu"}
H2 = {"x-ms-client-principal-name": "other@illinois.edu"}
Q = [{"prompt": "Request #7104?", "kind": "mc", "choices": ["Approve", "Decline", "Hold"], "correct": 2,
      "explain": "Deere was published on 6 days ago; the blackout is 14."},
     {"prompt": "No clause found: what then?", "kind": "short"}]


def _checkpoint_app(tmp_path):
    book = tmp_path / "html"
    book.mkdir()
    (book / "ch03-memory-rag.html").write_text(
        '<title>3. Memory Retrieval and RAG — AI · ML · Markets</title>'
        '<div class="wk-lcp" data-spot="ch03-retrieval" data-label="Chapter 3 · after the preview"></div>')
    m.HTML_DIR, m.APP_DB, m.SIGNIN_LOG = str(book), str(tmp_path / "app.db"), str(tmp_path / "signins.csv")
    m.ADMIN_USERS = {"admin@illinois.edu"}
    m._seen.clear()
    return TestClient(m.app)


def test_events(tmp_path):
    c = _checkpoint_app(tmp_path)
    assert c.post("/api/events", json={"kind": "page_view", "page": "ch01-agent-loop"}).status_code == 401
    assert c.post("/api/events", json={"kind": "page_view", "page": "ch01-agent-loop"}, headers=H).status_code == 200
    assert c.post("/api/events", json={"kind": "cell_run", "page": "ch01-agent-loop"}, headers=H).status_code == 200
    assert c.post("/api/events", json={"kind": "model_call", "page": "x"}, headers=H).status_code == 400   # server-only kind
    assert c.post("/api/events", json={"kind": "page_view", "page": "<script>"}, headers=H).status_code == 400
    c.get("/api/whoami", headers=H)
    c.get("/api/whoami", headers=ADMIN)                                    # admins are left out of the numbers
    assert c.get("/admin/api/data", headers=H).status_code == 403
    d = c.get("/admin/api/data", headers=ADMIN).json()
    assert d["total_students"] == 1 and d["active"] == 1 and d["cell_runs"] == 1
    assert d["chapters"] == [{"page": "ch01-agent-loop", "readers": 1, "views": 1, "cell_runs": 1, "title": "ch01-agent-loop"}]
    assert d["students"][0]["user"] == "student@illinois.edu" and d["students"][0]["days"] == 1
    assert d["spots"] == [{"spot": "ch03-retrieval", "label": "Chapter 3 · after the preview", "page": "ch03-memory-rag"}]


def test_lecture_checkpoint(tmp_path):
    c = _checkpoint_app(tmp_path)
    url = "/api/checkpoints/ch03-retrieval"
    status = lambda to: c.post(f"/admin/api/checkpoints/{cp['id']}/status", json={"status": to}, headers=ADMIN)
    assert c.get(url, headers=H).json() == {"spot": "ch03-retrieval", "status": "none"}
    assert c.post("/admin/api/checkpoints", json={"title": "Retrieval", "spot": "ch03-retrieval", "questions": Q}, headers=H).status_code == 403
    assert c.post("/admin/api/checkpoints", json={"title": "Retrieval", "spot": "nowhere", "questions": Q}, headers=ADMIN).status_code == 400
    bad = [{**Q[0], "correct": 7}]
    assert c.post("/admin/api/checkpoints", json={"title": "Retrieval", "spot": "ch03-retrieval", "questions": bad}, headers=ADMIN).status_code == 400
    assert c.post("/admin/api/checkpoints", json={"title": "Retrieval", "spot": "ch03-retrieval", "questions": Q}, headers=ADMIN).status_code == 200
    cp = c.get("/admin/api/data", headers=ADMIN).json()["checkpoints"][0]

    view = c.get(url, headers=H).json()                                     # closed before class: nothing to read ahead
    assert view["status"] == "closed" and not view["revealed"] and view["questions"] == []
    assert c.post(url, json={"answers": {"0": 2}}, headers=H).status_code == 409
    assert status("next").status_code == 409                               # can't advance a closed checkpoint

    assert status("open").status_code == 200                               # question 1 only
    view = c.get(url, headers=H).json()
    assert view["live"] == 0 and view["total"] == 2 and len(view["questions"]) == 1 and "correct" not in view["questions"][0]
    assert c.post(url, json={"answers": {"0": 9}}, headers=H).status_code == 400
    assert c.post(url, json={"answers": {"1": "Too early"}}, headers=H).status_code == 409   # question 2 not open yet
    assert c.post(url, json={"answers": {"0": 0}}, headers=H).json()["mine"] == {"0": "0"}
    assert c.post(url, json={"answers": {"0": 2}}, headers=H).status_code == 200            # change of mind overwrites
    c.post(url, json={"answers": {"0": 1}}, headers=H2)

    assert status("next").status_code == 200                               # question 1 locks, question 2 appears
    view = c.get(url, headers=H).json()
    assert view["live"] == 1 and len(view["questions"]) == 2 and "correct" not in view["questions"][0]
    assert c.post(url, json={"answers": {"0": 0}}, headers=H).status_code == 409             # locked
    assert c.post(url, json={"answers": {"1": "Send it to compliance"}}, headers=H).status_code == 200
    assert status("next").status_code == 409                               # it was the last question
    edit = {"id": cp["id"], "title": "Changed", "spot": "ch03-retrieval", "questions": Q}
    assert c.post("/admin/api/checkpoints", json=edit, headers=ADMIN).status_code == 409   # locked once answered

    assert status("closed").status_code == 200
    assert c.post(url, json={"answers": {"1": "Later"}}, headers=H).status_code == 409
    view = c.get(url, headers=H).json()
    assert view["revealed"] and view["live"] is None and len(view["questions"]) == 2
    assert view["questions"][0]["correct"] == 2 and view["mine"] == {"0": "2", "1": "Send it to compliance"}
    assert view["questions"][0]["explain"].startswith("Deere was published") and view["questions"][1]["explain"] == ""
    cp = c.get("/admin/api/data", headers=ADMIN).json()["checkpoints"][0]
    assert cp["answered"] == 2 and len(cp["answers"]) == 3
    assert sorted(a["correct"] for a in cp["answers"] if a["q"] == 0) == [0, 1]


def test_old_database_gains_live_column(tmp_path):
    import sqlite3
    db = tmp_path / "old.db"
    con = sqlite3.connect(db)                                              # the table as first deployed, without `live`
    con.execute("CREATE TABLE lecture_checkpoints (id INTEGER PRIMARY KEY, spot TEXT UNIQUE NOT NULL, title TEXT NOT NULL,"
                " status TEXT NOT NULL DEFAULT 'closed', questions TEXT NOT NULL, opened_at TEXT, closed_at TEXT)")
    con.execute("INSERT INTO lecture_checkpoints (spot, title, questions) VALUES ('ch03-retrieval', 'Old', ?)", (json.dumps(Q),))
    con.commit(); con.close()
    m.APP_DB = str(db)
    assert m._q("SELECT live FROM lecture_checkpoints")[0][0] is None
