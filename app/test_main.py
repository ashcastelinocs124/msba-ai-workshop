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


def test_proxy(monkeypatch):
    m.ENDPOINT, m.API_KEY, m.DAILY_CAP = "https://x.cognitiveservices.azure.com", "k", 1000
    m._usage.clear()
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
    m.SIGNIN_LOG = str(tmp_path / "data" / "signins.csv")
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
