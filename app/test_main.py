"""ponytail: one runnable check. `uv run --with fastapi --with httpx --with pytest pytest app/test_main.py`"""
import httpx
from fastapi.testclient import TestClient

import app.main as m

H = {"x-ms-client-principal-name": "Student@illinois.edu"}


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
    assert who == {"user": "student@illinois.edu", "used": 900, "cap": 1000, "model": "gpt-5-mini"}
    assert c.post("/api/chat", json={"messages": [], "max_tokens": 99999}, headers=H).status_code == 200
    assert c.post("/api/chat", json={"messages": []}, headers=H).status_code == 429   # cap reached
