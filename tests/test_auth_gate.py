"""Phase 13e — Mode A unchanged; Mode B shared-password gate."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core import config
from app.main import create_app


def _mode_b_app(monkeypatch: pytest.MonkeyPatch, password: str = "correct-horse") -> TestClient:
    monkeypatch.setattr(config.settings, "ACCESS_MODE", "shared_password")
    monkeypatch.setattr(config.settings, "SHARED_ACCESS_PASSWORD", password)
    monkeypatch.setattr(config.settings, "SECRET_KEY", "test-secret-key")
    monkeypatch.setattr(config.settings, "APP_ENV", "development")
    return TestClient(create_app())


def _mode_a_app(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(config.settings, "ACCESS_MODE", "tailscale")
    monkeypatch.setattr(config.settings, "SHARED_ACCESS_PASSWORD", "")
    return TestClient(create_app())


def test_mode_a_no_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mode_a_app(monkeypatch)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    home = client.get("/", follow_redirects=False)
    assert home.status_code == 200
    assert "Wireless Site Survey Tool" in home.text

    # Mode A never forces /login; unused auth routes redirect home (no session stack).
    login = client.get("/login", follow_redirects=False)
    assert login.status_code == 303
    assert login.headers["location"] == "/"


def test_mode_b_health_exempt(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mode_b_app(monkeypatch)
    r = client.get("/health", follow_redirects=False)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_mode_b_unauthenticated_redirects_to_login(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mode_b_app(monkeypatch)
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_mode_b_wrong_password_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mode_b_app(monkeypatch)
    r = client.post("/login", data={"password": "wrong", "next": "/"}, follow_redirects=False)
    assert r.status_code == 200
    assert "Incorrect password" in r.text

    gated = client.get("/", follow_redirects=False)
    assert gated.status_code == 303
    assert gated.headers["location"] == "/login"


def test_mode_b_correct_password_admits(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mode_b_app(monkeypatch, password="s3cret!")
    r = client.post(
        "/login",
        data={"password": "s3cret!", "next": "/"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/"
    assert "session" in r.cookies

    home = client.get("/", follow_redirects=False)
    assert home.status_code == 200
    assert "Wireless Site Survey Tool" in home.text


def test_mode_b_logout_clears_session(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mode_b_app(monkeypatch)
    client.post("/login", data={"password": "correct-horse", "next": "/"})
    assert client.get("/", follow_redirects=False).status_code == 200

    out = client.post("/logout", follow_redirects=False)
    assert out.status_code == 303
    assert out.headers["location"] == "/login"

    gated = client.get("/", follow_redirects=False)
    assert gated.status_code == 303
    assert gated.headers["location"] == "/login"


def test_mode_b_login_page_open(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mode_b_app(monkeypatch)
    r = client.get("/login", follow_redirects=False)
    assert r.status_code == 200
    assert "Sign in" in r.text
