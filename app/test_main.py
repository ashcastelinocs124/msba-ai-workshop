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
