from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_json():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_page_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "Wireless Site Survey Tool" in r.text
